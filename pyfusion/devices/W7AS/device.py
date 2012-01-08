from pyfusion.devices.base import Device
from pyfusion.orm.utils import orm_register

class W7AS(Device):
    pass

@orm_register()
def orm_load_w7asdevice(man):
    from sqlalchemy import Table, Column, Integer, ForeignKey
    from sqlalchemy.orm import mapper
    man.w7asdevice_table = Table('w7asdevice', man.metadata, 
                            Column('basedevice_id', Integer, ForeignKey('devices.id'), primary_key=True))
    mapper(W7AS, man.w7asdevice_table, inherits=Device, polymorphic_identity='w7as')
