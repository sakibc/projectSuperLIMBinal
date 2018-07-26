import multiprocessing as mp
import serial
import struct
import time
import numpy as np
import socket
import pickle

def packSynActivation(dat):  # pack data into uint16_t's to send
    dat = [int(i*1000) for i in dat]
    # print(dat)
    return struct.pack('>'+'H'*len(dat),*dat)    # the arduino expects a number between 0 and 1000

def move(s):
    # b = 0.1 # threshold of difference required in syn. activation and
    # last_c = [0,0,0,0]
    # c = [0,0,0,0]
    c = [0.5, 0]
    mult = 0.001
    # delc = 0.05
    # th = 0.7

    with serial.Serial("/dev/ttyACM0",115200,timeout=1,write_timeout=1) as arduOut:
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
            data = s.recv(1024)
            print(pickle.loads(data))
            # c[0] += mult
            # if c[0] >= 1 or c[0] <= 0:
            #     mult *= -1

            # dat = packSynActivation(c)
            # arduOut.write(dat)

            # time.sleep(0.01)

            # movements = np.swapaxes(q.get(),0,1) # transpose so we can iterate over the samples
            # for sample in movements:   # only for one synergy for now
            #     for i in range(4):
            #         if sample[i] >= last_c[i] + b:
            #             c[i] = last_c[i] + delc
            #             if c[i] > 1:
            #                 c[i] = 1
            #         elif sample[i] <= last_c[i] + b:
            #             c[i] = last_c[i] - delc
            #             if c[i] < 0:
            #                 c[i] = 0
            #         else:
            #             c[i] = last_c[i]
            #         # c[i] = sample[i]

            #     for i in range(2):
            #         if c[i*2] > th and c[i*2 + 1] > th:
            #             c[i*2] = last_c[i*2]
            #             c[i*2 + 1] = last_c[i*2 + 1]

            #         if c[i*2] > c[i*2 + 1]:
            #             c[i*2 + 1] = 0
            #         else:
            #             c[i*2] = 0
                    
            #     # print(c)
            #     dat = packSynActivation(c)
            #     arduOut.write(dat)
            #     # print(arduOut.readline().decode('utf-8'))
            #     # print(arduOut.readline().decode('utf-8'))
                
            #     last_c = c[:]

if __name__ == "__main__":  # this is extremely insecure
    host = '192.168.4.1'
    port = 5002
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            s.connect((host, port))
            move(s)
        except:
            pass
            
    s.close
