"""
Read data from local file
"""

from pyfusion.core import MultiChannelTimeseries
from pyfusion.devices.core import BasicLocalDataDevice

import gzip,bz2
from numpy import array

"""
Check check file suffix then open with normal, gzip or bzip2 command. read file and close.
"""
def genericfileread(filename, readlines = False):
    	if filename[-3:] == '.gz':
            file = gzip.open(filename)
        elif filename[-4:] == '.bz2':
            file = bz2.BZ2File(filename)
        else:
            file = open(filename)
        if readlines:
            data = file.readlines()
        else:
            data = file.read()
        file.close()
        return data

def readASCIIdata(filename, n_channels, sep = ''):
    """
    n_channels: excluding timebase
    sep = seperator, defulat = '' - will seperate any whitespace, including tab and newline
    """

    if sep == '':
        raw_data = genericfileread(filename).split()
    else:
        raw_data = genericfileread(filename).split(sep)        

    # use [::n_channels+1], where +1 is due to timebase
    tmp = array(map(float,raw_data[::n_channels+1]))
    mc_data = MultiChannelTimeseries(tmp)
    for cn in range(n_channels+1)[1:]:
        mc_data.add_channel(array(map(float,raw_data[cn::n_channels+1])),'UNKNOWN_DIAG_%d'%cn)

    return mc_data

class LocalData(BasicLocalDataDevice):
	def load_diag(self,diag_name, ignore_channels =[]):
		filename = settings.get_localdata_filename(diag_name)
		return readASCIIdata(filename, 14)
	
