from pyfusion.acquisition.base import BaseDataFetcher
from pyfusion.data.timeseries import Signal, Timebase, TimeseriesData
from pyfusion.data.base import Coords, Channel, ChannelList

import numpy as np
##### 

# Generate generic channel with dummy coordinates.
generic_ch = lambda x: Channel('channel_%03d' %(x+1), Coords('dummy', (x,0,0)))

named_ch = lambda x: Channel(x, Coords('dummy', (x,0,0)))

class BinaryMultiChannelTimeseriesFetcher(BaseDataFetcher):
    """Fetch binary data from specified filename.

    
    This data fetcher uses two configuration parameters, filename (required) and a dtype specification

    The filename parameter can include a substitution string ``(shot)`` which will be replaced with the shot number.

    dtype will be evaluated as string, numpy can be used with np namespace
    e.g. np.float32

    """
    def read_dtype(self):
        dtype = self.__dict__.get("dtype", None)
        return eval(dtype)

    def do_fetch(self):
        dtype = self.read_dtype()
        data = np.fromfile(self.filename.replace("(shot)", str(self.shot)),
                          dtype=dtype)        

        channel_names = [i for i in dtype.names if i.startswith('channel_')]
        
        ch_generator = (named_ch(i) for i in channel_names)
        ch = ChannelList(*ch_generator)

        signal_data = np.zeros((len(channel_names),data.shape[0]),dtype=dtype[channel_names[0]])
        for ch_i,ch_name in enumerate(channel_names):
            signal_data[ch_i,:] = data[ch_name]

        return TimeseriesData(timebase=Timebase(data['timebase']),
                              signal=Signal(signal_data),
                              channels=ch)

