"""MDSPlus data fetchers. """

from pyfusion.acquisition.MDSPlus.fetch import MDSPlusBaseDataFetcher, MDSPlusLocalBaseDataFetcher
from pyfusion.data.timeseries import TimeseriesData, Signal, Timebase
from pyfusion.data.base import Coords, Channel, ChannelList, get_coords_for_channel
def get_kh(mds_data):
    try:
        imain2 = mds_data.execute("mdsvalue('%(mds_path)s')" %{'mds_path':'.operations.magnetsupply.lcu.setup_main.i2'})
        isec2 = mds_data.execute("mdsvalue('%(mds_path)s')" %{'mds_path':'.operations.magnetsupply.lcu.setup_sec.i2'})
        return float(isec2/imain2)
    except:
        return None

class H1TimeseriesDataFetcher(MDSPlusBaseDataFetcher):
    """ subclass of mds fetcher which grabs kh config data"""

    def do_fetch(self):
        data = self.acq._Data.execute("mdsvalue('%(mds_path)s')" %{'mds_path':self.mds_path})
        timebase = self.acq._Data.execute("mdsvalue('dim_of(%(mds_path)s)')" %{'mds_path':self.mds_path})
        coords = get_coords_for_channel(**self.__dict__)
        ch = Channel(self.mds_path, coords)
        output_data = TimeseriesData(timebase=Timebase(timebase.value),
                                     signal=Signal(data.value), channels=ch)
        output_data.meta.update({'shot':self.shot, 'kh':get_kh(self.acq._Data)})
        return output_data

class H1LocalTimeseriesDataFetcher(MDSPlusLocalBaseDataFetcher):
    """ subclass of mds fetcher which grabs kh config data"""

    def do_fetch(self):
        data = self.tree.getNode(self.mds_path)
        timebase = data.dim_of().data()
        coords = get_coords_for_channel(**self.__dict__)
        ch = Channel(self.mds_path, coords)
        output_data = TimeseriesData(timebase=Timebase(timebase),
                                     signal=Signal(data.data()), channels=ch)
        output_data.meta.update({'shot':self.shot})
        return output_data

