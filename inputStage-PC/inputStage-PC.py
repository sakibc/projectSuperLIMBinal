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

import emgCapture
import emgPlot
import userGuide

electrodeNum = 8

if __name__ == "__main__":
    q = mp.Queue()
    p = mp.Process(target=emgCapture.capture, args=(q, electrodeNum))   #create separate process to handle
    #data capture so that it's not blocked by the live graph.
    promptp = mp.Process(target=userGuide.prompt)
    #process to manage timed prompts for data collection so it doesn't mess with
    #the capture or graph drawing

    emgPlotter = emgPlot.emgPlotter(q, electrodeNum)

    print("Starting capture process...")        
    p.start()
    message = q.get()

    if message == "Connection established.":
        promptp.start()
        emgPlotter.startAni()
    else:
        print("Connection failed!")
        sys.exit()

    p.join()
    promptp.terminate() # stop prompts if the capture process has ended
    promptp.join()
    sys.exit()
