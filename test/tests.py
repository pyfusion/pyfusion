"""Test code for pyfusion."""

import unittest, random, string, ConfigParser, os

from pyfusion.core.devices import Device
import pyfusion.conf

TEST_DATA_PATH = os.path.abspath(os.path.dirname(__file__))
TEST_CONFIG_FILE = os.path.join(TEST_DATA_PATH, "test.cfg")

CONFIG_TEST_DEVICE_NAME = "TestDevice"
CONFIG_TEST_CHANNEL = "TestChannel"
NONCONFIG_TEST_DEVICE_NAME = "UnlistedTestDevice"
CONFIG_EMPTY_TEST_DEVICE_NAME = "TestEmptyDevice"
TEST_SHOT_NUMBER = 12345

class BasePyfusionTestCase(unittest.TestCase):
    """Simple customisation of TestCase."""
    def __init__(self, *args):
        self.listed_device = CONFIG_TEST_DEVICE_NAME
        self.listed_config_channel = CONFIG_TEST_CHANNEL
        self.listed_empty_device = CONFIG_EMPTY_TEST_DEVICE_NAME
        self.unlisted_device = NONCONFIG_TEST_DEVICE_NAME
        self.shot_number = TEST_SHOT_NUMBER
        unittest.TestCase.__init__(self, *args)

    def setUp(self):
        pyfusion.conf.config.read(TEST_CONFIG_FILE)

class TestConfig(BasePyfusionTestCase):
    """Check test config file is as we expect"""

    def testListedDevices(self):
        self.assertTrue(pyfusion.conf.config.has_section(self.listed_device))
        self.assertTrue(pyfusion.conf.config.has_section(self.listed_empty_device))

    def testListedDeviceDatabase(self):
        self.assertTrue(
            pyfusion.conf.config.has_option(self.listed_device, 'database')
            )

    def testEmptyDevice(self):
        self.assertEqual(len(pyfusion.conf.config.options(self.listed_empty_device)),
        0)
        
    def testUnlistedDevice(self):
        self.assertFalse(pyfusion.conf.config.has_section(self.unlisted_device))


class TestInitImports(BasePyfusionTestCase):
    """Make sure that imports from __init__ files are present"""

    def testImportDevice(self):
        from pyfusion import Device


if __name__ == "__main__":
    unittest.main()

