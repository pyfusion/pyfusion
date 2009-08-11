"""Test code for MDSPlus data acquisition."""

from pyfusion.test.tests import BasePyfusionTestCase


class TestMDSPlusDataAcquisition(BasePyfusionTestCase):

    def testBaseClasses(self):
        from pyfusion.acquisition.MDSPlus.acq import MDSPlusAcquisition
        from pyfusion.acquisition.base import BaseAcquisition
        self.assertTrue(BaseAcquisition in MDSPlusAcquisition.__bases__)

class TestMDSPlusDataFetchers(BasePyfusionTestCase):

    def testDataFetchers(self):
        from pyfusion.acquisition.base import BaseDataFetcher
        from pyfusion.acquisition.MDSPlus.fetch import MDSPlusDataFetcher
        self.assertTrue(BaseDataFetcher in MDSPlusDataFetcher.__bases__)

