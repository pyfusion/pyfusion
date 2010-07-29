"""Test LHD device code."""

from pyfusion.test.tests import BasePyfusionTestCase

class TestLHDDevice(BasePyfusionTestCase):
    def test_device(self):
        import pyfusion as pf
        lhd = pf.getDevice('LHD')
        data = lhd.acq.getdata(90091, 'LHD_Mirnov_toroidal')
TestLHDDevice.lhd = True
