"""Timeseries data classes."""

import numpy as np

from pyfusion.data.base import BaseData

class Timebase:
    """Timebase vector with parameterised internal representation."""
    def __init__(self, t0=None, n_samples=None, sample_freq=None):
        self.t0 = t0
        self.n_samples = n_samples
        self.sample_freq = sample_freq
        self.timebase = self.generate_timebase()
    def generate_timebase(self):
        sample_time = 1./self.sample_freq
        return np.arange(self.t0, self.t0+self.n_samples*sample_time, sample_time)

class Signal(np.ndarray):
    """Timeseries signal class with (not-yet-implemented) configurable
    digitisation.

    see doc/subclassing.py in numpy code for details on subclassing ndarray
    """
    def __new__(cls, input_array):
        obj = np.asarray(input_array).view(cls)
        return obj

    def __array_finalize__(self,obj):
        pass
                                  


class TimeseriesData(BaseData):
    def __init__(self, timebase = None, signal=None, **kwargs):
        self.timebase = timebase
        self.signal = signal
        super(TimeseriesData, self).__init__(**kwargs)

