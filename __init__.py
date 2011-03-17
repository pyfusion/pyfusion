import os, logging

#import pyfusion.conf
from pyfusion.conf import PyfusionConfigParser
from pyfusion.conf.utils import read_config

config = PyfusionConfigParser()


# set up logger
import logging.config
PYFUSION_ROOT_DIR = os.path.dirname(__file__)
logging.config.fileConfig(os.path.join(PYFUSION_ROOT_DIR, "conf","logging.cfg"))
logger = logging.getLogger("pyfusion")



# version information
VERSION = (0, 0, 1, '', 0)

def get_version():
    """Human-readable version info."""
    
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3:] == ('alpha', 0):
        version = '%s pre-alpha' % version
    else:
        version = '%s %s' % (version, VERSION[3])
        if VERSION[3] != 'final':
            version = '%s %s' % (version, VERSION[4])
    """
    # not yet implemented
    from pyfusion.utils.version import get_git_revision
    git_rev = get_git_revision()
    if git_rev != u'Git-unknown':
        version = "%s %s" % (version, git_rev)
    """
    return version


# find config files
DEFAULT_CONFIG_FILE = os.path.join(PYFUSION_ROOT_DIR, 'pyfusion.cfg')
USER_PYFUSION_DIR = os.path.join(os.path.expanduser('~'), '.pyfusion')
if not os.path.exists(USER_PYFUSION_DIR):
    os.mkdir(USER_PYFUSION_DIR)
USER_CONFIG_FILE = os.path.join(USER_PYFUSION_DIR, 'pyfusion.cfg')
USER_TEST_CONFIG_FILE = os.path.join(USER_PYFUSION_DIR, 'tests.cfg')

USER_ENV_CONFIG_FILE = os.getenv('PYFUSION_CONFIG_FILE','')

read_config([DEFAULT_CONFIG_FILE, USER_CONFIG_FILE, USER_ENV_CONFIG_FILE])

from pyfusion.devices.base import getDevice
from pyfusion.acquisition.utils import getAcquisition

from pyfusion.orm import ORMManager
orm_manager = ORMManager()
