import multiprocessing as mp
import serial
import struct

def move(q):
    attemptConnect = True
    timeout = 5

    lastMovement = 0

    while attemptConnect:
        attemptConnect = False
        try:
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
                    movements = q.get()
                    for i in range(4):
                        movement = [int(m*255) for m in movements[i]]
                        if i == 0:
                            for c in movement:
                                lastMovement = c
                                # print(c)
                                toSend = struct.pack('i',c)
                                # print(toSend)
                                # print(toSend)
                                arduOut.write(toSend)
                                # sent = arduOut.readline().decode('utf-8')
                                # print(sent)
        except:
            print("Error!")
            print("Last movement: {0}".format(lastMovement))
            timeout -= 1
            if timeout >= 0:
                print("Retrying connection...")
                attemptConnect = True
            else:
                print("Tried connecting to arm 5 times. Connection timed out.")
