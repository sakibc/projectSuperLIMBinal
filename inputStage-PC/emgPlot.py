""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""

from pyqtgraph.Qt import QtGui, QtCore
import multiprocessing as mp
import numpy as np
import pyqtgraph as pg
import queue

from constants import *

# app = QtGui.QApplication([])
# w = QtGui.QWidget()
# w.show()

# p = mp.Process(target=app.exec_)
# p.start

class emgPlotter:
    def __init__(self, electrodeNum, q):
        self.electrodeNum = electrodeNum
        self.q = q

        self.p = mp.Process(target=self.startGraph,args=(q,))
        self.p.start()

    def close(self):
        self.p.terminate()
        self.p.join()

    def startGraph(self, q):
        app = QtGui.QApplication([])
        w = pg.GraphicsWindow(title="EMG Plot")
        w.setGeometry(0,0,720,600)
        w.setWindowTitle("EMG Plot")

        self.x = np.linspace(0,10,6010)
        self.y = np.full((8,self.x.size),0.5)
        # self.ys = np.
        curves = []
        plots = []
        self.start = 0
        self.stop = 10

        self.t = 0

        for i in range(self.electrodeNum):
            plot = w.addPlot(title="Sensor {0}".format(i+1))
            plot.setMouseEnabled(x=False, y=False)
            plot.disableAutoRange()
            plot.showGrid(x=True, y=True)
            xaxis = plot.getAxis('bottom')
            xaxis.setTickSpacing(2,2)
            curves.append(plot.plot(pen='y'))
            plots.append(plot)
                
            if ((i+1) % 2 == 0):
                w.nextRow()

        def update():   # efficiency? where we're going, we don't need efficiency... or understandability
            dat = [self.q.get(timeout=0.1,block=True) for i in range(60)]

            if self.t >= 100:
                self.x = self.x + 0.1
                self.start += 0.1
                self.stop += 0.1

                for i in range(self.electrodeNum):
                    self.y[i,:-60] = self.y[i,60:]
                    self.y[i,-60:] = [(dat[j][i])/256 for j in range(60)]

            else:
                for i in range(self.electrodeNum):
                    self.y[i,self.t*60:(self.t*60+60)] = [(dat[j][i])/256 for j in range(60)]

            self.t += 1

            if self.t % 100 == 0:
                dat = [self.q.get(timeout=0.1,block=True) for i in range(10)]   # get the tennish extras that'll have built up
                for i in range(self.electrodeNum):
                    self.y[i,-10:] = [(dat[j][i])/256 for j in range(10)]

            for i in range(self.electrodeNum):
                curves[i].setData(self.x,self.y[i,:])
                plots[i].setRange(xRange=(self.start,self.stop),padding=0)
            
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(update)
        self.timer.start(100)

        app.exec_()
