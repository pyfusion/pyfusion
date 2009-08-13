"""Test code for MDSPlus data acquisition."""

from pyfusion.test.tests import BasePyfusionTestCase

class TestMDSPlusDataAcquisition(BasePyfusionTestCase):

    def testBaseClasses(self):
        from pyfusion.acquisition.MDSPlus.acq import MDSPlusAcquisition
        from pyfusion.acquisition.base import BaseAcquisition
        self.assertTrue(BaseAcquisition in MDSPlusAcquisition.__bases__)

class TestMDSPlusDataFetchers(BasePyfusionTestCase):

    def testDataFetcherBaseClass(self):
        from pyfusion.acquisition.base import BaseDataFetcher
        from pyfusion.acquisition.MDSPlus.fetch import MDSPlusDataFetcher
        self.assertTrue(BaseDataFetcher in MDSPlusDataFetcher.__bases__)

class TestMDSPlusH1Connection(BasePyfusionTestCase):
    """tests which require access to h1data.anu.edu.au"""

    def testH1Data(self):
        from pyfusion.acquisition.MDSPlus.acq import MDSPlusAcquisition
        #h1mds = MDSPlusAcquisition(server="h1data.anu.edu.au")
        #test_data = h1.acq.getdata(45637, "mirnov_array_1_coil_1")
        
TestMDSPlusH1Connection.h1 = True
TestMDSPlusH1Connection.net = True
TestMDSPlusH1Connection.slow = True
