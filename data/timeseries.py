"""Timeseries data classes."""

import numpy as np

from pyfusion.data.base import BaseData


class Timebase(np.ndarray):
    """Timebase vector with parameterised internal representation.

    see doc/subclassing.py in numpy code for details on subclassing ndarray
    """
    def __new__(cls, input_array):
        obj = np.asarray(input_array).view(cls).copy()
        return obj

    def __array_finalize__(self,obj):
        pass

def generate_timebase(t0=0.0, n_samples=1.e4, sample_freq=1.e6):
    sample_time = 1./sample_freq
    return Timebase(np.arange(t0, t0+n_samples*sample_time, sample_time))
"""
class Timebase:
    def __init__(self, t0=None, n_samples=None, sample_freq=None):
        self.t0 = t0
        self.n_samples = n_samples
        self.sample_freq = sample_freq
        self.timebase = self.generate_timebase()
    def generate_timebase(self):
"""

class Signal(np.ndarray):
    """Timeseries signal class with (not-yet-implemented) configurable
    digitisation.

    see doc/subclassing.py in numpy code for details on subclassing ndarray
    """
    def __new__(cls, input_array):
        obj = np.asarray(input_array).view(cls).copy()
        return obj

    def __array_finalize__(self,obj):
        pass

    def n_channels(self):
        if self.ndim == 1:
            return 1
        else:
            return self.shape[0]

    def n_samples(self):
        if self.ndim == 1:
            return self.shape[0]
        else:
            return self.shape[1]

    #def add_channel(self, additional_array):
    ##### -- problems with resizing subclass of ndarray, need to be careful 
    #    additional_signal = Signal(additional_array)
    #    new_n_channels = self.n_channels() + additional_signal.n_channels()
    #    self.resize((new_n_channels, self.n_samples()))
    #    self[-additional_signal.n_channels():,:] = additional_signal
    

class TimeseriesData(BaseData):
    def __init__(self, timebase = None, signal=None, **kwargs):
        self.timebase = timebase
        self.signal = signal
        super(TimeseriesData, self).__init__(**kwargs)

