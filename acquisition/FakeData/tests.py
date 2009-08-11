"""Test code for data acquisition."""

from pyfusion.test.tests import BasePyfusionTestCase

# channel names in pyfusion test config file
SCT_test_channel_name = "test_SCT_channel"


class TestFakeDataAcquisition(BasePyfusionTestCase):
    """Test the fake data acquisition used for testing."""

    def testBaseClasses(self):
        """Make sure FakeDataAcquisition is subclass of Acquisition."""
        from pyfusion.acquisition.FakeData.acq import FakeDataAcquisition
        from pyfusion.acquisition.base import BaseAcquisition
        self.assertTrue(BaseAcquisition in FakeDataAcquisition.__bases__)

    def testGetDataReturnObject(self):
        from pyfusion.acquisition.FakeData.acq import FakeDataAcquisition
        from pyfusion import conf
        # make sure the requested data type is returned
        test_acq = FakeDataAcquisition('test_fakedata')
        from pyfusion.data.timeseries import SCTData
        data_instance = test_acq.getdata(self.shot_number, SCT_test_channel_name)
        self.assertTrue(isinstance(data_instance, SCTData))
        
    def testDeviceConnection(self):
        from pyfusion.devices.base import Device
        test_device = Device('TestDevice')
        from pyfusion import conf, config
        acq_name = config.pf_get('Device', 'TestDevice', 'acq_name')
        test_acq = conf.utils.import_setting('Acquisition', acq_name, 'acq_class')
        self.assertTrue(isinstance(test_device.acquisition, test_acq))
        # test that device.acq shortcut works
        self.assertEqual(test_device.acquisition, test_device.acq)
        

    def test_get_data(self):
        from pyfusion import getDevice
        test_device = getDevice(self.listed_device)
        test_data = test_device.acquisition.getdata(self.shot_number, SCT_test_channel_name)
        from pyfusion.data.timeseries import SCTData
        self.assertTrue(isinstance(test_data, SCTData))


class TestFakeDataFetchers(BasePyfusionTestCase):
    """test DataFetcher subclasses for fake data acquisition."""

    def test_base_classes(self):
        from pyfusion.acquisition.base import BaseDataFetcher
        from pyfusion.acquisition.base import DataFetcher
        self.assertTrue(BaseDataFetcher in DataFetcher.__bases__)
        from pyfusion.acquisition.FakeData.fetch import SingleChannelSineDF
        self.assertTrue(BaseDataFetcher in SingleChannelSineDF.__bases__)

    def test_singlechannelsinedf(self):
        from pyfusion.acquisition.FakeData.fetch import SingleChannelSineDF
        n_samples = 1000
        sample_freq=1.e6
        amplitude = 1.0
        frequency = 3.e4
        t0 = 0.0
        output_data_fetcher = SingleChannelSineDF(sample_freq=sample_freq,
                                                  n_samples=n_samples,
                                                  amplitude=amplitude,
                                                  frequency=frequency,
                                                  t0 = t0)
        output_data = output_data_fetcher.fetch()
        from pyfusion.data.timeseries import SCTData
        self.assertTrue(isinstance(output_data, SCTData))
        from numpy import arange, sin, pi
        test_timebase = arange(t0, t0+float(n_samples)/sample_freq, 1./sample_freq)
        self.assertTrue((output_data.timebase.timebase == test_timebase).all())
        test_signal = amplitude*sin(2*pi*frequency*test_timebase)
        self.assertTrue((output_data.signal.signal == test_signal).all())
