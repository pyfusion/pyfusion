"""Tests for data code."""

from pyfusion.test.tests import BasePyfusionTestCase
from pyfusion.data.base import BaseData, DataSet
from pyfusion.data.timeseries import TimeseriesData

class TestTimeseriesData(BasePyfusionTestCase):
    """Test timeseries data"""
    def testBaseClasses(self):
        from pyfusion.data.timeseries import TimeseriesData
        self.assertTrue(BaseData in TimeseriesData.__bases__)

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


    def test_timebase(self):
        from pyfusion.data.timeseries import generate_timebase
        from numpy import arange
        t0=0.3
        n_samples=500
        sample_freq=1.e6
        test_tb = generate_timebase(t0=t0,n_samples=n_samples, sample_freq=sample_freq)
        local_tb = arange(t0, t0+n_samples/sample_freq, 1./sample_freq)
        self.assertTrue((test_tb == local_tb).all())


## dummy filters for testing filter method loading
def dummy_filter_1(input_data, *args, **kwargs):
    return input_data
dummy_filter_1.allowed_class=[TimeseriesData]


def dummy_filter_2(input_data, *args, **kwargs):
    return input_data
dummy_filter_2.allowed_class=[TimeseriesData, DataSet]

def dummy_filter_3(input_data, *args, **kwargs):
    return input_data
dummy_filter_3.allowed_class=[BaseData]


class TestSignal(BasePyfusionTestCase):
    """Test Signal class."""
    
    def test_base_class(self):
        from pyfusion.data.timeseries import Signal
        from numpy import ndarray
        self.assertTrue(ndarray in Signal.__bases__)

    def test_n_channels(self):
        from pyfusion.data.timeseries import Signal
        import numpy as np
        test_sig_1a = Signal(np.random.rand(10))
        self.assertEqual(test_sig_1a.n_channels(), 1)
        test_sig_1b = Signal(np.random.rand(1,10))
        self.assertEqual(test_sig_1b.n_channels(), 1)
        test_sig_2 = Signal(np.random.rand(2,10))
        self.assertEqual(test_sig_2.n_channels(), 2)
        
    def test_n_samples(self):
        from pyfusion.data.timeseries import Signal
        import numpy as np
        test_sig_1a = Signal(np.random.rand(10))
        self.assertEqual(test_sig_1a.n_samples(), 10)
        test_sig_1b = Signal(np.random.rand(1,10))
        self.assertEqual(test_sig_1b.n_samples(), 10)
        test_sig_2 = Signal(np.random.rand(2,10))
        self.assertEqual(test_sig_2.n_samples(), 10)

class TestFilters(BasePyfusionTestCase):

    def test_reduce_time_filter_single_channel(self):
        from pyfusion.data.filters import reduce_time
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted
        new_times = [-0.25, 0.25]
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd = TimeseriesData(timebase=tb, signal=Signal(arange(len(tb))))
        new_time_args = searchsorted(tb, new_times)
        timebase_test = tsd.timebase[new_time_args[0]:new_time_args[1]].copy()
        signal_test = tsd.signal[new_time_args[0]:new_time_args[1]].copy()
        reduced_tsd = reduce_time(tsd, new_times)
        self.assertTrue(isinstance(reduced_tsd, TimeseriesData))
        from numpy.testing import assert_array_almost_equal
        assert_array_almost_equal(reduced_tsd.timebase, timebase_test)
        assert_array_almost_equal(reduced_tsd.signal, signal_test)
        
    def test_reduce_time_filter_multi_channel(self):
        from pyfusion.data.filters import reduce_time
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        new_times = [-0.25, 0.25]
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd = TimeseriesData(timebase=tb, signal=Signal(resize(arange(5*len(tb)), (5,len(tb)))))
        new_time_args = searchsorted(tb, new_times)
        timebase_test = tsd.timebase[new_time_args[0]:new_time_args[1]].copy()
        signal_test = tsd.signal[:,new_time_args[0]:new_time_args[1]].copy()
        reduced_tsd = reduce_time(tsd, new_times)
        self.assertTrue(isinstance(reduced_tsd, TimeseriesData))
        from numpy.testing import assert_array_almost_equal
        assert_array_almost_equal(reduced_tsd.timebase, timebase_test)
        assert_array_almost_equal(reduced_tsd.signal, signal_test)
    
    def test_reduce_time_filter_multi_channel_attached_method(self):
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        from pyfusion.data import filter_register
        new_times = [-0.25, 0.25]
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd = TimeseriesData(timebase=tb, signal=Signal(resize(arange(5*len(tb)), (5,len(tb)))))
        new_time_args = searchsorted(tb, new_times)
        timebase_test = tsd.timebase[new_time_args[0]:new_time_args[1]].copy()
        signal_test = tsd.signal[:,new_time_args[0]:new_time_args[1]].copy()
        reduced_tsd = tsd.reduce_time(new_times)
        self.assertTrue(isinstance(reduced_tsd, TimeseriesData))
        from numpy.testing import assert_array_almost_equal
        assert_array_almost_equal(reduced_tsd.timebase, timebase_test)
        assert_array_almost_equal(reduced_tsd.signal, signal_test)
    

    def test_filter_method_loader(self):
        import pyfusion
        pyfusion.data.filter_register.add_module('pyfusion.data.tests')
        self.assertTrue(dummy_filter_1 in pyfusion.data.filter_register.get_for(TimeseriesData))
        from pyfusion.data.filters import reduce_time
        self.assertTrue(reduce_time in pyfusion.data.filter_register.get_for(TimeseriesData))

    def test_reduce_time_dataset(self):
        from pyfusion.data.base import DataSet
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        new_times = [-0.25, 0.25]
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd_1 = TimeseriesData(timebase=tb, signal=Signal(resize(arange(5*len(tb)), (5,len(tb)))))
        tsd_2 = TimeseriesData(timebase=tb, signal=Signal(resize(arange(5*len(tb))+1, (5,len(tb)))))
        test_dataset = DataSet()
        test_dataset.add(tsd_1)
        test_dataset.add(tsd_2)
        test_dataset.reduce_time(new_times)
        
    def test_subclass(self):
        import pyfusion
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        pyfusion.data.filter_register.add_module('pyfusion.data.tests')
        new_times = [-0.25, 0.25]
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd = TimeseriesData(timebase=tb, signal=Signal(resize(arange(5*len(tb)), (5,len(tb)))))
        self.assertTrue(hasattr(tsd, 'dummy_filter_3'))

class TestDataSet(BasePyfusionTestCase):

    def test_dataset(self):
        from pyfusion.data.base import DataSet
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        new_times = [-0.25, 0.25]
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd_1 = TimeseriesData(timebase=tb, signal=Signal(resize(arange(5*len(tb)), (5,len(tb)))))
        tsd_2 = TimeseriesData(timebase=tb, signal=Signal(resize(arange(5*len(tb))+1, (5,len(tb)))))
        test_dataset = DataSet()
        test_dataset.add(tsd_1)
        test_dataset.add(tsd_2)
        self.assertTrue(tsd_1 in test_dataset)
        test_dataset.remove(tsd_1)
        self.assertFalse(tsd_1 in test_dataset)
        self.assertTrue(tsd_2 in test_dataset)
        
    def test_dataset_filters(self):
        from pyfusion.data.base import DataSet
        import pyfusion
        pyfusion.data.filter_register.add_module('pyfusion.data.tests')
        test_dataset = DataSet()
        self.assertFalse(hasattr(test_dataset, 'dummy_filter_1'))
        self.assertTrue(hasattr(test_dataset, 'dummy_filter_2'))
        #x = test_dataset.reduce_time([0,1])

    def test_dataset_filters_2(self):
        from pyfusion.data.base import DataSet
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        new_times = [-0.25, 0.25]
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd_1 = TimeseriesData(timebase=tb, signal=Signal(resize(arange(5*len(tb)), (5,len(tb)))))
        tsd_2 = TimeseriesData(timebase=tb, signal=Signal(resize(arange(5*len(tb))+1, (5,len(tb)))))
        test_dataset = DataSet()
        test_dataset.add(tsd_1)
        test_dataset.add(tsd_2)
        test_dataset.reduce_time(new_times)
        test_dataset.add(3)
"""        
class TestSegmentFilter(BasePyfusionTestCase):
    
    def test_single_channel_timeseries(self):
        from pyfusion.data.base import DataSet
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd_1 = TimeseriesData(timebase=tb, signal=Signal(resize(arange(len(tb)), (5,20))))
        
"""
