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
#      -try switching from matplotlib to pyqtgraph to plot faster...

# Imports
import time
import sys

import multiprocessing as mp
import numpy as np
import scipy.io
import scipy.signal

import emgCapture
import emgPlot
import userGuide

electrodeNum = L = 8
synergyNum = N = 4
Fs = 4808

def clearQueue(q):
    while q.empty() == False:
        q.get()

def getData(collectionTime, q):
    dat = np.zeros((collectionTime*Fs,8))
    return dat

def calibrate(q):
    W = np.ones((electrodeNum, synergyNum))
    print("Starting calibration. Follow the instructions as they appear.")
    promptp = mp.Process(target=userGuide.calibration)

    clearQueue(q)  # let's empty the queue first so we can grab the latest data
    promptp.start()
    calibrationData = getData(45, q)   # capture 45 seconds of data

    print("Processing data...")

    return W

def run(q): # main program logic
    input("Press enter to start calibration.")

    W = calibrate(q)
    print(W)


if __name__ == "__main__":
    q = mp.Queue(60)   # let a maximum of ~100ms of data pile up in the queue
    p = mp.Process(target=emgCapture.capture, args=(q,))
    #data capture process so that it's not blocked by program logic.

    print("Connecting to device...")        
    p.start()
    message = q.get()

    if message == "Connection established.":
        run(q)

    else:
        print("Connection failed!")
        sys.exit()

    p.join()
    sys.exit()
