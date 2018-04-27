# Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
# This script monitors the serial port and captures the data in chunks of 64
# bytes as the Arduino sends it at its maximum transfer rate. It separates the
# data out of the chunk into arrays for each electrode and displays it on the
# screen.

# Imports

import serial, struct, csv
import time, datetime
import sys

import matplotlib
matplotlib.use('Qt5Agg') # don't need python as a framework

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Variables

baudRate = 500000 # any slower and the Arduino can't send the data fast enough

port = '/dev/tty.usbmodem1411'  # port number for right-most USB port on a
# Macbook Air running macOS. For Windows 10 you'll have to change this to
# "COMX", determined from Device Manager.

# sampling rate overall is 16MHz/(32prescale*13cycles) ~= 38462
# for each channel, at 4 channels is ~9615 Hz

samplingRate = 9616 # make it an even multiple of 16 to ease data capture
captureTime = 6 # for now let's just save 6 seconds worth of data
sampleNo = 0

# array to save data to import into MATLAB to determine how to process it.
# once a processing algorithm is determined it the algorithm will be rewritten
# in numpy so that we can run it on a raspberry pi, and we'll stop saving
# the data once we capture it
elecData = np.zeros((4,samplingRate*captureTime))

# t = np.arange(0,samplingRate*timePeriod)    #graph boundaries

# Logic

# fig = plt.figure(1)
# ax1 = fig.add_subplot(411)
# line1, = ax1.plot(t, elecStream1)

# ax1.set_xlabel("Sample number")
# ax1.set_ylabel("Activation level")
# # ax1.set_xlim(t[0],t[-1])
# ax1.set_ylim(0,255)

# ax1.grid(True)

# fig.canvas.draw()

try:
    with serial.Serial(port, baudRate, timeout=1, rtscts=True, dsrdtr=None) as arduIn:
        startMessage = arduIn.readline()
        print(startMessage.decode('utf-8'))

        print("Capturing data...")
        capturing = True
        startTime = time.time() # for now let's capture a set amount of data

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
                if sampleNo >= samplingRate*captureTime:
                    capturing = False   # we're done capturing
                    break

                elecData[0][sampleNo:(sampleNo+16)] = dat[0::4]
                elecData[1][sampleNo:(sampleNo+16)] = dat[1::4]
                elecData[2][sampleNo:(sampleNo+16)] = dat[2::4]
                elecData[3][sampleNo:(sampleNo+16)] = dat[3::4]

                sampleNo += 16

                # updatePlot()
                # if sampleNo < 9616*6:  #for plotting
                #     elecStream1[sampleNo:(sampleNo+16)] = dat[0::4]
                #     sampleNo += 16
                # else:
                #     elecStream1 = np.append(elecStream1[16:],dat[0::4])
                #     t += 16

        print("\nData capture complete.")
        
        csvfile = datetime.datetime.fromtimestamp(startTime).strftime("%Y%m%d-%H%M%S") + ".csv"
        csvfile = "../inputStage-analysis/capturedData/" + csvfile

        np.savetxt(csvfile, elecData, fmt="%d", delimiter=",")

        print("Data saved to", csvfile)

except serial.SerialException:
    print("Error: Device not found.")
except KeyboardInterrupt:
    print("\nProgram execution interrupted.")

sys.exit()
