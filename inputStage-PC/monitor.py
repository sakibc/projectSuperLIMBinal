""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
import multiprocessing as mp
import filterData

from helpers import *
from constants import *

def monitor(q, W, baselines, maxes, plotter):
    print("Calculating inverse...")
    Winv = np.linalg.pinv(W)
    print("Inverse matrix calculated.")

    print("Starting graphs...")
    plotter.startEmg()
    plotter.startSyn()

    filter = filterData.liveFilter()
    
    clearQueue(q)

    while True:
        sample = q.get(block=True, timeout=0.1)
        sample = reorder(sample)
        sample = filter.prep(sample)

        for i in range(electrodeNum):
            sample[i,:] -= baselines[i]
            sample[i,:] /= maxes[i]

        activation = np.matmul(Winv,sample)

        plotter.sendEmg(sample)
        plotter.sendSyn(activation)

    plotter.stopEmg()
    plotter.stopSyn()
