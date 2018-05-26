""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    This script monitors the serial port and captures the data in chunks of 64
    bytes as the Arduino sends it at its maximum transfer rate. It separates the
    data out of the chunk into arrays for each electrode and plots it live on
    the screen.

    This script currently only saves data once a desired amount of seconds has
    passed, so it cannot be run indefinitely without running out of memory.
"""

#TODO: -get rid of magic numbers...
#      -end calibration if device disconnected
#      -make the animation of the graphs driven by data rather than by time?

# Imports
import time
import sys

import multiprocessing as mp
import numpy as np

import emgCapture
import userGuide
import calibration
import monitor

from constants import *
from helpers import *

def run(q, deviceConnected=True): # main program logic
    op = 0
    W = np.zeros((8,4))
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
            W = calibration.calibrate(q)
            calibrated = True

            print("\nCalibration complete. Synergy matrix W:")
            print(W)
            toSave = input("\nWould you like to save this matrix? (y/n): ")

            if toSave == "y":
                np.save("calibrationMatrix.npy",W)
                print("Matrix saved.")
            else:
                print("Matrix not saved.")

            op = 0
        elif op == 2: # load
            try:
                W = np.load("calibrationMatrix.npy")
                calibrated = True
                print("Calibration matrix loaded.")
            except:
                print("Error: Calibration matrix not found!")

            op = 0
        elif op == 3:
            if calibrated:
                monitor.monitor(q, W)
            else:
                print("Error: Calibrate or load a calibration matrix first.")

            op = 0
        elif op == 4: # run test
            W = calibration.calibrate(q, True)
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
