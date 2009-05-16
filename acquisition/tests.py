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

    def testGetDataReturnObject(self):
        from pyfusion.acquisition.fakedata import FakeDataAcquisition
        from pyfusion import conf
        # make sure the requested data type is returned
        test_acq = FakeDataAcquisition('test_fakedata')
        data_class = conf.utils.import_setting('Diagnostic',
                                               SCT_test_channel_name,
                                               'data_class')
        data_instance = test_acq.getdata(self.shot_number, SCT_test_channel_name)
        self.assertTrue(isinstance(data_instance, data_class))

        
    def testDeviceConnection(self):
        from pyfusion import Device
        test_device = Device('TestDevice')
        from pyfusion import conf
        acq_name = conf.config.pf_get('Device', 'TestDevice', 'acquisition')
        test_acq = conf.utils.import_setting('Acquisition', acq_name, 'acq_class')
        # TMPCOMMENT self.assertTrue(isinstance(test_device.acquisition, test_acq))
        #test_data = test_device.acquisition.getdata(SCT_test_channel_name)
        
