import os, logging
import logging.config

from pyfusion.conf import PyfusionConfigParser
from pyfusion.conf.utils import read_config
from pyfusion.orm import ORMManager
from pyfusion.version import get_version

# This grabs the directory of the pyfusion module.
PYFUSION_ROOT_DIR = os.path.dirname(__file__)

# Location of the logging configuration file.
LOGGING_CONFIG_FILE = os.path.join(PYFUSION_ROOT_DIR, 'conf', 'logging.cfg')

# Grab the pyfusion version
VERSION = get_version()

# This creates a parser to process and store configuration file data.
# PyfusionConfigParser is a subclass of ConfigParser.ConfigParser in the
# python standard library. It is customised to parse [Type:Name] sections
# in configuration files.
config = PyfusionConfigParser()

# This allows us to activate and de-activate the object relational
# mapping (ORM) code from within a python session, and also helps to
# keep the ORM code separate so it doesn't slow things down for
# users who don't want the database backend. 
orm_manager = ORMManager()

# This sets up an instance of logger from the python standard library.
logging.config.fileConfig(LOGGING_CONFIG_FILE)
logger = logging.getLogger("pyfusion")

# Find the default pyfusion configuration file...
DEFAULT_CONFIG_FILE = os.path.join(PYFUSION_ROOT_DIR, 'pyfusion.cfg')

# ... and the user's custom configuration file. First, if they don't
# already have a folder for pyfusion stuff then let's make one
USER_PYFUSION_DIR = os.path.join(os.path.expanduser('~'), '.pyfusion')
if not os.path.exists(USER_PYFUSION_DIR):
    os.mkdir(USER_PYFUSION_DIR)
# and here is the custom user configuration file
USER_CONFIG_FILE = os.path.join(USER_PYFUSION_DIR, 'pyfusion.cfg')

# Also allow specification of other configuration files from
# a PYFUSION_CONFIG_FILE environment variable
USER_ENV_CONFIG_FILE = os.getenv('PYFUSION_CONFIG_FILE','')
if not(os.path.exists(USER_ENV_CONFIG_FILE)): 
    raise IOError('Error - cfg file {f} ponted to by USER_ENV_CONFIG_FILE'
                  ' not found!  Check/delete the env var {v}'
                  .format(f=USER_ENV_CONFIG_FILE,v="PYFUSION_CONFIG_FILE"))


# Now we actually load the configuration files. Settings in
# DEFAULT_CONFIG_FILE will be superseded by those in USER_CONFIG_FILE,
# and USER_ENV_CONFIG_FILE will supersede both. As well as storing the
# settings, read_config() will set up the ORM backend if required.
# Note that the $HOME/.pyfusion file overrides the $PYFUSION_ROOT_DIR file.
DEBUG = os.getenv('PYFUSION_DEBUG','0')  # probably better as an env var
try:   # if it looks like an int, make it one.
    DEBUG=int(DEBUG)
except:
    pass
# VERBOSE is likely to be used as an env var for debugging and as a config
# var, depending on taste.
VERBOSE = int(os.getenv('PYFUSION_VERBOSE','0'))  # allows config info to be debugged
read_config([DEFAULT_CONFIG_FILE, USER_CONFIG_FILE, USER_ENV_CONFIG_FILE])

# verbosity level from environment has priority, otherwise use config, which 
# defaults to 0.  Note that we looked at the env var previously to allow debug of config
VERBOSE = int(os.getenv('PYFUSION_VERBOSE',
                    config.get('global','VERBOSE',vars={'VERBOSE':'0'})))
## Variable precision - allows data sets to be much bigger - up to 4x  bdb Dec-2012

root_dir = os.path.split(os.path.abspath( __file__ ))[0]

try:
    from numpy import dtype as npdtype
    # Beware!  vars takes  precedence over others!
    prec_med=npdtype(config.get('global','precision_medium')) #,vars={'precision_medium':'float32'}))
except:
    print('unknown medium precision value')
    from numpy import dtype as npdtype
    prec_med=npdtype('float32')

try:
    COLORS=config.get('global','colors')
except:
    if VERBOSE>0: print('colors not in config file - no color!')
    COLORS=None


# We import these into the base pyfusion namespace for convenience.
from pyfusion.devices.base import getDevice
from pyfusion.acquisition.utils import getAcquisition

