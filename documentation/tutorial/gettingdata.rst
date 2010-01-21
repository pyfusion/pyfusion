.. _tut-getting:

************
Getting Data
************

The recommended method of retrieving data with pyfusion is by creating
an instance of :class:`Device` class (to represent LHD, H-1, TJ-II,
etc) and using the attached :meth:`getdata` method::

   import pyfusion
   h1 = pyfusion.getDevice('H1')
   mirnov_data = h1.acq.getdata(58133, 'H1_mirnov_array_1_coil_1')


