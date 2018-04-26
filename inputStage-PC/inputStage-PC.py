# ==============================================================================
# Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
# ==============================================================================
# Project SuperLIMBinal inputStage-PC.py
# This script monitors the serial port and captures the data in chunks of 64
# bytes as the Arduino sends it at its maximum transfer rate. It separates the
# data out of the chunk into arrays for each electrode and displays it on the
# screen.
# ==============================================================================

# Imports ======================================================================

import serial
import struct

import matplotlib.pyplot as plt
import numpy as np

# Variables ====================================================================

baudRate = 500000 # any slower and the Arduino can't send the data fast enough

# sampling rate overall is 16MHz/(32prescale*13cycles) ~= 38462
# for each channel, at 4 channels is ~9615 Hz

samplingRate = 9616 # make it an even multiple of 16 to ease data capture
timePeriod = 6      # for now let's just graph 6 seconds worth of data

elecStream1 = np.zeros(samplingRate*timePeriod)
elecStream2 = np.zeros(samplingRate*timePeriod)
elecStream3 = np.zeros(samplingRate*timePeriod)
elecStream4 = np.zeros(samplingRate*timePeriod)

t = 0
timex = np.arange(0,samplingRate*timePeriod)

# Logic ========================================================================

def EMGgraph():
    plt.plot(timex, elecStream1)

try:
    with serial.Serial('/dev/tty.usbmodem1411', 500000, timeout=1) as arduIn:
        startMessage = arduIn.readline()
        print(startMessage.decode('utf-8'))

        capturing = True

        while capturing:
            try:
                rawdat = arduIn.read(64)
                dat = struct.unpack('64B',rawdat)
            except serial.SerialException:
                print("Error: Connection lost.")
                capturing = False
            except struct.error:
                print("Error: Device sent invalid data.")
                capturing = False
            else:
                if t < 9616*6:
                    elecStream1[t:(t+16)] = dat[0::4]
                    t += 16
                else:
                    elecStream1 = np.append(elecStream1[16:],dat[0::4])
                    timex += 16

except serial.SerialException:
    print("Error: Device not found.")
