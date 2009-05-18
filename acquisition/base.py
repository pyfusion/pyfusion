"""Base classes for pyfusion data acquisition."""

from pyfusion.conf.utils import import_setting

class BaseAcquisition:
    """Base class for data acquisition.

    Usage: BaseAcquisition(acq_name, **kwargs)
    
    Arguments:
    acq_name -- name of acquisition as specified in configuration file.

    Keyword arguments can be used to override configuration settings.
    """
    def __init__(self, acq_name):
        self.acq_name = acq_name

    def getdata(self, shot, diag_name):
        """Get the data and return prescribed subclass of BaseData."""
        data_class = import_setting('Diagnostic', diag_name, 'data_class')
        return data_class()

class BaseDataFetcher(object):
    """Takes diagnostic/channel data and returns data object."""
    def fetch(self):
        pass


class DataFetcher(BaseDataFetcher):
    """No difference yet between this an BaseDataFetcher"""
    pass

