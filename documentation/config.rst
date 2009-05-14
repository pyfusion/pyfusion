.. _config-files:

Pyfusion configuration files
""""""""""""""""""""""""""""

Any custom configuration should be in a file "pyfusion.cfg" in a
directory ".pyfusion" in your home directory.

The sections in the configuration file have the syntax
[Component:name], where Component is one of: Acquisition, Device, Diagnostic.


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
