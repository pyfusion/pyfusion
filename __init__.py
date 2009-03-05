import ConfigParser
 
from core import Device, Shot

DEFAULT_CONFIG_FILE = 'pyfusion.cfg'

config = ConfigParser.ConfigParser()
config.read(DEFAULT_CONFIG_FILE)

# keep track of connected databases so we don't connect multiple
# devices to the same database. There might be a better way to do this
# using sqlalchemy functionality (which might also work for the case
# of multiple pyfusion instances?)
_connected_databases = []
