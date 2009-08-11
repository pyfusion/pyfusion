"""Test code for data acquisition."""

from pyfusion.test.tests import BasePyfusionTestCase

acquisition_modules = ['FakeData', 'MDSPlus']

class TestGetAcquisition(BasePyfusionTestCase):
    """test getAcquisition function."""

    def test_get_acquistion(self):
        from pyfusion.acquisition.utils import getAcquisition
        test_acq_1 = getAcquisition('test_fakedata')
        from pyfusion.acquisition.FakeData.acq import FakeDataAcquisition
        test_acq_2 = FakeDataAcquisition('test_fakedata')
        self.assertEqual(test_acq_1.__class__, test_acq_2.__class__)

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

