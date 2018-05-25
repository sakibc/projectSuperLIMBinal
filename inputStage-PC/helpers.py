""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
import time
import datetime
import scipy.io

def clearQueue(q):
    while q.empty() == False:
        q.get()

def saveData(dat):
    filename = datetime.datetime.fromtimestamp(
        time.time()).strftime("%Y%m%d-%H%M%S") + ".mat"
    filename = "../inputStage-analysis/capturedData/" + filename

    scipy.io.savemat(filename, {'capturedData': dat})

    print("Data saved to", filename)
