"""
"""

from pyfusion.test.tests import BasePyfusionTestCase
from pyfusion.data.timeseries import TimeseriesData

class TestH1MirnovCoords(BasePyfusionTestCase):

    def test_single_mirnov_channel_kappah_as_argument(self):
        import pyfusion
        d=pyfusion.getDevice('H1')
        data = d.acq.getdata(58073, 'H1_mirnov_array_1_coil_1')
        self.assertTrue(isinstance(data, TimeseriesData))
        from pyfusion.data.base import MetaData
        self.assertTrue(isinstance(data.meta, MetaData))
        self.assertTrue(hasattr(data, 'coordinates'))
        from pyfusion.data.base import Coords
        for c in data.coordinates:
            self.assertTrue(isinstance(c, Coords))
            self.assertTrue(hasattr(c, 'cylindrical'))
            self.assertTrue(hasattr(c, 'magnetic'))
        coil_1_coords_kh_0 = data.coordinates[0].magnetic(kh=0.0)
        self.assertTrue(isinstance(coil_1_coords_kh_0, tuple))
        self.failUnlessAlmostEqual(data.coordinates[0].magnetic(kh=0.0)[0], -0.183250233, places=8)
        self.failUnlessAlmostEqual(data.coordinates[0].magnetic(kh=0.5)[0], -0.139925787181, places=8)
        self.failUnlessAlmostEqual(data.coordinates[0].magnetic(kh=1.0)[0], -0.024546986649, places=8)


    def test_single_mirnov_channel_kappah_from_metadata(self):
        import pyfusion
        h1test = pyfusion.getDevice('H1')
        shot_kh = (58073, 0.74)
        data = h1test.acq.getdata(shot_kh[0],
                                  'H1_mirnov_array_1_coil_1')
        self.assertAlmostEqual(data.coordinates[0].magnetic(), data.coordinates[0].magnetic(kh=shot_kh[1]))        

    def test_single_channel_with_kappah_supplied_through_metadata(self):
        pass
    
    def test_multichannel_mirnov_bean_kappah_as_argument(self):
        import pyfusion
        d=pyfusion.getDevice('H1')
        data = d.acq.getdata(58073, 'H1_mirnov_array_1')
        self.assertEqual(data.signal.n_channels(), len(data.coordinates))
        
    def test_multichannel_mirnov_bean_kappah_from_metadata(self):
        pass

TestH1MirnovCoords.h1 = True
TestH1MirnovCoords.net = True
TestH1MirnovCoords.slow = True
TestH1MirnovCoords.busted = True

class TestH1Device(BasePyfusionTestCase):

    def test_load_h1(self):
        from pyfusion.devices.base import Device
        from pyfusion.devices.H1.device import H1

        self.assertTrue(issubclass(H1, Device))
        
    def test_getdevice(self):
        import pyfusion
        h1test = pyfusion.getDevice('H1')
        from pyfusion.devices.H1.device import H1

        self.assertTrue(isinstance(h1test, H1))

    def test_kh(self):
        import pyfusion
        h1test = pyfusion.getDevice('H1')
        shot_kh = (58073, 0.74)
        data = h1test.acq.getdata(shot_kh[0], 'H1_mirnov_array_1_coil_1')        
        self.assertAlmostEqual(data.meta['kh'], shot_kh[1])


TestH1Device.slow = True
TestH1Device.h1 = True
TestH1Device.net = True
