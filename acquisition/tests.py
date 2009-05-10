"""Test code for data acquisition."""

from pyfusion.test.tests import BasePyfusionTestCase

class TestBaseAcquisition(BasePyfusionTestCase):
    pass

class TestFakeDataAcquisition(BasePyfusionTestCase):
    """Test the fake data acquisition used for testing."""

    def testBaseClasses(self):
        from pyfusion.acquisition.fakedata import FakeDataAcquisition
        from pyfusion.acquisition.base import BaseAcquisition
        self.assertTrue(BaseAcquisition in FakeDataAcquisition.__bases__)

    def testSCTAcquisition(self):
        """Test acquisition for single channel timeseries (SCT)."""
        from pyfusion.acquisition.fakedata import FakeDataAcquisition
        from pyfusion.data.timeseries import SCTData
        test_fakedata_acq = FakeDataAcquisition(self.listed_device,
                                                self.shot_number,
                                                self.listed_device_single_channel_timeseries,
                                                SCTData)
        test_data = test_fakedata_acq.getdata()
        self.assertEqual(test_data.__class__, SCTData)
        self.assertEqual(len(test_data.timebase), len(test_data.signal))
        self.assertEqual(self.listed_device, test_data.device_name)
        self.assertEqual(self.shot_number, test_data.shot_number)
        
    def testMCTAcquisition(self):
        """Test acquisition for multiple channel timeseries (MCT)."""
        from pyfusion.acquisition.fakedata import FakeDataAcquisition
        from pyfusion.data.timeseries import MCTData
        test_fakedata_acq = FakeDataAcquisition(self.listed_device,
                                                self.shot_number,
                                                self.listed_device_multiple_channel_timeseries,
                                                MCTData)
        test_data = test_fakedata_acq.getdata()
        self.assertEqual(test_data.__class__, MCTData)

        
