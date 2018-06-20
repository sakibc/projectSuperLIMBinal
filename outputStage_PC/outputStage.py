import multiprocessing as mp
import serial
import struct
import time

def packData(dat):  # pack data into a uint16_t to send
    return struct.pack('>H',dat)    # the arduino expects a number between 0 and 1000

def move(q):
    pos = 0

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
            # movements = q.get()
            dat = packData(pos)
            arduOut.write(dat)
            pos += 1
            time.sleep(0.01)
            if pos > 1000:
                pos = 1
                dat = packData(0)
                arduOut.write(dat)
                time.sleep(10)

if __name__ == "__main__":
    move(None)