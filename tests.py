"""
Test code for pyfusion
"""

import unittest, random, string, ConfigParser

import pyfusion

TEST_CONFIG_FILE = "test.cfg"

CONFIG_TEST_DEVICE_NAME = "TestDevice"
NONCONFIG_TEST_DEVICE_NAME = "UnlistedTestDevice"
CONFIG_EMPTY_TEST_DEVICE_NAME = "TestEmptyDevice"
TEST_SHOT_NUMBER = 12345

class PyfusionTestCase(unittest.TestCase):
    def __init__(self, *args):
        self.listed_device = CONFIG_TEST_DEVICE_NAME
        self.listed_empty_device = CONFIG_EMPTY_TEST_DEVICE_NAME
        self.unlisted_device = NONCONFIG_TEST_DEVICE_NAME
        self.shot_number = TEST_SHOT_NUMBER
        unittest.TestCase.__init__(self, *args)

    def setUp(self):
        pyfusion.config.read(TEST_CONFIG_FILE)
        

class TestConfig(PyfusionTestCase):
    """Check test config file is as we expect"""

    def testListedDevices(self):
        self.assertTrue(pyfusion.config.has_section(self.listed_device))
        self.assertTrue(pyfusion.config.has_section(self.listed_empty_device))

    def testListedDeviceDatabase(self):
        self.assertTrue(
            pyfusion.config.has_option(self.listed_device, 'database')
            )

    def testEmptyDevice(self):
        self.assertEqual(len(pyfusion.config.options(self.listed_empty_device)),
        0)
        
    def testUnlistedDevice(self):
        self.assertFalse(pyfusion.config.has_section(self.unlisted_device))

class TestDevice(PyfusionTestCase):
    """Test for the Device class in pyfusion.core"""
    
    def testUnknownDevice(self):
        """
        If a device is not listed in the config file, it should fail
        if no database is specified
        """
        # invalid database name, but we can let sqlalchemy deal with that
        test_database = "mytestdatabase"
        # Device unlisted in config should raise error if no database specified
        self.assertRaises(ConfigParser.NoSectionError,
        pyfusion.Device, self.unlisted_device)
        # This one should work because we supply a database name...
        test_device_2 = pyfusion.Device(self.unlisted_device, test_database)
        self.assertEqual(test_device_2.database, test_database)
        self.assertEqual(test_device_2.name, self.unlisted_device)
        
    def testKnownDeviceWithListedDatabase(self):
        """If a device is listed in config file, it should use the
        database listed there, if no database is supplied as an argument
        """
        device_config_database = pyfusion.config.get(
            self.listed_device, 'database')        
        test_device = pyfusion.Device(self.listed_device)
        self.assertEqual(test_device.database, device_config_database)

    def testKnownDeviceWithSuppliedDatabase(self):
        """Test that a supplied database is used in place of config"""
        dummy_database = "dummy_database"
        test_device = pyfusion.Device(
            self.listed_device, database=dummy_database)
        self.assertEqual(test_device.database, dummy_database)

    def testKnownEmptyDevice(self):
        """device in config with no specified database should raise
        exception when no database specified
        """
        self.assertRaises(ConfigParser.NoOptionError,
                          pyfusion.Device, self.listed_empty_device)

    def testFailMultipleDeviceWithSameDatabase(self):
        """Should fail if we connect a second device to same
        database (dummy_database).

        If we delete the first instance, we should be able to create another
        device instance with same database.
        """
        from pyfusion.exceptions import DatabaseInUseException
        dummy_database = "dummy_database"
        
        test_device_1 = pyfusion.Device(
            self.listed_device, database=dummy_database)

        self.assertRaises(DatabaseInUseException, pyfusion.Device,
                          self.unlisted_device, database=dummy_database)

        del test_device_1
        test_device_2 = pyfusion.Device(self.unlisted_device,
                                        database=dummy_database)

class TestShot(PyfusionTestCase):
    """Test the Shot class in pyfusion.core"""
    def testShotDevice(self):
        d = pyfusion.Device(self.listed_device)
        s = pyfusion.Shot(d, self.shot_number)
        self.assertEqual(s.device, d)
        self.assertEqual(s.shot_number, self.shot_number)
        
    def testDeviceShotMethodIsShot(self):
        d = pyfusion.Device(self.listed_device)
        s1 = pyfusion.Shot(d, self.shot_number)
        s2 = d.shot(self.shot_number)
        self.assertEqual(s1.shot_number, s2.shot_number)
        self.assertEqual(s1.device, s2.device)
    
if __name__ == "__main__":
    unittest.main()

