"""Tests for data code."""
from numpy.testing import assert_array_almost_equal, assert_almost_equal
from numpy import arange, pi, zeros, resize, random, cos, array

from pyfusion.test.tests import BasePyfusionTestCase
from pyfusion.data.base import BaseData, DataSet, Coords, ChannelList, Channel
from pyfusion.data.timeseries import TimeseriesData, Timebase, Signal
from pyfusion.data.utils import cps


def get_n_channels(n_ch):
    return ChannelList(*(Channel('ch_%02d' %i, Coords('cylindrical',(1.0,i,0.0))) for i in 2*pi*arange(n_ch)/n_ch))

# modes: [amplitude, freq, phase at angle0, phase offset]
def get_multimode_test_data(n_channels = 10,
                            channels = get_n_channels(10),
                            timebase = Timebase(arange(0.0,0.01,1.e-5)),
                            modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                            noise = 0.2):
    data_array = zeros((n_channels, len(timebase)))
    timebase_matrix = resize(timebase, (n_channels, len(timebase)))
    angle_matrix = resize(array([i.coords.cylindrical[1] for i in channels]), (len(timebase), n_channels)).T
    for m in modes:
        data_array += m[0]*cos(2*pi*m[2]*timebase_matrix + m[1]*angle_matrix + m[3])
    data_array += noise*2*(random.random(data_array.shape)-0.5)
    output = TimeseriesData(timebase=timebase,
                            signal=Signal(data_array), channels=channels)
    return output


class TestChannels(BasePyfusionTestCase):
    def test_channel_class(self):
        from pyfusion.data.base import Channel, Coords

        test_coords = Coords('cylindrical',(0.0,0.0,0.0))
        
        test_ch = Channel('test_1', test_coords)

        self.assertEqual(test_ch.name, 'test_1')
        self.assertEqual(test_ch.coords, test_coords)

    def test_channels_ORM(self):
        import pyfusion
        if pyfusion.USE_ORM:
            from pyfusion.data.base import Channel, Coords
            test_coords = Coords('cylindrical',(0.0,0.0,0.0))
        
            test_ch = Channel('test_1', test_coords)
            test_ch.save()

            session = pyfusion.Session()
            our_channel = session.query(Channel).first()
            self.assertEqual(our_channel.name, 'test_1')

        

class TestChannelList(BasePyfusionTestCase):
    def test_channel_list(self):
        from pyfusion.data.base import ChannelList, Channel, Coords

        ch01 = Channel('test_1', Coords('dummy', (0,0,0)))
        ch02 = Channel('test_2', Coords('dummy', (0,0,0)))
        ch03 = Channel('test_3', Coords('dummy', (0,0,0)))
                       
        new_cl = ChannelList([ch01, ch02, ch03])

    def test_channellist_ORM(self):
        import pyfusion
        if pyfusion.USE_ORM:
            from pyfusion.data.base import ChannelList, Channel, Coords
            
            ch01 = Channel('test_1', Coords('dummy', (0,0,0)))
            ch02 = Channel('test_2', Coords('dummy', (0,0,0)))
            ch03 = Channel('test_3', Coords('dummy', (0,0,0)))
                       
            new_cl = ChannelList(ch03, ch01, ch02)
            
            new_cl.save()

            # get our channellist
            session = pyfusion.Session()
            our_channellist = session.query(ChannelList).order_by("id").first()

            self.assertEqual(our_channellist[0].name, 'test_3')
            self.assertEqual(our_channellist[1].name, 'test_1')
            self.assertEqual(our_channellist[2].name, 'test_2')


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
                                                     channels=get_n_channels(1),
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
        channels = ChannelList(*(Channel('ch_%d' %i, Coords('cylindrical',(1.0,i,0.0))) for i in 2*pi*arange(n_ch)/n_ch))
        multichannel_data = get_multimode_test_data(n_channels = n_ch,
                                                    channels = channels,
                                                    timebase = timebase,
                                                    modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                    noise = 0.5)


    """
    def test_channel_names(self):
        n_ch = 10
        n_samples = 1024
        timebase = Timebase(arange(n_samples)*1.e-6)
        channels = ChannelList((Channel('ch_%02d' %i, Coords('cylindrical',(1.0,i,0.0))) for i in 2*pi*arange(n_ch)/n_ch))
        multichannel_data = get_multimode_test_data(n_channels = n_ch,
                                                    channels=channels,
                                                    timebase = timebase,
                                                    modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                    noise = 0.5)
        self.assertEqual(ch_names, multichannel_data.channel_names)
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
        self.assertAlmostEqual(test_tb.sample_freq, sample_freq, 4)

    def test_timebase_slice(self):
        from pyfusion.data.timeseries import generate_timebase
        from numpy import arange
        t0=0.3
        n_samples=500
        sample_freq=1.e6
        test_tb = generate_timebase(t0=t0,n_samples=n_samples, sample_freq=sample_freq)

        self.assertTrue(hasattr(test_tb, 'sample_freq'))

        sliced_tb = test_tb[:10]

        self.assertTrue(hasattr(sliced_tb, 'sample_freq'))


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
                             signal=Signal(arange(len(tb))),
                             channels=get_n_channels(1))
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
                             channels=get_n_channels(5))
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
                             channels=get_n_channels(5))
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
                               channels=get_n_channels(5))
        tsd_2 = TimeseriesData(timebase=tb, signal=Signal(resize(arange(5*len(tb))+1,(5,len(tb)))),
                               channels=get_n_channels(5))
        test_dataset = DataSet('test_dataset')
        test_dataset.add(tsd_1)
        test_dataset.add(tsd_2)
        test_dataset.reduce_time(new_times)
        
class TestDataSet(BasePyfusionTestCase):

    def test_dataset(self):
        from pyfusion.data.base import DataSet
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        ch=get_n_channels(5)
        new_times = [-0.25, 0.25]
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd_1 = TimeseriesData(timebase=tb, signal=Signal(resize(arange(5*len(tb)),(5,len(tb)))),
                               channels=ch)
        tsd_2 = TimeseriesData(timebase=tb,
                               signal=Signal(resize(arange(5*len(tb))+1, (5,len(tb)))),
                               channels=ch)
        test_dataset = DataSet('test_ds_1')
        test_dataset.add(tsd_1)
        test_dataset.add(tsd_2)
        self.assertTrue(tsd_1 in test_dataset)
        
        """
        # we don't support removing items from dataset yet...
        test_dataset.remove(tsd_1)
        self.assertFalse(tsd_1 in test_dataset)
        self.assertTrue(tsd_2 in test_dataset)
        """

    def test_dataset_filters_2(self):
        from pyfusion.data.base import DataSet
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        new_times = [-0.25, 0.25]
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        ch = get_n_channels(5)
        tsd_1 = TimeseriesData(timebase=tb, signal=Signal(resize(arange(5*len(tb)),(5,len(tb)))),
                               channels=ch)
        tsd_2 = TimeseriesData(timebase=tb,
                               signal=Signal(resize(arange(5*len(tb))+1,(5,len(tb)))),
                               channels=ch)
        test_dataset = DataSet('test_ds_2')
        test_dataset.add(tsd_1)
        test_dataset.add(tsd_2)
        test_dataset.reduce_time(new_times)

class TestSegmentFilter(BasePyfusionTestCase):
    
    def test_single_channel_timeseries(self):
        from pyfusion.data.base import DataSet
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd = TimeseriesData(timebase=tb,
                             signal=Signal(arange(len(tb))), channels=get_n_channels(1))
        seg_dataset = tsd.segment(n_samples=10)
        self.assertTrue(len(seg_dataset)==10)

    def test_multi_channel_timeseries(self):
        from pyfusion.data.base import DataSet
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd = TimeseriesData(timebase=tb,
                             signal=Signal(resize(arange(3*len(tb)), (3,len(tb)))),
                             channels=get_n_channels(3))
        seg_dataset = tsd.segment(n_samples=10)
        self.assertTrue(len(seg_dataset)==10)

    def test_dataset(self):
        from pyfusion.data.base import DataSet
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted, resize
        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tsd_1 = TimeseriesData(timebase=tb,
                               signal=Signal(resize(arange(3*len(tb)), (3,len(tb)))),
                               channels=get_n_channels(3))
        tsd_2 = TimeseriesData(timebase=tb,
                               signal=Signal(resize(arange(3*len(tb)+1),(3,len(tb)))),
                               channels=get_n_channels(3))
        input_dataset = DataSet('test_dataset')
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
        dummy_coords = Coords('cylindrical',(1.0,1.0,1.0))
        self.assertEqual(dummy_coords.cylindrical, (1.0,1.0,1.0))
        # testing adding of coords
        dummy_coords.add_coords(cartesian=(0.1,0.5,0.2))
        self.assertEqual(dummy_coords.cartesian, (0.1,0.5,0.2))

    def test_coord_transform(self):
        from pyfusion.data.base import Coords
        cyl_coords = (1.0,1.0,1.0)
        dummy_coords = Coords('cylindrical',cyl_coords)
        dummy_coords.load_transform(DummyCoordTransform)
        self.assertEqual(dummy_coords.dummy(), (2*cyl_coords[0], 3*cyl_coords[1], 4*cyl_coords[2]))
        cyl_coords = (2.0,1.0,4.0)
        dummy_coords_1 = Coords('cylindrical',cyl_coords)
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

        test_dataset = DataSet('test_dataset')
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
        channels = ChannelList(*(Channel('ch_%02d' %i, Coords('cylindrical',(1.0,i,0.0))) for i in 2*pi*arange(n_ch)/n_ch))
        multichannel_data = get_multimode_test_data(n_channels = n_ch,
                                                    channels = channels,
                                                    timebase = timebase,
                                                    modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                    noise = 0.5)

        test_svd = multichannel_data.svd()
        self.assertTrue(isinstance(test_svd, SVDData))
        self.assertEqual(len(test_svd.topos[0]), n_ch)
        self.assertEqual(len(test_svd.chronos[0]), n_samples)
        assert_array_almost_equal(test_svd.chrono_labels, timebase)
        for c_i, ch in enumerate(channels):
            self.assertEqual(ch, test_svd.channels[c_i])

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

    """
    def test_fs_grouping(self):
        ## disabled because filter isn't returning a DataSet subclass
        # this signal should be grouped as [0,1], [2,3] + noise 
        multichannel_data = get_multimode_test_data(n_channels = 10,
                                                    channels = get_n_channels(10),
                                                    #timebase = Timebase(arange(0.0,0.01,1.e-6)),
                                                    timebase = Timebase(arange(1024)*1.e-6),
                                                    modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                    noise = 0.5)

        fs_groups = multichannel_data.fs_group_geometric()
        self.assertEqual(fs_groups[0], [0,1])
        self.assertEqual(fs_groups[1], [2,3])
        

    def test_fs_grouping_from_svd(self):
        ## disabled because filter isn't returning a DataSet subclass
        n_ch = 10
        n_samples = 1024
        multichannel_data = get_multimode_test_data(n_channels = n_ch,
                                                    channels = get_n_channels(n_ch),
                                                    timebase = Timebase(arange(n_samples)*1.e-6),
                                                    modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                    noise = 0.5)

        test_svd = multichannel_data.svd()
        fs_groups = test_svd.fs_group_geometric()
    """
    
    def test_flucstruc_signals(self):
        # make sure that flucstruc derived from all singular values
        # gives back the original signal
        from pyfusion.data.timeseries import SVDData, FlucStruc
        from pyfusion.data.base import DataSet
        from numpy import array
        n_ch = 10
        n_samples = 1024
        multichannel_data = get_multimode_test_data(n_channels = n_ch,
                                                    channels=get_n_channels(n_ch),
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
                                                    channels=get_n_channels(n_ch),
                                                    timebase = Timebase(arange(n_samples)*1.e-6),
                                                    modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                    noise = 0.01)
        fs_data = multichannel_data.flucstruc(min_dphase = -2*pi)
        self.assertTrue(isinstance(fs_data, DataSet))
        self.assertTrue(len([i for i in fs_data.data]) > 0)
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
#                                                     ch_coords = tuple(Coords('cylindrical',(1.0,i,0.0)) for i in 2*pi*arange(10)/10),
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
                                                        channels=get_n_channels(n_ch),
                                                        timebase = Timebase(arange(n_samples)*1.e-6),
                                                        modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                        noise = 0.01)
            # produce a dataset of flucstrucs
            #print ">> ", multichannel_data.channels
            fs_data = multichannel_data.flucstruc(min_dphase = -2*pi)
            print type(fs_data)
            #print list(fs_data)[0].dphase[0].channel_1
            #print '---'
            # save our dataset to the database
            fs_data.save()
            session = pyfusion.Session()
            from pyfusion.data.timeseries import FlucStruc
            from pyfusion.data.base import DataSet
            d1 = DataSet('test_dataset_1')
            d1.save()
            d2 = DataSet('test_dataset_2')
            d2.save()
            
            # get our dataset from database
            our_dataset = session.query(DataSet).order_by("id").first()
            self.assertEqual(our_dataset.created, fs_data.created)

            self.assertEqual(len([i for i in our_dataset.data]), len(our_dataset))

            #check flucstrucs have freq, t0 and d_phase..
            #for i in our_dataset.data:
            #    print i
            #print 'w'
            #assert False

            #our guinea pig flucstruc:
            test_fs = our_dataset.pop()
            self.assertTrue(isinstance(test_fs.freq, float))
            self.assertTrue(isinstance(test_fs.t0, float))

            # now, are the phase data correct?

            from pyfusion.data.base import BaseOrderedDataSet
            self.assertTrue(isinstance(test_fs.dphase, BaseOrderedDataSet))
            self.assertEqual(len(test_fs.dphase), n_ch-1)

            # what if we close the session and try again?

            session.close()
            session = pyfusion.Session()

            ds_again = session.query(DataSet).order_by("id").first()
            fs_again = list(ds_again)[0]
            """
            for i in fs_again.dphase:
                print i
            assert False
            """

class TestFloatDelta(BasePyfusionTestCase):
    """delta phase data class."""

    def test_d_phase(self):
        from pyfusion.data.base import FloatDelta, Channel, Coords
        channel_01 = Channel('channel_01', Coords('dummy', (0,0,0)))
        channel_02 = Channel('channel_02', Coords('dummy', (0,0,0)))

        fd = FloatDelta(channel_01, channel_02, 0.45)
        
    def test_ORM_floatdelta(self):
        """ check that floatdelta can be saved to database"""
        from pyfusion.data.base import FloatDelta, Channel, Coords
        channel_01 = Channel('channel_01', Coords('dummy', (0,0,0)))
        channel_02 = Channel('channel_02', Coords('dummy', (0,0,0)))
        import pyfusion
        if pyfusion.USE_ORM:
            fd = FloatDelta(channel_01, channel_02, 0.45)
            fd.save()
            session = pyfusion.Session()
            db_fd = session.query(FloatDelta).first()
            self.assertEqual(db_fd.delta, 0.45)


class TestOrderedDataSet(BasePyfusionTestCase):
    """test the ordered dataset"""

    ## need to fix for datasetitems..
    """
    def test_ordereddataset(self):
        from pyfusion.data.base import BaseOrderedDataSet, BaseData
        #pretend these are datapoints
        class TestData(BaseData):
            def __init__(self, a, b):
                self.a = a
                self.b = b
                super(TestData, self).__init__()

        d1=TestData(1,2)
        d2=TestData(2,1)

        ods = BaseOrderedDataSet('test_ods')
        ods.append(d1)
        ods.append(d2)

        self.assertEqual(ods[0], d1)
        self.assertEqual(ods[1], d2)

    """ 

    """
    def test_submethod(self):
        from pyfusion.data.base import OrderedDataSet, BaseData
        class TestData(BaseData):
            def __init__(self, a):
                self.a = a
                super(TestData, self).__init__()

        d1 = TestData(TestData(1))
        d2 = TestData(TestData(2))
        d3 = TestData(TestData(3))

        ds = OrderedDataSet(ordered_by='a.a')
        for d in [d3, d1, d2]:
            ds.add(d)
        self.assertEqual(ds[0].a.a, 1)
        self.assertEqual(ds[1].a.a, 2)
        self.assertEqual(ds[2].a.a, 3)
    """
    def test_ordered_dataset_ORM(self):
        from pyfusion.data.base import FloatDelta, BaseOrderedDataSet, Channel, Coords

        channel_01 = Channel('channel_01', Coords('dummy', (0,0,0)))
        channel_02 = Channel('channel_02', Coords('dummy', (0,0,0)))
        channel_03 = Channel('channel_03', Coords('dummy', (0,0,0)))
        channel_04 = Channel('channel_04', Coords('dummy', (0,0,0)))
        

        fd1 = FloatDelta(channel_01, channel_02, 0.45)
        fd2 = FloatDelta(channel_02, channel_03, 0.25)
        fd3 = FloatDelta(channel_03, channel_04, 0.49)

        #ods = OrderedDataSet(ordered_by="channel_1.name")
        ods = BaseOrderedDataSet('test_ods')
        
        for fd in [fd3, fd1, fd2]:
            ods.append(fd)

        ods.save()

        # now read out of database
        import pyfusion
        if pyfusion.USE_ORM:
            session = pyfusion.Session()
            db_ods = session.query(BaseOrderedDataSet).first()
            self.assertEqual(db_ods[0].channel_1.name, 'channel_03')
            self.assertEqual(db_ods[1].channel_1.name, 'channel_01')
            self.assertEqual(db_ods[2].channel_1.name, 'channel_02')
        
class TestRemoveNonContiguousFilter(BasePyfusionTestCase):

    def test_remove_noncontiguous(self):
        from pyfusion.data.filters import reduce_time
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from pyfusion.data.base import DataSet
        from numpy import arange, searchsorted,mean

        tb1 = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tb2 = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        tb3 = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        # nonzero signal mean
        tsd1 = TimeseriesData(timebase=tb1,
                              signal=Signal(arange(len(tb1))), channels=ChannelList(Channel('ch_01',Coords('dummy',(0,0,0)))))
        tsd2 = TimeseriesData(timebase=tb2,
                              signal=Signal(arange(len(tb2))), channels=ChannelList(Channel('ch_01',Coords('dummy',(0,0,0)))))
        tsd3 = TimeseriesData(timebase=tb3,
                              signal=Signal(arange(len(tb3))), channels=ChannelList(Channel('ch_01',Coords('dummy',(0,0,0)))))

        self.assertTrue(tb1.is_contiguous())
        self.assertTrue(tb2.is_contiguous())
        self.assertTrue(tb3.is_contiguous())
        tsd2.timebase[-50:] += 1.0
        self.assertFalse(tb2.is_contiguous())

        ds = DataSet('ds')
        for tsd in [tsd1, tsd2, tsd3]:
            ds.add(tsd)
        
        for tsd in [tsd1, tsd2, tsd3]:
            self.assertTrue(tsd in ds)

        filtered_ds = ds.remove_noncontiguous()
        for tsd in [tsd1, tsd3]:
            self.assertTrue(tsd in filtered_ds)
            
        self.assertFalse(tsd2 in filtered_ds)


        
class TestSubtractMeanFilter(BasePyfusionTestCase):
    """Test mean subtraction filter for timeseries data."""


    def test_remove_mean_single_channel(self):
        from pyfusion.data.filters import reduce_time
        from pyfusion.data.timeseries import TimeseriesData, generate_timebase, Signal
        from numpy import arange, searchsorted,mean

        tb = generate_timebase(t0=-0.5, n_samples=1.e2, sample_freq=1.e2)
        # nonzero signal mean
        tsd = TimeseriesData(timebase=tb,
                             signal=Signal(arange(len(tb))), channels=ChannelList(Channel('ch_01',Coords('dummy',(0,0,0)))))

        filtered_tsd = tsd.subtract_mean()

        assert_almost_equal(mean(filtered_tsd.signal), 0)
        
    
    def test_remove_mean_multichanel(self):
        from numpy import mean, zeros_like
        multichannel_data = get_multimode_test_data(n_channels = 10,
                                                    channels=get_n_channels(10),
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
                                                      channels=get_n_channels(10),
                                                      timebase = Timebase(arange(0.0,0.01,1.e-5)),
                                                      modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                      noise = 0.2)
        multichannel_data_2 = get_multimode_test_data(n_channels = 15,
                                                      channels=get_n_channels(15),
                                                      timebase = Timebase(arange(0.0,0.01,1.e-5)),
                                                      modes = [[0.7, 7., 24.e3, 3.2], [1.0, 90., 37.e3, 10.3]],
                                                      noise = 0.7)
        multichannel_data_3 = get_multimode_test_data(n_channels = 13,
                                                      channels=get_n_channels(13),
                                                      timebase = Timebase(arange(0.0,0.01,1.e-5)),
                                                      modes = [[0.7, 7., 24.e3, 3.2], [1.0, 90., 37.e3, 10.3]],
                                                      noise = 0.7)
        # add some non-zero offset
        multichannel_data_1.signal += random.rand(*multichannel_data_1.signal.shape)
        multichannel_data_2.signal += random.rand(*multichannel_data_2.signal.shape)

        test_dataset = DataSet('test_dataset')
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
                                                    channels=get_n_channels(2),
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
                                                    channels=get_n_channels(n_ch),
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
        ch = get_n_channels(1)
        tsd = TimeseriesData(timebase=tb,
                             signal=Signal(arange(len(tb))), channels=ch)

        filtered_tsd = tsd.subtract_mean()
        self.assertEqual(len(filtered_tsd.history.split('\n')), 2)
        filtered_tsd.normalise(method='rms')
        print filtered_tsd.history
        self.assertEqual(filtered_tsd.history.split('> ')[-1], "normalise(method='rms')")


class TestDataSetLabels(BasePyfusionTestCase):
    def test_dataset_label(self):
        import pyfusion
        from pyfusion.data.base import DataSet
        test_ds = DataSet('test_ds_1')
        test_ds.save()
        self.assertEqual(test_ds.label, 'test_ds_1')
        if pyfusion.USE_ORM:
            session = pyfusion.Session()
            db_ods = session.query(DataSet).filter_by(label='test_ds_1')
            
    def test_baseordereddataset_label(self):
        import pyfusion
        from pyfusion.data.base import BaseOrderedDataSet
        test_ds = BaseOrderedDataSet('test_ods_1')
        test_ds.save()
        self.assertEqual(test_ds.label, 'test_ods_1')
        if pyfusion.USE_ORM:
            session = pyfusion.Session()
            db_ods = session.query(BaseOrderedDataSet).filter_by(label='test_ods_1')
            
        
        
class TestGetCoords(BasePyfusionTestCase):
    def test_get_coords_for_channel_config(self):
        from pyfusion.data.base import get_coords_for_channel
        channel_name = "H1_mirnov_array_1_coil_15"
        coords = get_coords_for_channel(channel_name)
        self.assertTrue(isinstance(coords, Coords))
        self.assertEqual(coords.default_name, 'cylindrical')
        #print coords.magnetic(kh=1.2)



class TestStoredMetaDataForDataSets(BasePyfusionTestCase):
    def test_stored_metadata_datasets(self):
        """Make sure metadata attached to dataset classes is saved to sql."""
        import pyfusion
        if pyfusion.USE_ORM:
            n_ch = 3
            n_samples = 1024
            multichannel_data = get_multimode_test_data(n_channels = n_ch,
                                                        channels=get_n_channels(n_ch),
                                                        timebase = Timebase(arange(n_samples)*1.e-6),
                                                        modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                        noise = 0.01)
            # put in some fake metadata 
            multichannel_data.meta = {'hello':'world'}
            print multichannel_data.meta


            # produce a dataset of flucstrucs
            fs_data = multichannel_data.flucstruc(min_dphase = -2*pi)

            # check that metadata is carried to the flucstrucs
            
            self.assertEqual(fs_data.meta, multichannel_data.meta)
            
            # save our dataset to the database
            fs_data.save()

            session = pyfusion.Session()
            from pyfusion.data.base import DataSet

            some_ds = session.query(DataSet).all().pop()
            print type(some_ds)
            self.assertEqual(some_ds.meta, multichannel_data.meta)

            #print some_ds.meta
            #assert False
    
class TestStoredMetaData(BasePyfusionTestCase):
    def test_stored_metadata_data(self):
        """ metadata should be stored to data instances, rather than datasets - this might be slower, but more likely to guarantee data is kept track of."""
        import pyfusion
        if pyfusion.USE_ORM:
            n_ch = 3
            n_samples = 1024
            multichannel_data = get_multimode_test_data(n_channels = n_ch,
                                                        channels=get_n_channels(n_ch),
                                                        timebase = Timebase(arange(n_samples)*1.e-6),
                                                        modes = [[0.7, 3., 24.e3, 0.2], [0.5, 4., 37.e3, 0.3]],
                                                        noise = 0.01)




            # put in some fake metadata 
            multichannel_data.meta = {'hello':'world'}
            print multichannel_data.meta

            # produce a dataset of flucstrucs
            fs_data = multichannel_data.flucstruc(min_dphase = -2*pi)

            # check that metadata is carried to the individual flucstrucs
            for fs in fs_data:
                self.assertEqual(fs.meta, multichannel_data.meta)

            # save our dataset to the database
            fs_data.save()

            ## now test to make sure metadata is saved in database

            session = pyfusion.Session()
            from pyfusion.data.timeseries import FlucStruc

            some_fs = session.query(FlucStruc).all().pop()
            

            self.assertEqual(some_fs.meta, multichannel_data.meta)





class TestSciPyFilters(BasePyfusionTestCase):
    def test_sp_filter_butterworth_bandpass(self):
        import pyfusion
        n_ch = 3
        n_samples = 1024
        sample_period = 1.e-6
        # Let's generate a test signal with strong peaks at 20kHz and
        # 60kHz and a weaker peak at 40kHz. 
        
        multichannel_data = get_multimode_test_data(n_channels = n_ch,
                                                    channels=get_n_channels(n_ch),
                                                    timebase = Timebase(arange(n_samples)*sample_period),
                                                    modes = [[10.0, 3., 20.e3, 0.2], [2.0, 4., 40.e3, 0.3], [10.0, 5., 60.e3, 0.4]],
                                                    noise = 0.1)

        filtered_data = multichannel_data.sp_filter_butterworth_bandpass([35.e3, 45.e3], [25.e3, 55.e3], 1.0, 10.0)


TestSciPyFilters.dev = True
