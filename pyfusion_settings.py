"""
Settings for PyFusion. 
To keep customisations outside of revision control, local settings should be in a seperate file 'pyfusion_local_settings.py' located somewhere in your python path.

Here, we define default settings used throughout pyfusion which should be replaced by local settings.

General Settings
================
	DEVICE
	------
	One of:
		- H1
		- HeliotronJ
		- TJII
        TIMEBASE_DIFFERENCE_TOLERANCE
	-----------------------------
	if max(abs(timebase_a - timebase_b)) < TIMEBASE_DIFFERENCE_TOLERANCE then timebase_a and timebase_b will be treated as identical

SQL settings
============
	SQL_SERVER
	----------
	SQLAlchemy (U{http://www.sqlalchemy.org}) is used for all SQL interaction. SQL_SERVER is a string as defined by SQLAlchemy's create_engine() method I{driver://username:password@host:port/database} (see  U{http://www.sqlalchemy.org/docs/04/dbengine.html#dbengine_establishing})
	For example:
	 	- 'postgres://scott:tiger@localhost:5432/mydatabase'
		- 'sqlite:////absolute/path/to/database.txt'
		- 'mysql://localhost/foo'

        CHANNEL_NAME_STRING_LENGTH
	--------------------------
	length of string for channel name in SQL database.

DataMining Settings
===================
	N_SAMPLES_TIME_SEGMENT
	----------------------
	Number of samples for a short-time segment. Used for:
	 	- generating fluctuation structures (pyfusion.datamining.clustering)

        SV_GROUPING_THRESHOLD
	---------------------
	Threshold value of gamma_1,2 used for grouping singular values into fluctuation structures
	ENERGY_THRESHOLD
	----------------
	The fraction of signal energy to represent in fluctuation structures. At present, only used instead of SV_GROUPING_THRESHOLD for the threshold-less SV grouping function. A value of 0.99 keeps 99% of signal energy.


Optimisation
============
        OPT
	---
	-2: test some expensive assertions
	-1: test some assertions
	0: conservative
	1: pretty safe
	2..: etc
 
Console Output
==============
        VERBOSE
        -------
	Level of console output for monitoring and debugging:
	0 none (except warnings and errors)
	1,2 => 1, few per shot     (for each print call)
	3,4 => 1, few per segment
	5     etc
Note for VERBOSE and OPT - perhaps it would be smart to have function forms
of these to allow changing "on the fly", and even under intelligent program 
control.  For example, OPT could be used to check some conditions randomly
so that there was not a significant performance hit, but repeated violations 
would probably be detected.
Probably still should retain the
simple variable form so that in speed critical cases, the decision would not
waste time.

"""

# General:
DEVICE = ''
TIMEBASE_DIFFERENCE_TOLERANCE = 1.e-16

SHOT_T_MIN = -1.e10
SHOT_T_MAX = 1.e10

# SQL
SQL_SERVER = 'sqlite:///pyfusion_database.txt'
CHANNEL_NAME_STRING_LENGTH = 10

# Data Mining
N_SAMPLES_TIME_SEGMENT = 2**10
SV_GROUPING_THRESHOLD = 0.7
ENERGY_THRESHOLD = 0.99 

# Device specific:

# H1
H1_MDS_SERVER = 'h1data.anu.edu.au'

# TJ-II
RPCLIB = "$HOME/libs/libRpcC.a.linux.3.1"
COMPILE_COMMAND = "gcc  -g -I/usr/include/python2.5 -c tjiidata.c -o tjiidata.o"
LINKING_COMMAND = "ld -shared -o tjiidata.so  tjiidata.o %s" %RPCLIB
def compile_tjiidata(current_dir, comp_command = COMPILE_COMMAND, link_command = LINKING_COMMAND):
	import commands
	tmp = commands.getstatusoutput("cd %s; %s; %s" %(current_dir,comp_command,link_command))
	return tmp

#Optimisation
OPT=5

# Console Output
VERBOSE=3

try:
	from pyfusion_local_settings import *
	if VERBOSE>0:
		print('importing pyfusion_local_settings')

except:
	print "Local settings not found (looking for pyfusion_local_settings.py in python path)"
