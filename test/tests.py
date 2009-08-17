"""General test code for pyfusion.

Test code which doesn't have any other obvious home
(e.g.: data, acquisition, ...) goes here.

"""

import unittest, random, string, ConfigParser, os

from pyfusion.devices.base import Device
#from pyfusion.conf import config
import pyfusion

# Find location of test configuration file
TEST_DATA_PATH = os.path.abspath(os.path.dirname(__file__))
TEST_CONFIG_FILE = os.path.join(TEST_DATA_PATH, "test.cfg")

# These values must match those in test.cfg
# TODO: test configuration data should be generated from these values,
#       there is no reason to duplicate the information in a file.
CONFIG_TEST_DEVICE_NAME = "TestDevice"
CONFIG_TEST_DEVICE_SINGLE_CHANNEL_TIMESERIES = "TestSCTChannel"
CONFIG_TEST_DEVICE_MULTIPLE_CHANNEL_TIMESERIES = "TestMCTChannel"
NONCONFIG_TEST_DEVICE_NAME = "UnlistedTestDevice"
CONFIG_EMPTY_TEST_DEVICE_NAME = "TestEmptyDevice"
TEST_SHOT_NUMBER = 12345
UNLISTED_CONFIG_SECTION_TYPE = "UnlistedType"

class BasePyfusionTestCase(unittest.TestCase):
    """Simple customisation of TestCase."""
    def __init__(self, *args):
        self.listed_device = CONFIG_TEST_DEVICE_NAME
        self.listed_device_single_channel_timeseries = \
                                CONFIG_TEST_DEVICE_SINGLE_CHANNEL_TIMESERIES
        self.listed_device_multiple_channel_timeseries = \
                                CONFIG_TEST_DEVICE_MULTIPLE_CHANNEL_TIMESERIES
        self.listed_empty_device = CONFIG_EMPTY_TEST_DEVICE_NAME
        self.unlisted_device = NONCONFIG_TEST_DEVICE_NAME
        self.shot_number = TEST_SHOT_NUMBER
        self.unlisted_config_section_type = UNLISTED_CONFIG_SECTION_TYPE
        unittest.TestCase.__init__(self, *args)

    def setUp(self):
        pyfusion.config.read(TEST_CONFIG_FILE)
        # read custom user config file to disable/enable certain tests
        pyfusion.config.read(pyfusion.USER_TEST_CONFIG_FILE)
        
        
class TestConfig(BasePyfusionTestCase):
    """Check test config file is as we expect"""

    def testListedDevices(self):
        self.assertTrue(pyfusion.config.pf_has_section('Device', self.listed_device))
        self.assertTrue(pyfusion.config.pf_has_section('Device',
                                              self.listed_empty_device))

    def testListedDeviceDatabase(self):
        self.assertTrue(pyfusion.config.pf_has_option('Device',
                                             self.listed_device, 'database'))

    def testEmptyDevice(self):
        self.assertEqual(len(pyfusion.config.pf_options('Device',
                                               self.listed_empty_device)), 0)
        
    def testUnlistedDevice(self):
        self.assertFalse(pyfusion.config.pf_has_section('Device', self.unlisted_device))


class TestInitImports(BasePyfusionTestCase):
    """Make sure that imports from __init__ files are present"""

    def testImportgetDevice(self):
        from pyfusion import getDevice

    def testImportgetAcquisition(self):
        from pyfusion import getAcquisition

class TestConfigLoaders(BasePyfusionTestCase):
    """Check pyfusion.read_config and pyfusion.refresh_config"""

    def testReadConfig(self):
        """Check that new config is added but old retained"""
        import pyfusion
        # check that unlisted device is not in config
        self.assertFalse(pyfusion.config.pf_has_section('Device', self.unlisted_device))
        self.assertTrue(pyfusion.config.pf_has_section('Device', self.listed_device))
        # create a simple file in memory
        import StringIO
        tmp_config = StringIO.StringIO("[Device:%s]\n"
                                       %(self.unlisted_device))
        pyfusion.read_config(tmp_config)
        self.assertTrue(pyfusion.config.pf_has_section('Device', self.unlisted_device))
        self.assertTrue(pyfusion.config.pf_has_section('Device', self.listed_device))
        

    def testClearConfig(self):
        """Check that pyfusion.clear_config works."""
        import pyfusion
        self.assertTrue(pyfusion.config.pf_has_section('Device', self.listed_device))
        
        pyfusion.conf.utils.clear_config()
        self.assertFalse(pyfusion.config.pf_has_section('Device', self.listed_device))
        self.assertEqual(pyfusion.config.sections(), [])
        
# Run unit tests if this file is called explicitly
if __name__ == "__main__":
    unittest.main()

