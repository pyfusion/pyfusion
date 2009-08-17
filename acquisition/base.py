"""Base classes for pyfusion data acquisition."""

from pyfusion.conf.utils import import_setting, kwarg_config_handler, get_config_as_dict, import_from_str

class BaseAcquisition(object):
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

    def getdata(self, shot, config_name=None, **kwargs):
        """Get the data and return prescribed subclass of BaseData.
        
        usage: getdata(shot, config_name=None, **kwargs)
        shot is required (first argument)
        optional second argument config_name to read in from config
        file

        'fetcher_class' must be either in referenced config file or in
        keyword args
        """

        fetcher_args = {}
        if config_name != None:
            fetcher_args.update(get_config_as_dict('Diagnostic', config_name))
        fetcher_args.update(kwargs)
        
        try:
            fetcher_class_str = fetcher_args.pop('data_fetcher')
            fetcher_class = import_from_str(fetcher_class_str)
        except KeyError:
            print "getdata requires 'fetcher_class' defined in either config or keyword arguments"
            raise
        return fetcher_class(shot, **fetcher_args).fetch()

class BaseDataFetcher(object):
    """Takes diagnostic/channel data and returns data object."""
    def __init__(self, shot, **kwargs):
        self.shot = shot
        self.__dict__.update(kwargs)
    def setup(self):
        pass
    def do_fetch(self):
        pass
    def pulldown(self):
        pass
    def fetch(self):
        self.setup()
        data = self.do_fetch()
        self.pulldown()
        return data

class DataFetcher(BaseDataFetcher):
    """No difference yet between this an BaseDataFetcher"""
    pass

