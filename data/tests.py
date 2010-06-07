"""Tests for data code."""
from numpy.testing import assert_array_almost_equal, assert_almost_equal
from numpy import arange, pi, zeros, resize, random, cos, array

from pyfusion.test.tests import BasePyfusionTestCase
from pyfusion.data.base import BaseData, DataSet, Coords
from pyfusion.data.timeseries import TimeseriesData, Timebase, Signal
from pyfusion.data.utils import cps


# modes: [amplitude, freq, phase at angle0]
def get_multimode_test_data(n_channels = 10,
                            ch_coords = tuple(Coords(cylindrical=(1.0,i,0.0)) for i in 2*pi*arange(10)/10),
                            timebase = Timebase(arange(0.0,0.01,1.e-5)),
                            modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                            noise = 0.2):

    data_array = zeros((n_channels, len(timebase)))
    timebase_matrix = resize(timebase, (n_channels, len(timebase)))
    angle_matrix = resize(array([i.cylindrical[1] for i in ch_coords]), (len(timebase), n_channels)).T
    for m in modes:
        data_array += m[0]*cos(2*pi*m[2]*timebase_matrix + m[1]*angle_matrix + m[3])
    data_array += noise*2*(random.random(data_array.shape)-0.5)
    output = TimeseriesData(timebase=timebase,
                            signal=Signal(data_array), coords=ch_coords)
    return output


class TestUtils(BasePyfusionTestCase):
    def test_remap_periodic(self):
        from numpy import pi, array
        from utils import remap_periodic
        data = array([-3,-2,-1,0,1,2,2.5, 3])
        output = remap_periodic(data, min_val = 0, period=3)
        expected = array([0, 1, 2, 0, 1, 2, 2.5, 0])
        assert_array_almost_equal(output, expected)

    def test_peak_freq(self):
        from utils import peak_freq
        test_freq = 27.e3
        single_mode_signal = get_multimode_test_data(n_channels=1,
                                                     ch_coords=[Coords(cylindrical=(0.0,0.0,0.0))],
                                                     timebase=Timebase(arange(0.0,0.01, 1.e-6)),
                                                     modes = [[0.5, 2, test_freq, 0.1]],
                                                     noise=0.1
                                                     )
        p_f = peak_freq(single_mode_signal.signal[0], single_mode_signal.timebase)
        # check that we get 27.0 kHz (1 decimal place accuracy)
        self.assertAlmostEqual(1.e-3*p_f, 1.e-3*test_freq, 1)

    

class TestTimeseriesData(BasePyfusionTestCase):
    """Test timeseries data"""
    def testBaseClasses(self):
        from pyfusion.data.timeseries import TimeseriesData
        self.assertTrue(BaseData in TimeseriesData.__bases__)


    def test_timebase_and_coords(self):
        n_ch = 10
        n_samples = 1024
        timebase = Timebase(arange(n_samples)*1.e-6)
        ch_coords = tuple(Coords(cylindrical=(1.0,i,0.0)) for i in 2*pi*arange(n_ch)/n_ch)
        multichannel_data = get_multimode_test_data(n_channels = n_ch,
                                                    ch_coords = ch_coords,
                                                    timebase = timebase,
                                                    modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                    noise = 0.5)


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
        self.assertAlmostEqual(test_tb.sample_freq, sample_freq, 4)


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
        tsd = TimeseriesData(timebase=tb,
                             signal=Signal(arange(len(tb))), coords=[Coords()])
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
        tsd = TimeseriesData(timebase=tb,
                             signal=Signal(resize(arange(5*len(tb)),(5,len(tb)))),
                             coords=(Coords(),Coords(),Coords(),Coords(),Coords()))
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
        new_times = [-0.25, 0.25]
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd = TimeseriesData(timebase=tb,
                             signal=Signal(resize(arange(5*len(tb)),(5,len(tb)))),
                             coords=(Coords(), Coords(),Coords(),Coords(),Coords()))
        new_time_args = searchsorted(tb, new_times)
        timebase_test = tsd.timebase[new_time_args[0]:new_time_args[1]].copy()
        signal_test = tsd.signal[:,new_time_args[0]:new_time_args[1]].copy()
        reduced_tsd = tsd.reduce_time(new_times)
        self.assertTrue(isinstance(reduced_tsd, TimeseriesData))
        assert_array_almost_equal(reduced_tsd.timebase, timebase_test)
        assert_array_almost_equal(reduced_tsd.signal, signal_test)
    

    def test_reduce_time_dataset(self):
        from pyfusion.data.base import DataSet
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        new_times = [-0.25, 0.25]
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd_1 = TimeseriesData(timebase=tb,
                               signal=Signal(resize(arange(5*len(tb)),(5,len(tb)))),
                               coords=(Coords(),Coords(),Coords(),Coords(),Coords()))
        tsd_2 = TimeseriesData(timebase=tb, signal=Signal(resize(arange(5*len(tb))+1,(5,len(tb)))),
                               coords=(Coords(),Coords(),Coords(),Coords(),Coords()))
        test_dataset = DataSet()
        test_dataset.add(tsd_1)
        test_dataset.add(tsd_2)
        test_dataset.reduce_time(new_times)
        
class TestDataSet(BasePyfusionTestCase):

    def test_dataset(self):
        from pyfusion.data.base import DataSet
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        new_times = [-0.25, 0.25]
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd_1 = TimeseriesData(timebase=tb, signal=Signal(resize(arange(5*len(tb)),(5,len(tb)))),
                               coords=(Coords(),Coords(),Coords(),Coords(),Coords()))
        tsd_2 = TimeseriesData(timebase=tb,
                               signal=Signal(resize(arange(5*len(tb))+1, (5,len(tb)))),
                               coords=(Coords(),Coords(),Coords(),Coords(),Coords()))
        test_dataset = DataSet()
        test_dataset.add(tsd_1)
        test_dataset.add(tsd_2)
        self.assertTrue(tsd_1 in test_dataset)
        test_dataset.remove(tsd_1)
        self.assertFalse(tsd_1 in test_dataset)
        self.assertTrue(tsd_2 in test_dataset)
        

    def test_dataset_filters_2(self):
        from pyfusion.data.base import DataSet
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        new_times = [-0.25, 0.25]
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd_1 = TimeseriesData(timebase=tb, signal=Signal(resize(arange(5*len(tb)),(5,len(tb)))),
                               coords=(Coords(),Coords(),Coords(),Coords(),Coords()))
        tsd_2 = TimeseriesData(timebase=tb,
                               signal=Signal(resize(arange(5*len(tb))+1,(5,len(tb)))),
                               coords=(Coords(),Coords(),Coords(),Coords(),Coords()))
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
        tsd = TimeseriesData(timebase=tb,
                             signal=Signal(arange(len(tb))), coords=[Coords()])
        seg_dataset = tsd.segment(n_samples=10)
        self.assertTrue(len(seg_dataset)==10)

    def test_multi_channel_timeseries(self):
        from pyfusion.data.base import DataSet
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd = TimeseriesData(timebase=tb,
                             signal=Signal(resize(arange(3*len(tb)), (3,len(tb)))),
                             coords=(Coords(), Coords(), Coords()))
        seg_dataset = tsd.segment(n_samples=10)
        self.assertTrue(len(seg_dataset)==10)

    def test_dataset(self):
        from pyfusion.data.base import DataSet
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd_1 = TimeseriesData(timebase=tb,
                               signal=Signal(resize(arange(3*len(tb)), (3,len(tb)))),
                               coords=(Coords(), Coords(), Coords()))
        tsd_2 = TimeseriesData(timebase=tb,
                               signal=Signal(resize(arange(3*len(tb)+1),(3,len(tb)))),
                               coords=(Coords(), Coords(), Coords()))
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

"""
class TestFlucstrucs(BasePyfusionTestCase):

    def test_fakedata_single_shot(self):
        import pyfusion
        #d=pyfusion.getDevice('H1')
        #data = d.acq.getdata(58073, 'H1_mirnov_array_1')
        #fs_data = data.reduce_time([0.030,0.031])
"""     

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


        # try for dataset
        from pyfusion.data.base import DataSet
        channel_data_for_set = test_acq.getdata(self.shot_number, "test_timeseries_channel_2")

        test_dataset = DataSet()
        test_dataset.add(channel_data_for_set)
        test_dataset.normalise(method='rms')
        for d in test_dataset:
            assert_array_almost_equal(channel_data.signal/rms_value, d.signal)
            

        
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



class TestFlucstrucs(BasePyfusionTestCase):

    def test_svd_data(self):
        from pyfusion.data.timeseries import SVDData
        from pyfusion.data.base import Coords
        n_ch = 10
        n_samples = 1024
        timebase = Timebase(arange(n_samples)*1.e-6)
        ch_coords = tuple(Coords(cylindrical=(1.0,i,0.0)) for i in 2*pi*arange(n_ch)/n_ch)
        multichannel_data = get_multimode_test_data(n_channels = n_ch,
                                                    ch_coords = ch_coords,
                                                    timebase = timebase,
                                                    modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                    noise = 0.5)

        test_svd = multichannel_data.svd()
        self.assertTrue(isinstance(test_svd, SVDData))
        self.assertEqual(len(test_svd.topos[0]), n_ch)
        self.assertEqual(len(test_svd.chronos[0]), n_samples)
        assert_array_almost_equal(test_svd.dim1, timebase)
        print test_svd.dim2
        for c_i, coord in enumerate(ch_coords):
            self.assertEqual(coord, test_svd.dim2[c_i])

    def test_SVDData_class(self):
        from pyfusion.data.timeseries import SVDData
        from numpy import linalg, transpose, array
        n_ch = 5
        n_samples = 512
        fake_data = resize(arange(n_ch*n_samples), (n_ch, n_samples))
        numpy_svd = linalg.svd(fake_data, 0)
        test_svd  = SVDData(arange(n_samples), arange(n_ch), numpy_svd)
        assert_array_almost_equal(test_svd.topos, transpose(numpy_svd[0]))
        assert_array_almost_equal(test_svd.svs, numpy_svd[1])
        assert_array_almost_equal(test_svd.chronos, numpy_svd[2])

        E = sum(numpy_svd[1]*numpy_svd[1])
        self.assertEqual(test_svd.E, E)
        p = array([i**2 for i in test_svd.svs])/test_svd.E
        assert_array_almost_equal(test_svd.p, p)
        
        self_cps = test_svd.self_cps()
        assert_array_almost_equal(self_cps, array([(0.99999999999999989+0j),
                                                   (0.99999999999999922+0j),
                                                   (0.99999999999999767+0j),
                                                   (0.99999999999999867+0j),
                                                   (1.0000000000000002+0j)])
                                  )

    def test_fs_grouping(self):
        # this signal should be grouped as [0,1], [2,3] + noise 
        multichannel_data = get_multimode_test_data(n_channels = 10,
                                                    ch_coords = tuple(Coords(cylindrical=(1.0,i,0.0)) for i in 2*pi*arange(10)/10),
                                                    #timebase = Timebase(arange(0.0,0.01,1.e-6)),
                                                    timebase = Timebase(arange(1024)*1.e-6),
                                                    modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                    noise = 0.5)

        fs_groups = multichannel_data.fs_group()
        self.assertEqual(fs_groups[0], [0,1])
        self.assertEqual(fs_groups[1], [2,3])
        

    def test_fs_grouping_from_svd(self):
        n_ch = 10
        n_samples = 1024
        multichannel_data = get_multimode_test_data(n_channels = n_ch,
                                                    ch_coords = tuple(Coords(cylindrical=(1.0,i,0.0)) for i in 2*pi*arange(n_ch)/n_ch),
                                                    timebase = Timebase(arange(n_samples)*1.e-6),
                                                    modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                    noise = 0.5)

        test_svd = multichannel_data.svd()
        fs_groups = test_svd.fs_group()

    def test_flucstruc_signals(self):
        # make sure that flucstruc derived from all singular values
        # gives back the original signal
        from pyfusion.data.timeseries import SVDData, FlucStruc
        from pyfusion.data.base import DataSet
        from numpy import array
        n_ch = 10
        n_samples = 1024
        multichannel_data = get_multimode_test_data(n_channels = n_ch,
                                                    ch_coords = tuple(Coords(cylindrical=(1.0,i,0.0)) for i in 2*pi*arange(n_ch)/n_ch),
                                                    timebase = Timebase(arange(n_samples)*1.e-6),
                                                    modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                    noise = 0.01)
        svd_data = multichannel_data.svd()
        test_fs = FlucStruc(svd_data, range(len(svd_data.svs)), multichannel_data.timebase)

        assert_almost_equal(test_fs.signal, multichannel_data.signal)

    def test_flucstruc_phases(self):
        from pyfusion.data.timeseries import SVDData, FlucStruc
        from pyfusion.data.base import DataSet
        from numpy import array
        n_ch = 10
        n_samples = 1024
        multichannel_data = get_multimode_test_data(n_channels = n_ch,
                                                    ch_coords = tuple(Coords(cylindrical=(1.0,i,0.0)) for i in 2*pi*arange(n_ch)/n_ch),
                                                    timebase = Timebase(arange(n_samples)*1.e-6),
                                                    modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                    noise = 0.01)
        fs_data = multichannel_data.flucstruc(min_dphase = -2*pi)
        self.assertTrue(isinstance(fs_data, DataSet))
        self.assertTrue(len(fs_data) > 0)
        E = 0.7**2 + 0.5**2
        for fs in fs_data:
            self.assertTrue(isinstance(fs, FlucStruc))
            # fs_data is not ordered, so we identify flucstrucs by the sv indicies
            if fs.svs == [0,1]:
                # check that freq is correct to within 1kHz
                self.assertAlmostEqual(1.e-4*fs.freq, 1.e-4*24.e3, 1)
                # 
                fake_phases = -3.0*2*pi*arange(n_ch+1)[:-1]/(n_ch)
                fake_dphases = fake_phases[1:]-fake_phases[:-1]

                test_dphase = fs.dphase
                # check phases within 0.5 rad
                assert_array_almost_equal(test_dphase, fake_dphases, 1)
                # check fs energy is correct to 3 decimal places
                self.assertAlmostEqual(fs.p, 0.7**2/E, 3)
            if fs.svs == [2,3]:
                self.assertAlmostEqual(1.e-4*fs.freq, 1.e-4*37.e3, 1)
                fake_phases = -4.0*2*pi*arange(n_ch+1)[:-1]/(n_ch)
                fake_dphases = fake_phases[1:]-fake_phases[:-1]

                test_dphase = fs.dphase
                # check phases within 0.5 rad
                assert_array_almost_equal(test_dphase, fake_dphases, 1)
                # check fs energy is correct to 3 decimal places
                self.assertAlmostEqual(fs.p, 0.5**2/E, 3)


        #assert False
        #import pylab as pl
        #multichannel_data.plot_signals()

#     def test_svd(self):
#         multichannel_data = get_multimode_test_data(n_channels = 10,
#                                                     ch_coords = tuple(Coords(cylindrical=(1.0,i,0.0)) for i in 2*pi*arange(10)/10),
#                                                     timebase = Timebase(arange(0.0,0.01,1.e-5)),
#                                                     modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
#                                                     noise = 0.2)
#         self.assertTrue(isinstance(multichannel_data, TimeseriesData))
#         svd_data = multichannel_data.svd()
        
        #import pylab as pl
        #multichannel_data.plot_signals()
        

    def test_ORM_flucstrucs(self):
        """ check that flucstrucs can be saved to database"""
        import pyfusion
        if pyfusion.USE_ORM:
            n_ch = 10
            n_samples = 1024
            multichannel_data = get_multimode_test_data(n_channels = n_ch,
                                                        ch_coords = tuple(Coords(cylindrical=(1.0,i,0.0)) for i in 2*pi*arange(n_ch)/n_ch),
                                                        timebase = Timebase(arange(n_samples)*1.e-6),
                                                        modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                        noise = 0.01)
            # produce a dataset of flucstrucs
            fs_data = multichannel_data.flucstruc(min_dphase = -2*pi)
            # save our dataset to the database
            fs_data.save()
            session = pyfusion.Session()
            from pyfusion.data.timeseries import FlucStruc
            from pyfusion.data.base import DataSet
            d1 = DataSet()
            d1.save()
            d2 = DataSet()
            d2.save()
            
            # get our dataset from database
            our_dataset = session.query(DataSet).order_by("id").first()
            self.assertEqual(our_dataset.created, fs_data.created)

            self.assertEqual(len(our_dataset.data), len(our_dataset))


TestFlucstrucs.dev = True

class TestSubtractMeanFilter(BasePyfusionTestCase):
    """Test mean subtraction filter for timeseries data."""


    def test_remove_mean_single_channel(self):
        from pyfusion.data.filters import reduce_time
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted,mean

        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        # nonzero signal mean
        tsd = TimeseriesData(timebase=tb,
                             signal=Signal(arange(len(tb))), coords=[Coords()])

        filtered_tsd = tsd.subtract_mean()

        assert_almost_equal(mean(filtered_tsd.signal), 0)
        
    
    def test_remove_mean_multichanel(self):
        from numpy import mean, zeros_like
        multichannel_data = get_multimode_test_data(n_channels = 10,
                                                    ch_coords = tuple(Coords(cylindrical=(1.0,i,0.0)) for i in 2*pi*arange(10)/10),
                                                    timebase = Timebase(arange(0.0,0.01,1.e-5)),
                                                    modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                    noise = 0.2)
        # add some non-zero offset
        multichannel_data.signal += random.rand(*multichannel_data.signal.shape)

        filtered_data = multichannel_data.subtract_mean()
        mean_filtered_data = mean(filtered_data.signal, axis=1)
        assert_array_almost_equal(mean_filtered_data, zeros_like(mean_filtered_data))


    def test_remove_mean_dataset(self):
        from numpy import mean, zeros_like
        from pyfusion.data.base import DataSet
        multichannel_data_1 = get_multimode_test_data(n_channels = 10,
                                                    ch_coords = tuple(Coords(cylindrical=(1.0,i,0.0)) for i in 2*pi*arange(10)/10),
                                                    timebase = Timebase(arange(0.0,0.01,1.e-5)),
                                                    modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                    noise = 0.2)
        multichannel_data_2 = get_multimode_test_data(n_channels = 15,
                                                    ch_coords = tuple(Coords(cylindrical=(1.0,i,0.0)) for i in 2*pi*arange(15)/15),
                                                    timebase = Timebase(arange(0.0,0.01,1.e-5)),
                                                    modes = [[0.7, 7., 24.e3, 3.2], [1.0, 90., 37.e3, 10.3]],
                                                    noise = 0.7)
        multichannel_data_3 = get_multimode_test_data(n_channels = 13,
                                                    ch_coords = tuple(Coords(cylindrical=(1.0,i,0.0)) for i in 2*pi*arange(13)/13),
                                                    timebase = Timebase(arange(0.0,0.01,1.e-5)),
                                                    modes = [[0.7, 7., 24.e3, 3.2], [1.0, 90., 37.e3, 10.3]],
                                                    noise = 0.7)
        # add some non-zero offset
        multichannel_data_1.signal += random.rand(*multichannel_data_1.signal.shape)
        multichannel_data_2.signal += random.rand(*multichannel_data_2.signal.shape)

        test_dataset = DataSet()
        test_dataset.add(multichannel_data_1)
        test_dataset.add(multichannel_data_2)


        filtered_data = test_dataset.subtract_mean()
        for d in filtered_data:
            mean_filtered_data = mean(d.signal, axis=1)
            assert_array_almost_equal(mean_filtered_data, zeros_like(mean_filtered_data))


class TestFilterMetaClass(BasePyfusionTestCase):

    def test_new_filter(self):
        from pyfusion.data import filters
        from pyfusion.data.base import BaseData
        # add some filters
        @filters.register("TestData")
        def test_filter(self):
            return self

        @filters.register("TestData", "TestData2")
        def other_test_filter(self):
            return self

        # now create TestData 

        class TestData(BaseData):
            pass
        
        test_data = TestData()
        for attr_name in ["test_filter", "other_test_filter"]:
            self.assertTrue(hasattr(test_data, attr_name))


class TestNumpyFilters(BasePyfusionTestCase):

    def test_correlate(self):
        from numpy import correlate
        multichannel_data = get_multimode_test_data(n_channels = 2,
                                                    ch_coords = tuple(Coords(cylindrical=(1.0,i,0.0)) for i in 2*pi*arange(2)/2),
                                                    timebase = Timebase(arange(0.0,0.01,1.e-5)),
                                                    modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                    noise = 0.2)
        numpy_corr = correlate(multichannel_data.signal[0], multichannel_data.signal[1])

        pyfusion_corr = multichannel_data.correlate(0,1)
        assert_array_almost_equal(numpy_corr, pyfusion_corr)


class TestPlotMethods(BasePyfusionTestCase):
    def test_svd_plot(self):
        from pyfusion.data.timeseries import SVDData
        n_ch = 4
        n_samples = 256
        multichannel_data = get_multimode_test_data(n_channels = n_ch,
                                                    ch_coords = tuple(Coords(cylindrical=(1.0,i,0.0)) for i in 2*pi*arange(n_ch)/n_ch),
                                                    timebase = Timebase(arange(n_samples)*1.e-6),
                                                    modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                    noise = 0.5)

        test_svd = multichannel_data.svd()
        self.assertTrue(hasattr(test_svd, 'svdplot'))
        

class TestDataHistory(BasePyfusionTestCase):
    def testNewData(self):
        from pyfusion.data.base import BaseData
        test_data = BaseData()
        self.assertEqual(test_data.history.split('> ')[1], 'New BaseData')

    def testFilteredDataHistory(self):
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange

        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        # nonzero signal mean
        tsd = TimeseriesData(timebase=tb,
                             signal=Signal(arange(len(tb))), coords=[Coords()])

        filtered_tsd = tsd.subtract_mean()
        self.assertEqual(len(filtered_tsd.history.split('\n')), 2)
        filtered_tsd.normalise(method='rms')
        self.assertEqual(filtered_tsd.history.split('> ')[-1], "normalise(method='rms')")

