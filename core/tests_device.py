"""Test cases for pyfusion.core.devices."""

from ConfigParser import NoSectionError, NoOptionError

import pyfusion.conf
from pyfusion.test import BasePyfusionTestCase
from pyfusion.core.devices import Device

class TestDevice(BasePyfusionTestCase):
    """Test for the Device class in pyfusion.core"""
    
    def testUnknownDevice(self):
        """
        If a device is not listed in the config file, it should fail
        if no database is specified
        """
        # invalid database name, but we can let sqlalchemy deal with that
        test_database = "mytestdatabase"
        # Device unlisted in config should raise error if no database specified
        self.assertRaises(NoSectionError, Device, self.unlisted_device)
        # This one should work because we supply a database name...
        test_device_2 = Device(self.unlisted_device, test_database)
        self.assertEqual(test_device_2.database, test_database)
        self.assertEqual(test_device_2.name, self.unlisted_device)
        
    def testKnownDeviceWithListedDatabase(self):
        """If a device is listed in config file, it should use the
        database listed there, if no database is supplied as an argument
        """
        device_config_database = pyfusion.conf.config.pf_get('Device',
            self.listed_device, 'database')        
        test_device = Device(self.listed_device)
        self.assertEqual(test_device.database, device_config_database)

    def testKnownDeviceWithSuppliedDatabase(self):
        """Test that a supplied database is used in place of config"""
        dummy_database = "dummy_database"
        test_device = Device(
            self.listed_device, database=dummy_database)
        self.assertEqual(test_device.database, dummy_database)

    def testKnownEmptyDevice(self):
        """device in config with no specified database should raise
        exception when no database specified
        """
        self.assertRaises(NoOptionError,Device, self.listed_empty_device)

