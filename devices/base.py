"""Basic device class"""

from pyfusion.conf.utils import kwarg_config_handler, import_from_str, get_config_as_dict
import pyfusion

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
    def __init__(self, config_name=None, **kwargs):
        if config_name != None:
            self.__dict__.update(get_config_as_dict('Device', config_name))
        self.__dict__.update(kwargs)

        #### attach acquisition
        if hasattr(self, 'acq_name'):
            acq_class_str = pyfusion.config.pf_get('Acquisition',
                                          self.acq_name, 'acq_class')
            self.acquisition = import_from_str(acq_class_str)(self.acq_name)
            # shortcut
            self.acq = self.acquisition
        else:
            pyfusion.logging.warning(
                "No acquisition class specified for device")

class Device(BaseDevice):
    """At present, there is no difference between Device and BaseDevice."""
    pass


def getDevice(device_name):
    """Find and instantiate Device (sub)class from config."""
    print pyfusion.config.sections()
    dev_class_str = pyfusion.config.pf_get('Device', device_name, 'dev_class')
    return import_from_str(dev_class_str)(device_name)
