from pyfusion.devices.base import Device
from pyfusion.orm.utils import orm_register

class HeliotronJ(Device):
    pass

@orm_register()
def orm_load_heliotronjdevice(man):
    from sqlalchemy import Table, Column, Integer, ForeignKey
    from sqlalchemy.orm import mapper
    man.heliotronjdevice_table = Table('heliotronjdevice', man.metadata, 
                            Column('basedevice_id', Integer, ForeignKey('devices.id'), primary_key=True))
    mapper(HeliotronJ, man.heliotronjdevice_table, inherits=Device, polymorphic_identity='heliotronj')
