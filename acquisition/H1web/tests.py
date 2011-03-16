""" Test code for H1 HTTP data acces."""
import os
from pyfusion.test.tests import PfTestBase
import pyfusion as pf

TEST_DATA_PATH = os.path.abspath(os.path.dirname(__file__))
TEST_CONFIG_FILE = os.path.join(TEST_DATA_PATH, "test.cfg")

class H1WebTestCase(PfTestBase):
    def __init__(self, *args):
        self.test_config_file = TEST_CONFIG_FILE
        super(H1WebTestCase, self).__init__(*args)


class TestH1WebDataAcq(H1WebTestCase):

    def test_acq(self):
        test_device = pf.getDevice("TestH1WebDevice")
        test_data = test_device.acq.getdata(58063, "TestMirnovOne")

TestH1WebDataAcq.net = True
