""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
import multiprocessing as mp
import emgPlot

from helpers import *
from constants import *

def monitor(q, W):
    clearQueue(q)

    plotq = mp.Queue()
    plotter = emgPlot.emgPlotter(electrodeNum, plotq)

    while True:
        sample = q.get(block=True, timeout=0.1)
        sample = reorder(sample)
        plotq.put(sample)

    plotter.close()
