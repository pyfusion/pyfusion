"""Basic device class"""

import pyfusion.conf

class BaseDevice:
    """Represent a laboratory device with ORM for processed data.

    In general, a customised subclass of BaseDevice will be used.
    
    Usage: BaseDevice(device_name, database=None)

    Arguments:
    device_name -- name of device as listed in configuration file, 
       i.e.: [Device:device_name]
    
    Keyword arguments:
    database -- database URL for storage of processed data (not the
       data acquisition). If the database argument is not supplied,
       pyfusion will look for a database in the [Device:device_name]
       section in the pyfusion configuration file.

    """
    def __init__(self, device_name, database=None):
        self.name = device_name
        if database != None:
            self.database = database
        else:
            from ConfigParser import NoSectionError, NoOptionError
            try:
                self.database = pyfusion.conf.config.pf_get(
                    'Device', self.name, 'database')
            except NoSectionError:
                print """
                Device: No database specified and device
                section '[%s]' not found in configuration file.
                Raising NoSectionError...""" %(self.name)
                raise
            except NoOptionError:
                print """
                Device: No database specified and device
                section '[%s]' in configuration file does not
                contain database definition.
                Raising NoOptionError...""" %(self.name)
                raise


class Device(BaseDevice):
    """At present, there is no difference between Device and BaseDevice."""
    pass


