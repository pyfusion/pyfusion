from ConfigParser import ConfigParser

from pyfusion.conf.exceptions import DisallowedSectionType, ConfigSectionSyntaxError

allowed_section_types = ['Device']

class PyfusionConfigParser(ConfigParser):
    """Customised parser to facilitate [Type:Name] config sections."""

    def pf_has_section(self, sectiontype, sectionname):
        return self.has_section("%s:%s"%(sectiontype, sectionname))

    def pf_get(self, sectiontype, sectionname, option):
        return self.get("%s:%s"%(sectiontype, sectionname), option)

    def pf_options(self, sectiontype, sectionname):
        return self.options("%s:%s"%(sectiontype, sectionname))

    def pf_has_option(self, sectiontype, sectionname, option):
        return self.has_option("%s:%s"%(sectiontype, sectionname), option)

    def check_section_syntax(self):
        for section in self.sections():
            split_name = section.split(':')
            if not len(split_name)==2:
                raise ConfigSectionSyntaxError, section
            if not (len(split_name[0])>0 and len(split_name[1])>0):
                raise ConfigSectionSyntaxError, section

    def check_section_types(self, type_list):
        self.check_section_syntax()
        for section in self.sections():
            section_name = section.split(':')[0]
            if not section_name in type_list:
                raise DisallowedSectionType, section_name

config = PyfusionConfigParser()

