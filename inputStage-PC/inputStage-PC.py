# Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
# This script monitors the serial port and captures the data in chunks of 64
# bytes as the Arduino sends it at its maximum transfer rate. It separates the
# data out of the chunk into arrays for each electrode and displays it on the
# screen.

# Imports

import serial, struct, csv
import time, datetime
import sys
import queue

import matplotlib
matplotlib.use('tkagg')

import multiprocessing as mp
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Variables

baudRate = 500000 # any slower and the Arduino can't send the data fast enough

port = '/dev/tty.usbmodem1411'  # port number for right-most USB port on a
# Macbook Air running macOS. For Windows 10 you'll have to change this to
# "COMX", determined from Device Manager.
#TODO: Autodetect Arduino port

# sampling rate overall is 16MHz/(32prescale*13cycles) ~= 38462
# for each channel, at 4 channels is ~9615 Hz
# we sample 601 times per second, which is 10 samples per frame at 60 fps.

samplingRate = 9616 # make it an even multiple of 16 to ease data capture
captureTime = 20

# array to save data to import into MATLAB to determine how to process it.
# once a processing algorithm is determined it the algorithm will be rewritten
# in numpy so that we can run it on a raspberry pi, and we'll stop saving
# the data once we capture it
elecData = np.zeros((4,samplingRate*captureTime))

# Logic

drawTime = 10 # only show the last 6 seconds of data on the screen

plt.style.use('seaborn-darkgrid')

fig, ax = plt.subplots(4,1,sharex=True)
line = [ax[i].plot([],[])[0] for i in range(4)]
xdata = []
ydata = [[],[],[],[]]

fig.suptitle("EMG Sensor Data")
fig.text(0.5,0,"Time", ha='center')
fig.text(0.04,0.5,"Normalized Activation Level", va='center', rotation='vertical')

def data_gen(t=0):
    while True:
        t += 1/30
        try:
            dat = q.get(block=True, timeout=0.5)
            yield t, dat
        except queue.Empty:
            break

def init():
    del xdata[:]

    for i in range(4):
        ax[i].set_ylim(0,1)
        ax[i].set_xlim(0,drawTime)
    
        del ydata[i][:]

        line[i].set_data(xdata, ydata[i])

    return line

def run(data):
      # update the data
    t, elec = data
    xdata.append(t)
    for i in range(4):
        ydata[i].append(elec[i]/255)

        line[i].set_data(xdata, ydata[i])
        xmin,xmax = ax[i].get_xlim()

        if t >= xmax:
            ax[i].set_xlim(xmin+1,xmax+1)
            ax[i].figure.canvas.draw()

    return line

def capture(q):
    sampleNo = 0
    queueTimer = 0  # every 10 sets of samples, push some data to the queue for the graph to plot.

    try:
        with serial.Serial(port, baudRate, timeout=1, dsrdtr=True) as arduIn:
            print("Opening port...")

            startMessage = arduIn.readline()
            q.put(startMessage.decode('utf-8'))

            print("Initializing graph...")
            capturing = True
            startTime = time.time() # for now let's capture a set amount of data

            while capturing:
                try:
                    rawdat = arduIn.read(64)
                    dat = struct.unpack('64B',rawdat)

                except serial.SerialException:
                    print("Error: Connection lost.")
                    print("\nSaving stored data...")
                    capturing = False

                except struct.error:
                    print("Error: Device sent invalid data.")
                    print("\nSaving stored data...")
                    capturing = False

                else:
                    elecData[0][sampleNo:(sampleNo+16)] = dat[0::4]
                    elecData[1][sampleNo:(sampleNo+16)] = dat[1::4]
                    elecData[2][sampleNo:(sampleNo+16)] = dat[2::4]
                    elecData[3][sampleNo:(sampleNo+16)] = dat[3::4]

                    sampleNo += 16

                    queueTimer += 1

                    if queueTimer % 20 == 0:
                        queueTimer = 0
                        q.put([dat[0],dat[1],dat[2],dat[3]])    # we don't need to show all the data on the graph...
                        

                    if sampleNo >= samplingRate*captureTime:
                        capturing = False   # we're done capturing
                        print("Data capture complete.")


            csvfile = datetime.datetime.fromtimestamp(startTime).strftime("%Y%m%d-%H%M%S") + ".csv"
            csvfile = "../inputStage-analysis/capturedData/" + csvfile

            np.savetxt(csvfile, elecData, fmt="%d", delimiter=",")

            print("Data saved to", csvfile)
            print("Close live plot to continue.")

    except serial.SerialException:
        print("Error: Device not found.")
    except KeyboardInterrupt:
        print("\nProgram execution interrupted.")

    #TODO: Handle exceptions from child process better...

if __name__ == "__main__":
    q = mp.Queue()
    p = mp.Process(target=capture, args=(q,))   #create separate process to handle
    print("Starting capture process...")        #data capture so that it's not blocked
    p.start()                                   #by the live graph.
    print(q.get())

    ani = animation.FuncAnimation(
        fig, run, data_gen, blit=True, interval=10, repeat=False, init_func=init)

    mng = plt.get_current_fig_manager() # maximize window, because it doesn't like
    mng.resize(*mng.window.maxsize())   # being maximized after the fact...
    plt.show()

    p.join()
