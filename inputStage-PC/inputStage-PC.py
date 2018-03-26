# Copyright 2018 Sakib Chowdhury and Claudia Lutfallah

import serial
import struct

try:
    with serial.Serial('/dev/tty.usbmodem1411', 500000, timeout=1) as arduIn:
        startMessage = arduIn.readline()
        print(startMessage.decode('utf-8'))

        capturing = True;

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
                print(dat)
except serial.SerialException:
    print("Error: Device not found.")
