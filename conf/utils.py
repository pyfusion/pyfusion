""" Useful functions for manipulating config files."""

import pyfusion

def CannotImportFromConfigError(Exception):
    """Failed to import a module, class or method from config setting."""
    
def import_from_str(string_value):
    # TODO: make shortcuts for loading from within pyfusion
    split_val = string_value.split('.')
    val_module = __import__('.'.join(split_val[:-1]),
                            globals(), locals(),
                            [split_val[-1]])
    return val_module.__dict__[split_val[-1]]

def import_setting(component, component_name, setting):
    """Attempt to import and return a config setting."""
    value_str = pyfusion.config.pf_get(component, component_name, setting)
    return import_from_str(value_str)

def kwarg_config_handler(component_type, component_name, **kwargs):
    for config_var in pyfusion.config.pf_options(component_type, component_name):
            if not config_var in kwargs.keys():
                kwargs[config_var] = pyfusion.config.pf_get(component_type,
                                                   component_name, config_var)
    return kwargs


def get_config_as_dict(component_type, component_name):
    config_option_list = pyfusion.config.pf_options(component_type, component_name)
    config_map = lambda x: (x, pyfusion.config.pf_get(component_type, component_name, x))
    return dict(map(config_map, config_option_list))


def read_config(config_files):
    """Read config files.

    Argument is either a single file object, or a list of filenames.
    """
    try:
        pyfusion.config.readfp(config_files)
    except:
        pyfusion.config.read(config_files)

def clear_config():
    """Clear pyfusion.config."""
    import pyfusion
    pyfusion.config = pyfusion.conf.PyfusionConfigParser()
