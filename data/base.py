"""Base data classes."""
try:
    set
except NameError:
    from sets import Set as set # Python 2.3 fallback

from pyfusion.conf.utils import import_from_str
from pyfusion.data.filters import MetaFilter
import pyfusion
                
class Coords(object):
    def __init__(self, **kwargs):
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

class MetaData(dict):
    coords = Coords()

class BaseData(object):
    """Base class for handling processed data.

    In general, specialised subclasses of BaseData will be used
    to handle processed data rather than BaseData itself.

    Usage: ..........
    """
    __metaclass__ = MetaFilter

    def __init__(self):
        self.meta = MetaData()
        filter_list = pyfusion.data.filter_register.get_for(self.__class__)
        for filter_method in filter_list:
            self._add_method(filter_method)

    def _add_method(self, method_fn):
        def _fn(*args, **kwargs):
            return method_fn(self, *args, **kwargs)
        self.__dict__[method_fn.__name__] = _fn
            
class DataSet(set):
    def __init__(self):
        filter_list = pyfusion.data.filter_register.get_for(self.__class__)
        for filter_method in filter_list:
            self._add_method(filter_method)

    def _add_method(self, method_fn):
        def _fn(*args, **kwargs):
            return method_fn(self, *args, **kwargs)
        self.__dict__[method_fn.__name__] = _fn


class BaseCoordTransform(object):
    """Base class does nothing useful at the moment"""
    input_coords = 'base_input'
    output_coords = 'base_output'

    def transform(self, coords):
        return coords
