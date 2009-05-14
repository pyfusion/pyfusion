.. _config-files:

Pyfusion configuration files
""""""""""""""""""""""""""""

Any custom configuration should be in a file "pyfusion.cfg" in a
directory ".pyfusion" in your home directory.

The sections in the configuration file have the syntax
[Component:name], where Component is one of: Acquisition, Channel, Device.


[Device:device_name]
--------------------

database
~~~~~~~~

Location of database in the `SQLAlchemy database URL syntax`_. 

.. _SQLAlchemy database URL syntax: http://www.sqlalchemy.org/docs/04/dbengine.html#dbengine_establishing

acquisition
~~~~~~~~~~~

Name of Acquisition config setting ( [Acquisition:name] ) to be used for this device.

