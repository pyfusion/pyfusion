"""Basic device class"""

from pyfusion.conf.utils import kwarg_config_handler, import_from_str
from pyfusion.conf import config
from pyfusion import logging

class BaseDevice:
    """Represent a laboratory device with ORM for processed data.

    In general, a customised subclass of BaseDevice will be used.
    
    Usage: BaseDevice(device_name, **kwargs)

    Arguments:
    device_name -- name of device as listed in configuration file, 
       i.e.: [Device:device_name]
    
    Keyword arguments:
    Any setting in the [Device:device_name] section of the
    configuration file can be overridden by supplying a keyword
    arguement to here, e.g.: BaseDevice(device_name, database='sqlite://')

    """
    def __init__(self, device_name, **kwargs):
        self.name = device_name
        kwargs = kwarg_config_handler('Device', self.name, **kwargs)
        self.__dict__.update(kwargs)
        #### attach acquisition
        if hasattr(self, 'acq_name'):
            acq_class_str = config.pf_get('Acquisition',
                                          self.acq_name, 'acq_class')
            self.acquisition = import_from_str(acq_class_str)(self.acq_name)
        else:
            logging.warning(
                "No acquisition class specified for device %s" %self.name)

class Device(BaseDevice):
    """At present, there is no difference between Device and BaseDevice."""
    pass


