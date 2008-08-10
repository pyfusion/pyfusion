"""
This init file sets up an SQLAlchemy session, accessible as pyfusion.session, 
and updates the SQL database by checking for new channels, diagnostics and devices
defined in their respective sub-modules.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

import pyfusion_settings as settings
from pyfusion.utils import update_device_info

engine = create_engine(settings.SQL_SERVER, echo=settings.VERBOSE > 6)
Session = scoped_session(sessionmaker(autoflush=True, transactional=False, bind=engine))
Base = declarative_base(engine)

session = Session()

# Device, Diagnostic, Channel require pyfusion.Base, so need to be imported _after_ Base = ... 
from pyfusion.core import Device, Diagnostic,Channel

# import the device module, as defined by DEVICE setting
_device_module = __import__('pyfusion.devices.%s.%s' %(settings.DEVICE,settings.DEVICE), globals(), locals(), [settings.DEVICE])

# create the tables defined by imports from pyfusion.core (if they do not already exist)
Base.metadata.create_all()

# update Channel, Diagnostic, Device data by looking for instances of these classes in _device_module
for pyf_class in [Channel, Diagnostic, Device]:
    update_device_info(pyf_class)

# the instance of Device to be used (taken from _device_module)
_device = session.query(Device).filter(Device.name == _device_module.__dict__[settings.DEVICE].name).one()

if settings.VERBOSE>0:
    for ds in session.query(Diagnostic): print (" %s: list=%d, channels=%d ") % (ds.name,len(ds.ordered_channel_list),len(ds.channels))

# shortcut - pyfusion.session.query() -> pyfusion.q()
def q(*args,**kwargs):
    return session.query(*args,**kwargs)

# allow classes  pyfusion.core.xx to be referenced as pyfusion.xx
# this might not be good design - will consider removal, or only importing selected classes
from core import *
