""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
import numpy as np
import multiprocessing as mp
import scipy.io
from sklearn.decomposition import NMF
import time

import emgPlot
import filterData
import userGuide

from helpers import *
from constants import *

def getCalibData(collectionTime, q):
    dat = np.zeros((electrodeNum,collectionTime*Fs))

    plotq = mp.Queue()
    plotter = emgPlot.emgPlotter(electrodeNum, plotq)

    clearQueue(q)  # let's empty the queue first so we can grab some fresh data

    for i in range(int(collectionTime*Fs/blockSamples)):
        sample = q.get(block=True, timeout=0.1)
        plotq.put(sample)

        for j in range(electrodeNum):
            dat[j][i:(i+blockSamples)] = sample[j::electrodeNum]

    plotter.close()

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
        caliData = getCalibData(45, q)   # capture 45 seconds of data
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
       caliData[i,:] /= (caliData[i,:]).max()

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
        (W0*(H0[0]).max(), W1*(H1[0]).max(), W2*(H2[0]).max(), W3*(H3[0]).max()), axis=1)

    return W    # it works!
