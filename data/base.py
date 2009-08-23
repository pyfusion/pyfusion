"""Base data classes."""
try:
    set
except NameError:
    from sets import Set as set # Python 2.3 fallback

import pyfusion
                

class BaseData(object):
    """Base class for handling processed data.

    In general, specialised subclasses of BaseData will be used
    to handle processed data rather than BaseData itself.

    Usage: ..........
    """
    def __init__(self):
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

