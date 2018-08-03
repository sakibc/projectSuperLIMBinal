""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah

"""
import multiprocessing as mp
import filterData
# from outputStage_PC import outputStage

from helpers import *
from constants import *

def monitor(q, motionq, W, baselines, maxes, plotter, server=None, headless=False):
    if headless == False:
        print("Calculating inverse...")

    Winv = np.linalg.pinv(W)

    if headless == False:
        print("Inverse matrix calculated.")

        print("Setting up arm...")

    # movep = mp.Process(target=outputStage.move,args=(moveq,))
    # movep.start()

    if headless == False:
        print("Starting graphs...")
        plotter.startEmg()

    plotter.startSyn()

    filterer = filterData.liveFilter()

    clearQueue(q)
    clearQueue(motionq)

    buffer = np.zeros((8,16))
    timer = 0

    while True:
        for i in range(2):
            sample = q.get(block=True)
            sample = reorder(sample)

            index = i*8
            buffer[:, (index):(index+8)] = sample

        buffer = filterer.prep(buffer)

        for i in range(electrodeNum):
            buffer[i,:] -= baselines[i]
            buffer[i,:] /= maxes[i]

        activation = np.matmul(Winv,buffer)
        activation = activation.clip(0,1)

        motionq.put(activation[:,0:8])

        if headless == False:
            plotter.sendEmg(buffer)
        else:
            if server.empty() == False:
                dat = server.get()
                if dat == "abort":
                    break
            timer += 1
            if timer == 10:
                plotter.sendSyn(activation)
                timer = 0

    filterer.stop()
    plotter.stopEmg()
    plotter.stopSyn()
