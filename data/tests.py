

from pyfusion.test.tests import BasePyfusionTestCase
from pyfusion.data.base import BaseData
from pyfusion.data.timeseries import SCTData, MCTData

class TestBaseData(BasePyfusionTestCase):
    pass

class TestSCTData(BasePyfusionTestCase):
    def testBaseClasses(self):
        self.assertTrue(BaseData in SCTData.__bases__)

class TestMCTData(BasePyfusionTestCase):
    def testBaseClasses(self):
        self.assertTrue(BaseData in MCTData.__bases__)
