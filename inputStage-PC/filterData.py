""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
from scipy import signal as sig
import numpy as np

from constants import *

# generate numerator and denominator for comb filter to remove mains noise
w0 = 60/(Fs/2)
Q = 35

bComb, aComb = sig.iirnotch(w0, Q)

# smoothing filter coefficients, from MATLAB
# it's just a butterworth lowpass with f_c = 4 and -40dB/dec
sos = [[1,2,1,1,-1.98520158288979,0.985310278158978]]
g = 2.71738172958892e-05


for i in range(2,7): # remove 5 more harmonics for good measure...
    w0i = i*w0
    b, a = sig.iirnotch(w0i, Q)
    bComb = sig.convolve(bComb, b)
    aComb = sig.convolve(aComb, a)

def mainsComb(signal):
    """Remove 60Hz mains noise from prerecorded signal."""
    return sig.filtfilt(bComb, aComb, signal)

def center(signal):
    """Move a 0-255 signal to -128 to 127."""
    return np.subtract(signal, 128)

def longPrep(signal):
    """Prep a prerecorded signal array for NNMF decomposition."""
    signal = mainsComb(center(signal))
    signal = np.square(signal)
    windowLen = round(0.5*Fs)
    window = np.ones(windowLen)/windowLen
    return sig.lfilter(window,1,signal)
    
class liveFilter():
    """A filter that keeps track of previous states for realtime filtering."""
    def __init__(self):
        self.zic = np.zeros((electrodeNum,(max(bComb.size,aComb.size)-1)))
        # internal state for 60Hz comb filter
        self.zis = np.expand_dims(np.tile(sig.sosfilt_zi(sos),(8,1)),axis=0)
        # internal state for smoothing filter

    def comb(self, signal):
        y, self.zic = sig.lfilter(bComb, aComb, signal, zi=self.zic)
        return y

    def smooth(self, signal):
        y, self.zis = sig.sosfilt(sos,signal,zi=self.zis)
        return g*y
        # let's see if this works, okay?

    def prep(self, signal):
        signal = self.comb(center(signal))
        signal = np.square(signal)
        return self.smooth(signal)


    
