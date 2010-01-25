"""Tests for data code."""
from numpy.testing import assert_array_almost_equal, assert_almost_equal

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

class TestSegmentFilter(BasePyfusionTestCase):
    
    def test_single_channel_timeseries(self):
        from pyfusion.data.base import DataSet
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd = TimeseriesData(timebase=tb, signal=Signal(arange(len(tb))))
        seg_dataset = tsd.segment(n_samples=10)
        self.assertTrue(len(seg_dataset)==10)

    def test_multi_channel_timeseries(self):
        from pyfusion.data.base import DataSet
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd = TimeseriesData(timebase=tb, signal=Signal(resize(arange(3*len(tb)), (3,len(tb)))))
        seg_dataset = tsd.segment(n_samples=10)
        self.assertTrue(len(seg_dataset)==10)

    def test_dataset(self):
        from pyfusion.data.base import DataSet
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd_1 = TimeseriesData(timebase=tb, signal=Signal(resize(arange(3*len(tb)), (3,len(tb)))))
        tsd_2 = TimeseriesData(timebase=tb, signal=Signal(resize(arange(3*len(tb)+1), (3,len(tb)))))
        input_dataset = DataSet()
        input_dataset.add(tsd_1)
        input_dataset.add(tsd_2)
        seg_dataset = input_dataset.segment(n_samples=10)
        self.assertTrue(len(seg_dataset)==20)

from pyfusion.data.base import BaseCoordTransform
class DummyCoordTransform(BaseCoordTransform):
    input_coords = 'cylindrical'
    output_coords = 'dummy'

    def transform(self, coords):
        return (2*coords[0], 3*coords[1], 4*coords[2])

class TestCoordinates(BasePyfusionTestCase):

    def test_load_coords(self):
        from pyfusion.data.base import Coords
        dummy_coords = Coords(cylindrical=(1.0,1.0,1.0))
        self.assertEqual(dummy_coords.cylindrical, (1.0,1.0,1.0))
        # testing adding of coords
        dummy_coords.add_coords(cartesian=(0.1,0.5,0.2))
        self.assertEqual(dummy_coords.cartesian, (0.1,0.5,0.2))

    def test_coord_transform(self):
        from pyfusion.data.base import Coords
        cyl_coords = (1.0,1.0,1.0)
        dummy_coords = Coords(cylindrical=cyl_coords)
        dummy_coords.load_transform(DummyCoordTransform)
        self.assertEqual(dummy_coords.dummy(), (2*cyl_coords[0], 3*cyl_coords[1], 4*cyl_coords[2]))
        cyl_coords = (2.0,1.0,4.0)
        dummy_coords_1 = Coords(cylindrical=cyl_coords)
        dummy_coords_1.load_transform(DummyCoordTransform)
        self.assertEqual(dummy_coords_1.dummy(), (2*cyl_coords[0], 3*cyl_coords[1], 4*cyl_coords[2]))

class TestFlucstrucs(BasePyfusionTestCase):

    def test_fakedata_single_shot(self):
        import pyfusion
        #d=pyfusion.getDevice('H1')
        #data = d.acq.getdata(58073, 'H1_mirnov_array_1')
        #fs_data = data.reduce_time([0.030,0.031])
        

class TestNormalise(BasePyfusionTestCase):

    def test_single_channel_fakedata(self):
        from pyfusion.acquisition.FakeData.acq import FakeDataAcquisition
        from numpy import sqrt, mean, max, var
        test_acq = FakeDataAcquisition('test_fakedata')
        channel_data = test_acq.getdata(self.shot_number, "test_timeseries_channel_2")
        channel_data_norm_no_arg = test_acq.getdata(self.shot_number, "test_timeseries_channel_2").normalise()
        channel_data_rms_norm_by_arg = test_acq.getdata(self.shot_number, "test_timeseries_channel_2").normalise(method='rms')
        channel_data_peak_norm_by_arg = test_acq.getdata(self.shot_number, "test_timeseries_channel_2").normalise(method='peak')
        channel_data_var_norm_by_arg = test_acq.getdata(self.shot_number, "test_timeseries_channel_2").normalise(method='var')
        rms_value = sqrt(mean(channel_data.signal**2))
        peak_value = max(abs(channel_data.signal))
        var_value = var(channel_data.signal)


        assert_array_almost_equal(channel_data.signal/rms_value, channel_data_rms_norm_by_arg.signal)
        assert_array_almost_equal(channel_data.signal/peak_value, channel_data_peak_norm_by_arg.signal)
        assert_array_almost_equal(channel_data.signal/var_value, channel_data_var_norm_by_arg.signal)

        # check that default is peak
        assert_array_almost_equal(channel_data_peak_norm_by_arg.signal, channel_data_norm_no_arg.signal)

        
    def test_multichannel_fakedata(self):
        from pyfusion.acquisition.FakeData.acq import FakeDataAcquisition
        from numpy import sqrt, mean, max, var
        test_acq = FakeDataAcquisition('test_fakedata')
        multichannel_data = test_acq.getdata(self.shot_number, "test_multichannel_timeseries")

        mcd_ch_0 = multichannel_data.signal.get_channel(0)
        mcd_ch_0_peak = max(abs(mcd_ch_0))
        mcd_ch_0_rms = sqrt(mean(mcd_ch_0**2))
        mcd_ch_0_var = var(mcd_ch_0)
        
        mcd_ch_1 = multichannel_data.signal.get_channel(1)
        mcd_ch_1_peak = max(abs(mcd_ch_1))
        mcd_ch_1_rms = sqrt(mean(mcd_ch_1**2))
        mcd_ch_1_var = var(mcd_ch_1)
        
        mcd_peak_separate = test_acq.getdata(self.shot_number,
                                             "test_multichannel_timeseries").normalise(method='peak', separate=True)
        mcd_peak_whole = test_acq.getdata(self.shot_number,
                                          "test_multichannel_timeseries").normalise(method='peak', separate=False)
        mcd_rms_separate = test_acq.getdata(self.shot_number,
                                            "test_multichannel_timeseries").normalise(method='rms', separate=True)
        mcd_rms_whole = test_acq.getdata(self.shot_number,
                                         "test_multichannel_timeseries").normalise(method='rms', separate=False)
        mcd_var_separate = test_acq.getdata(self.shot_number,
                                            "test_multichannel_timeseries").normalise(method='var', separate=True)
        mcd_var_whole = test_acq.getdata(self.shot_number,
                                         "test_multichannel_timeseries").normalise(method='var', separate=False)
        
        # peak - separate
        assert_array_almost_equal(mcd_peak_separate.signal.get_channel(0), mcd_ch_0/mcd_ch_0_peak)
        assert_array_almost_equal(mcd_peak_separate.signal.get_channel(1), mcd_ch_1/mcd_ch_1_peak)
        # peak - whole
        max_peak = max(mcd_ch_0_peak, mcd_ch_1_peak)
        assert_array_almost_equal(mcd_peak_whole.signal.get_channel(0), mcd_ch_0/max_peak)
        assert_array_almost_equal(mcd_peak_whole.signal.get_channel(1), mcd_ch_1/max_peak)
        
        # rms - separate
        assert_array_almost_equal(mcd_rms_separate.signal.get_channel(0), mcd_ch_0/mcd_ch_0_rms)
        assert_array_almost_equal(mcd_rms_separate.signal.get_channel(1), mcd_ch_1/mcd_ch_1_rms)
        # rms - whole
        max_rms = max(mcd_ch_0_rms, mcd_ch_1_rms)
        assert_array_almost_equal(mcd_rms_whole.signal.get_channel(0), mcd_ch_0/max_rms)
        assert_array_almost_equal(mcd_rms_whole.signal.get_channel(1), mcd_ch_1/max_rms)

        # var - separate
        assert_array_almost_equal(mcd_var_separate.signal.get_channel(0), mcd_ch_0/mcd_ch_0_var)
        assert_array_almost_equal(mcd_var_separate.signal.get_channel(1), mcd_ch_1/mcd_ch_1_var)
        # var - whole
        max_var = max(mcd_ch_0_var, mcd_ch_1_var)
        assert_array_almost_equal(mcd_var_whole.signal.get_channel(0), mcd_ch_0/max_var)
        assert_array_almost_equal(mcd_var_whole.signal.get_channel(1), mcd_ch_1/max_var)


from pyfusion.data.timeseries import Timebase, Signal
from numpy import arange, pi, zeros, resize, random, cos

# modes: [amplitude, freq, phase at angle0]
def get_multimode_test_data(n_channels = 10,
                            ch_angles = 2*pi*arange(10)/10,
                            timebase = Timebase(arange(0.0,0.01,1.e-5)),
                            modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                            noise = 0.2):
    data_array = zeros((n_channels, len(timebase)))
    timebase_matrix = resize(timebase, (n_channels, len(timebase)))
    angle_matrix = resize(ch_angles, (len(timebase), n_channels)).T
    for m in modes:
        data_array += m[0]*cos(2*pi*m[2]*timebase_matrix + m[1]*angle_matrix + m[3])
    data_array += noise*2*(random.random(data_array.shape)-0.5)
    output = TimeseriesData(timebase=timebase, signal=Signal(data_array))
    return output

class TestFlucstrucs(BasePyfusionTestCase):

    def test_svd(self):
        multichannel_data = get_multimode_test_data(n_channels = 10,
                                                    ch_angles = 2*pi*arange(10)/10,
                                                    timebase = Timebase(arange(0.0,0.01,1.e-5)),
                                                    modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                    noise = 0.2)
        self.assertTrue(isinstance(multichannel_data, TimeseriesData))
        svd_data = multichannel_data.svd()
        
        #import pylab as pl
        #multichannel_data.plot_signals()
        
TestFlucstrucs.tmp = True

class TestSubtractMeanFilter(BasePyfusionTestCase):
    """Test mean subtraction filter for timeseries data."""


    def test_remove_mean_single_channel(self):
        from pyfusion.data.filters import reduce_time
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted,mean

        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        # nonzero signal mean
        tsd = TimeseriesData(timebase=tb, signal=Signal(arange(len(tb))))

        filtered_tsd = tsd.subtract_mean()

        assert_almost_equal(mean(filtered_tsd.signal), 0)
        
    
    def test_remove_mean_multichanel(self):
        from numpy import mean, zeros_like
        multichannel_data = get_multimode_test_data(n_channels = 10,
                                                    ch_angles = 2*pi*arange(10)/10,
                                                    timebase = Timebase(arange(0.0,0.01,1.e-5)),
                                                    modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                    noise = 0.2)
        # add some non-zero offset
        multichannel_data.signal += random.rand(*multichannel_data.signal.shape)

        filtered_data = multichannel_data.subtract_mean()
        mean_filtered_data = mean(filtered_data.signal, axis=1)
        assert_array_almost_equal(mean_filtered_data, zeros_like(mean_filtered_data))

class TestFilterMetaClass(BasePyfusionTestCase):

    def test_new_filter(self):
        from pyfusion.data import filters
        from pyfusion.data.base import BaseData
        # add some filters
        @filters.register("TestData")
        class MyTestFilter:
            def test_filter(self):
                return self

        @filters.register("TestData", "TestData2")
        class MyOtherTestFilter:
            def other_test_filter(self):
                return self

        # now create TestData 

        class TestData(BaseData):
            pass
        
        test_data = TestData()
        for attr_name in ["test_filter", "other_test_filter"]:
            self.assertTrue(hasattr(test_data, attr_name))
TestFilterMetaClass.dev = True

