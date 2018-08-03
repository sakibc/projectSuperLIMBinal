import multiprocessing as mp
import serial
import struct
import time
import numpy as np
import socket
import pickle

def packSynActivation(dat):  # pack data into uint16_t's to send
    dat = [int(i*500) for i in dat]
    # print(dat)
    out = [0, 0]

    if dat[0] >= dat[1]:
        out[0] = 500 - dat[0]
    else:
        out[0] = 500 + dat[1]

    if dat[2] >= dat[3]:
        out[1] = 500 - dat[2]
    else:
        out[1] = 500 + dat[3]

    return struct.pack('>'+'H'*len(out),*out)    # the arduino expects a number between 0 and 1000

def move(q):
    with serial.Serial("/dev/ttyACM0", 9600) as arduOut:
    # with serial.Serial("/dev/ttyACM0", 9600, timeout=1, write_timeout=1) as arduOut:
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

        # counter = 0

        while moving:
            c = q.get()
            # counter += 1
            dat = packSynActivation(c)
            arduOut.write(dat)
            # counter = 0
            

def run(s):
    # b = 0.1 # threshold of difference required in syn. activation and
    last_c = [0,0,0,0]
    c = [0, 0, 1, 0]
    # delc = 0.3
    # th = 0.2
    print("connection established.")

    processing = True

    cq = mp.Queue()

    arduprocess = mp.Process(target=move, args=(cq,))

    arduprocess.start()

    while processing:
        # cq.put([0, 1, 1, 0])
        # time.sleep(1)
        data = s.recv(1024)

        try:
            data = np.frombuffer(data, count=32)
        except ValueError:
            print("error, reconnecting...")
            arduprocess.terminate()
            break

        data = np.reshape(data, (4, 8))
        # print(data)

        # transpose so we can iterate over the samples
        movements = np.swapaxes(data, 0, 1)
        # sample = movements[0]

        for sample in movements:   # only for one synergy for now
            print(sample)
            if sample[0] > 0.4 and sample[1] < 0.1:
                c[0] = 1
                c[1] = 0
            elif sample[1] > 0.4 and sample[0] < 0.1:
                c[1] = 1
                c[0] = 0
            else:
                c[0] = last_c[0]
                c[1] = last_c[1]
        # for i in range(4):
        #     if sample[i] >= last_c[i] + b:
        #         c[i] = last_c[i] + delc
        #         if c[i] > 1:
        #             c[i] = 1
        #     elif sample[i] <= last_c[i] + b:
        #         c[i] = last_c[i] - delc
        #         if c[i] < 0:
        #             c[i] = 0
        #     else:
        #         c[i] = last_c[i]

        # for i in range(2):
        #     if c[i*2] > th and c[i*2 + 1] > th:
        #         c[i*2] = last_c[i*2]
        #         c[i*2 + 1] = last_c[i*2 + 1]

        #     if c[i*2] > c[i*2 + 1]:
        #         c[i*2 + 1] = 0
        #     else:
        #         c[i*2] = 0

        print(c)
        cq.put(c)

        last_c = c[:]

    

if __name__ == "__main__":  # this is extremely insecure
    host = '192.168.1.66'
    port = 5002
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            s.connect((host, port))
            run(s)
        except KeyboardInterrupt:
            s.close
            break
        except:
            s.close
            pass
