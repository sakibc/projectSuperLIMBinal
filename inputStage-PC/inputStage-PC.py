# Copyright 2018 Sakib Chowdhury and Claudia Lutfallah

import serial
import struct
import matplotlib.pyplot as plt
from drawnow import drawnow

elecStream1 = []
elecStream2 = []
elecStream3 = []
elecStream4 = []

def makeFig():
    plt.ylim(0,255)
    plt.title("EMG Data Capture")
    plt.grid(True)
    plt.ylabel("Value")
    plt.plot(elecStream1, 'ro-', label="Electrode 1")
    plt.legend(loc="upper right")

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
                # elecStream1.append(dat[0::4])
                # if len(elecStream1) > 60000:
                #     del elecStream1[0:16]
                # print(elecStream1)
                print(dat[0::4])

except serial.SerialException:
    print("Error: Device not found.")
