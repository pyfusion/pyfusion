"""MDSPlus data fetchers. """

import os, re
import numpy as np
import MDSplus
from pyfusion.acquisition.base import BaseDataFetcher
from pyfusion.data.timeseries import TimeseriesData, Signal, Timebase
from pyfusion.data.base import Coords, ChannelList, Channel

mds_path_regex = re.compile(
    r'^\\(?P<tree>\w+?)::(?P<tagname>\w+?)[.|:](?P<nodepath>[\w.:]+)')

def get_tree_path(path_string):
     components = mds_path_regex.search(path_string)
     return components.group('tree'), components.group('nodepath')

def get_mds_signal_from_node(fetcher, node):
    # TODO: load actual coordinates
    ch = Channel(fetcher.node_from_fullpath, Coords('dummy', (0,0,0)))
    signal = Signal(node.data())    
    dim = node.dim_of().data()
    # TODO: stupid hack,  the test signal has dim  of [[...]], real data
    # has [...].  Figure out  why. (...probably because  original signal
    # uses a build_signal function)
    if len(dim) == 1:
        dim = dim[0]
    timebase = Timebase(dim)
    output_data = TimeseriesData(timebase=timebase, signal=signal, channels=ch)
    output_data.meta.update({'shot':fetcher.shot})
    return output_data

class MDSPlusDataFetcher(BaseDataFetcher):
     """Determine which access mode should be used, and fetch the MDSplus data."""

     def setup(self):
          self.tree_from_fullpath, self.node_from_fullpath = get_tree_path(self.mds_path)
          if hasattr(self.acq, '%s_path' %self.tree_from_fullpath):
               self.tree = MDSplus.Tree(self.tree_from_fullpath, self.shot)
               self.is_thin_client = False
          else:
               self.acq.connection.openTree(self.tree_from_fullpath, self.shot)
               self.is_thin_client = True


     def do_fetch(self):
          # TODO support non-signal datatypes
          if self.is_thin_client:
               ch = Channel(self.tree_from_fullpath, Coords('dummy', (0,0,0)))
               data = self.acq.connection.get(self.node_from_fullpath)
               dim = self.acq.connection.get('dim_of(%s)' %self.node_from_fullpath)
               # TODO: fix this hack (same hack as when getting signal from node)
               if len(data.shape) > 1:
                    data = np.array(data)[0,]
               if len(dim.shape) > 1:
                    dim = np.array(dim)[0,]
               output_data = TimeseriesData(timebase=Timebase(dim), signal=Signal(data), channels=ch)
               output_data.meta.update({'shot':self.shot})
               return output_data
               
          else:
               node = self.tree.getNode(self.mds_path)
               if int(node.dtype) == 195:
                    return get_mds_signal_from_node(self, node)

     def pulldown(self):
          if self.is_thin_client:
               self.acq.connection.closeTree(self.tree_from_fullpath, self.shot)
