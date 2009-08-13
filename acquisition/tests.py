"""Test code for data acquisition."""

from pyfusion.test.tests import BasePyfusionTestCase

# Add new acquisition modules here for basic module structure test
acquisition_modules = ['FakeData', 'MDSPlus']

class TestAcquisitionArgs(BasePyfusionTestCase):
    """Make sure we get the same result if we use config or kwargs"""

    def testAcqArgs(self):
        from pyfusion.acquisition.FakeData.acq import FakeDataAcquisition
        acq_from_config = FakeDataAcquisition('test_fakedata')
        # create a FakeDataAcquisition instance with keyword args
        from pyfusion import config
        config_option_list = config.pf_options('Acquisition', 'test_fakedata')
        

class TestGetAcquisition(BasePyfusionTestCase):
    """test getAcquisition function."""

    def test_get_acquistion(self):
        from pyfusion.acquisition.utils import getAcquisition
        test_acq_1 = getAcquisition('test_fakedata')
        from pyfusion.acquisition.FakeData.acq import FakeDataAcquisition
        test_acq_2 = FakeDataAcquisition('test_fakedata')
        self.assertEqual(test_acq_1.__class__, test_acq_2.__class__)
        self.assertEqual(test_acq_1.__dict__, test_acq_2.__dict__)


class TestAcquisitionModules(BasePyfusionTestCase):
    """Check for existence of acquisition modules."""

    def check_module(self, module_name):
        from pyfusion.conf.utils import import_from_str
        import_from_str('.'.join(['pyfusion.acquisition', module_name]))
        import_from_str('.'.join(['pyfusion.acquisition', module_name, 'acq']))
        import_from_str('.'.join(['pyfusion.acquisition', module_name, 'fetch']))

    def testModules(self):
        for module_name in acquisition_modules:
            self.check_module(module_name)

