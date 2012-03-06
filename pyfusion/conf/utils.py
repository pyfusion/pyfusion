""" Useful functions for manipulating config files."""

from ConfigParser import NoSectionError
import pyfusion
from numpy import sort, shape

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


def dump():
    buff = []
    sections = pyfusion.config.sections()
    front = []
    back = []
    for section in sections:
        if section.find(':') < 0:
            front.append(section)
        else:
            back.append(section)    

    for sec in sort(front).tolist() + sort(back).tolist():
        buff.append("[%s]:" % sec)
        for option in sort(pyfusion.config.options(sec)):
            buff.append("%s = %s" %(option, pyfusion.config.get(sec, option)))

    # append all config filenames in order loaded        
    hist = pyfusion.conf.history        
    ordered_keys = sort(hist.keys())
    for key in ordered_keys: 
        buff.append(hist[key][0])
    return(buff)    

def diff(dumpa=None, dumpb=None):
    """ use /usr/bin/diff or alternative in PYFUSION_DIFF to show the differences
    adding a config file made.
    key gives the read sequence of files - this would be lost in a dictionary
    """
    if dumpa == None:
        pf_hist = pyfusion.conf.history
        seq = sort(pf_hist.keys())
        for s in seq[0:-1]:
            diff(pf_hist[seq[s]], pf_hist[seq[s+1]])
        return

    import os
    fa = '/tmp/filea'
    fb = '/tmp/fileb'
    filea = open(fa,'w')
    filea.writelines([lin+'\n' for lin in dumpa])
    filea.close()
    fileb = open(fb,'w')
    fileb.writelines([lin+'\n' for lin in dumpb])
    fileb.close()
    diffprog = os.getenv('PYFUSION_DIFF','/usr/bin.diff')
    os.spawnvp(os.P_NOWAIT,diffprog,[diffprog,fa, fb])


def read_config(config_files):
    """Read config files.

    Argument is either a single file object, or a list of filenames.
    """
    try:
        existing_database = pyfusion.config.get('global', 'database')
    except NoSectionError:
        existing_database = 'None'

    try:
        # note - history not kept for file objects yet - should be easy to add.
        files_read = pyfusion.config.readfp(config_files)
        if pyfusion.VERBOSE>0: 
            for f in config_files: print f.name
    except:
        files_read = []
        if len(shape(config_files))==0: config_files = [config_files]
        for config_file in config_files:
            if pyfusion.VERBOSE>0: 
                print(config_file)

            files_read.append(pyfusion.config.read(config_file))
            # the history dict has each cfg file followed by the ensuing config.
            # keyed by the time sequence
            pyfusion.conf.history.update({len(pyfusion.conf.history.keys()): 
                                          [config_file] +dump()})

    if files_read != None: # readfp returns None
        if len(files_read) == 0: 
            raise LookupError, str('failed to read config files from [%s]' %
                                   (config_files))
        
    config_database  = pyfusion.config.get('global', 'database')

    if config_database.lower() != existing_database.lower():
        pyfusion.orm_manager.shutdown_orm() 
        if config_database.lower() != 'none':
            pyfusion.orm_manager.load_orm()

def clear_config():
    """Clear pyfusion.config."""
    import pyfusion
    pyfusion.config = pyfusion.conf.PyfusionConfigParser()
