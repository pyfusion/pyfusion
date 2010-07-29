""" Test code for LHD data acquision."""

from pyfusion.test.tests import BasePyfusionTestCase

class TestLHDDataAcq(BasePyfusionTestCase):

    def test_return_type(self):
        from pyfusion.acquisition.LHD.acq import LHDAcquisition
        
TestLHDDataAcq.lhd = True
