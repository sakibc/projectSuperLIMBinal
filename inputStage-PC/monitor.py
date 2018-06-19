""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
import multiprocessing as mp
import filterData
from outputStage_PC import outputStage

from helpers import *
from constants import *

def monitor(q, W, baselines, maxes, plotter):
    print("Calculating inverse...")
    Winv = np.linalg.pinv(W)
    print("Inverse matrix calculated.")

    print("Setting up arm...")
    moveq = mp.Queue()
    movep = mp.Process(target=outputStage.move,args=(moveq,))
    movep.start()

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
        activation = activation.clip(0,1)

        moveq.put(activation)

        plotter.sendEmg(sample)
        plotter.sendSyn(activation)

    plotter.stopEmg()
    plotter.stopSyn()
