:mod:`devices` ---  Devices
================================

:mod:`devices.base`
-------------------

The :mod:`pyfusion.devices.base` module defines the following classes
and exceptions

.. class:: BaseDevice(device_name, \*\*kwargs)

    Represent a laboratory device with ORM for processed data.

    In general, a customised subclass of BaseDevice will be used.
    
    Usage: BaseDevice(device_name, \*\*kwargs)

    Arguments:
    
    device_name -- name of device as listed in configuration file, i.e.: [Device:device_name]
    
    Keyword arguments:
    
    Any configuration setting can be overridden by supplying a keyword
    argument with the setting name, e.g.: ``BaseDevice(device_name, database='sqlite://')``


    see also: getDevice()