.. Pyfusion documentation master file, created by sphinx-quickstart on Sat Feb 14 02:45:33 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pyfusion documentation
======================

:Release: |version|
:Date: |today|

Introduction
============

Pyfusion is a modular, object-orientated framework designed to
facilitate analysis of data from nuclear fusion research experiments. 


The motivation for the development of pyfusion came from the desire to
use a common data analysis library across multiple fusion devices,
each with different data acquisition systems. Pyfusion abstracts out
the data acquisition process, and provides common, easily customisable
data objects for most types of data. 

..
   classes: Device, Acquisition, DataFetcher, Diagnostic, Data, DataFilter loosely
   coupled by easy to edit test config file.

   processed data is mapped to SQL with SQLAlchemy ORM


.. toctree::
   :maxdepth: 2

   install/index
   tutorial/index
   ref/index

Development
-----------
.. toctree::
   :maxdepth: 1

   Overview <development/overview>
   Roadmap <development/roadmap>
   development/tests/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

