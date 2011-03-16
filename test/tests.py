"""General test code for pyfusion.

Test code which doesn't have any other obvious home
(e.g.: data, acquisition, ...) goes here.

"""

import unittest, random, string, ConfigParser, os
import inspect, pkgutil, sys

#from pyfusion.devices.base import Device
#from pyfusion.conf import config
import pyfusion

# Find location of test configuration file
TEST_DATA_PATH = os.path.abspath(os.path.dirname(__file__))
TEST_CONFIG_FILE = os.path.join(TEST_DATA_PATH, "test.cfg")
TEST_NOSQL_CONFIG_FILE = os.path.join(TEST_DATA_PATH, "test_nosql.cfg")

# These values must match those in test.cfg
# TODO: test configuration data should be generated from these values,
#       there is no reason to duplicate the information in a file.
CONFIG_TEST_DEVICE_NAME = "TestDevice"
NONCONFIG_TEST_DEVICE_NAME = "UnlistedTestDevice"
CONFIG_EMPTY_TEST_DEVICE_NAME = "TestEmptyDevice"
TEST_SHOT_NUMBER = 12345
UNLISTED_CONFIG_SECTION_TYPE = "UnlistedType"

class _BasePyfusionTestCase(unittest.TestCase):
    """Simple customisation of TestCase."""
    def __init__(self, *args):
        self.listed_device = CONFIG_TEST_DEVICE_NAME
        self.listed_empty_device = CONFIG_EMPTY_TEST_DEVICE_NAME
        self.unlisted_device = NONCONFIG_TEST_DEVICE_NAME
        self.shot_number = TEST_SHOT_NUMBER
        self.unlisted_config_section_type = UNLISTED_CONFIG_SECTION_TYPE
        import pyfusion
        self.pf = pyfusion
        unittest.TestCase.__init__(self, *args)


    #def setUp(self):
    #    self.pf.config.read(TEST_CONFIG_FILE)


class PfTestBase(object):
    """Base class for generated sql and non-sql test cases."""
    pass

class SQLTestCase(_BasePyfusionTestCase):

    def setUp(self):
        self.pf.conf.utils.clear_config()
        self.pf.conf.utils.read_config(TEST_CONFIG_FILE)
        

class NoSQLTestCase(_BasePyfusionTestCase):

    def setUp(self):
        self.pf.conf.utils.clear_config()
        #try:
        #    self.pf.config.read(self.test_config_file)
        #except AttributeError:
        self.pf.conf.utils.read_config(TEST_NOSQL_CONFIG_FILE)

class ConfigCheck(PfTestBase):
    """Check test config file is as we expect"""

    def testListedDevices(self):
        self.assertTrue(self.pf.config.pf_has_section('Device', self.listed_device))
        self.assertTrue(self.pf.config.pf_has_section('Device',
                                              self.listed_empty_device))

    def testListedDeviceDatabase(self):
        self.assertTrue(self.pf.config.pf_has_option('Device',
                                             self.listed_device, 'database'))

    def testEmptyDevice(self):
        self.assertEqual(len(self.pf.config.pf_options('Device',
                                               self.listed_empty_device)), 0)

    def testUnlistedDevice(self):
        self.assertFalse(self.pf.config.pf_has_section('Device', self.unlisted_device))


class InitImports(PfTestBase):
    """Make sure that imports from __init__ files are present"""

    def testImportgetDevice(self):
        from pyfusion import getDevice

    def testImportgetAcquisition(self):
        from pyfusion import getAcquisition

class ConfigLoaders(PfTestBase):
    """Check pyfusion.read_config and pyfusion.refresh_config"""

    def testReadConfig(self):
        """Check that new config is added but old retained"""
        import pyfusion
        # check that unlisted device is not in config
        self.assertFalse(self.pf.config.pf_has_section('Device', self.unlisted_device))
        self.assertTrue(self.pf.config.pf_has_section('Device', self.listed_device))
        # create a simple file in memory
        import StringIO
        tmp_config = StringIO.StringIO("[Device:%s]\n"
                                       %(self.unlisted_device))
        self.pf.read_config(tmp_config)
        self.assertTrue(self.pf.config.pf_has_section('Device', self.unlisted_device))
        self.assertTrue(self.pf.config.pf_has_section('Device', self.listed_device))
        

    def testClearConfig(self):
        """Check that pyfusion.clear_config works."""
        import pyfusion
        self.assertTrue(self.pf.config.pf_has_section('Device', self.listed_device))
        
        self.pf.conf.utils.clear_config()
        self.assertFalse(self.pf.config.pf_has_section('Device', self.listed_device))
        self.assertEqual(self.pf.config.sections(), [])
        




class SQLConfigCheck(PfTestBase):
    """Test module-wide SQLAlchemy config."""

    def testSQLConfig(self):
        database = self.pf.config.get('global', 'database')
        if database == 'None':
            self.assertEqual(self.pf.USE_ORM, False)
            self.assertFalse(hasattr(self.pf, 'Session'))
            self.assertFalse(hasattr(self.pf, 'metadata'))
            self.assertFalse(hasattr(self.pf, 'orm_engine'))
        else:
            self.assertEqual(self.pf.USE_ORM, True)
            self.assertTrue(hasattr(self.pf, 'Session'))
            self.assertTrue(hasattr(self.pf, 'metadata'))
            self.assertTrue(hasattr(self.pf, 'orm_engine'))
        if self.pf.USE_ORM:
            self.assertEqual(self.pf.orm_engine.url.__str__(), database)

        


###############################################################################
## Get all subclasses of PfTestBase and generate classes to test             ##
## both SQL and non-SQL environments (code now in generated_tests.py)        ##
###############################################################################



def find_subclasses(module, input_class):
    mod_list = [i for i in pkgutil.walk_packages(module.__path__, module.__name__+'.')]
    output = []
    
    for tmp_instance, mod_name, is_pack  in mod_list:
        __import__(mod_name)
        for name, cls in inspect.getmembers(sys.modules[mod_name]):
            if inspect.isclass(cls) and issubclass(cls, input_class) and cls != input_class:
                output.append(cls)
    return output


###############################################################################
###############################################################################
###############################################################################

