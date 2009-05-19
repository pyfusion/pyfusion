.. _config-files:

Pyfusion configuration files
""""""""""""""""""""""""""""

Any custom configuration should be in a file "pyfusion.cfg" in a
directory ".pyfusion" in your home directory.

The sections in the configuration (except for [variabletypes]) file have the syntax
[Component:name], where Component is one of: Acquisition, Device,
Diagnostic. When instantiating a class, such as Device, Acquisition,
Diagnostic, etc. which looks in the configuration file for settings,
individual settings can be overridden using the corresponding keyword
arguments. For example, ``Device('my_device')`` will use settings in
the ``[Device:my_device]`` configuration section, and
``Device('my_device', database='sqlite://')`` will override the
database configuration setting with ``sqlite://`` (a temporary in-memory database).  

[variabletypes]
---------------
variabletypes is a section for defining the types (integer, float,
boolean) of variables specified throughout the configuration file. By
default, variables are assumed to be strings (text) - only variables
of type integer, float or boolean should be listed here.

For example, if three variables (arguments) for the Diagnostic class
are n_samples (integer), sample_freq (float) and normalise (boolean)
the syntax is:: 

	Diagnostic__n_samples = int
	Diagnostic__sample_freq = float
	Diagnostic__normalise = bool

Note the double underscore (__) separating the class type and the
variable name.

[Device:name]
-------------

database
~~~~~~~~

Location of database in the `SQLAlchemy database URL syntax`_. 

e.g.::
   
   no example yet

.. _SQLAlchemy database URL syntax: http://www.sqlalchemy.org/docs/04/dbengine.html#dbengine_establishing

acq_name
~~~~~~~~

Name of Acquisition config setting ( [Acquisition:acq_name] ) to be used for this device.

e.g.::

   acq_name = test_fakedata

dev_class
~~~~~~~~~

Name of device class (subclass of pyfusion.core.devices.BaseDevice)
to be used for this device. This is called when using the convenience
function pyfusion.getDevice. For example, if the configuration file
contains::

	[Device:my_tjii_device]
	dev_class = pyfusion.devices.TJII

then using::

     import pyfusion
     my_dev = pyfusion.getDevice('my_tjii_device')

``my_dev`` will be an instance of pyfusion.devices.TJII

[Acquisition:name]
------------------

acq_class
~~~~~~~~~

Location of acquisition class (subclass of pyfusion.acquisition.base.BaseAcquisition). 

e.g.::
  
   acq_class = pyfusion.acquisition.fakedata.FakeDataAcquisition

[Diagnostic:name]
-----------------


data_fetcher
~~~~~~~~~~~~

Location of class (subclass of pyfusion.acquisition.base.BaseDataFetcher) to fetch
the data for the diagnostic.
