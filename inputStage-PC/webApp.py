""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
from flask import Flask, url_for
from flask import render_template
from subprocess import call

import multiprocessing as mp
import platform

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
        call("sleep 1s; sudo shutdown -h now", shell=True)
        
    return render_template('shutdown.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html')

def runApp():
    app.run()

# def start(q):
#     appProcess = mp.Process(target=runApp, args=(q,))
#     appProcess.start()
#     appProcess.join()
