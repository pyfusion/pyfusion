"""Base data classes."""
try:
    set
except NameError:
    from sets import Set as set # Python 2.3 fallback

from datetime import datetime

from pyfusion.conf.utils import import_from_str
from pyfusion.data.filters import filter_reg
from pyfusion.data.plots import plot_reg
import pyfusion

if pyfusion.USE_ORM:
    from sqlalchemy import Table, Column, String, Integer, Float, ForeignKey, DateTime
    from sqlalchemy.orm import reconstructor, mapper, relationship, dynamic_loader

def history_reg_method(method):
    def updated_method(input_data, *args, **kwargs):
        input_data.history += '\n%s > %s' %(datetime.now(), method.__name__ + '(' + ', '.join(map(str,args)) + ', '.join("%s='%s'" %(str(i[0]), str(i[1])) for i in kwargs.items()) + ')')
        return method(input_data, *args, **kwargs)
    return updated_method

class MetaMethods(type):
    def __new__(cls, name, bases, attrs):
        for reg in [filter_reg, plot_reg]:
            filter_methods = reg.get(name, [])
            attrs.update((i.__name__,history_reg_method(i)) for i in filter_methods)
        return super(MetaMethods, cls).__new__(cls, name, bases, attrs)


class Coords(object):
    def __init__(self, default_coords_name, default_coords_tuple,  **kwargs):
        self.default_name = default_coords_name
        self.default_value_1 = default_coords_tuple[0]
        self.default_value_2 = default_coords_tuple[1]
        self.default_value_3 = default_coords_tuple[2]
        kwargs.update(((default_coords_name, default_coords_tuple),))
        self.__dict__.update(kwargs)

    def add_coords(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def load_from_config(self, **kwargs):
        for kw in kwargs.iteritems():
            if kw[0] == 'coord_transform':
                transform_list = pyfusion.config.pf_options('CoordTransform', kw[1])
                for transform_name in transform_list:
                    transform_class_str = pyfusion.config.pf_get('CoordTransform', kw[1], transform_name)
                    transform_class = import_from_str(transform_class_str)
                    self.load_transform(transform_class)
            elif kw[0].startswith('coords_'):
                coord_values = tuple(map(float,kw[1].split(',')))
                self.add_coords(**{kw[0][7:]: coord_values})
    
    def load_transform(self, transform_class):
        def _new_transform_method(**kwargs):
            return transform_class().transform(self.__dict__.get(transform_class.input_coords),**kwargs)
        self.__dict__.update({transform_class.output_coords:_new_transform_method})

    def save(self):
        if pyfusion.USE_ORM:
            # this may be inefficient: get it working, then get it fast
            session = pyfusion.Session()
            session.add(self)
            session.commit()
            session.close()
        

if pyfusion.USE_ORM:
    coords_table = Table('coords', pyfusion.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('default_name', String(30), nullable=False),
                            Column('default_value_1', Float),
                            Column('default_value_2', Float),
                            Column('default_value_3', Float))
    pyfusion.metadata.create_all()
    mapper(Coords, coords_table)


class Channel(object):
    def __init__(self, name, coords):
        self.name = name
        self.coords = coords

    def save(self):
        if pyfusion.USE_ORM:
            # this may be inefficient: get it working, then get it fast
            self.coords.save()
            session = pyfusion.Session()
            session.add(self)
            session.commit()
            session.close()

if pyfusion.USE_ORM:
    channel_table = Table('channel', pyfusion.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String(30), nullable=False),
                            Column('coords_id', Integer, ForeignKey('coords.id'), nullable=False))
    pyfusion.metadata.create_all()
    mapper(Channel, channel_table, properties={'coords': relationship(Coords)})


    
if pyfusion.USE_ORM:
    channel_association_table = Table('channel_association', pyfusion.metadata,
                                      Column('channellist_id', Integer, ForeignKey('channellist.id'), primary_key=True),
                                      Column('channel_id', Integer, ForeignKey('channel.id'), primary_key=True),
                                      )

class ChannelList(list):
    def __init__(self, *args):
        self.extend(args)

    def save(self):
        if pyfusion.USE_ORM:
            self._channels.extend(self)
            session = pyfusion.Session()
            session.add(self)
            session.commit()
            session.close()

    if pyfusion.USE_ORM:
        @reconstructor
        def repopulate(self):
            for i in self._channels:
                if not i in self: self.append(i)
    
if pyfusion.USE_ORM:
    channellist_table = Table('channellist', pyfusion.metadata,
                              Column('id', Integer, primary_key=True))
                              
    pyfusion.metadata.create_all()
    mapper(ChannelList, channellist_table,
           properties={'_channels': relationship(Channel, secondary=channel_association_table)})
    


class MetaData(dict):
    pass

class BaseData(object):
    """Base class for handling processed data.

    In general, specialised subclasses of BaseData will be used
    to handle processed data rather than BaseData itself.

    Usage: ..........
    """
    __metaclass__ = MetaMethods

    def __init__(self):
        self.meta = MetaData()
        self.history = "%s > New %s" %(datetime.now(), self.__class__.__name__)
        if not hasattr(self, 'channels'):
            self.channels = ChannelList()
        
    def save(self):
        if pyfusion.USE_ORM:
            # this may be inefficient: get it working, then get it fast
            self.channels.save()
            session = pyfusion.Session()
            session.add(self)
            session.commit()
            session.close()

if pyfusion.USE_ORM:
    basedata_table = Table('basedata', pyfusion.metadata,
                            Column('basedata_id', Integer, primary_key=True),
                            Column('type', String(30), nullable=False))
    pyfusion.metadata.create_all()
    mapper(BaseData, basedata_table, polymorphic_on=basedata_table.c.type, polymorphic_identity='basedata')


class BaseDataSet(object):
    __metaclass__ = MetaMethods

    def __init__(self):
        self.history = "%s > New %s" %(datetime.now(), self.__class__.__name__)
        self.created = datetime.now()

    def save(self):
        if pyfusion.USE_ORM:
            # this may be inefficient: get it working, then get it fast
            session = pyfusion.Session()
            session.add(self)
            #session.flush()
            #for item in self:
            #    self.data.append(item)
            #    item.save()
            session.commit()
            session.close()

    # the set elements are stored in the database as foreign keys, after retrieving them
    # from the database the elements are stored at DataSet.data; we then need to put them back
    # in the set:
    if pyfusion.USE_ORM:
        @reconstructor
        def repopulate(self):
            for i in self.data:
                if not i in self: self.add(i)

if pyfusion.USE_ORM:
    basedataset_table = Table('basedataset', pyfusion.metadata,
                              Column('id', Integer, primary_key=True),
                              Column('created', DateTime),
                              Column('type', String(30), nullable=False))

    # many to many mapping of data to datasets
    data_basedataset_table = Table('data_basedataset', pyfusion.metadata,
                                   Column('basedataset_id', Integer, ForeignKey('basedataset.id')),
                                   Column('data_id', Integer, ForeignKey('basedata.basedata_id'))
                                   )
    pyfusion.metadata.create_all()
    mapper(BaseDataSet, basedataset_table,
           polymorphic_on=basedataset_table.c.type, polymorphic_identity='base_dataset',
           properties={'data': dynamic_loader(BaseData, secondary=data_basedataset_table, backref='datasets', cascade='all')})



class DataSet(BaseDataSet, set):
    pass
        
if pyfusion.USE_ORM:
    dataset_table = Table('dataset', pyfusion.metadata,
                            Column('basedataset_id', Integer, ForeignKey('basedataset.id'), primary_key=True))
    pyfusion.metadata.create_all()
    mapper(DataSet, dataset_table, inherits=BaseDataSet, polymorphic_identity='dataset')


class OrderedDataSet(BaseDataSet, list):

    def __init__(self, *args, **kwargs):
        self.ordered_by = kwargs.pop('ordered_by')
        super(OrderedDataSet, self).__init__(*args, **kwargs)

    def _get_order_attr(self, item):
        ret_value = item
        for attribute in self.ordered_by.split('.'):
            ret_value = ret_value.__getattribute__(attribute)
        return ret_value

    def sort(self):
        super(OrderedDataSet, self).sort(key=self._get_order_attr)

    def add(self, item):
        self.append(item)
        self.sort()

if pyfusion.USE_ORM:
    ordered_dataset_table = Table('ordered_dataset', pyfusion.metadata,
                                  Column('basedataset_id', Integer, ForeignKey('basedataset.id'), primary_key=True),
                                  Column('ordered_by', String(50)))

    pyfusion.metadata.create_all()
    mapper(OrderedDataSet, ordered_dataset_table, inherits=BaseDataSet, polymorphic_identity='ordered_dataset')

class BaseCoordTransform(object):
    """Base class does nothing useful at the moment"""
    input_coords = 'base_input'
    output_coords = 'base_output'

    def transform(self, coords):
        return coords

class FloatDelta(BaseData):
    def __init__(self, channel_1, channel_2, delta, **kwargs):
        self.channel_1 = channel_1
        self.channel_2 = channel_2
        self.delta = delta
        super(FloatDelta, self).__init__(**kwargs)

if pyfusion.USE_ORM:
    floatdelta_table = Table('floatdelta', pyfusion.metadata,
                            Column('basedata_id', Integer, ForeignKey('basedata.basedata_id'), primary_key=True),
                            Column('channel_1_id', Integer, ForeignKey('channel.id')),
                            Column('channel_2_id', Integer, ForeignKey('channel.id')),
                            Column('delta', Float))    
    pyfusion.metadata.create_all()
    mapper(FloatDelta, floatdelta_table, inherits=BaseData, polymorphic_identity='floatdelta',
           properties={'channel_1': relationship(Channel, primaryjoin=floatdelta_table.c.channel_1_id==channel_table.c.id),
                       'channel_2': relationship(Channel, primaryjoin=floatdelta_table.c.channel_2_id==channel_table.c.id)})
