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


class MultiFileBinaryMultiChannelTimeseriesFetcher(BaseDataFetcher):
    """Combine multiple binary datafiles into a single timeseries data instance.

    """


    def do_fetch(self):
        # evaluate filename list
        try:
            filenames = eval(self.__dict__.get("filenames", "[]"))
        except TypeError:
            # assume we have been given a list of filenames as a keyword argument, rather than
            # reading the config file.
            filenames = self.__dict__.get("filenames")
        
        data_array = []
        channel_names = []
        dtypes=[]
        for fn_i,fn in enumerate(filenames):
            dt = eval(self.__dict__.get("dtype_%d" %(fn_i+1),None))
            dtypes.append(dt)
            data_array.append(np.fromfile(fn.replace("(shot)", str(self.shot)),
                                          dtype=dt))
            channel_names.extend([i for i in dt.names if i.startswith('channel_')])
        
        ch_generator = (named_ch(i) for i in channel_names)
        ch = ChannelList(*ch_generator)
        
        signal_data = np.zeros((len(channel_names),data_array[0].shape[0]),dtype=dtypes[0][channel_names[0]])
        
        sig_counter = 0
        for d_i,d in enumerate(data_array):
            for ch_name in dtypes[d_i].names:
                if ch_name.startswith('channel_'):
                    signal_data[sig_counter,:] = d[ch_name]
                    sig_counter +=1

        tsd = TimeseriesData(timebase=Timebase(data_array[0]['timebase']),
                              signal=Signal(signal_data),
                              channels=ch)
        tsd.phase_pairs = self.__dict__.get("phase_pairs", None)
        if tsd.phase_pairs != None:
            tsd.phase_pairs = eval(tsd.phase_pairs)

        return tsd

