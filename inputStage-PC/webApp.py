""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
from flask import Flask, url_for, jsonify
from flask import render_template
from flask_socketio import SocketIO, send, emit
from subprocess import call

import multiprocessing as mp
import platform
import time

from helpers import clearQueue

class webPlotDataManager:
    def __init__(self, sampleq):
        self.sampleq = sampleq

    def startEmg(self):
        pass    # dummy fn to work in place of other plotter
    def stopEmg(self):
        pass    # same
    def sendEmg(self, dat):
        self.sampleq.put(dat)
    def startSyn(self):
        pass    # dummy fn to work in place of other plotter
    def stopSyn(self):
        pass    # same
    def sendSyn(self, dat):
        self.sampleq.put(dat)

def runApp(q, sampleq):   # this is awful, I should at least make a class...
    app = Flask(__name__,
                static_folder = "./dist/static",
                template_folder="./dist")

    socketio = SocketIO(app)

    @socketio.on('getSample')
    def sendSample():
        i = 0

        while sampleq.empty() == False:
     
            dat = sampleq.get()
            emit('receiveSample', dat.tolist())

    @socketio.on('loadMatrix')
    def loadMatrix():
        q.put("loadMatrix")
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
        q.put("getSystemStatus")
        dat = q.get()

        sensStatus, motStatus, calibStatus = dat
        response = {
            'sensorStatus': sensStatus,
            'motionStatus': motStatus,
            'calibStatus': calibStatus
        }

        emit('systemStatus', response)

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
