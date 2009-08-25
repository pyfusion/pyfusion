"""
"""

from pyfusion.test.tests import BasePyfusionTestCase
from pyfusion.data.timeseries import TimeseriesData

class TestH1MirnovCoords(BasePyfusionTestCase):

    def test_single_mirnov_channel(self):
        import pyfusion
        d=pyfusion.getDevice('H1')
        data = d.acq.getdata(58073, 'H1_mirnov_array_1_coil_1')
        self.assertTrue(isinstance(data, TimeseriesData))
        from pyfusion.data.base import MetaData
        self.assertTrue(isinstance(data.meta, MetaData))
        self.assertTrue(hasattr(data.meta, 'coords'))
        from pyfusion.data.base import Coords
        self.assertTrue(isinstance(data.meta.coords, Coords))
        self.assertTrue(hasattr(data.meta.coords, 'cylindrical'))
        self.assertTrue(hasattr(data.meta.coords, 'magnetic'))
        
        
    def test_multichannel_mirnov_bean(self):
        pass
