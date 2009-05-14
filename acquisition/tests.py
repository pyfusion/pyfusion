"""Test code for data acquisition."""

from pyfusion.test.tests import BasePyfusionTestCase

# channel names in pyfusion test config file
SCT_test_channel_name = "test_SCT_channel"



class TestFakeDataAcquisition(BasePyfusionTestCase):
    """Test the fake data acquisition used for testing."""

    def testBaseClasses(self):
        """Make sure FakeDataAcquisition is subclass of Acquisition."""
        from pyfusion.acquisition.fakedata import FakeDataAcquisition
        from pyfusion.acquisition.base import BaseAcquisition
        self.assertTrue(BaseAcquisition in FakeDataAcquisition.__bases__)

    def testSCT(self):
        from pyfusion.acquisition.fakedata import FakeDataAcquisition
        from pyfusion import conf
        # make sure the requested data type is returned
        test_acq = FakeDataAcquisition('test_fakedata')
        data_class = conf.utils.import_setting('Diagnostic',
                                               SCT_test_channel_name,
                                               'data_class')
        data_instance = test_acq.getdata(self.shot_number, SCT_test_channel_name)
    """
    def testSCTAcquisitionDEPRECIATED(self):
        from pyfusion.acquisition.fakedata import FakeDataAcquisition
        from pyfusion.data.timeseries import SCTData
        test_fakedata_acq = FakeDataAcquisition(
            self.listed_device,
            self.shot_number,
            self.listed_device_single_channel_timeseries,
            SCTData)
        test_data = test_fakedata_acq.getdata()
        self.assertEqual(test_data.__class__, SCTData)
        self.assertEqual(len(test_data.timebase), len(test_data.signal))
        self.assertEqual(self.listed_device, test_data.device_name)
        self.assertEqual(self.shot_number, test_data.shot_number)
        
    def testMCTAcquisitionDEPRECIATED(self):
        from pyfusion.acquisition.fakedata import FakeDataAcquisition
        from pyfusion.data.timeseries import MCTData
        test_fakedata_acq = FakeDataAcquisition(
            self.listed_device,
            self.shot_number,
            self.listed_device_multiple_channel_timeseries,
            MCTData)
        test_data = test_fakedata_acq.getdata()
        self.assertEqual(test_data.__class__, MCTData)
    """
        
