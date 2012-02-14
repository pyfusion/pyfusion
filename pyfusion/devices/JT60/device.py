from pyfusion.devices.base import Device
from pyfusion.orm.utils import orm_register

class JT60(Device):
    pass

@orm_register()
def orm_load_jt60device(man):
    from sqlalchemy import Table, Column, Integer, ForeignKey
    from sqlalchemy.orm import mapper
    man.jt60device_table = Table('jt60device', man.metadata, 
                            Column('basedevice_id', Integer, ForeignKey('devices.id'), primary_key=True))
    mapper(JT60, man.jt60device_table, inherits=Device, polymorphic_identity='jt60')
