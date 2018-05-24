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
from sklearn.decomposition import NMF

import emgCapture
import emgPlot
import userGuide
import filterData

from constants import *

# testDat = scipy.io.loadmat("../inputStage-analysis/test-data/set2.mat")['elecData']
# testDat = filterData.mainsComb(filterData.center(testDat))
# emgCapture.saveData(testDat)

def clearQueue(q):
    while q.empty() == False:
        q.get()

def getData(collectionTime, q):
    dat = np.zeros((electrodeNum,collectionTime*Fs))
    clearQueue(q)  # let's empty the queue first so we can grab some fresh data

    for i in range(int(collectionTime*Fs/blockSamples)):
        sample = q.get(block=True, timeout=0.1)

        for j in range(electrodeNum):
            dat[j][i:(i+blockSamples)] = sample[j::electrodeNum]

    return dat

def calibrate(q, testmode=False):
    W = np.ones((electrodeNum, synergyNum))

    if testmode:
        caliData = scipy.io.loadmat(
            "../inputStage-analysis/test-data/set3.mat")['elecData']
        print("\nTest data loaded. Generating calibration matrix...")
    else:
        print("\nStarting calibration. Follow the instructions as they appear.")
        time.sleep(1)  # give the user time to read...
        promptp = mp.Process(target=userGuide.calibration)

        promptp.start()
        caliData = getData(45, q)   # capture 45 seconds of data
        promptp.join()

        print("Processing data...")

    caliData = filterData.longPrep(caliData)

    if testmode:
        timeStart = [(t+8)*Fs for t in range(0, 45, 9)]
    else:
        timeStart = [(t+4)*Fs for t in range(0,45,9)]

    timeEnd = [t + 3*Fs for t in timeStart]

    relaxed = caliData[:,timeStart[0]:timeEnd[0]]
    baselines = np.mean(relaxed,-1)
   
    for i in range(8):  # normalize signals
       caliData[i,:] -= baselines[i]
       caliData[i,:] /= max(caliData[i,:])

    caliData = np.clip(caliData,0,1)

    openData    = caliData[:, timeStart[1]:timeEnd[1]]
    closeData   = caliData[:, timeStart[2]:timeEnd[2]]
    proData     = caliData[:, timeStart[3]:timeEnd[3]]
    soupData    = caliData[:, timeStart[4]:timeEnd[4]]

    model = NMF(n_components=1,solver="mu") # solve for W matrix
    W0 = model.fit_transform(openData)
    H0 = model.components_

    W1 = model.fit_transform(closeData)
    H1 = model.components_

    W2 = model.fit_transform(proData)
    H2 = model.components_

    W3 = model.fit_transform(soupData)
    H3 = model.components_

    W = np.concatenate( # put it all together
        (W0*max(H0[0]), W1*max(H1[0]), W2*max(H2[0]), W3*max(H3[0])), axis=1)

    return W    # it works!

def run(q): # main program logic
    op = 0

    while True:
        if op == 0:
            userGuide.menuPrompt()
            op = input("Operation: ")
            try:
                tmp = int(op)
                op = tmp
            except:
                pass

        elif op == 1: # calibrate
            W = calibrate(q)
            print(W)
            op = 0
        elif op == 2: # load
            pass
        elif op == 3: # run test
            W = calibrate(q, True)
            print(W)
            op = 0
        elif op == 4: # quit
            userGuide.endMessage()
            break
        else:
            print("Command unrecognized.\n")
            op = 0


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

    p.terminate()
    p.join()
    sys.exit()
