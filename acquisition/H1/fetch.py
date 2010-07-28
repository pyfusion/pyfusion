"""MDSPlus data fetchers. """

from pyfusion.acquisition.MDSPlus.fetch import MDSPlusBaseDataFetcher
from pyfusion.data.timeseries import TimeseriesData, Signal, Timebase
from pyfusion.data.base import Coords
def get_kh(mds_data):
    imain2 = mds_data.execute("mdsvalue('%(mds_path)s')" %{'mds_path':'.operations.magnetsupply.lcu.setup_main.i2'})
    isec2 = mds_data.execute("mdsvalue('%(mds_path)s')" %{'mds_path':'.operations.magnetsupply.lcu.setup_sec.i2'})
    return isec2/imain2

class H1TimeseriesDataFetcher(MDSPlusBaseDataFetcher):
    """ subclass of mds fetcher which grabs kh config data"""

    def do_fetch(self):
        data = self.acq._Data.execute("mdsvalue('%(mds_path)s')" %{'mds_path':self.mds_path})
        timebase = self.acq._Data.execute("mdsvalue('dim_of(%(mds_path)s)')" %{'mds_path':self.mds_path})
        #coords = Coords('dummy',(0.0,0.0,0.0))
        #coords.load_from_config(**self.__dict__)
        output_data = TimeseriesData(timebase=Timebase(timebase.value),
                                     signal=Signal(data.value))#, coords=[coords])
        output_data.meta.update({'shot':self.shot, 'kh':get_kh(self.acq._Data)})
        return output_data

