Object relational mapping
=========================

Overview
--------

`Object relational mapping <http://en.wikipedia.org/wiki/Object-relational_mapping>`_ (ORM) is a method of maintaining a connection between a `relational database <http://en.wikipedia.org/wiki/Relational_database>`_ (e.g. `MySQL <http://en.wikipedia.org/wiki/MySQL>`_) and `object orientated <http://en.wikipedia.org/wiki/Object_oriented>`_ programming languages (e.g. `python <http://en.wikipedia.org/wiki/Python_(programming_language)>`_). The types of data used with pyfusion are very well suited to being stored in relational databases, i.e. we deal with a large number of items which all share the same set of attributes. With an ORM, we get the benefits of both fast and efficient `SQL <http://en.wikipedia.org/wiki/SQL>`_ querying of the data, and object orientated code. 

In pyfusion, the ORM is activated by setting the ``database`` configuration variable in the ``[global]`` section of your configuration file. Pyfusion will not use ORM if  ``database`` is set to ``None``. 


SQLAlchemy
^^^^^^^^^^

`SQLAlchemy <http://www.sqlalchemy.org>`_ is a python library which provides a comprehensive interface to relational databases, and includes ORM. The documentation is available here: http://www.sqlalchemy.org/docs/ 

The pyfusion ORM configuration
------------------------------

Pyfusion uses SQLAlchemy for its ORM. The standard method for configuring an ORM with SQLAlchemy is to explicitly construct Table objects and link them to Python classes with a mapping object. An alternative configuration is to use the SQLAlchemy declarative extension, which provides a base class which provides Table and mapper attributes to any class which inherits it. The two approaches represent different styles code rather than providing different functionality. Pyfusion uses the standard approach to keep ORM code separate from non-ORM (class definitions) code, allowing pyfusion to be used without ORM.

------------------------------

Module-wide configuration
^^^^^^^^^^^^^^^^^^^^^^^^^

Most, if not all, the pyfusion ORM code lives in two places: module-wide code is located in ``pyfusion/__init__.py``, while class specific code resides in the class itself. The module-wide configuration consists of ``Engine`` and ``Session`` instances, and definition of a base class for declarative SQLAlchemy.  


Engine
""""""

The SQLAlchemy engine provides an abstraction of the relational database (beneath it could be MySQL, Postgres, SQLite, etc), and a pool of connections to the database. Starting a database connection is an expensive operation, to streamline database interaction, the engine keeps a pool of connections which it uses and recycles to avoid the overhead of creating database connections for each operation. In pyfusion, the SQLAlchemy engine is created when pyfusion is imported (``pyfusion/__init__.py``)::


 from sqlalchemy import create_engine
 orm_engine = create_engine(config.get('global', 'database'))

Presently there is no support for changing database configuration within a single pyfusion session, i.e. reloading the configuration file will not reset the database. 

Session
"""""""

An instance of the  SQLAlchemy ``Session`` class is used to manage interactions with the database, it can keep track of modifications to data instances and flush multiple changes to the database when required. We use ``scoped_session`` to provide a thread-local ``Session`` instance, which allows us to use the same session in different parts of pyfusion. The session configuration looks like::

 Session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=orm_engine))

The ``autocommit`` and ``autoflush`` arguments  prescribe how the session should organise transactions. A `database transaction <http://en.wikipedia.org/wiki/Database_transaction>`_ refers to a group of queries which should be treated as a single operation on the database, either all queries in a should be applied, or none of them should. Using ``commit()`` in an sqlalchemy session commits the current transaction, whereas ``flush()`` will write pending data to the database without closing the transaction. In ``autocommit`` mode SQLAlchemy automatically commits after each ``flush()``, while this removes some flexibility in construction of transactions it can be useful for testing and debug purposes. Regardless of these settings, ``commit()`` will always call a ``flush()`` before committing the transaction. The ``autoflush=True`` argument specifies that ``flush()`` should be called before any individual query is issued.  


Class-level configuration
^^^^^^^^^^^^^^^^^^^^^^^^^

Does pyfusion read from the config file or data database?
---------------------------------------------------------

notes:
e.g. when a device is created which has a config definition, it will be loaded from sql if it exists. if it doesnt exist it will be created. at present there is no checking to make sure that the sql version matches the params of the config. there is no automated way of changing the sql version if you change the config - this shoulnt be done anyway, as other data may have been created with the existing device, diagnostic etc and it we dont want to have processed data attached to an instance which is not responsible for its creation... etc...


