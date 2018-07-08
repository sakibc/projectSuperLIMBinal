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

# isPi = (platform.machine() == 'armv7l')
isPi = True # for dev purposes
notPi = (isPi == False)

if notPi:
    import emgPlot
else:
    import webApp

from constants import electrodeNum, synergyNum


def run(q, deviceConnected=True): # main program logic
    op = 0

    W = np.zeros((electrodeNum,synergyNum))
    baselines = np.zeros(electrodeNum)
    maxes = np.full(electrodeNum,256*256)

    # if is pi, start up webserver and treat it as the plotter, input, and output
    # it's not worth the time to design it better to work nicely in both modes
    # so I'll just rewrite a lot of the non-interactive mode here
    # start a queue to get commands from the server
    # every cycle, get a command from the queue
    # if it's valid, enter a mode and tell the webserver that it's all good

    # if not a pi, start up emgplot and treat it as the plotter
    # get a command from the input queue

    calibrated = False

    if isPi:
        serverq = mp.Queue()
        sampleq = mp.Queue()
        # app.run(host='0.0.0.0') # insecure, but it works for now
        webApp.start(serverq, sampleq)
        webPlotter = webApp.webPlotDataManager(sampleq)
        # webApp.runApp()

        while True:
            op = serverq.get(block=True)
            # print(op)
            if op == "getSystemStatus":
                serverq.put((deviceConnected,False,calibrated))
            elif op == "startCalibration":
                W, baselines, maxes = calibration.calibrate(q, webPlotter, isPi=True)

                print("\nCalibration complete. Synergy matrix W:")
                print(W)
                print("\nBaselines:")
                print(baselines)
                print("\nMax values:")
                print(maxes)

                np.save("calibrationMatrix.npy",W)
                np.save("baselines.npy", baselines)
                np.save("maxes.npy",maxes)
                print("Matrix saved.")

            elif op == "loadMatrix":
                try:
                    W = np.load("calibrationMatrix.npy")
                    baselines = np.load("baselines.npy")
                    maxes = np.load("maxes.npy")
                    calibrated = True
                    serverq.put((True, False))
                except:
                    serverq.put((False, True))

            elif op == "startMonitor":
                pass
            elif op == "stopMonitor":
                pass
            elif op == "rebooting...":
                print("Reboot command received.")

    elif notPi:   # interactive main loop
        plotter = emgPlot.plotManager()
    
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
                break
            else:
                print("Invalid command.\n")
                op = 0

    userGuide.endMessage()

if __name__ == "__main__":
    q = mp.Queue(60)   # let a maximum of ~100ms of data pile up in the queue
    p = mp.Process(target=emgCapture.capture, args=(q,))
    #data capture process so that it's not blocked by program logic.

    if isPi:
        print("Starting Project SuperLIMBinal in headless mode...")
    else:
        print("Starting Project SuperLIMBinal in interactive mode...")

    print("\nConnecting to device...")        
    p.start()
    message = q.get()

    if message == "Connection established.":
        print(message)
        run(q)

    else:
        print("Connection failed!")
        run(q,False)

    p.terminate()
    p.join()
    sys.exit()
