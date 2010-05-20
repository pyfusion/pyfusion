"""Test cases for pyfusion.devices."""

from ConfigParser import NoSectionError, NoOptionError

from pyfusion import config
from pyfusion.test import BasePyfusionTestCase
from pyfusion.devices.base import Device

class TestDevice(BasePyfusionTestCase):
    """Test for the Device class in pyfusion.devices.base."""
    
    def testDeviceAcquisition(self):
        """Test that we can use an acquisition specified in config file."""
        
        test_device = Device(self.listed_device)
        # check that acquisition system is connected
        acq_name = config.pf_get('Device',
                                 self.listed_device,
                                 'acq_name')
        from pyfusion.acquisition import get_acq_from_config
        acq_class = get_acq_from_config(acq_name)
        from pyfusion.acquisition.FakeData.acq import FakeDataAcquisition
        self.assertEqual(acq_class, FakeDataAcquisition)
        
    def test_device_keyword_args(self):
        """ Check that Device correctly processes config/kwarg options."""

        test_kwargs = {'database': 'dummy_database',
                       'other_var': 'other_val'}
        test_device = Device('TestDevice', **test_kwargs)

        self.assertEqual(test_device.database, test_kwargs['database'])
        self.assertEqual(test_device.other_var, test_kwargs['other_var'])

        # make sure that config vars not in test_kwargs are included in kwargs
        for config_var in config.pf_options('Device', 'TestDevice'):
            if not config_var in test_kwargs.keys():
                self.assertEqual(test_device.__dict__[config_var],
                                 config.pf_get('Device',
                                               'TestDevice', config_var))
        
    def test_device_no_config(self):
        """Check Device works with only keyword args (no reference to config)"""
        test_kwargs = {'database': 'dummy_database',
                       'other_var': 'other_val'}
        test_device = Device('some_device_not_in_config_file', **test_kwargs)

        
    def testORM(self):
        """Check that creating a new device is reflected in the database"""
        import pyfusion
        # give test device a name
        test_device = Device(self.listed_device)
        session = pyfusion.Session()
        session.add(test_device)
        session.commit()
        # query by name and make sure we can retrieve device
        from_query = session.query(Device).filter(Device.name == self.listed_device).one()
        self.assertEqual(test_device, from_query)


class TestEmptyDevice(BasePyfusionTestCase):
    """Make sure things don't fail for device with no config settings."""
    def test_empty_device(self):
        test_device = Device(self.listed_empty_device)
        
class TestGetDevice(BasePyfusionTestCase):
    """test getDevice."""

    def test_getDevice(self):
        from pyfusion.devices.base import getDevice
        test_device_1 = getDevice(self.listed_device)
        test_device_2 = Device(self.listed_device)
        self.assertEqual(test_device_1.__class__, test_device_2.__class__)

