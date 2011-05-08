"""Interface  for MDSplus  data  acquisition and  storage.

This  package depends  on  the MDSplus  python  package, available  from
http://www.mdsplus.org/binaries/python/

Pyfusion supports three modes for accessing MDSplus data:

 #. local
 #. thick client
 #. thin client

The  data access  mode used  is determined  by the  mds path  and server
variables  in the  configuration file  (or supplied  to  the acquisition
class via keyword arguments)::

 [Acquisition:my_data]
 acq_class = pyfusion.acquisition.MDSPlus.acq.MDSPlusAcquisition
 mydata_path = ...
 server = my.mdsdataserver.net

The  full MDSplus  node path  is  stored in  a diagnostic  configuration
section::

  [Diagnostic:my_probe]
  data_fetcher = pyfusion.acquisition.MDSPlus.fetch.MDSPlusDataFetcher
  mds_node_path = \mydata::top.probe_signal
 
Local data access
-----------------

The 'local' mode is used when a tree path definition refers to the local
file  system  rather  than  an  MDSplus  server  on  the  network.   The
:attr:`mydata_path`  entry in  the  above example  would look  something
like::

 mydata_path = /path/to/my/data


Thick client access
-------------------

The 'thick client'  mode uses an MDSplus data server  to retieve the raw
data files, but the client is responsible for evaluating expressions and
decompressing the  data. The server  tree definitions are used,  and the
server  for a  given  mds tree  is specified  by  the tree  path in  the
format::

 mydata_path = my.mdsdataserver.net::

or, if a port other than the default (8000) is used::

 mydata_path = my.mdsdataserver.net:port_number::

Thin client access
------------------

The  'thin  client' mode  maintains  a  connection  to an  MDSplus  data
server. Expressions  are evaluated and data decompressed  on the server,
requiring  greater   amounts  of  data   to  be  transferred   over  the
network. Because the thin client mode uses the tree paths defined on the
server, no path variable  is required. Instead, the :attr:`server` entry
is used::

 server = my.mdsdataserver.net

or, if a port other than the default (8000) is used::

 server = my.mdsdataserver.net:port_number


How Pyfusion chooses the access mode
------------------------------------

If an acquisition configuration section contains a :attr:`server` entry,
then :class:`~acq.MDSPlusAcquisition`  will set  up a connection  to the
server when it is  instantiated. Additionally, any tree path definitions
(local and thick client) are loaded into the runtime environment at this
time. When a call to the data fetcher is made (via :meth:`getdata`), the
data  fetcher uses the  full node  path (including  tree name)  from the
configuration file.  If a matching (tree  name) :attr:`_path` variable is
defined  for the  acquisition module,  then the  corresponding  local or
thick client mode will be used. If  no tree path is defined then, if the
:attr:`server`  variable is defined,  pyfusion will  attempt to  use the
thin client mode.

"""
