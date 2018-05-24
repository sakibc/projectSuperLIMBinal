""" Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
    
"""
from scipy import signal as sig
import numpy as np

from constants import *

# generate numerator and denominator for comb filter to remove mains noise
w0 = 60/(Fs/2)
Q = 35

bComb, aComb = sig.iirnotch(w0, Q)

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
    