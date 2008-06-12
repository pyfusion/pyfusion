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

"""

# General:
DEVICE = ''
TIMEBASE_DIFFERENCE_TOLERANCE = 1.e-16

# SQL
SQL_SERVER = 'sqlite:///pyfusion_database.txt'
CHANNEL_NAME_STRING_LENGTH = 10

# Data Mining
N_SAMPLES_TIME_SEGMENT = 2**10
SV_GROUPING_THRESHOLD = 0.7

# Device specific:

# H1
H1_MDS_SERVER = 'h1data.anu.edu.au'

try:
	from pyfusion_local_settings import *
except:
	print "Local settings not found (looking for pyfusion_local_settings.py in python path)"
