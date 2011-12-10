"""Heliotron J acquisition module."""
from pyfusion.acquisition.base import BaseAcquisition


class HeliotronJAcquisition(BaseAcquisition):
    """Acquisition class for HeliotronJ data system.

    """
    def __init__(self, *args, **kwargs):
        super(HeliotronJAcquisition, self).__init__(*args, **kwargs)

