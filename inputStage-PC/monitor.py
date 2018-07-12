""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
import multiprocessing as mp
import filterData
from outputStage_PC import outputStage

from helpers import *
from constants import *

def monitor(q, W, baselines, maxes, plotter, server=None, isPi=False):
    if isPi == False:
        print("Calculating inverse...")

    Winv = np.linalg.pinv(W)

    if isPi == False:
        print("Inverse matrix calculated.")

        print("Setting up arm...")
    # moveq = mp.Queue()
    # movep = mp.Process(target=outputStage.move,args=(moveq,))
    # movep.start()

    if isPi == False:
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

        # moveq.put(activation)

        if isPi == False:
            plotter.sendEmg(sample)
        else:
            if server.empty() == False:
                dat = server.get()
                if dat == "abort":
                    break

        plotter.sendSyn(activation)

    plotter.stopEmg()
    plotter.stopSyn()
