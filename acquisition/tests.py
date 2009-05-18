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
        from pyfusion.core.devices import Device
        test_device = Device('TestDevice')
        from pyfusion import conf
        acq_name = conf.config.pf_get('Device', 'TestDevice', 'acq_name')
        test_acq = conf.utils.import_setting('Acquisition', acq_name, 'acq_class')
        self.assertTrue(isinstance(test_device.acquisition, test_acq))

    def test_get_data(self):
        from pyfusion import getDevice
        test_device = getDevice(self.listed_device)
        test_data = test_device.acquisition.getdata(self.shot_number, SCT_test_channel_name)
        from pyfusion.data.timeseries import SCTData
        self.assertTrue(isinstance(test_data, SCTData))

class TestGetAcquisition(BasePyfusionTestCase):
    """test getAcquisition function."""

    def test_get_acquistion(self):
        from pyfusion.acquisition.utils import getAcquisition
        test_acq_1 = getAcquisition('test_fakedata')
        from pyfusion.acquisition.fakedata import FakeDataAcquisition
        test_acq_2 = FakeDataAcquisition('test_fakedata')
        self.assertEqual(test_acq_1.__class__, test_acq_2.__class__)

class TestFakeDataFetchers(BasePyfusionTestCase):
    """test DataFetcher subclasses for fake data acquisition."""

    def test_base_classes(self):
        from pyfusion.acquisition.base import BaseDataFetcher
        from pyfusion.acquisition.base import DataFetcher
        self.assertTrue(BaseDataFetcher in DataFetcher.__bases__)
        from pyfusion.acquisition.fakedata import SingleChannelSineDF
        self.assertTrue(BaseDataFetcher in SingleChannelSineDF.__bases__)

    def test_singlechannelsinedf(self):
        from pyfusion.acquisition.fakedata import SingleChannelSineDF
        output_data_fetcher = SingleChannelSineDF(sample_rate=1.e6, n_samples=1000,
                                                  amplitude=1.0, frequency=3.e4)
        output_data = output_data_fetcher.fetch()
        from pyfusion.data.timeseries import SCTData
        self.assertTrue(isinstance(output_data, SCTData))
        #from numpy import arange
        #self.assertEqual(output_data.timebase, arange())
