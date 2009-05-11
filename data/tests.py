"""Tests for data code."""

from pyfusion.test.tests import BasePyfusionTestCase
from pyfusion.data.base import BaseData
from pyfusion.data.timeseries import SCTData, MCTData

class TestSCTData(BasePyfusionTestCase):
    """Tests for single channel timeseries (SCT) data."""
    def testBaseClasses(self):
        self.assertTrue(BaseData in SCTData.__bases__)

class TestMCTData(BasePyfusionTestCase):
    """Tests for multiple-channel timeseries (MCT) data."""
    def testBaseClasses(self):
        self.assertTrue(BaseData in MCTData.__bases__)
