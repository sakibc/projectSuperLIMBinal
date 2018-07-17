""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
import datetime
import numpy as np
import queue
import scipy.io
import serial
import serial.tools.list_ports
import struct
import time

def getPort():
    ports = list(serial.tools.list_ports.comports())
    port = None

    for p in ports:
        if "CDC" in p[1]:  # let's just grab one and see what happens...
            port = p[0]
        elif "USB2.0-Serial" in p[1]:
            port = p[0]

    return port

def capture(q):
    """Capture data from Arduino in a separate process and push it to the queue.

    Keyword arguments:
    q -- the queue to push data to, 64 8-byte ints each time
    e -- the queue for expected control messages, checked each cycle
    """

    baudRate = 500000  # any slower and the Arduino can't send the data fast enough

    # sampling rate overall is 16MHz/(32prescale*13cycles) ~= 38462
    # for each channel, at 8 channels is ~4808 Hz
    # we sample chunks 601 times per second

    attemptConnect = True
    timeout = 5

    while attemptConnect:
        attemptConnect = False
        port = getPort()
        try:
            with serial.Serial(port, baudRate, timeout=1, dsrdtr=True) as arduIn:

                print("Opening port...")

                startMessage = arduIn.readline().decode('utf-8')
                while ("Serial OK. Initializing..." in startMessage) != True:
                    startMessage = arduIn.readline().decode('utf-8')    # keep trying until we get what we want

                q.put("Connection established.")
                print(startMessage)

                capturing = True

                while capturing:
                    try:
                        rawdat = arduIn.read(64)
                        dat = struct.unpack('64B', rawdat)

                    except serial.SerialException:
                        print("Error: Connection lost.")
                        capturing = False

                    except struct.error:
                        print("Error: Device sent invalid data.")
                        capturing = False

                    else:
                        try:
                            q.put_nowait(dat)
                            # send captured data to the main process
                        except queue.Full:
                            pass    # if the queue's full, don't force it...

        except serial.SerialException:
            print("Error: Device not found. Trying again in 10 seconds...")
            q.put("error")  # so the main program knows not to continue
            time.sleep(10)
            attemptConnect = True
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
