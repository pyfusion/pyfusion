"""Base classes for data."""

import operator
import uuid
from datetime import datetime

from pyfusion.conf.utils import import_from_str, get_config_as_dict
from pyfusion.data.filters import filter_reg
from pyfusion.data.plots import plot_reg
import pyfusion

if pyfusion.USE_ORM:
    from sqlalchemy import Table, Column, String, Integer, Float, ForeignKey, \
         DateTime, PickleType
    from sqlalchemy.orm import reconstructor, mapper, relation, dynamic_loader
    from sqlalchemy.orm.collections import column_mapped_collection


def history_reg_method(method):
    """Wrapper for filter and plot methods which updates the data history."""
    def updated_method(input_data, *args, **kwargs):
        args_string = ', '.join(map(str,args))
        if args_string is not '':
            args_string += ', '
        kwargs_string = ', '.join("%s='%s'" %(str(i[0]), str(i[1]))
                                  for i in kwargs.items())
        history_string = "\n%s > %s(%s%s)" %(datetime.now(), method.__name__,
                                               args_string, kwargs_string)
        input_data.history += history_string
        output = method(input_data, *args, **kwargs)
        # TODO This looks wrong - if a filter modifies a meta value, does this
        # overwrite the modified version with the original?
        output.meta.update(input_data.meta)
        return output
    return updated_method

class MetaMethods(type):
    """Metaclass which provides filter and plot methods for data classes."""
    def __new__(cls, name, bases, attrs):
        for reg in [filter_reg, plot_reg]:
            reg_methods = reg.get(name, [])
            attrs.update((i.__name__,history_reg_method(i))
                         for i in reg_methods)
        return super(MetaMethods, cls).__new__(cls, name, bases, attrs)


class Coords(object):
    """Stores coordinates with an interface for coordinate transforms."""
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



def get_coords_for_channel(channel_name=None, **kwargs):
    config_dict = kwargs.copy()
    if channel_name:
        config_dict.update(get_config_as_dict('Diagnostic', channel_name))
    coord_name = 'dummy'
    coord_values = (0.0,0.0,0.0)
    transforms = []
    for k in config_dict.keys():
        if k.startswith('coords_'):
            coord_name = k[7:]
            coord_values = tuple(map(float,config_dict[k].split(',')))
    coords_instance = Coords(coord_name, coord_values)
    if config_dict.has_key('coord_transform'):
        transform_list = pyfusion.config.pf_options('CoordTransform', config_dict['coord_transform'])
        for transform_name in transform_list:
            transform_class_str = pyfusion.config.pf_get('CoordTransform', config_dict['coord_transform'], transform_name)
            transform_class = import_from_str(transform_class_str)
            coords_instance.load_transform(transform_class)

    return coords_instance

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
                            Column('name', String(200), nullable=False),
                            Column('coords_id', Integer, ForeignKey('coords.id'), nullable=False))
    pyfusion.metadata.create_all()
    mapper(Channel, channel_table, properties={'coords': relation(Coords)})


    
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
           properties={'_channels': relation(Channel, secondary=channel_association_table)})
    


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
                            Column('type', String(30), nullable=False),
                            Column('meta', PickleType(comparator=operator.eq))
                           )
    pyfusion.metadata.create_all()
    mapper(BaseData, basedata_table, polymorphic_on=basedata_table.c.type, polymorphic_identity='basedata')



class BaseDataSet(object):
    __metaclass__ = MetaMethods

    def __init__(self, label=''):
        self.meta = MetaData()
        self.created = datetime.now()
        self.history = "%s > New %s" %(self.created, self.__class__.__name__)
        if label == '':
            label = str(uuid.uuid4())
        self.label = label
        if not pyfusion.USE_ORM:
            self.data = set()
        
    def save(self):
        if pyfusion.USE_ORM:
            session = pyfusion.Session()
            session.add(self)
            session.commit()
            session.close()

    def remove(self, item):
        self.data.remove(item)

    def update(self, item):
        self.data.update(item)
    
    def copy(self):
        return self.data.copy()
        
    def add(self, item):
        self.data.add(item)

    def __iter__(self):
        return self.data.__iter__()

    def __len__(self):
        return self.data.__len__()

    def pop(self):
        return self.data.pop()

if pyfusion.USE_ORM:
    basedataset_table = Table('basedataset', pyfusion.metadata,
                              Column('id', Integer, primary_key=True),
                              Column('created', DateTime),
                              Column('label', String(100), nullable=False, unique=True),
                              Column('type', String(30), nullable=False),
                              Column('meta', PickleType(comparator=operator.eq)))

    # many to many mapping of data to datasets
    data_basedataset_table = Table('data_basedataset', pyfusion.metadata,
                                   Column('basedataset_id', Integer, ForeignKey('basedataset.id')),
                                   Column('data_id', Integer, ForeignKey('basedata.basedata_id'))
                                   )
    pyfusion.metadata.create_all()

    mapper(BaseDataSet, basedataset_table,
           polymorphic_on=basedataset_table.c.type, polymorphic_identity='base_dataset')
#           properties={'data': relation(BaseData, secondary=data_basedataset_table, backref='basedatasets', cascade='all', collection_class=set)})


class DynamicDataSet(BaseDataSet):
    pass
if pyfusion.USE_ORM:
    dynamicdataset_table = Table('dynamic_dataset', pyfusion.metadata,
                            Column('basedataset_id', Integer, ForeignKey('basedataset.id'), primary_key=True))
    pyfusion.metadata.create_all()
    mapper(DynamicDataSet, dynamicdataset_table, inherits=BaseDataSet, polymorphic_identity='dynamic_dataset',
           properties={'data': dynamic_loader(BaseData, secondary=data_basedataset_table, backref='dynamicdatasets', cascade='all')})
    


class DataSet(BaseDataSet):
    pass
        
        
if pyfusion.USE_ORM:
    dataset_table = Table('dataset', pyfusion.metadata,
                            Column('basedataset_id', Integer, ForeignKey('basedataset.id'), primary_key=True))
    pyfusion.metadata.create_all()
    mapper(DataSet, dataset_table, inherits=BaseDataSet, polymorphic_identity='dataset',
           properties={'data': relation(BaseData, secondary=data_basedataset_table, backref='datasets', cascade='all', collection_class=set)})


class OrderedDataSetItem(object):
    def __init__(self, item, index):
        self.item = item
        self.index = index

class BaseOrderedDataSet(object):
    __metaclass__ = MetaMethods

    def __init__(self, label=''):
        self.created = datetime.now()
        self.label = label
        self.history = "%s > New %s" %(self.created, self.__class__.__name__)
        if label == '':
            label = str(uuid.uuid4())
        if not pyfusion.USE_ORM:
            self.data_items = []
        
    def save(self):
        if pyfusion.USE_ORM:
            session = pyfusion.Session()
            session.add(self)
            session.commit()
            session.close()

    def append(self, item):
        if pyfusion.USE_ORM:
            self.data_items[len(self)] = OrderedDataSetItem(item, len(self))
        else:
            self.data_items.append(OrderedDataSetItem(item, len(self)))
    def __len__(self):
        #if pyfusion.USE_ORM:
        #    return self.data_items.count()
        #else:
        return self.data_items.__len__()

    def __getitem__(self, key):
        if pyfusion.USE_ORM:
            return self.data_items[key].item
        else:
            return self.data_items.__getitem__(key)

if pyfusion.USE_ORM:
    baseordereddataset_table = Table('baseordereddataset', pyfusion.metadata,
                                     Column('id', Integer, primary_key=True),
                                     Column('created', DateTime),
                                     Column('label', String(50), nullable=False, unique=True),
                                     Column('type', String(30), nullable=False))

    ordereditems_table = Table('ordereddata_items', pyfusion.metadata,
                         Column('dataset_id', Integer, ForeignKey('baseordereddataset.id'),
                                primary_key=True),
                         Column('item_id', Integer, ForeignKey('basedata.basedata_id'),
                                primary_key=True),
                         Column('index', Integer, nullable=False)
                         )
    
    pyfusion.metadata.create_all()

    mapper(BaseOrderedDataSet, baseordereddataset_table,
           polymorphic_on=baseordereddataset_table.c.type, polymorphic_identity='base_ordered_dataset',
           properties={'data_items': relation(OrderedDataSetItem,
                                                  backref='ordered_datasets_items',
                                                  cascade='all, delete-orphan',
                                                  collection_class=column_mapped_collection(ordereditems_table.c.index))
                       }
           )
    mapper(OrderedDataSetItem, ordereditems_table, properties={
        'item': relation(BaseData, lazy='joined', backref='dataitem')
        })


class OrderedDataSet(BaseOrderedDataSet):
    pass
"""
if pyfusion.USE_ORM:
    ordered_dataset_table = Table('ordered_dataset', pyfusion.metadata,
                                  Column('base_ordered_dataset_id', Integer,
                                         ForeignKey('baseordereddataset.id'), primary_key=True))
                                  #Column('ordered_by', String(50)))

    pyfusion.metadata.create_all()
    mapper(OrderedDataSet, ordered_dataset_table, inherits=BaseOrderedDataSet, polymorphic_identity='ordered_datasets')
"""

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
           properties={'channel_1': relation(Channel, primaryjoin=floatdelta_table.c.channel_1_id==channel_table.c.id),
                       'channel_2': relation(Channel, primaryjoin=floatdelta_table.c.channel_2_id==channel_table.c.id)})


