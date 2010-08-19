"""Base classes for pyfusion data acquisition."""
from numpy.testing import assert_array_almost_equal
from pyfusion.conf.utils import import_setting, kwarg_config_handler, get_config_as_dict, import_from_str
from pyfusion.data.timeseries import Signal, Timebase, TimeseriesData
from pyfusion.data.base import ChannelList

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
        from pyfusion import config
        # if there is a data_fetcher arg, use that, otherwise get from config
        if kwargs.has_key('data_fetcher'):
            fetcher_class_name = kwargs['data_fetcher']
        else:
            fetcher_class_name = config.pf_get('Diagnostic',
                                               config_name,
                                               'data_fetcher')
        fetcher_class = import_from_str(fetcher_class_name)
        return fetcher_class(self, shot, config_name=config_name, **kwargs).fetch()
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
        """
        
class BaseDataFetcher(object):
    """Takes diagnostic/channel data and returns data object."""
    def __init__(self, acq, shot, config_name=None,**kwargs):
        self.shot = shot
        self.acq = acq
        if config_name != None:
            self.__dict__.update(get_config_as_dict('Diagnostic', config_name))
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
        data.meta.update({'shot':self.shot})
        ## Coords shouldn't be fetched for BaseData (they are required
        ## for TimeSeries)
        #data.coords.load_from_config(**self.__dict__)
        self.pulldown()
        return data

class DataFetcher(BaseDataFetcher):
    """No difference yet between this an BaseDataFetcher"""
    def fetch(self):
        pass

class MultiChannelFetcher(BaseDataFetcher):
    """... for timeseries..."""
    def ordered_channel_names(self):
        channel_list = []
        for k in self.__dict__.keys():
            if k.startswith('channel_'):
                channel_list.append([int(k.split('channel_')[1]), self.__dict__[k]])
        channel_list.sort()
        return [i[1] for i in channel_list]
    
    def fetch(self):
        ## initially, assume only single channel signals
        ordered_channel_names = self.ordered_channel_names()
        data_list = []
        channels = ChannelList()
        timebase = None
        meta_dict={}
        for chan in ordered_channel_names:
            fetcher_class = import_setting('Diagnostic', chan, 'data_fetcher')
            tmp_data = fetcher_class(self.acq, self.shot, config_name=chan).fetch()
            channels.append(tmp_data.channels)
            meta_dict.update(tmp_data.meta)
            if timebase == None:
                timebase = tmp_data.timebase
                data_list.append(tmp_data.signal)
            else:
                try:
                    assert_array_almost_equal(timebase, tmp_data.timebase)
                    data_list.append(tmp_data.signal)
                except:
                    raise
        signal=Signal(data_list)
        output_data = TimeseriesData(signal=signal, timebase=timebase,
                                     channels=channels)
        #output_data.meta.update({'shot':self.shot})
        output_data.meta.update(meta_dict)
        return output_data

