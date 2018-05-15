""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    This script monitors the serial port and captures the data in chunks of 64
    bytes as the Arduino sends it at its maximum transfer rate. It separates the
    data out of the chunk into arrays for each electrode and plots it live on
    the screen.

    This script currently only saves data once a desired amount of seconds has
    passed, so it cannot be run indefinitely without running out of memory.
"""

#TODO: -get rid of magic numbers...
#      -make it modular...
#      -end calibration if device disconnected

# Imports

import serial, struct, csv
import time, datetime
import sys
import queue

import serial.tools.list_ports

import matplotlib
matplotlib.use('tkagg') # change drawing backend so that a framework version of
                        # python is not necessary on mac.

import multiprocessing as mp
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import scipy.io

electrodeNum = 8

def data_gen(t=0):  # get data to show on graph from other process
    while True:
        tlist = [t+0.1*i/60 for i in range(60)]
        t += 0.1
        try:
            dat = [q.get(block=True,timeout=1) for i in range(60)]
            # there's probably a more efficient way to do this...
            # pickling and unpickling 60 lists instead of 1 large list seems expensive
            yield tlist, dat
        except queue.Empty:
            break

def init(): # initialize empty graph
    del xdata[:]

    for i in range(electrodeNum):
        ax[i].set_ylim(0,1)
        ax[i].set_xlim(0,drawTime)
    
        del ydata[i][:]

        line[i].set_data(xdata, ydata[i])

    return line

def run(data): # redraw graph
      # update the data
    t, elec = data
    xdata.extend(t)
    for i in range(electrodeNum):
        for j in range(60):
            ydata[i].append(elec[j][i]/255)

        line[i].set_data(xdata, ydata[i])
        xmin,xmax = ax[i].get_xlim()

        if t[-1] >= xmax:
            xshift = drawTime/2
            ax[i].set_xlim(xmin+xshift,xmax+xshift)
            ax[i].figure.canvas.draw()

    return line

def getPort():
    ports = list(serial.tools.list_ports.comports())
    port = None

    for p in ports:
        if "Arduino" in p[1]:
            port = p[0]
        elif "CDC" in p[1]: # let's just grab one and see what happens...
            port = p[0]

    return port

def capture(q): # capture data
    sampleNo = 0
    # queueTimer = 0  # every 10 sets of samples, push some data to the queue for the graph to plot.

    baudRate = 500000 # any slower and the Arduino can't send the data fast enough

    port = getPort()
    # sampling rate overall is 16MHz/(32prescale*13cycles) ~= 38462
    # for each channel, at 8 channels is ~4807 Hz
    # we sample chunks 601 times per second, which is ~10 samples per frame at 60 fps.

    blockSamples = int(64/electrodeNum)  # number of samples in a block

    samplingRate = int(blockSamples*round(float(38462/electrodeNum)/blockSamples))
    # make it an even multiple of 8 to ease data capture
    captureTime = 90    # amount of time to capture for before saving and exiting

    # array to save data to import into MATLAB to determine how to process it.
    #TODO: once a processing algorithm is determined it the algorithm must be rewritten
    # in numpy so that we can run it on a raspberry pi, and we can stop saving
    # the data once we capture it
    elecData = np.zeros((electrodeNum,samplingRate*captureTime))

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
                        for i in range(electrodeNum):
                            elecData[i][sampleNo:(
                                sampleNo+blockSamples)] = dat[i::electrodeNum]

                        sampleNo += blockSamples

                        # queueTimer += 1

                        # if queueTimer % 15 == 0:
                        #     queueTimer = 0
                        q.put(dat[i] for i in range(electrodeNum)])
                        # we don't need to show all the data on the graph, as nice as that would be...

                        if sampleNo >= samplingRate*captureTime:
                            capturing = False   # we're done capturing
                            print("Data capture complete.")

                filename = datetime.datetime.fromtimestamp(
                    startTime).strftime("%Y%m%d-%H%M%S") + ".mat"
                filename = "../inputStage-analysis/capturedData/" + filename

                scipy.io.savemat(filename,{'elecData':elecData})

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

def prompt():
    print("Letting the graph start up...")
    time.sleep(0.2)
    print("Starting calibration. Please follow the instructions as they appear.")
    time.sleep(3.8) # calibration start time, 4 seconds

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

if __name__ == "__main__":

    drawTime = 10  # only show the last 10 seconds of data on the screen

    plt.style.use('seaborn-darkgrid')   # this graph style looks pretty...
    matplotlib.rcParams['toolbar'] = 'None'

    fig, ax = plt.subplots(int(electrodeNum/2), 2, sharex=True, sharey=True)
    ax = np.transpose(ax).flatten()
    line = [ax[i].plot([], [])[0] for i in range(electrodeNum)]
    xdata = []
    ydata = [[] for i in range(electrodeNum)]

    fig.suptitle("EMG Sensor Data")
    fig.text(0.5, 0.04, "Time", ha='center')
    fig.text(0.04, 0.5, "Normalized Activation Level", 
            va='center', rotation='vertical')

    for i in range(electrodeNum):
        ax[i].set_title("Electrode "+str(i+1))

    q = mp.Queue()
    p = mp.Process(target=capture, args=(q,))   #create separate process to handle
    #data capture so that it's not blocked by the live graph.
    promptp = mp.Process(target=prompt)
    #process to manage timed prompts for data collection so it doesn't mess with
    #the capture or graph drawing

    print("Starting capture process...")        
    p.start()
    message = q.get()

    if message == "Connection established.":
        promptp.start()

        ani = animation.FuncAnimation(
            fig, run, data_gen, blit=True, interval=100, repeat=False, init_func=init)

        mng = plt.get_current_fig_manager() # maximize window, because it doesn't like
        mng.resize(*mng.window.maxsize())   # being maximized after the fact...
        plt.show()
    else:
        print("Connection failed!")

    p.join()
    promptp.join()
    sys.exit()
