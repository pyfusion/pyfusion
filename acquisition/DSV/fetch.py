"""DSV data fetchers. """

from pyfusion.acquisition.base import BaseDataFetcher
from pyfusion.data.timeseries import Signal, Timebase, TimeseriesData
from pyfusion.data.base import Coords

from numpy import genfromtxt

class DSVMultiChannelTimeseriesFetcher(BaseDataFetcher):
    def do_fetch(self):
        data = genfromtxt(self.filename, unpack=True)
        output_data = TimeseriesData(timebase=Timebase(data[0]), signal=Signal(data[1:]), coords=tuple(Coords() for i in data[1:]))
        #output_data.meta.update({'shot':self.shot})
        return output_data 
