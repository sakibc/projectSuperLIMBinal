""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
from flask import Flask, url_for
from flask import render_template
from subprocess import call

import multiprocessing as mp
import platform
import time

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/calibrate')
def calibrate():
    return render_template('calibrate.html')

@app.route('/monitor')
def monitor():
    return render_template('monitor.html')

@app.route('/shutdown')
def shutdown():
    if (platform.machine() == 'armv7l'):
        shutdownProcess = mp.Process(target=poweroffPi)
        shutdownProcess.start() # not pretty but it works...

    return render_template('shutdown.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html')

def runApp():
    app.run(host="0.0.0.0")

# def start(q):
#     appProcess = mp.Process(target=runApp, args=(q,))
#     appProcess.start()
#     appProcess.join()

def poweroffPi():
    # run this in another process to shutdown the pi
    # after sending the user a shutdown message

    time.sleep(1)
    call("sudo poweroff", shell=True)
