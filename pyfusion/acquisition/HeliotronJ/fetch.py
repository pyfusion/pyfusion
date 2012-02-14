"""Heliotron J data fetchers. """

import tempfile
import numpy as np
from pyfusion.acquisition.base import BaseDataFetcher
from pyfusion.data.timeseries import TimeseriesData, Signal, Timebase
from pyfusion.data.base import Coords, ChannelList, Channel

try:
    import gethjdata
except:
    # don't raise an exception - otherwise tests will fail.
    # TODO: this should go into logfile
    print ImportError, "Can't import Heliotron J data aquisition library"

VERBOSE = 0
OPT = 0

class HeliotronJDataFetcher(BaseDataFetcher):
     """Fetch the HJ data."""

     def do_fetch(self):
         channel_length = int(self.length)
         outdata=np.zeros(1024*2*256+1)
         with tempfile.NamedTemporaryFile(prefix="pyfusion_") as outfile:
             getrets=gethjdata.gethjdata(self.shot,channel_length,self.path,
                                         VERBOSE, OPT,
                                         outfile.name, outdata)
         ch = Channel(self.path,
                      Coords('dummy', (0,0,0)))

         output_data = TimeseriesData(timebase=Timebase(getrets[1::2]),
                                 signal=Signal(getrets[2::2]), channels=ch)
         output_data.meta.update({'shot':self.shot})
         
         return output_data

