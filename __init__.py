import ConfigParser
import os

from core import Device, Shot

DEFAULT_CONFIG_FILE = 'pyfusion.cfg'
USER_PYFUSION_DIR = os.path.join(os.path.expanduser('~'), '.pyfusion')
if not os.path.exists(USER_PYFUSION_DIR):
    os.mkdir(USER_PYFUSION_DIR)
USER_CONFIG_FILE = os.path.join(USER_PYFUSION_DIR, 'pyfusion.cfg')

config = ConfigParser.ConfigParser()
config.read(DEFAULT_CONFIG_FILE)
config.read(USER_CONFIG_FILE)

# keep track of connected databases so we don't connect multiple
# devices to the same database. There might be a better way to do this
# using sqlalchemy functionality (which might also work for the case
# of multiple pyfusion instances?)
_connected_databases = []
