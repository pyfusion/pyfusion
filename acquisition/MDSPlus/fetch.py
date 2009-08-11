"""MDSPlus data fetchers. """

from pyfusion.acquisition.base import BaseDataFetcher

class MDSPlusDataFetcher(BaseDataFetcher):
    pass

"""
    def __init__(self, **kwargs):
        super(MDSPlusDataFetcher, self).__init__(**kwargs)


        self.t0=t0
        self.sample_freq=sample_freq
        self.amplitude=amplitude
        self.frequency=frequency
        self.n_samples = n_samples
        super(SingleChannelSineDF, self).__init__(**kwargs)

    def fetch(self):
        from pyfusion.data.timeseries import SCTData, Timebase, Signal
        from numpy import sin, pi
        tb = Timebase(t0=self.t0, n_samples=self.n_samples, sample_freq=self.sample_freq)
        sig = Signal(self.amplitude*sin(2*pi*self.frequency*tb.timebase))
        return SCTData(timebase=tb, signal=sig)
"""
