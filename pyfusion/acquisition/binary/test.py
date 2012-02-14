"""Test code for binary file acquisition."""

import os
from numpy.testing import assert_array_almost_equal, assert_almost_equal
import numpy as np
from pyfusion.acquisition.binary.acq import BinaryAcquisition
from pyfusion.acquisition.binary.fetch import BinaryMultiChannelTimeseriesFetcher
from pyfusion.acquisition.base import BaseAcquisition
from pyfusion.test.tests import PfTestBase

binary_datafile_dtype = np.dtype([('timebase',np.float32),
                                  ('channel_1',np.float32),
                                  ('channel_2',np.float32)])

class CheckBinaryAcquisition(PfTestBase):
    """Test the fake data acquisition used for testing."""

    def testBaseClasses(self):
        """Make sure BinaryAcquisition is subclass of Acquisition."""
        self.assertTrue(BaseAcquisition in BinaryAcquisition.__bases__)

    def test_config_dtype(self):
        """Make sure that we correctly interpret dtype specified in config file."""

        filename = os.path.join(os.path.dirname(__file__), "test_bin.dat")
        test_acq = BinaryAcquisition()
        test_shot_number = 12345
        fetcher = BinaryMultiChannelTimeseriesFetcher(test_acq, test_shot_number,"test_binary_diag", filename=filename)
        test_dtype = fetcher.read_dtype()
        self.assertEqual(test_dtype, binary_datafile_dtype)



    def testdata(self):
        """read in a test file and compare returned data object to expected result""" 
        filename = os.path.join(os.path.dirname(__file__), "test_bin.dat")
        data = np.fromfile(filename, dtype=binary_datafile_dtype)
        test_acq = BinaryAcquisition()
        test_shot_number = 12345

        test_data = test_acq.getdata(test_shot_number, "test_binary_diag", filename=filename)

        assert_array_almost_equal(data['timebase'], test_data.timebase)        
        assert_array_almost_equal(data['channel_1'], test_data.signal[0])
        assert_array_almost_equal(data['channel_2'], test_data.signal[1])

        self.assertEqual(test_shot_number, test_data.meta['shot'])

    def test_shot_data(self):
        """Check that filenames with shot numbers are are used when requested."""
        filename = os.path.join(os.path.dirname(__file__), "test_binary_shot_(shot).dat")
        test_acq = BinaryAcquisition()
        test_shot_number = 12345
        test_data = test_acq.getdata(test_shot_number, "test_binary_diag", filename=filename)

class CheckBinaryMultiFileFetch(PfTestBase):
    """Test the multiple-file data fetcher class."""

    def test_multi_fetch(self):
        filename_1 = os.path.join(os.path.dirname(__file__), "test_binary_shot_(shot)_1.dat")
        filename_2 = os.path.join(os.path.dirname(__file__), "test_binary_shot_(shot)_2.dat")
        test_acq = BinaryAcquisition()
        test_shot_number = 12345
        test_data = test_acq.getdata(test_shot_number, "test_binary_diag_multifile", filenames=[filename_1, filename_2])
        
        data = np.fromfile(filename_1.replace("(shot)", str(test_shot_number)), dtype=binary_datafile_dtype)
        assert_array_almost_equal(data['timebase'], test_data.timebase)        
        assert_array_almost_equal(data['channel_1'], test_data.signal[0])
        assert_array_almost_equal(data['channel_2'], test_data.signal[1])

        data = np.fromfile(filename_2.replace("(shot)", str(test_shot_number)), dtype=binary_datafile_dtype)
        assert_array_almost_equal(data['timebase'], test_data.timebase)        
        assert_array_almost_equal(data['channel_1'], test_data.signal[2])
        assert_array_almost_equal(data['channel_2'], test_data.signal[3])
        

    def test_dphase_subset(self):
        """Test that we can specify subset of channels for use in flucstruc d_phases.

        TODO: this should be tested more generally, not just for binary data fetchers.
        """

        filename_1 = os.path.join(os.path.dirname(__file__), "test_binary_shot_(shot)_1.dat")
        filename_2 = os.path.join(os.path.dirname(__file__), "test_binary_shot_(shot)_2.dat")
        test_acq = BinaryAcquisition()
        test_shot_number = 12345
        phase_pairs = "[('channel_1','channel_2'),('channel_3','channel_4')]"
        # delta phases used in generating test data files...
        phase_diffs = [-0.1*np.pi, -0.4*np.pi]
        phase_pairs_eval = eval(phase_pairs)
        test_data = test_acq.getdata(test_shot_number, "test_binary_diag_multifile", 
                                     filenames=[filename_1, filename_2],
                                     phase_pairs = phase_pairs)
        
        flucstrucs = test_data.subtract_mean().flucstruc()
        # get top fs
        max_p = 0
        for fs in flucstrucs:
            if fs.p > max_p:
                top_fs = fs
                max_p = fs.p

        
        self.assertEqual(len(top_fs.dphase),len(phase_pairs_eval))
        self.assertEqual(top_fs.dphase[0].channel_1.name, phase_pairs_eval[0][0])
        self.assertEqual(top_fs.dphase[0].channel_2.name, phase_pairs_eval[0][1])
        self.assertEqual(top_fs.dphase[1].channel_1.name, phase_pairs_eval[1][0])
        self.assertEqual(top_fs.dphase[1].channel_2.name, phase_pairs_eval[1][1])
        self.assertTrue(np.abs(top_fs.dphase[0].delta-phase_diffs[0])<0.01)
        self.assertTrue(np.abs(top_fs.dphase[1].delta-phase_diffs[1])<0.01)



        test_data_2 = test_acq.getdata(test_shot_number, "test_binary_diag_multifile", 
                                       filenames=[filename_1, filename_2])

        flucstrucs_2 = test_data_2.subtract_mean().flucstruc()
        max_p = 0
        for fs in flucstrucs_2:
            if fs.p > max_p:
                top_fs = fs
                max_p = fs.p

        self.assertEqual(len(top_fs.dphase),3)
        all_phase_diffs = [-0.1*np.pi, -0.2*np.pi, -0.4*np.pi]
        self.assertTrue(np.abs(top_fs.dphase[0].delta-all_phase_diffs[0])<0.01)
        self.assertTrue(np.abs(top_fs.dphase[1].delta-all_phase_diffs[1])<0.01)
        self.assertTrue(np.abs(top_fs.dphase[2].delta-all_phase_diffs[2])<0.01)


