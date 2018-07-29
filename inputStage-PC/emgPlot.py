""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

import multiprocessing as mp
import numpy as np
import queue


from constants import *

# app = QtGui.QApplication([])
# w = QtGui.QWidget()
# w.show()

# p = mp.Process(target=app.exec_)
# p.start

class plotManager:
    def __init__(self):
        self.q = mp.Queue()
        self.qapp = mp.Process(target=self.runApp, args=(self.q,))
        self.qapp.start()

    def runApp(self,q):
        app = QtGui.QApplication([])

        self.eq = mp.Queue()
        self.emgPlotter = emgPlotter(self.eq)
        self.sq = mp.Queue()
        self.synPlotter = synergyPlotter(self.sq)

        def check():
            ops = []
            while q.empty() == False:
                ops.append(q.get(block=True))

            for bundle in ops:
                target = bundle[0]

                if target == "emg-start":
                    self.emgPlotter.startGraph()
                elif target == "syn-start":
                    self.synPlotter.startGraph()
                elif target == "emg-stop":
                    self.emgPlotter.close()
                elif target == "syn-stop":
                    self.synPlotter.close()
                elif target == "emg-send":
                    self.eq.put(bundle[1])
                elif target == "syn-send":
                    self.sq.put(bundle[1])

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(check)
        self.timer.start(10)

        app.exec_()

    def startEmg(self):
        self.q.put(("emg-start",))
    def startSyn(self):
        self.q.put(("syn-start",))
    def stopEmg(self):
        self.q.put(("emg-stop",))
    def stopSyn(self):
        self.q.put(("syn-stop",))
    def sendEmg(self, dat):
        self.q.put(("emg-send",dat))
    def sendSyn(self, dat):
        self.q.put(("syn-send",dat))
        
class plotWindow(pg.GraphicsWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def closeEvent(self, event):

        event.accept()

class plotter:
    def __init__(self, q):
        self.q = q
        self.initialize()
        self.w = plotWindow(title=self.title)
        self.w.setGeometry(self.posx, self.posy, self.width, self.height)
        self.w.setWindowTitle(self.title)

        self.curves = []
        self.plots = []
        self.setupPlots(self.w, self.curves, self.plots)

    def close(self):
        self.timer.stop()

    def createAxesData(self):
        x = np.linspace(0, 10, 10*Fs/blockSamples)
        y = np.full((electrodeNum, x.size), 0.5)
        return (x, y)
    
    def initialize(self):
        self.title = "Base Plotter Class"
        self.width = 720
        self.height = 600
        self.posx = 0
        self.posy = 0
        self.yRange = (0,1)

    def setupPlots(self, w, curves, plots):
        for i in range(electrodeNum):
            plot = w.addPlot(title="Sensor {0}".format(i+1))
            
            curves.append(plot.plot(pen='y'))
            plots.append(plot)

            if ((i+1) % 2 == 0):
                w.nextRow()

    def startGraph(self):
        self.x, self.y = self.createAxesData()

        for plot in self.plots:
            plot.setMouseEnabled(x=False, y=False)
            plot.disableAutoRange()
            plot.showGrid(x=True, y=True)
            plot.setRange(yRange=self.yRange)
            xaxis = plot.getAxis('bottom')
            xaxis.setTickSpacing(2, 2)

        self.start = 0
        self.stop = 10

        self.s = 0

        def update():
            dat = []

            while self.q.empty() == False:   # get all the data since the last update
                dat.append(self.q.get())

            for sample in dat:
                if self.s < self.x.size:    # if we're still on the graph, just add data to the matrix
                    # we only need the first sample, our plotting resolution isn't that high
                    self.y[:, self.s] = (sample[:, 0])
                    self.s += 1
                else:   # if we've made it off the graph, also shift the graph to the left slightly
                    self.y[:, :-1] = self.y[:, 1:]
                    self.y[:, -1] = (sample[:, 0])

            if self.s == self.x.size:   # if we're shifting, then adjust the scale to keep the graph in view
                self.x += 0.1
                self.start += 0.1
                self.stop += 0.1

            for i in range(len(self.curves)):
                self.curves[i].setData(self.x, self.y[i, :])
                self.plots[i].setRange(xRange=(self.start, self.stop), padding=0)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(update)
        self.timer.start(100)


class emgPlotter(plotter):
    def initialize(self):
        self.title = "EMG Plot"
        self.width = 720
        self.height = 556
        self.posx = 0
        self.posy = 0
        self.yRange = (0, 1)

    def createAxesData(self):
        x = np.linspace(0, 10, 10*Fs/blockSamples)
        y = np.full((electrodeNum, x.size), 0.5)
        return (x, y)

    def setupPlots(self, w, curves, plots):
        for i in range(electrodeNum):
            plot = w.addPlot(title="Sensor {0}".format(i+1))

            curves.append(plot.plot(pen='y'))
            plots.append(plot)

            if ((i+1) % 2 == 0):
                w.nextRow()
    

class synergyPlotter(plotter):
    def initialize(self):
        self.title = "Synergy Activation"
        self.width = 720
        self.height = 278
        self.posx = 0
        self.posy = 622
        self.yRange = (0, 1)

    def createAxesData(self):
        x = np.linspace(0, 10, 10*Fs/blockSamples)
        y = np.full((synergyNum, x.size), 0.5)
        return (x, y)

    def setupPlots(self, w, curves, plots):
        synergies = ["Hand Open", "Hand Close", "Pronation", "Supination"]
        for i in range(synergyNum):
            plot = w.addPlot(title=synergies[i])

            curves.append(plot.plot(pen='r'))
            plots.append(plot)

            if ((i+1) % 2 == 0):
                w.nextRow()
