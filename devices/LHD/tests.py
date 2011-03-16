"""Test LHD device code."""

from pyfusion.test.tests import PfTestBase

class CheckLHDDevice(PfTestBase):
    def test_device(self):
        import pyfusion as pf
        lhd = pf.getDevice('LHD')
        data = lhd.acq.getdata(90091, 'LHD_Mirnov_toroidal')
CheckLHDDevice.net = True
CheckLHDDevice.lhd = True
