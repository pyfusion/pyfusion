"""
	Introduction
	============
	PyFusion aims to provide well-documented, open-source tools for fusion researchers.
	The project was started by Dave Pretty in 2007 as an implementation of the data mining code 
	contained in his PhD thesis that aims to be easy to for others to use and to be machine/lab independent.
	The scope is not limited to data mining tools; we hope that a collaborative repository of tools will benefit all areas of fusion research.
	
	Requirements
	============
	numpy
        sqlalchemy > 0.4.4
        
        for clustering: R, RPy
	for plots: matplotlib

	Settings
	========
	Local settings can be specified in a file called pyfusion_local_settings.py, which can be anywhere in your python path.
	
"""

from sqlalchemy import create_engine, Column, Integer, String, exceptions, ForeignKey, PickleType, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, sessionmaker, scoped_session, synonym

import pyfusion_settings as settings

engine = create_engine(settings.SQL_SERVER, echo=settings.VERBOSE > 6)
Session = scoped_session(sessionmaker(autoflush=True, transactional=True, bind=engine))
Base = declarative_base(engine)

session = Session()

class Device(Base):
    __tablename__ = "devices"
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(50), nullable=False, unique=True)

class Diagnostic(Base):
    __tablename__ = "diagnostics"
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(50), nullable=False, unique=True)
    ordered_channel_list = Column('ordered_channel_list', PickleType)

    def __init__(self, name):
        self.name= name
        self.ordered_channel_list = []
        if settings.VERBOSE>2:
            print('Class Diagnostic __init__ %s') % self.name

    def add_channel(self, channel):
        self.ordered_channel_list.append(channel.name)
        self.channels.append(channel)

    def ordered_channels(self):
#bdb
        if len(self.channels) != len(self.ordered_channel_list): 
            print('******** Inconsistency in ordered channels %d != %d') % (len(self.channels), len(self.ordered_channel_list))
        outlist = []
        for oc in self.ordered_channel_list:
            outlist.append(session.query(Channel).filter_by(name=oc, diagnostic_id=self.id).one())
        return outlist


class Coordinates(Base):
    __tablename__ = "coords"
    id = Column('id', Integer, primary_key=True)
    coord_system = Column('coord_system', String(50))
    __mapper_args__ = {'polymorphic_on':coord_system}
    A = Column('A', Float)
    B = Column('B', Float)
    C = Column('C', Float)
    def transform(self,func):
        """
        transform coordinate systems.
        should this just return values? or a new Coordinates object with different coord_system?
        """
        raise NotImplementedError
    

class ToroidalCoordinates(Coordinates):
    __tablename__ = 'coords_toroidal'
    __mapper_args__ = {'polymorphic_identity':'toroidal'}
    id = Column('id', Integer, ForeignKey('coords.id'), primary_key=True)
    def _get_attr_A(self):
        return self.A
    def _set_attr_A(self, attr):
        self.A = attr
    def _get_attr_B(self):
        return self.B
    def _set_attr_B(self, attr):
        self.B = attr
    def _get_attr_C(self):
        return self.C
    def _set_attr_C(self, attr):
        self.C = attr
    r = synonym('A', descriptor=property(_get_attr_A, _set_attr_A))
    phi = synonym('B', descriptor=property(_get_attr_B, _set_attr_B))
    theta = synonym('C', descriptor=property(_get_attr_C, _set_attr_C))

class CylindricalCoordinates(Coordinates):
    __tablename__ = 'coords_cylindrical'
    __mapper_args__ = {'polymorphic_identity':'cylindrical'}
    id = Column('id', Integer, ForeignKey('coords.id'), primary_key=True)
    def _get_attr_A(self):
        return self.A
    def _set_attr_A(self, attr):
        self.A = attr
    def _get_attr_B(self):
        return self.B
    def _set_attr_B(self, attr):
        self.B = attr
    def _get_attr_C(self):
        return self.C
    def _set_attr_C(self, attr):
        self.C = attr
    r = synonym('A', descriptor=property(_get_attr_A, _set_attr_A))
    phi = synonym('B', descriptor=property(_get_attr_B, _set_attr_B))
    z = synonym('C', descriptor=property(_get_attr_C, _set_attr_C))


class Channel(Base):
    __tablename__ = "channels"
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(50), nullable=False, unique=True)
    data_acq_type = Column('data_acq_type', String(50))
    __mapper_args__ = {'polymorphic_on':data_acq_type}
    diagnostic_id = Column('diagnostic_id', Integer, ForeignKey('diagnostics.id'))
    diagnostic = relation(Diagnostic, primaryjoin=diagnostic_id==Diagnostic.id, backref="channels")
    processdata_override = Column('processdata_override', PickleType, nullable=True)
    coord_id = Column('coord_id', Integer, ForeignKey('coords.id'))
    coords = relation(Coordinates, primaryjoin=coord_id==Coordinates.id)    

#_device_module = __import__('pyfusion.devices.%s.%s' %(DEVICE,DEVICE), globals(), locals(), [DEVICE], -1)
_device_module = __import__('pyfusion.devices.%s.%s' %(settings.DEVICE,settings.DEVICE), globals(), locals(), [settings.DEVICE])
Base.metadata.create_all()



# here we check all instances defined in _device_module and update the database 

def update_device_info(pyf_class):
    existing = session.query(pyf_class).all()
    for devmod_object_str in _device_module.__dict__.keys():
        if hasattr(_device_module.__dict__[devmod_object_str], '__class__'):        
            devmod_inst_bases = _device_module.__dict__[devmod_object_str].__class__.__bases__
            if pyf_class in devmod_inst_bases:
                if _device_module.__dict__[devmod_object_str].name not in [i.name for i in existing]:
                    session.save_or_update(_device_module.__dict__[devmod_object_str]) 
                    session.flush()
    # this commit isn't needed for H1 (python 2.5), but is for heliotron (python 2.4) - why?
    session.commit()

# do seperately with Channels first, so they are defined for Diagnostics, though this may not be ness - check

update_device_info(Channel)
update_device_info(Diagnostic)
update_device_info(Device)


_device = session.query(Device).filter(Device.name == _device_module.__dict__[settings.DEVICE].name).one()
if settings.VERBOSE>0:
    for ds in session.query(Diagnostic): print (" %s: list=%d, channels=%d ") % (ds.name,len(ds.ordered_channel_list),len(ds.channels))

session.commit()

from core import *
