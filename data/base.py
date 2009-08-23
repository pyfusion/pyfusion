"""Base data classes."""
import pyfusion


class BaseData(object):
    """Base class for handling processed data.

    In general, specialised subclasses of BaseData will be used
    to handle processed data rather than BaseData itself.

    Usage: ..........
    """
    def __init__(self):
        filter_list = pyfusion.data.filter_register.get_for(self.__class__.__name__)
        for filter_method in filter_list:
            #self.__dict__[filter_method.__name__] = lambda *args, **kwargs: filter_method(self, *args, **kwargs)
            self._add_method(filter_method)
    def _add_method(self, method_fn):
        def _fn(*args, **kwargs):
            return method_fn(self, *args, **kwargs)
        self.__dict__[method_fn.__name__] = _fn
            
