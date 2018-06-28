""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    This script monitors the serial port and captures the data in chunks of 64
    bytes as the Arduino sends it at its maximum transfer rate. It separates the
    data out of the chunk into arrays for each electrode and plots it live on
    the screen.

    This script currently only saves data once a desired amount of seconds has
    passed, so it cannot be run indefinitely without running out of memory.
"""

#TODO:
#      -end calibration if device disconnected
#      -make it more robust, if the window is closed or keyboard interrupt etc.
#       cause right now erroring is really the only way it exits...

# Imports
import time
import sys
sys.path.append('../')

import multiprocessing as mp
import numpy as np

import emgCapture

import userGuide
import calibration
import monitor

import platform

isPi = (platform.machine() == 'armv7l')
notPi = (isPi == False)

if notPi:
    import emgPlot

from constants import electrodeNum, synergyNum


def run(q, deviceConnected=True): # main program logic
    op = 0

    W = np.zeros((electrodeNum,synergyNum))
    baselines = np.zeros(electrodeNum)
    maxes = np.full(electrodeNum,256*256)

    if notPi:
        plotter = emgPlot.plotManager()

    calibrated = False

    while True:
        if op == 0:
            userGuide.menuPrompt()
            op = input("Option: ")
            try:
                tmp = int(op)
                op = tmp
            except:
                pass

        elif op == 1 and deviceConnected: # calibrate
            W, baselines, maxes = calibration.calibrate(q, plotter)
            calibrated = True

            print("\nCalibration complete. Synergy matrix W:")
            print(W)
            print("\nBaselines:")
            print(baselines)
            print("\nMax values:")
            print(maxes)

            toSave = input("\nWould you like to save this matrix? (y/n): ")

            if toSave == "y":
                np.save("calibrationMatrix.npy",W)
                np.save("baselines.npy", baselines)
                np.save("maxes.npy",maxes)
                print("Matrix saved.")
            else:
                print("Matrix not saved.")

            op = 0
        elif op == 2: # load
            try:
                W = np.load("calibrationMatrix.npy")
                baselines = np.load("baselines.npy")
                maxes = np.load("maxes.npy")
                calibrated = True
                print("Calibration matrix loaded.")
            except:
                print("Error: Calibration matrix not found!")

            op = 0
        elif op == 3 and deviceConnected:
            if calibrated:
                monitor.monitor(q, W, baselines, maxes, plotter)
            else:
                print("Error: Calibrate or load a calibration matrix first.")

            op = 0
        elif op == 4: # run test
            W = calibration.calibrate(q, plotter, testmode=True)
            print(W)
            op = 0
        elif op == 5: # quit
            userGuide.endMessage()
            break
        else:
            print("Invalid command.\n")
            op = 0


if __name__ == "__main__":
    q = mp.Queue(60)   # let a maximum of ~100ms of data pile up in the queue
    p = mp.Process(target=emgCapture.capture, args=(q,))
    #data capture process so that it's not blocked by program logic.

    print("Connecting to device...")        
    p.start()
    message = q.get()

    if message == "Connection established.":
        print(message)
        run(q)

    else:
        print("Connection failed!")
        run(q,False)
        sys.exit()

    p.terminate()
    p.join()
    sys.exit()
