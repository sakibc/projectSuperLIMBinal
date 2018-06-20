import multiprocessing as mp
import serial
import struct
import time

def packSynActivation(dat):  # pack data into a uint16_t to send
    return struct.pack('>H',dat)    # the arduino expects a number between 0 and 1000

def move(q):

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
            movements = (q.get()*1000).astype(int)
            for movement in movements[0]:
                dat = packSynActivation(movement)
                arduOut.write(dat)

if __name__ == "__main__":
    move(None)