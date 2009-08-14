"""Base classes for pyfusion data acquisition."""

from pyfusion.conf.utils import import_setting, kwarg_config_handler, get_config_as_dict

class BaseAcquisition:
    """Base class for data acquisition.

    Usage: BaseAcquisition(acq_name, **kwargs)
    
    Arguments:
    acq_name -- name of acquisition as specified in configuration file.

    Keyword arguments can be used to override configuration settings.
    """
    def __init__(self, config_name=None, **kwargs):
        if config_name != None:
            self.__dict__.update(get_config_as_dict('Acquisition', config_name))
        self.__dict__.update(kwargs)

    def getdata(self, shot, diag_name, **kwargs):
        """Get the data and return prescribed subclass of BaseData."""
        fetcher_class = import_setting('Diagnostic', diag_name, 'data_fetcher')
        conf_kwargs = kwarg_config_handler('Diagnostic', diag_name, **kwargs)
        return fetcher_class(**conf_kwargs).fetch()

class BaseDataFetcher(object):
    """Takes diagnostic/channel data and returns data object."""
    def __init__(self, *args, **kwargs):
        pass
    def fetch(self):
        pass


class DataFetcher(BaseDataFetcher):
    """No difference yet between this an BaseDataFetcher"""
    pass

