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
