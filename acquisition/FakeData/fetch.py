"""Fake data acquisition fetchers used for testing pyfusion code."""

from pyfusion.acquisition.base import BaseDataFetcher
from pyfusion.data.base import Coords, ChannelList, Channel

class SingleChannelSineDF(BaseDataFetcher):
    """Data fetcher for single channel sine wave."""
    """
    def __init__(self, shot, t0=None, sample_freq=None, amplitude=None,
                 frequency=None, n_samples=None, **kwargs):
        self.t0=t0
        self.sample_freq=sample_freq
        self.amplitude=amplitude
        self.frequency=frequency
        self.n_samples = n_samples
        super(SingleChannelSineDF, self).__init__(shot, **kwargs)
    """
    def fetch(self):
        from pyfusion.data.timeseries import TimeseriesData, Signal, generate_timebase
        from numpy import sin, pi
        tb = generate_timebase(t0=self.t0, n_samples=self.n_samples, sample_freq=self.sample_freq)
        sig = Signal(self.amplitude*sin(2*pi*self.frequency*tb))
        output_data = TimeseriesData(timebase=tb, signal=sig, channels=ChannelList(Channel('ch_01',Coords('dummy', (0,0,0)))))
        output_data.meta.update({'shot':self.shot})
        return output_data
