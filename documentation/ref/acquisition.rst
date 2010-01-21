:mod:`acquisition` -- Connect to a data acquisition system
==========================================================
.. module:: acquisition
   :synopsis: Connect to a data acquisition system

Data acquisition in pyfusion is handled by two classes, an Acquisition
class which allows persistent connection to a data acquisition system
(e.g. MDSPlus), and a DataFetcher which is used by the Acquisition
class to fetch data from the data acquisition system and return a Data
instance. 

Base Classes
------------

.. module:: acquisition.base


.. class:: BaseAcquisition(config_name=None, **kwargs)

