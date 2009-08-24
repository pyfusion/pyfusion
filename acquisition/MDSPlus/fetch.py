"""MDSPlus data fetchers. """

from pyfusion.acquisition.base import BaseDataFetcher

class MDSPlusBaseDataFetcher(BaseDataFetcher):    
    def setup(self):
        self.mds_status=self.acq._Data.execute("mdsopen('%(mds_tree)s',%(shot)d)" %{'mds_tree':self.mds_tree, 'shot':self.shot})
    def pulldown(self):
        self.mds_status=self.acq._Data.execute("mdsclose()")
        
        
class MDSPlusTimeseriesDataFetcher(MDSPlusBaseDataFetcher):
    def do_fetch(self):
        data = self.acq._Data.execute("mdsvalue('%(mds_path)s')" %{'mds_path':self.mds_path})
        timebase = self.acq._Data.execute("mdsvalue('dim_of(%(mds_path)s)')" %{'mds_path':self.mds_path})
        from pyfusion.data.timeseries import TimeseriesData, Signal, Timebase

        output_data = TimeseriesData(timebase=Timebase(timebase.value),
                                     signal=Signal(data.value))
        output_data.meta.update({'shot':self.shot})
        return output_data
class MDSPlusDataFetcher(MDSPlusBaseDataFetcher):
    pass

