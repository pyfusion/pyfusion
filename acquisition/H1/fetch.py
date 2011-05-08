"""MDSPlus data fetchers. """

#from pyfusion.acquisition.MDSPlus.fetch import MDSPlusBaseDataFetcher, MDSPlusLocalBaseDataFetcher
from pyfusion.acquisition.MDSPlus.fetch import MDSPlusDataFetcher
from pyfusion.data.timeseries import TimeseriesData, Signal, Timebase
from pyfusion.data.base import Coords, Channel, ChannelList, get_coords_for_channel

class H1DataFetcher(MDSPlusDataFetcher):
    """ subclass of mds fetcher which grabs kh config data"""

    def do_fetch(self):
        output_data = super(H1DataFetcher, self).do_fetch()
        coords = get_coords_for_channel(**self.__dict__)
        ch = Channel(self.mds_path, coords)
        output_data.channels = ch
        output_data.meta.update({'shot':self.shot, 'kh':self.get_kh()})
        return output_data

    def get_kh(self):
        imain2_path = '.operations.magnetsupply.lcu.setup_main.i2'
        isec2_path = '.operations.magnetsupply.lcu.setup_sec.i2'
        if self.is_thin_client:
            try:
                imain2 = self.acq.connection.get(imain2_path)
                isec2 = self.acq.connection.get(isec2_path)
                return float(isec2/imain2)
            except:
                return None
        else:
            try:
                imain2 = self.tree.getNode(imain2_path)
                isec2 = self.tree.getNode(isec2_path)
                return float(isec2/imain2)
            except:
                return None
        

