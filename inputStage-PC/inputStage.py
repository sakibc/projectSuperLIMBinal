""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
"""

#TODO:
#      -end calibration if device disconnected
#      -make it more robust, if the window is closed or keyboard interrupt etc.
#       cause right now erroring is really the only way it exits...

# Imports
import argparse
import platform
import serial.tools.list_ports
import sys
import time

import multiprocessing as mp
import numpy as np

import calibration
import emgCapture
import monitor
import userGuide
import webApp

from constants import electrodeNum, synergyNum
from helpers import clearQueue

isPi = (platform.machine() == 'armv7l') # check if running on a pi
notPi = (isPi == False)

# check for interactive mode command-line argument

# NOTE: interactive mode doesn't work properly in macOS >= High Sierra without
# first running "export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES"
# due to changes made by Apple to make fork() safer

parser = argparse.ArgumentParser(
    description='Project SuperLIMBinal Management Program')
parser.add_argument('-i', '--interactive', action='store_true')
args = parser.parse_args()

if args.interactive and notPi:
    headless = False
    import emgPlot
else:
    headless = True

# setup necessary queues and processes
motionq = mp.Queue()
armStatusq = mp.Queue()
webApp.startOutput(motionq, armStatusq)

if headless:
    print("Starting Project SuperLIMBinal in headless mode...")

    serverq = mp.Queue()
    sampleq = mp.Queue()

    webApp.start(serverq, sampleq)
    webPlotter = webApp.webPlotDataManager(sampleq)
else:
    print("Starting Project SuperLIMBinal in interactive mode...")

    plotter = emgPlot.plotManager()

if isPi:
    port = '/dev/ttyUSB0'   # com port for pi
else:
    port = None  # if on a real computer it'll figure it out by itself...

def checkArmStatus(armConnected):
    while armStatusq.empty() == False:
        armConnected = armStatusq.get()
    
    return armConnected

def run(): # main program logic
    # let a maximum of ~100ms (60 sample sets) of data pile up in the queue
    q = mp.Queue(60)
    # data capture is done in separate process so that it's not blocked by program logic.
    deviceStatusq = mp.Queue()

    def checkDeviceStatus(deviceConnected):
        while deviceStatusq.empty() == False:
            deviceConnected = deviceStatusq.get()

        return deviceConnected

    p = mp.Process(target=emgCapture.capture, args=(q, deviceStatusq, port))

    deviceConnected = False
    print("\nConnecting to device...")
    p.start()
    message = q.get()

    if message == "Connection established.":
        print(message)
        deviceConnected = True
    else:
        print("Connection failed!")
        p.join()

    op = 0

    W = np.zeros((electrodeNum,synergyNum))
    baselines = np.zeros(electrodeNum)
    maxes = np.full(electrodeNum,256*256)

    calibrated = False
    armConnected = False

    while True:
        if deviceConnected:
            if headless:
                op = serverq.get(block=True)

                if op == "getSystemStatus":
                    armConnected = checkArmStatus(armConnected)
                    deviceConnected = checkDeviceStatus(deviceConnected)
                    serverq.put((deviceConnected,armConnected,calibrated))

                elif op == "startCalibration":
                    W, baselines, maxes = calibration.calibrate(q, webPlotter, headless=True, server=serverq)

                    if W != "failed!":
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

                        calibrated = True

                        serverq.put("done")
                        time.sleep(1)

                elif op == "loadMatrix":
                    # print("loading matrix...")
                    try:
                        W = np.load("calibrationMatrix.npy")
                        baselines = np.load("baselines.npy")
                        maxes = np.load("maxes.npy")
                        calibrated = True
                        serverq.put((True, False))
                    except:
                        serverq.put((False, True))

                elif op == "startMonitor":
                    monitor.monitor(q, motionq, W, baselines, maxes, webPlotter, server=serverq, isPi=True)
                elif op == "rebooting...":
                    print("Rebooting...")

        #     else:   # interactive main loop
        #         if op == 0:
        #             userGuide.menuPrompt()
        #             op = input("Option: ")
        #             try:
        #                 tmp = int(op)
        #                 op = tmp
        #             except:
        #                 pass

        #         elif op == 1 and deviceConnected: # calibrate
        #             W, baselines, maxes = calibration.calibrate(q, plotter)
        #             calibrated = True

        #             print("\nCalibration complete. Synergy matrix W:")
        #             print(W)
        #             print("\nBaselines:")
        #             print(baselines)
        #             print("\nMax values:")
        #             print(maxes)

        #             toSave = input("\nWould you like to save this matrix? (y/n): ")

        #             if toSave == "y":
        #                 np.save("calibrationMatrix.npy",W)
        #                 np.save("baselines.npy", baselines)
        #                 np.save("maxes.npy",maxes)
        #                 print("Matrix saved.")
        #             else:
        #                 print("Matrix not saved.")

        #             op = 0
        #         elif op == 2: # load
        #             try:
        #                 W = np.load("calibrationMatrix.npy")
        #                 baselines = np.load("baselines.npy")
        #                 maxes = np.load("maxes.npy")
        #                 calibrated = True
        #                 print("Calibration matrix loaded.")
        #             except:
        #                 print("Error: Calibration matrix not found!")

        #             op = 0
        #         elif op == 3 and deviceConnected:
        #             if calibrated:
        #                 monitor.monitor(q, None, W, baselines, maxes, plotter)
        #             else:
        #                 print("Error: Calibrate or load a calibration matrix first.")

        #             op = 0
        #         elif op == 4: # run test
        #             W = calibration.calibrate(q, plotter, testmode=True)
        #             print(W)
        #             op = 0
        #         elif op == 5: # quit
        #             break
        #         else:
        #             print("Invalid command.\n")
        #             op = 0
        else:
            break

    p.terminate()
    p.join()



if __name__ == "__main__":
    while True:
        try:
            run()
            print("Retrying in 10 seconds...\n")
            time.sleep(10)
        except KeyboardInterrupt:
            print("\nEnding program execution...")
            break
        except Exception as e:
            print("Program died!")
            print(e)
            print("Retrying in 10 seconds...\n")
            time.sleep(10)

    time.sleep(0.1)
    userGuide.endMessage()
    sys.exit()
