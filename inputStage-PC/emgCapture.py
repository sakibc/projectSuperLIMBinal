""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
import datetime
import numpy as np
import scipy.io
import serial
import serial.tools.list_ports
import struct
import time

def getPort():
    ports = list(serial.tools.list_ports.comports())
    port = None

    for p in ports:
        if "Arduino" in p[1]:
            port = p[0]
        elif "CDC" in p[1]:  # let's just grab one and see what happens...
            port = p[0]

    return port

def capture(q, electrodeNum):  # capture data
    sampleNo = 0
    # queueTimer = 0  # every 10 sets of samples, push some data to the queue for the graph to plot.

    baudRate = 500000  # any slower and the Arduino can't send the data fast enough

    port = getPort()
    # sampling rate overall is 16MHz/(32prescale*13cycles) ~= 38462
    # for each channel, at 8 channels is ~4807 Hz
    # we sample chunks 601 times per second, which is ~10 samples per frame at 60 fps.

    blockSamples = int(64/electrodeNum)  # number of samples in a block

    samplingRate = int(
        blockSamples*round(float(38462/electrodeNum)/blockSamples))
    # make it an even multiple of 8 to ease data capture
    captureTime = 90    # amount of time to capture for before saving and exiting

    # array to save data to import into MATLAB to determine how to process it.
    #TODO: once a processing algorithm is determined it the algorithm must be rewritten
    # in numpy so that we can run it on a raspberry pi, and we can stop saving
    # the data once we capture it
    elecData = np.zeros((electrodeNum, samplingRate*captureTime))

    attemptConnect = True
    timeout = 5

    while attemptConnect:
        attemptConnect = False
        try:
            with serial.Serial(port, baudRate, timeout=1, dsrdtr=True) as arduIn:

                print("Opening port...")

                startMessage = arduIn.readline().decode('utf-8')

                q.put("Connection established.")
                print(startMessage)

                capturing = True
                startTime = time.time()  # for now let's capture a set amount of data

                while capturing:
                    try:
                        rawdat = arduIn.read(64)
                        dat = struct.unpack('64B', rawdat)

                    except serial.SerialException:
                        print("Error: Connection lost.")
                        print("\nSaving stored data...")
                        capturing = False

                    except struct.error:
                        print("Error: Device sent invalid data.")
                        print("\nSaving stored data...")
                        capturing = False

                    else:
                        for i in range(electrodeNum):
                            elecData[i][sampleNo:(
                                sampleNo+blockSamples)] = dat[i::electrodeNum]

                        sampleNo += blockSamples

                        q.put([dat[i] for i in range(electrodeNum)])
                        # send some data to the graph

                        if sampleNo >= samplingRate*captureTime:
                            capturing = False   # we're done capturing
                            print("Data capture complete.")

                filename = datetime.datetime.fromtimestamp(
                    startTime).strftime("%Y%m%d-%H%M%S") + ".mat"
                filename = "../inputStage-analysis/capturedData/" + filename

                scipy.io.savemat(filename, {'elecData': elecData})

                print("Data saved to", filename)
                print("Close live plot to continue.")

        except serial.SerialException:
            print("Error: Device not found.")
            q.put("error")  # so the main program knows not to continue
        except KeyboardInterrupt:
            print("\nProgram execution interrupted.")
        except UnicodeDecodeError:  # this happens sometimes...
            print("Error: Device sent invalid data!")
            timeout -= 1
            if timeout >= 0:
                print("Retrying connection...")
                attemptConnect = True
            else:
                print("Invalid data received 5 times. Connection timed out.")
