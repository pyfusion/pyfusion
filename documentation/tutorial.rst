=================
Pyfusion tutorial
=================

Example session: using only raw data
------------------------------------

In this first example, we consider a session where we simply want to
view raw data, rather than manipulate the data in any way. In this
case, we don't need to use SQLAlchemy ORM functionality (which saves
processed data to an SQL database). 

**lets use a real example with TJII etc**

**first, make config file - write docs when tjii acquisition is working**

Load the pyfusion module:

   >>> import pyfusion

next, we create an instance of the Device class
(:class:`pyfusion.core.devices.Device` is mapped to
:class:`pyfusion.Device` for convenience).

   >>> mydevice = pyfusion.Device("MyDevice")


Example session: with data processing
-------------------------------------

xxxxxx
The database argument is a SQLAlchemy database URL (see
:ref:`db-urls`). If your configuration file ( :ref:`config-files` ) includes a section
"MyDevice", pyfusion will look there for a database URL. If the config
file specifies a database URL, then the Device database argument is
optional. The Device database argument will override the config file
value in the case where both are present. In this example, the
"sqlite://:memory:" database URL specifies that any processed data should
persist only in memory, and not be saved to a permanent database.

 
