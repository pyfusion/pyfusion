from pyfusion.devices.base import Device
from pyfusion.orm.utils import orm_register

class LHD(Device):
    pass

@orm_register()
def orm_load_lhddevice(man):
    from sqlalchemy import Table, Column, Integer, ForeignKey
    from sqlalchemy.orm import mapper
    man.lhddevice_table = Table('lhddevice', man.metadata, 
                            Column('basedevice_id', Integer, ForeignKey('devices.id'), primary_key=True))
    mapper(LHD, man.lhddevice_table, inherits=Device, polymorphic_identity='lhd')
