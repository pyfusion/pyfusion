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

    def testAcquisition(self):
        from pyfusion.acquisition.fakedata import FakeDataAcquisition
        from pyfusion.data.base import BaseData
        test_fakedata_acq = FakeDataAcquisition(self.listed_device, self.shot_number, self.listed_config_channel)
        test_data = test_fakedata_acq.getdata()
        
