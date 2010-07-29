"""LHD data fetchers.
Large chunks of code copied from Boyd, not covered by unit tests.
"""

from os import path
from numpy import mean, array, double, arange, dtype
import numpy as np
import array as Array

from pyfusion.acquisition.base import BaseDataFetcher
from pyfusion.data.timeseries import TimeseriesData, Signal, Timebase
from pyfusion.data.base import Coords, Channel, ChannelList

data_filename = "%(diag_name)s-%(shot)d-1-%(channel_number)s"

class LHDBaseDataFetcher(BaseDataFetcher):
    pass

class LHDTimeseriesDataFetcher(LHDBaseDataFetcher):
    def do_fetch(self):
        filename_dict = {'diag_name':self.diag_name, 
                         'channel_number':self.channel_number, 
                         'shot':self.shot}
        self.basename = path.join(self.filepath, data_filename %filename_dict)

        files_exist = path.exists(self.basename + ".dat") and path.exists(self.basename + ".prm")
        if files_exist: 
            return fetch_data_from_file(self)
        else:
            raise NotImplementedError

def fetch_data_from_file(fetcher):
    prm_dict = read_prm_file(fetcher.basename+".prm")
    bytes = int(prm_dict['DataLength(byte)'][0])
    bits = int(prm_dict['Resolution(bit)'][0])
    if not(prm_dict.has_key('ImageType')):      #if so assume unsigned
        bytes_per_sample = 2
        arr = Array.array('H')
        offset = 2**(bits-1)
        dtype = np.dtype('uint16')
    else:
        if prm_dict['ImageType'][0] == 'INT16':
            bytes_per_sample = 2
            if prm_dict['BinaryCoding'][0] == 'offset_binary':
                arr = Array.array('H')
                offset = 2**(bits-1)
                dtype = np.dtype('uint16')
            elif prm_dict['BinaryCoding'][0] == "shifted_2's_complementary":
                arr = Array.array('h')
                offset = 0
                dtype = np.dtype('int16')
            else: raise NotImplementedError,' binary coding ' + prm_dict['BinaryCoding']

    fp = open(fetcher.basename + '.dat', 'rb')
    arr.fromfile(fp, bytes/bytes_per_sample)
    fp.close()

    clockHz = None

    if prm_dict.has_key('SamplingClock'): 
        clockHz =  double(prm_dict['SamplingClock'][0])
    if prm_dict.has_key('SamplingInterval'): 
        clockHz =  clockHz/double(prm_dict['SamplingInterval'][0])
    if prm_dict.has_key('ClockSpeed'): 
        if clockHz != None:
            pyfusion.utils.warn('Apparent duplication of clock speed information')
        clockHz =  double(prm_dict['ClockSpeed'][0])
    if clockHz != None:
        timebase = arange(len(arr))/clockHz
    else:  raise NotImplementedError, "timebase not recognised"
    
    ch = Channel("%s-%s" %(fetcher.diag_name, fetcher.channel_number), Coords('dummy', (0,0,0)))
    output_data = TimeseriesData(timebase=Timebase(timebase),
                                 signal=Signal(arr), channels=ch)
    output_data.meta.update({'shot':fetcher.shot})

    return output_data


def read_prm_file(filename):
    """ Read a prm file into a dictionary.  Main entry point is via filename,
    possibly reserve the option to access vai shot and subshot
    >>> pd = read_prm_file(filename=filename)
    >>> pd['Resolution(bit)']
    ['14', '2']
    """
    f = open(filename)
    prm_dict = {}
    for s in f:
        s = s.strip("\n")
        toks = s.split(',')  
        if len(toks)<2: print('bad line %s in %f' % (s, filename))
        key = toks[1]
        prm_dict.update({key: toks[2:]})
    f.close()
    return prm_dict
