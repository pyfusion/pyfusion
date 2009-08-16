"""Test code for MDSPlus data acquisition."""

from pyfusion.test.tests import BasePyfusionTestCase

class TestMDSPlusDataAcquisition(BasePyfusionTestCase):

    def testBaseClasses(self):
        from pyfusion.acquisition.MDSPlus.acq import MDSPlusAcquisition
        from pyfusion.acquisition.base import BaseAcquisition
        self.assertTrue(BaseAcquisition in MDSPlusAcquisition.__bases__)

    def testHaveMDSPlusDataObject(self):
        from pyfusion.acquisition.MDSPlus.acq import MDSPlusAcquisition
        test_acq = MDSPlusAcquisition(server='h1data.anu.edu.au')
        self.assertTrue(hasattr(test_acq, '_Data'))
        from MDSplus import Data
        self.assertEqual(Data.__dict__, test_acq._Data.__dict__)

TestMDSPlusDataAcquisition.h1 = True
TestMDSPlusDataAcquisition.net = True
TestMDSPlusDataAcquisition.slow = True

class TestMDSPlusDataFetchers(BasePyfusionTestCase):

    def testDataFetcherBaseClass(self):
        from pyfusion.acquisition.base import BaseDataFetcher
        from pyfusion.acquisition.MDSPlus.fetch import MDSPlusBaseDataFetcher, MDSPlusDataFetcher, MDSPlusTimeseriesDataFetcher
        self.assertTrue(BaseDataFetcher in MDSPlusBaseDataFetcher.__bases__)
        self.assertTrue(MDSPlusBaseDataFetcher in MDSPlusDataFetcher.__bases__)
        self.assertTrue(MDSPlusBaseDataFetcher in MDSPlusTimeseriesDataFetcher.__bases__)

        

class TestMDSPlusH1Connection(BasePyfusionTestCase):
    """tests which require access to h1data.anu.edu.au"""

    def testH1TimeseriesData(self):
        from pyfusion.acquisition.MDSPlus.acq import MDSPlusAcquisition
        h1mds = MDSPlusAcquisition(server="h1data.anu.edu.au")
        df_str = "pyfusion.acquisition.MDSPlus.fetch.MDSPlusTimeseriesDataFetcher"
        test_data = h1mds.getdata(58133,
                                  data_fetcher = df_str,
                                  tree = "H1DATA",
                                  mds_path=".operations.mirnov:a14_14:input_1")
        self.assertEqual(test_data.signal[0], -0.01953125)
        
TestMDSPlusH1Connection.h1 = True
TestMDSPlusH1Connection.net = True
TestMDSPlusH1Connection.slow = True
