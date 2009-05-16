.. _config-files:

Pyfusion configuration files
""""""""""""""""""""""""""""

Any custom configuration should be in a file "pyfusion.cfg" in a
directory ".pyfusion" in your home directory.

The sections in the configuration file have the syntax
[Component:name], where Component is one of: Acquisition, Device,
Diagnostic. When instantiating a class, such as Device, Acquisition,
Diagnostic, etc. which looks in the configuration file for settings,
individual settings can be overridden using the corresponding keyword
arguments. For example, ``Device('my_device')`` will use settings in
the ``[Device:my_device]`` configuration section, and
``Device('my_device', database='sqlite://')`` will override the
database configuration setting with ``sqlite://`` (a temporary in-memory database).  


[Device:name]
-------------

database
~~~~~~~~

Location of database in the `SQLAlchemy database URL syntax`_. 

e.g.::
   
   no example yet

.. _SQLAlchemy database URL syntax: http://www.sqlalchemy.org/docs/04/dbengine.html#dbengine_establishing

acquisition
~~~~~~~~~~~

Name of Acquisition config setting ( [Acquisition:name] ) to be used for this device.

e.g.::

   acquisition = test_fakedata

[Acquisition:name]
------------------

acq_class
~~~~~~~~~

Location of acquisition class (subclass of pyfusion.acquisition.base.BaseAcquisition). 

e.g.::
  
   acq_class = pyfusion.acquisition.fakedata.FakeDataAcquisition

[Diagnostic:name]
-----------------


data_class
~~~~~~~~~~

Location of class (subclass of pyfusion.data.base.BaseData) to represent the diagnostic.
