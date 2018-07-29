""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
from scipy import signal as sig
import numpy as np

from constants import *

# generate numerator and denominator for comb filter to remove mains noise
w0 = 60/(Fs/2)
Q = 35

bComb, aComb = sig.iirnotch(w0, Q)

wh = 20/(Fs/2)  # high-pass filter
bHigh, aHigh = sig.butter(3, wh, btype='highpass')

# smoothing filter coefficients, from MATLAB
# it's just a 2nd order butterworth lowpass with f_c = 4
sos = [[1, 2, 1, 1, -1.99260754938975, 0.992634773113031]]
g = 6.8059308200936e-06

# wl = 4/(Fs/2)
# bLow, aLow = sig.butter(2, wl)


for i in range(2,7): # remove 5 more harmonics for good measure...
    w0i = i*w0
    b, a = sig.iirnotch(w0i, Q)
    bComb = sig.convolve(bComb, b)
    aComb = sig.convolve(aComb, a)

b = sig.convolve(bComb, bHigh)
a = sig.convolve(aComb, aHigh)


def lowComb(signal):
    """Remove 60Hz mains noise from prerecorded signal, and run through high-pass filter."""
    return sig.filtfilt(b, a, signal)

def center(signal):
    """Move a 0-255 signal to -128 to 127."""
    return np.subtract(signal, 128)

def longPrep(signal):
    """Prep a prerecorded signal array for NNMF decomposition."""
    signal = lowComb(center(signal))
    signal = np.square(signal)
    windowLen = round(0.5*Fs)
    window = np.ones(windowLen)/windowLen
    return sig.lfilter(window,1,signal)
    # return g*sig.sosfilt(sos, signal)
    
class liveFilter():
    """A filter that keeps track of previous states for realtime filtering."""
    def __init__(self):
        self.zic = np.zeros((electrodeNum,(max(b.size,a.size)-1)))
        # internal state for 60Hz comb filter
        self.zis = np.expand_dims(np.tile(sig.sosfilt_zi(sos),(8,1)),axis=0)
        # internal state for smoothing filter

    def lowComb(self, signal):
        y, self.zic = sig.lfilter(b, a, signal, zi=self.zic)
        return y

    def smooth(self, signal):
        y, self.zis = sig.sosfilt(sos,signal,zi=self.zis)
        return g*y
        # let's see if this works, okay?

    def prep(self, signal):
        signal = self.lowComb(center(signal))
        signal = np.square(signal)
        return self.smooth(signal)


    
