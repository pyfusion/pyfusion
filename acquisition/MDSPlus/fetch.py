"""MDSPlus data fetchers. """

from pyfusion.acquisition.base import BaseDataFetcher

class MDSPlusBaseDataFetcher(BaseDataFetcher):    
    def setup(self):
        self.mds_status=self._Data.execute("mdsopen('%(mds_tree)s',%(shot)d)" %{'mds_tree':self.mds_tree, 'shot':self.shot})
    def pulldown(self):
        self.mds_status=self._Data.execute("mdsclose()")
        
        
class MDSPlusTimeseriesDataFetcher(MDSPlusBaseDataFetcher):
    def do_fetch(self):
        data = self._Data.execute("mdsvalue('%(mds_path)s')" %{'mds_path':self.mds_path})
        timebase = self._Data.execute("mdsvalue('dim_of(%(mds_path)s)')" %{'mds_path':self.mds_path})
        from pyfusion.data.timeseries import SCTData
        return SCTData(timebase.value, data.value)

class MDSPlusDataFetcher(MDSPlusBaseDataFetcher):
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
