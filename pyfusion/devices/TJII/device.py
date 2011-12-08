from pyfusion.devices.base import Device
from pyfusion.orm.utils import orm_register

class TJII(Device):
    pass

@orm_register()
def orm_load_h1device(man):
    from sqlalchemy import Table, Column, Integer, ForeignKey
    from sqlalchemy.orm import mapper
    man.h1device_table = Table('tjiidevice', man.metadata, 
                            Column('basedevice_id', Integer, ForeignKey('devices.id'), primary_key=True))
    mapper(TJII, man.tjiidevice_table, inherits=Device, polymorphic_identity='tjii')
