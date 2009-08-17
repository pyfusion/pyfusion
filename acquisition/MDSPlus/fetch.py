"""MDSPlus data fetchers. """

from pyfusion.acquisition.base import BaseDataFetcher

class MDSPlusBaseDataFetcher(BaseDataFetcher):    
    def setup(self):
        self.mds_status=self._Data.execute("mdsopen('%(mds_tree)s',%(shot)d)" %{'mds_tree':self.mds_tree, 'shot':self.shot})
    def pulldown(self):
        self.mds_status=self._Data.execute("mdsclose()")
        
        
class MDSPlusTimeseriesDataFetcher(MDSPlusBaseDataFetcher):
    def do_fetch(self):
        data = self._Data.execute("mdsvalue('%(mds_path)s')" %{'mds_path':self.mds_path})
        timebase = self._Data.execute("mdsvalue('dim_of(%(mds_path)s)')" %{'mds_path':self.mds_path})
        from pyfusion.data.timeseries import TimeseriesData
        return TimeseriesData(timebase.value, data.value)

class MDSPlusDataFetcher(MDSPlusBaseDataFetcher):
    pass

