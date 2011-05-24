"""Subclass of MDSplus data fetcher to grab additional H1-specific metadata."""

from pyfusion.acquisition.MDSPlus.fetch import MDSPlusDataFetcher
from pyfusion.data.timeseries import TimeseriesData, Signal, Timebase
from pyfusion.data.base import Coords, Channel, ChannelList, \
    get_coords_for_channel

class H1DataFetcher(MDSPlusDataFetcher):
    """Subclass of MDSplus fetcher to get additional H1-specific metadata."""

    def do_fetch(self):
        output_data = super(H1DataFetcher, self).do_fetch()
        coords = get_coords_for_channel(**self.__dict__)
        ch = Channel(self.mds_path, coords)
        output_data.channels = ch
        output_data.meta.update({'shot':self.shot, 'kh':self.get_kh()})
        return output_data

    def get_kh(self):
        # TODO: shouldn't need to worry about fetch mode here...
        imain2_path = '.operations.magnetsupply.lcu.setup_main.i2'
        isec2_path = '.operations.magnetsupply.lcu.setup_sec.i2'
        if self.fetch_mode == 'thin client':
            try:
                imain2 = self.acq.connection.get(imain2_path)
                isec2 = self.acq.connection.get(isec2_path)
                return float(isec2/imain2)
            except:
                return None
        elif self.fetch_mode == 'http':
            pass
        else:
            try:
                imain2 = self.tree.getNode(imain2_path)
                isec2 = self.tree.getNode(isec2_path)
                return float(isec2/imain2)
            except:
                return None
        

