"""Utilities for malipulating acquisition objects."""

from pyfusion.conf import config
from pyfusion.conf.utils import import_setting

def get_acq_from_config(acq_name):
    """Return acquisition class for acq. name, as defined in config."""
    acq_class = import_setting('Acquisition', acq_name, "acq_class")
    return acq_class

def getAcquisition(acq_name):
    """Instantiate an acquisition class as defined in config."""
    acq_class = get_acq_from_config(acq_name)
    return acq_class(acq_name)
