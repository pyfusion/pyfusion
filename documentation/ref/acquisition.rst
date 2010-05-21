Data Acquisition
================

Data acquisition in pyfusion is handled by two classes, an Acquisition
class which allows persistent connection to a data acquisition system
(e.g. MDSPlus), and a DataFetcher which is used by the Acquisition
class to fetch data from the data acquisition system and return a Data
instance. 


The acquisition class should be a device-specific subclass of
pyfusion.acquisition.base.BaseAcquisition. In general, the acquisition
class will be accessed through a configured device class::

  my_device = Device('my_configured_device')
  my_data = my_device.acquisition.getdata(12345, 'my_diagnostic')

Here, my_device is an instance of Device, my_device.acquisition is an
instance of an Acquisition class, and getdata is a method of the
Acquisition class which returns a Data instance. 

In this example, when Device is instantiated pyfusion will look in the
configuration file section [Device:my_configured_device] and read the
acquisition setting (acq_name), for example::

  [Device:my_configured_device]
  acq_name = my_test_acq


  [Acquisition:my_test_acq]
  acq_class = pyfusion.acquisition.fakedata.FakeDataAcquistion
  example_param_1 = example_setting_1  
  example_param_2 = example_setting_2  


In this case, FakeDataAcquistion is instantiated with parameters
example_param_1, example_param_2, and is attached to the my_device at
my_device.acquisition. Note that for any class, such as Device here, which
is instantiated with configuration settings, keyword arguments can be
used to override the configuration file settings. For example, using
``Device('my_configured_device', acquisition='some_other_acq')`` would instead
attach an acquisition object defined in the
``[Acquisition:some_other_acq]`` section of the configuration file.



The acquisition class allows for a persistent connection to a data
acquisition system. To access data, we call the ``getdata`` method with 2
arguments [#getdataargs]_, the shot number and the name of a
configured diagnostic. An example diagnostic configuration here might
be::

  [Diagnostic:my_diagnostic]
  data_fetcher = pyfusion.acquisition.fakedata.SingleChannelSineDF
  sample_freq = 1.e6
  n_samples = 1000
  t0 = 0.0

When getdata(12345, 'my_diagnostic') is called, the acquisition class
will look to the config file for the ``[Diagnostic:my_diagnostic]``
section, and use the specified data fetcher class to return a data instance. 


.. rubric:: Footnotes


.. [#getdataargs] Two non-keyword arguments - additional keyword arguments which override configuration settings are allowed.

