"""MDSPlus data fetchers. """

from pyfusion.acquisition.base import BaseDataFetcher
from pyfusion.data.timeseries import TimeseriesData, Signal, Timebase
from pyfusion.data.base import Coords, ChannelList, Channel
import MDSplus,os

class MDSPlusBaseDataFetcher(BaseDataFetcher):    
    def setup(self):
        self.mds_status=self.acq._Data.execute("mdsopen('%(mds_tree)s',%(shot)d)" %{'mds_tree':self.mds_tree, 'shot':self.shot})
    def pulldown(self):
        self.mds_status=self.acq._Data.execute("mdsclose()")
        

class MDSPlusLocalBaseDataFetcher(BaseDataFetcher):    
    def setup(self):
        #self.mds_status=self.acq._Data.execute("mdsopen('%(mds_tree)s',%(shot)d)" %{'mds_tree':self.mds_tree, 'shot':self.shot})
        os.environ['%s_path' %(self.mds_tree.lower())] = self.acq.__getattribute__('%s_path' %(self.mds_tree.lower()))
        self.tree = MDSplus.Tree(self.mds_tree, self.shot)
    def pulldown(self):
        pass
        #self.mds_status=self.acq._Data.execute("mdsclose()")

        
class MDSPlusTimeseriesDataFetcher(MDSPlusBaseDataFetcher):
    def do_fetch(self):
        data = self.acq._Data.execute("mdsvalue('%(mds_path)s')" %{'mds_path':self.mds_path})
        timebase = self.acq._Data.execute("mdsvalue('dim_of(%(mds_path)s)')" %{'mds_path':self.mds_path})
        #coords = Coords()
        #coords.load_from_config(**self.__dict__)
        ch = Channel(self.mds_path, Coords('dummy', (0,0,0)))

        output_data = TimeseriesData(timebase=Timebase(timebase.value),
                                     signal=Signal(data.value), channels=ch)#,
                                     #coords=[coords])
        output_data.meta.update({'shot':self.shot})
        return output_data
class MDSPlusDataFetcher(MDSPlusBaseDataFetcher):
    pass

