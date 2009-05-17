"""Test cases for pyfusion.core.devices."""

from ConfigParser import NoSectionError, NoOptionError

import pyfusion.conf
from pyfusion.test import BasePyfusionTestCase
from pyfusion.core.devices import Device

class TestDevice(BasePyfusionTestCase):
    """Test for the Device class in pyfusion.core."""
    
        

    def testDeviceAcquisition(self):
        """Test that we can use an acquisition specified in config file."""
        
        test_device = Device(self.listed_device)
        # check that acquisition system is connected
        acq_name = pyfusion.conf.config.pf_get('Device',
                                              self.listed_device,
                                              'acq_name')
        from pyfusion.acquisition import get_acq_from_config
        acq_class = get_acq_from_config(acq_name)
        from pyfusion.acquisition.fakedata import FakeDataAcquisition
        self.assertEqual(acq_class, FakeDataAcquisition)
        
    def test_device_keyword_args(self):
        """ Check that Device correctly processes config/kwarg options."""
        from pyfusion.conf import config

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
        
