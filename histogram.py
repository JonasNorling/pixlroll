#!/usr/bin/python
#
# Copyright 2014, Jonas Norling <jonas.norling@gmail.com>
#
# This software program is licensed under the GNU General Public License v2.
#

from __future__ import division
import numpy as np

class Histogram(object):    
    def __init__(self, length):
        self.length = length
        self.array = np.zeros(length, dtype=int)
        self.pos = 0
    
    def addData(self, values):
        for v in values:
            self.array[self.pos] = v
            self.pos = (self.pos + 1) % self.length

    # Return a histogram with values 0..1
    def calculate(self, datarange):
        hist, bins = np.histogram(self.array, bins=(datarange[1] - datarange[0] + 1), range=datarange)
        hist = np.flipud(np.cumsum(np.flipud(hist)))
        hist = hist * (1.0 / self.length)
        return hist
