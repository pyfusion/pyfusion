"""Data fetcher class for delimiter-separated value (DSV) data."""

from pyfusion.acquisition.base import BaseDataFetcher
from pyfusion.data.timeseries import Signal, Timebase, TimeseriesData
from pyfusion.data.base import Coords, Channel, ChannelList

from numpy import genfromtxt

class DSVMultiChannelTimeseriesFetcher(BaseDataFetcher):
    """Fetch DSV data from specified filename.

    This data fetcher requires a filename parameter to be set, either in a configuration file or as a keyword parameter to :py:meth:`DSVAcquisition.getdata`.
    """
    def do_fetch(self):
        data = genfromtxt(self.filename, unpack=True)
        ch = ChannelList(*(Channel('channel_%03d' %(i+1), Coords('dummy', (i,0,0))) for i in range(len(data[1:]))))
        output_data = TimeseriesData(timebase=Timebase(data[0]), signal=Signal(data[1:]), channels=ch)
        #output_data.meta.update({'shot':self.shot})
        return output_data 
