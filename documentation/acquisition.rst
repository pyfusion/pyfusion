Data Acquisition
================

Data acquisition is handled by a device-specific subclass of
pyfusion.acquisition.base.BaseAcquisition. In general, the acquisition
class will be accessed through a configured device class::

  my_device = Device('my_configured_device')
  my_data = my_device.acquisition.getdata(12345, 'my_diagnostic')

In this example, when Device is instantiated pyfusion will look in the
configuration file section [Device:my_configured_device] and read the
acquisition setting, for example::

  [Device:my_configured_device]
  acquisition = my_test_acq


  [Acquisition:my_test_acq]
  acq_class = pyfusion.acquisition.fakedata.FakeDataAcquistion
  example_param_1 = example_setting_1  
  example_param_2 = example_setting_2  


In this case, FakeDataAcquistion is instantiated with parameters
example_param_1, example_param_2, and is attached to the my_device at
my_device.acquisition.


The acquisition class allows for a persistent connection to a data
acquisition system. To access data, we call the getdata method with 2
arguments [#getdataargs]_, the shot number and the name of a
configured diagnostic. An example diagnostic configuration here might
be::

  [Diagnostic:my_diagnostic]
  data_class = pyfusion.data.timeseries.SCTData
  some_parameter = some_value

The data_class parameter sets the location of the class (subclass of
pyfusion.data.base.BaseData) to be returned by the getdata
method; here, SCTData is a single-channel timeseries data class. Other settings in the configuration file are used as keyword
parameters to getdata, allowing easy manipulation of custom acquisition classes.


.. rubric:: Footnotes


.. [#getdataargs] Two non-keyword arguments - additional keyword arguments which override configuration settings are allowed.

