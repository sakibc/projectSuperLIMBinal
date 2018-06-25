import multiprocessing as mp
import serial
import struct
import time
import numpy as np

def packSynActivation(dat):  # pack data into a uint16_t to send
    return struct.pack('>H',dat)    # the arduino expects a number between 0 and 1000

def move(q):
    b = 0.4 # threshold of difference required in syn. activation and
    last_c = [0,0,0,0]
    c = [0,0,0,0]
    delc = 0.05
    th = 0.7

    with serial.Serial("/dev/cu.usbmodem1411",115200,timeout=1,write_timeout=1) as arduOut:
        print("Connecting to arm...")

        startMessage = arduOut.readline().decode('utf-8')
        timeout = 5
        while ("Serial OK" in startMessage) != True and timeout >= 0:
            timeout -= 1
            print("Device sent invalid data! Retrying...")
            startMessage = arduOut.readline().decode('utf-8')

        if timeout >= 0:
            print(startMessage)
            print("Moving...")
            moving = True
        else:
            moving = False

        while moving:
            movements = np.swapaxes(q.get(),0,1) # transpose so we can iterate over the samples
            for sample in movements:   # only for one synergy for now
                for i in range(4):
                    if sample[i] >= last_c[i] + b:
                        c[i] = last_c[i] + delc
                        if c[i] > 1:
                            c[i] = 1
                    elif sample[i] <= last_c[i] + b:
                        c[i] = last_c[i] - delc
                        if c[i] < 0:
                            c[i] = 0
                    else:
                        c[i] = last_c[i]

                for i in range(2):
                    if c[i*2] > th and c[i*2 + 1] > th:
                        c[i*2] = last_c[i*2]
                        c[i*2 + 1] = last_c[i*2 + 1]

                    if c[i*2] > c[i*2 + 1]:
                        c[i*2 + 1] = 0
                    else:
                        c[i*2] = 0
                    
                dat = packSynActivation(c)
                arduOut.write(dat)
                
                last_c = c[:]

if __name__ == "__main__":
    move(None)
