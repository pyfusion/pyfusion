:mod:`core` ---  Core components
================================

:mod:`core.devices`
-------------------

The :mod:`pyfusion.core.devices` module defines the following classes
and exceptions

.. class:: BaseDevice(device_name, database=None)

    Represent a laboratory device with ORM for processed data.

    In general, a customised subclass of BaseDevice will be used.
    
    Usage: BaseDevice(device_name, database=None)

    Arguments:
    
    device_name -- name of device as listed in configuration file, i.e.: [Device:device_name]
    
    Keyword arguments:
    
    database -- database URL for storage of processed data (not the
    data acquisition). If the database argument is not supplied,
    pyfusion will look for a database in the [Device:device_name]
    section in the pyfusion configuration file.

