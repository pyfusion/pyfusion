"""
Test code for pyfusion
"""

import unittest, random, string, ConfigParser

import pyfusion

TEST_CONFIG_FILE = "test.cfg"


def randstr(string_length):
    return ''.join([random.choice(string.letters) for x in xrange(string_length)]).capitalize()

class TestRandStr(unittest.TestCase):
    def testRandStr(self):
        str_length = random.randint(1,10)
        rand_str = randstr(str_length)
        self.assertEqual(len(rand_str), str_length)

class TestShot(unittest.TestCase):
    """Test for the Shot class in pyfusion.core"""
    def testShotHasCorrectShotNumber(self):
        shot_number = random.randint(1,10)
        shot = pyfusion.Shot(shot_number)
        self.assertEqual(shot.shot, shot_number)

class TestDevice(unittest.TestCase):
    """Test for the Device class in pyfusion.core"""
    def setUp(self):
        """
        Load test config file
        """

        pyfusion.config.read(TEST_CONFIG_FILE)
    
    def testUnknownDevice(self):
        """
        If a device is not listed in the config file, it should fail
        if no database is specified
        """
        device_name = randstr(random.randint(1,10))
        # invalid database name, but we can let sqlalchemy deal with that
        test_database = "mytestdatabase"
        # randomly named device should raise error if no database specified
        self.assertRaises(ConfigParser.NoSectionError,
        pyfusion.Device, device_name)
        # This one should work because we supply a database name...
        test_device_2 = pyfusion.Device(device_name, test_database)
        self.assertEqual(test_device_2.database, test_database)
        self.assertEqual(test_device_2.name, device_name)
        
    def testKnownDevice(self):
        """
        If a device is listed in config file, it should use the
        database listed there, if no database is supplied as an argument
        """
        device_name = "TestDevice"
        device_config_database = pyfusion.config.get(device_name, 'database')
        
        test_device = pyfusion.Device(device_name)
        self.assertEqual(test_device.database, device_config_database)
        self.assertEqual(test_device.name, device_name)

        # now test that a supplied database is used in place of config
        dummy_database = "dummy_database"
        test_device_2 = pyfusion.Device(device_name, database=dummy_database)
        self.assertEqual(test_device_2.database, dummy_database)

        # device in config with no specified database should raise
        # exception when no database specified
        empty_device_name = "TestDeviceEmpty"
        self.assertRaises(ConfigParser.NoOptionError,
        pyfusion.Device, empty_device_name)

        # Should fail if we connect a second device to same database (dummy_database)
        from pyfusion.exceptions import DatabaseInUseException
        second_device_name = randstr(random.randint(1,10))
        self.assertRaises(DatabaseInUseException, pyfusion.Device, second_device_name, database=dummy_database)
        # if we delete the original test_device_2, then we should now
        # be able to create a new device to the same database
        del test_device_2
        test_device_3 = pyfusion.Device(second_device_name, database=dummy_database)

if __name__ == "__main__":
    unittest.main()

