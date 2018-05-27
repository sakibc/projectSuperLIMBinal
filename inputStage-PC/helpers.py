""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
import datetime, time, scipy.io
import numpy as np
from constants import electrodeNum

def reorder(dat):
    """Take in a chunk of data from the Arduino and separate into a NumPy Array."""
    return np.array([dat[i::electrodeNum] for i in range(electrodeNum)])

def clearQueue(q):
    while q.empty() == False:
        q.get()

def saveData(dat):
    filename = datetime.datetime.fromtimestamp(
        time.time()).strftime("%Y%m%d-%H%M%S") + ".mat"
    filename = "../inputStage-analysis/capturedData/" + filename

    scipy.io.savemat(filename, {'capturedData': dat})

    print("Data saved to", filename)
