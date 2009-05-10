"""Timeseries data classes."""

from pyfusion.data.base import BaseData

class SCTData(BaseData):
    """Single Channel Timeseries (SCT) data."""
    timebase = []
    signal = []
    device_name = None

class MCTData(BaseData):
    """Single Channel Timeseries (MCT) data."""
    pass
