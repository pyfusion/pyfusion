Introduction
============

Pyfusion is a modular, object-orientated framework designed to
facilitate analysis of data from nuclear fusion research experiments. 


The motivation for the development of pyfusion came from the desire to
use a common data analysis library across multiple fusion devices,
each with different data acquisition systems. Pyfusion abstracts out
the data acquisition process, and provides common, easily customisable
data objects for most types of data. 

xxxxx

classes: Device, Acquisition, Diagnostic, Data, DataFilter loosely
coupled by easy to edit test config file.

processed data is mapped to SQL with SQLAlchemy ORM




Database
--------
The database layer is handled by `SQLAlchemy <http://www.sqlalchemy.org>`_ 

.. _db-urls:

Database URL
^^^^^^^^^^^^
Database URLs are the same as for SQLAlchemy::

	 driver://username:password@host:port/database

For more details, refer to http://www.sqlalchemy.org/docs/05/dbengine.html#create-engine-url-arguments 