"""Tests for data code."""

from pyfusion.test.tests import BasePyfusionTestCase
from pyfusion.data.base import BaseData

class TestTimeseriesData(BasePyfusionTestCase):
    """Test timeseries data"""
    def testBaseClasses(self):
        from pyfusion.data.timeseries import TimeseriesData
        self.assertTrue(BaseData in TimeseriesData.__bases__)

    def testTimebase(self):
        from pyfusion.data.timeseries import TimeseriesData, Timebase
        self.assertTrue(hasattr(TimeseriesData(), 'timebase'))
    """
    def testAddChannels(self):
        from pyfusion.data.timeseries import TimeseriesData, Timebase
        t0=0.3
        n_samples=500
        sample_freq=1.e6
        tb = Timebase(t0=t0,n_samples=n_samples, sample_freq=sample_freq)
        ts = TimeseriesData(timebase=tb)
        self.assertEqual(ts.n_channels(), 0)
    """ 

class TestTimebase(BasePyfusionTestCase):
    """Test Timebase class."""

    """
    def test_timebase(self):
        from pyfusion.data.timeseries import Timebase
        from numpy import arange
        t0=0.3
        n_samples=500
        sample_freq=1.e6
        test_tb = Timebase(t0=t0,n_samples=n_samples, sample_freq=sample_freq)
        local_tb = arange(t0, t0+n_samples/sample_freq, 1./sample_freq)
        self.assertTrue((test_tb.timebase == local_tb).all())
    """

    
class TestSignal(BasePyfusionTestCase):
    """Test Signal class."""

    def test_base_class(self):
        from pyfusion.data.timeseries import Signal
        from numpy import ndarray
        self.assertTrue(ndarray in Signal.__bases__)

