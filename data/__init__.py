
class FilterRegister(object):
    def __init__(self):
        self.cache = {}
        self.add_module('pyfusion.data.filters')
        
    def add_module(self, module_str):
        from pyfusion.conf.utils import import_from_str
        module_inst = import_from_str(module_str)
        for attribute_name in module_inst.__dict__.keys():
            if hasattr(module_inst.__dict__[attribute_name], 'allowed_class'):
                for cl in module_inst.__dict__[attribute_name].allowed_class:
                    if not self.cache.has_key(cl):
                        self.cache[cl] = []
                    self.cache[cl].append(module_inst.__dict__[attribute_name])
    def get_for(self, class_name):
        return self.cache.get(class_name, [])

filter_register = FilterRegister()
