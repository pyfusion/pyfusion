import pyfusion

class Device():
    """Represent a laboratory device with ORM for processed data.

    If a section [device_name] exists in the pyfusion configuration
    file and the database argument is not used, then a database
    specified by the configuration file will be used. Otherwise, a
    database must be specified.

    The same database cannot be used for multiple instances of Device.
    """
    def __init__(self, device_name, database=None):
        self.name = device_name
        if database != None:
            self.database = database
        else:
            from ConfigParser import NoSectionError, NoOptionError
            try:
                self.database = pyfusion.config.get(self.name, 'database')
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
        if self.database in pyfusion._connected_databases:
            from pyfusion.exceptions import DatabaseInUseException
            # even though database is in use, we add it again to the
            # list. It is removed again straight away by __del__() -
            # adding it here simplified the __del__ code.
            pyfusion._connected_databases.append(self.database)
            raise DatabaseInUseException("Database '%s' already being used."
                             %(self.database))
        else:
            pyfusion._connected_databases.append(self.database)

    def __del__(self):
        # note - should add ref to parent __del__ when we specify parent
        try:
            remove_db = self.database
        except AttributeError:
            # there are cases when database is not defined, i.e. we
            # are exiting due to an exception raised in __init__()
            remove_db = None
        if remove_db != None:
            pyfusion._connected_databases.remove(remove_db)
            
