"""Exceptions for the pyfusion config parser."""

class DisallowedSectionType(Exception):
    def __init__(self, section_name):
        self.section_name = section_name
    def __str__(self):
        return repr(self.section_name)

class ConfigSectionSyntaxError(Exception):
    def __init__(self, section_name):
        self.section_name = section_name
    def __str__(self):
        return repr(self.section_name)

