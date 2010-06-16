"""DSV data fetchers. """

from pyfusion.acquisition.base import BaseDataFetcher
from pyfusion.data.timeseries import Signal, Timebase, TimeseriesData
from pyfusion.data.base import Coords, Channel, ChannelList

from numpy import genfromtxt

class DSVMultiChannelTimeseriesFetcher(BaseDataFetcher):
    def do_fetch(self):
        data = genfromtxt(self.filename, unpack=True)
        ch = ChannelList(*(Channel('channel_%03d' %i, Coords('dummy', (i,0,0))) for i in range(len(data[1:]))))
        output_data = TimeseriesData(timebase=Timebase(data[0]), signal=Signal(data[1:]), channels=ch)
        #output_data.meta.update({'shot':self.shot})
        return output_data 
