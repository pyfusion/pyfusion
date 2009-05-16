""" Useful functions for manipulating config files."""

from pyfusion.conf import config

def CannotImportFromConfigError(Exception):
    """Failed to import a module, class or method from config setting."""
    
def import_setting(component, component_name, setting):
    """Attempt to import and return a config setting."""
    value_str = config.pf_get(component, component_name, setting)
    # TODO: make shortcuts for loading from within pyfusion
    split_val = value_str.split('.')
    val_module = __import__('.'.join(split_val[:-1]),
                            globals(), locals(),
                            [split_val[-1]], -1)
    return val_module.__dict__[split_val[-1]]

def kwarg_config_handler(component_type, component_name, **kwargs):
    for config_var in config.pf_options(component_type, component_name):
            if not config_var in kwargs.keys():
                kwargs[config_var] = config.pf_get(component_type,
                                                   component_name, config_var)
    return kwargs
