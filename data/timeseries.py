"""Timeseries data classes."""

import numpy as np

from pyfusion.data.base import BaseData
from utils import cps, peak_freq, remap_periodic

        

class Timebase(np.ndarray):
    """Timebase vector with parameterised internal representation.

    see doc/subclassing.py in numpy code for details on subclassing ndarray
    """
    def __new__(cls, input_array):
        obj = np.asarray(input_array).view(cls).copy()
        obj.sample_freq = 1./(obj[1]-obj[0])
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

    def get_channel(self, channel_number):
        """allows us to use get_channel(0) no matter what ndim is"""
        if self.ndim == 1 and channel_number == 0:
            return self
        elif self.ndim > 1:
            return self[channel_number,:]
        else:
            raise ValueError

        
    #def add_channel(self, additional_array):
    ##### -- problems with resizing subclass of ndarray, need to be careful 
    #    additional_signal = Signal(additional_array)
    #    new_n_channels = self.n_channels() + additional_signal.n_channels()
    #    self.resize((new_n_channels, self.n_samples()))
    #    self[-additional_signal.n_channels():,:] = additional_signal
    

class TimeseriesData(BaseData):
    def __init__(self, timebase = None, signal=None, **kwargs):
        self.timebase = timebase
        if signal.n_samples() == len(timebase):
            self.signal = signal
        else:
            raise ValueError, "signal has different number of samples to timebase"
        super(TimeseriesData, self).__init__(**kwargs)


class SVDData(BaseData):
    def __init__(self, svd_input):
        """
        svd_input is a tuple as outputted by numpy.linalg.svd(data, 0)
        """
        self.topos = np.transpose(svd_input[0])
        self.svs = svd_input[1]
        self.chronos = svd_input[2]
        self.E = sum(self.svs*self.svs)
        self.p = self.svs**2/self.E

    def self_cps(self):
        try:
            return self._self_cps
        except AttributeError:
            self._self_cps = np.array([np.mean(cps(i,i)) for i in self.chronos])
            return self._self_cps

class FlucStruc(BaseData):
    def __init__(self, svd_data, sv_list, timebase, min_dphase = -np.pi):
        self.svs = sv_list
        # peak frequency for fluctuation structure
        self.freq = peak_freq(svd_data.chronos[sv_list[0]], timebase)
        self.timebase = timebase
        # singular value filtered signals
        self.signal = np.dot(np.transpose(svd_data.topos[self.svs,:]),
                           np.dot(np.diag(svd_data.svs.take(self.svs)), svd_data.chronos[self.svs,:]))
        # phase differences between nearest neighbour channels
        self.dphase = self._get_dphase(min_dphase=min_dphase)
        self.p = np.sum(svd_data.svs.take(self.svs)**2)/svd_data.E

    def _get_dphase(self, min_dphase = -np.pi):
        """
        remap to [min_dphase, min_dphase+2pi]
        """
        phases = np.array([self._get_single_channel_phase(i) for i in range(self.signal.shape[0])])
        return remap_periodic(phases[1:]-phases[:-1], min_val = min_dphase)
    def _get_single_channel_phase(self, ch_id):
        data_fft = np.fft.fft(self.signal[ch_id])
        # fft goes up to sample freq (mirror-like about Nyquist)
        freq_array = self.timebase.sample_freq*np.arange(len(data_fft))/(len(data_fft)-1)
        freq_elmt = np.searchsorted(freq_array,self.freq)
        a = data_fft[freq_elmt].real
        b = data_fft[freq_elmt].imag
        phase_val = np.arctan2(a,b)
        return phase_val
