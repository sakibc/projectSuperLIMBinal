""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
import time

def prompt():
    print("Letting the graph start up...")
    time.sleep(0.2)
    print("Starting calibration. Please follow the instructions as they appear.")
    time.sleep(3.8) # calibration start time, 4 seconds in

    movements = ["Rest","Open Hand","Close Hand","Pronate","Supinate","Pronate Open","Pronate Close","Supinate Open","Supinate Close"]

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
