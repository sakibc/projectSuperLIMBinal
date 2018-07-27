""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
from flask import Flask, url_for, jsonify
from flask import render_template
from flask_socketio import SocketIO, send, emit
from subprocess import call
import socket

import multiprocessing as mp
import platform
import time
import pickle

from helpers import clearQueue

class webPlotDataManager:
    def __init__(self, sampleq):
        self.sampleq = sampleq
        self.sampleTimer = 0

        self.samplesSent = 0

    def startEmg(self):
        pass    # dummy fn to work in place of other plotter
    def stopEmg(self):
        pass    # same
    def sendEmg(self, dat):
        self.sampleTimer += 1
        if self.sampleTimer == 20:
            self.sampleq.put(dat)
            self.sampleTimer = 0
    def startSyn(self):
        self.startTime = time.time()
    def stopSyn(self):
        pass    # same
    def sendSyn(self, dat):
        # print(dat)
        self.sampleTimer += 1
        if self.sampleTimer == 20:
            # print(dat)
            self.sampleq.put(dat)
            self.samplesSent += 1
            self.sampleTimer = 0
            if self.samplesSent == 100:
                currentTime = time.time()
                timePassed = currentTime - self.startTime
                print("Broadcast frequency:", 100/timePassed, "Hz")
                self.startTime = currentTime
                self.samplesSent = 0

def outputServer(motionq):
    host = ''
    port = 5002
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    conn, addr = s.accept()
    print("Connected to", addr)
    while True:
        data = motionq.get(block=True)
        # print(data)
        data = data.tobytes('C')
        conn.sendall(data)

    conn.close()

def startOutput(motionq):
    outAppProcess = mp.Process(target=outputServer, args=(motionq,))
    outAppProcess.start()

def runApp(q, sampleq):   # this is awful, I should at least make a class...
    app = Flask(__name__,
                static_folder = "./dist/static",
                template_folder="./dist")

    socketio = SocketIO(app)

    @socketio.on('getSample')
    def sendSample():

        while sampleq.empty() == False:
     
            dat = sampleq.get()
            # print(dat.tolist())
            emit('receiveSample', dat.tolist())

    @socketio.on('loadMatrix')
    def loadMatrix():
        q.put("loadMatrix")
        print("loading matrix...")
        calibLoaded, calibLoadFailed = q.get()
        response = {
            'calibLoaded': calibLoaded,
            'calibLoadFailed': calibLoadFailed
        }

        emit('loadMatrix', response)

    @socketio.on('startCalibration')
    def startCalibration():
        clearQueue(sampleq)
        q.put("startCalibration")

    @socketio.on('startMonitor')
    def startMonitor():
        clearQueue(sampleq)
        q.put("startMonitor")

    @socketio.on('stopMonitor')
    def stopMonitor():
        q.put("abort")

    @socketio.on('stopCalib')
    def stopCalib():
        q.put("abort")

    @socketio.on('processingStatus')
    def checkProcessingStatus():
        if q.empty() == False:
            emit('endCalibration')

    @socketio.on('systemStatus')
    @socketio.on('connect')
    def systemStatus():
        print("status requested.")
        q.put("getSystemStatus")
        dat = q.get()

        try:
            sensStatus, motStatus, calibStatus = dat
            response = {
                'sensorStatus': sensStatus,
                'motionStatus': motStatus,
                'calibStatus': calibStatus
            }

            emit('systemStatus', response)
        except:
            print("something bad happened...")

    @socketio.on('abortCalibration')
    def abortCalibration():
        q.put("abortCalibration")

    @socketio.on('shutdown')
    def shutdown():
        q.put("shutting down...")

        # only if we're really sure this is a pi...
        if (platform.machine() == 'armv7l'):
            shutdownProcess = mp.Process(target=poweroffPi)
            shutdownProcess.start()  # not pretty but it works...

    @socketio.on('restart')
    def reboot():
        q.put("rebooting...")

        # only if we're really sure this is a pi...
        if (platform.machine() == 'armv7l'):
            rebootProcess = mp.Process(target=rebootPi)
            rebootProcess.start()  # not pretty but it works...

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return render_template('index.html')

    # @app.errorhandler(404)
    # def page_not_found(error):
    #     return render_template('page_not_found.html')

    if (platform.machine() == 'armv7l'):
        socketio.run(app, host="0.0.0.0") # only run open to the network if on pi
    else:
        socketio.run(app)

def start(q, sampleq):
    appProcess = mp.Process(target=runApp, args=(q,sampleq))
    appProcess.start()

def poweroffPi():
    # run this in another process to shutdown the pi
    # after sending the user a shutdown message

    time.sleep(1)
    call("sudo poweroff", shell=True)

def rebootPi():
    # run this in another process to shutdown the pi
    # after sending the user a shutdown message

    time.sleep(1)
    call("sudo reboot", shell=True)
