"""Test cases for pyfusion.core.devices."""

from ConfigParser import NoSectionError, NoOptionError

import pyfusion.conf
from pyfusion.test import BasePyfusionTestCase
from pyfusion.core.devices import Device

class TestDevice(BasePyfusionTestCase):
    """Test for the Device class in pyfusion.core."""
    
    def testUnknownDevice(self):
        """Try creating a device without database argument.

        If a device is not listed in the config file, it should fail
        in the case where no database is specified
        
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
        """Test case where database argument is read from config file.
        
        If a device is listed in config file, it should use the
        database listed there, if no database is supplied as an argument

        """
        device_config_database = pyfusion.conf.config.pf_get('Device',
            self.listed_device, 'database')        
        test_device = Device(self.listed_device)
        self.assertEqual(test_device.database, device_config_database)

    def testKnownDeviceWithSuppliedDatabase(self):
        """Test that supplied database argument is used in place of config."""
        dummy_database = "dummy_database"
        test_device = Device(
            self.listed_device, database=dummy_database)
        self.assertEqual(test_device.database, dummy_database)

    def testKnownEmptyDevice(self):
        """Check that an error is raised if no database argument is available.

        A device in config with no specified database should raise
        exception when no database specified.
        """
        self.assertRaises(NoOptionError,Device, self.listed_empty_device)

    def testDeviceAcquisition(self):
        """Test that we can use an acquisition specified in config file."""
        test_device = Device(self.listed_device)
        # check that acquisition system is connected
        acq_name = pyfusion.conf.config.pf_get('Device',
                                              self.listed_device,
                                              'acquisition')
        from pyfusion.acquisition import get_acq_from_config
        acq_class = get_acq_from_config(acq_name)
        from pyfusion.acquisition.fakedata import FakeDataAcquisition
        self.assertEqual(acq_class, FakeDataAcquisition)
        
