""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
from flask import Flask, url_for, jsonify
from flask import render_template
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

def runApp(q, sampleq):   # this is awful, I should at least make a class...
    app = Flask(__name__,
                static_folder = "./dist/static",
                template_folder="./dist")

    @app.route('/api/getSample')
    def sendSample():
        dat = sampleq.get()
        print(dat)

        return jsonify(dat.tolist())

    @app.route('/api/startCalibration', methods=['POST'])
    def startCalibration():
        clearQueue(sampleq)
        q.put("startCalibration")

        return '', 204

    @app.route('/api/systemStatus')
    def systemStatus():
        q.put("getSystemStatus")
        sensStatus, motStatus, calibStatus = q.get()
        response = {
            'sensorStatus': sensStatus,
            'motionStatus': motStatus,
            'calibStatus': calibStatus
            # 'motionStatus': "Connected" if motStatus else "Disconnected"
        }

        return jsonify(response)

    @app.route('/api/shutdown', methods=['POST'])
    def shutdown():
        q.put("shutting down...")

        # only if we're really sure this is a pi...
        if (platform.machine() == 'armv7l'):
            shutdownProcess = mp.Process(target=poweroffPi)
            shutdownProcess.start()  # not pretty but it works...

        return '', 204

    @app.route('/api/reboot', methods=['POST'])
    def reboot():
        q.put("rebooting...")

        # only if we're really sure this is a pi...
        if (platform.machine() == 'armv7l'):
            rebootProcess = mp.Process(target=rebootPi)
            rebootProcess.start()  # not pretty but it works...

        return '', 204

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return render_template('index.html')

    # @app.errorhandler(404)
    # def page_not_found(error):
    #     return render_template('page_not_found.html')

    if (platform.machine() == 'armv7l'):
        app.run(host="0.0.0.0") # only run open to the network if on pi
    else:
        app.run()

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
