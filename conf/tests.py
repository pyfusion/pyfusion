"""Tests for pyfusion configuration files and parser."""

from pyfusion.test.tests import BasePyfusionTestCase

class TestConfigFileSectionNames(BasePyfusionTestCase):
    """Check section name conformity in configuration files.

    Allowed config section names must correspond to those
    described in the documentation (which should be the same
    list as pyfusion.conf.allowed_section_types).

    """
    def testSectionNames(self):
        from pyfusion.conf import allowed_section_types, config
        from pyfusion.conf.exceptions import DisallowedSectionType, ConfigSectionSyntaxError
        config.check_section_types(allowed_section_types)
        self.assertFalse(
            self.unlisted_config_section_type in allowed_section_types)
        config.add_section(
            "%s:%s" %(self.unlisted_config_section_type, 'dummy'))
        self.assertRaises(DisallowedSectionType,
                          config.check_section_types,
                          allowed_section_types)
        config.check_section_syntax()
        config.add_section("xxx")
        self.assertRaises(
            ConfigSectionSyntaxError, config.check_section_syntax)

class TestPyfusionConfigParser(BasePyfusionTestCase):
    """Test pyfusion customised config file parser."""

    def testBaseClass(self):
        from pyfusion.conf import PyfusionConfigParser
        from ConfigParser import ConfigParser
        self.assertTrue(ConfigParser in PyfusionConfigParser.__bases__)
        
    def test_pf_has_section(self):
        from pyfusion.conf import config
        self.assertTrue(config.pf_has_section('Device', self.listed_device))
        self.assertFalse(config.pf_has_section('Device', self.unlisted_device))


