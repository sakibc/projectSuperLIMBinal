""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
import matplotlib       # change drawing backend so that a framework version of
matplotlib.use('tkagg') # python is not necessary on mac.
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import multiprocessing as mp
import numpy as np
import queue

class emgPlotter:
    def __init__(self, q, electrodeNum):
        self.style()

        self.drawTime = 10  #only draw the last ten seconds
        self.electrodeNum = electrodeNum
        self.q = q
        self.fig, self.ax = plt.subplots(int(electrodeNum/2), 2, sharex=True, sharey=True)
        self.ax = np.transpose(self.ax).flatten()
        self.line = [self.ax[i].plot([], [])[0] for i in range(electrodeNum)]
        self.xdata = []
        self.ydata = [[] for i in range(electrodeNum)]

        self.fig.suptitle("EMG Sensor Data")
        self.fig.text(0.5, 0.04, "Time", ha='center')
        self.fig.text(0.04, 0.5, "Normalized Activation Level",
                va='center', rotation='vertical')

        for i in range(electrodeNum):
            self.ax[i].set_title("Electrode "+str(i+1))

    def startAni(self):
        self.ani = animation.FuncAnimation(
        self.fig, self.run, self.data_gen, blit=True, interval=100, repeat=False, init_func=self.setup)

        mng = plt.get_current_fig_manager() # maximize window, because it doesn't like
        mng.resize(*mng.window.maxsize())   # being maximized after the fact...
        plt.show()

    def style(self):
        plt.style.use('seaborn-darkgrid')   # this graph style looks pretty...
        matplotlib.rcParams['toolbar'] = 'None'

    def data_gen(self,t=0):  # get data to show on graph from other process
        while True:
            tlist = [t+0.1*i/60 for i in range(60)]
            t += 0.1
            try:
                dat = [self.q.get(block=True, timeout=1) for i in range(60)]
                # there's probably a more efficient way to do this...
                # pickling and unpickling 60 lists instead of 1 large list seems expensive
                yield tlist, dat
            except queue.Empty:
                break


    def setup(self):  # initialize empty graph
        del self.xdata[:]

        for i in range(self.electrodeNum):
            self.ax[i].set_ylim(0, 1)
            self.ax[i].set_xlim(0, self.drawTime)

            del self.ydata[i][:]

            self.line[i].set_data(self.xdata, self.ydata[i])

        return self.line


    def run(self,data):  # redraw graph
        # update the data
        t, elec = data
        self.xdata.extend(t)
        for i in range(self.electrodeNum):
            for j in range(60):
                self.ydata[i].append(elec[j][i]/255)

            self.line[i].set_data(self.xdata, self.ydata[i])
            xmin, xmax = self.ax[i].get_xlim()

            if t[-1] >= xmax:
                xshift = self.drawTime/2
                self.ax[i].set_xlim(xmin+xshift, xmax+xshift)
                self.ax[i].figure.canvas.draw()

        return self.line
