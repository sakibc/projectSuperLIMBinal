""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
import time

def calibration():
    movements = ["Rest position","Open Hand","Close Hand","Pronate","Supinate"]

    for movement in movements:
        print("\nReady? Next movement:",movement)
        time.sleep(2)
        print('Begin Movement')
        time.sleep(2)
        print('Hold Position')
        time.sleep(3)
        print('Release')
        time.sleep(2)

    print('Calibration data set collection complete.\n')
