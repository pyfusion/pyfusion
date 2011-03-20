""" Test code for H1 HTTP data acces."""
import os
from pyfusion.test.tests import PfTestBase, BasePyfusionTestCase
import pyfusion

TEST_DATA_PATH = os.path.abspath(os.path.dirname(__file__))
TEST_CONFIG_FILE = os.path.join(TEST_DATA_PATH, "test.cfg")

class H1WebTestCase(BasePyfusionTestCase):

    def setUp(self):
        pyfusion.conf.utils.clear_config()
        if pyfusion.orm_manager.IS_ACTIVE:
            pyfusion.orm_manager.Session.close_all()
            pyfusion.orm_manager.clear_mappers()
        pyfusion.conf.utils.read_config(TEST_CONFIG_FILE)

class TestH1WebDataAcq(H1WebTestCase):

    def test_acq(self):
        test_device = pyfusion.getDevice("TestH1WebDevice")
        test_data = test_device.acq.getdata(58063, "TestMirnovOne")

TestH1WebDataAcq.net = True
