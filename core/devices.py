"""Basic device class"""

import pyfusion.conf

class BaseDevice():
    """Represent a laboratory device with ORM for processed data.


    If database argument is not supplied, pyfusion will look for a
    database in the [device_name] section in the pyfusion configuration
    file.
    """
    def __init__(self, device_name, database=None):
        self.name = device_name
        if database != None:
            self.database = database
        else:
            from ConfigParser import NoSectionError, NoOptionError
            try:
                self.database = pyfusion.conf.config.pf_get('Device', self.name, 'database')
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

    def shot(self, shot_number):
        return Shot(self, shot_number)


class Device(BaseDevice):
    pass


