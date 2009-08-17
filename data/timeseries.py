"""Timeseries data classes."""

from numpy import arange

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
        return arange(self.t0, self.t0+self.n_samples*sample_time, sample_time)

class Signal:
    """Timeseries signal class with (not-yet-implemented) configurable digitisation."""
    def __init__(self, input_signal):
        self.signal = input_signal

class TimeseriesData(BaseData):
    def __init__(self, timebase = None, signal=None, **kwargs):
        self.timebase = timebase
        self.signal = signal
        super(TimeseriesData, self).__init__(**kwargs)

