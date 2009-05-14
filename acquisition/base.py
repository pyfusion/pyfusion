"""Base classes for pyfusion data acquisition."""

from pyfusion.data.timeseries import SCTData

class BaseAcquisition:
    """Base class for data acquisition.

    Usage: BaseAcquisition(device_name, shot, channel, data_class)
    
    Arguments:
    device_name -- name of device as specified in configuration file.
    shot --------- shot number. TODO: should work as iterator?
    channel ------ channel name: TODO: should work as iterator?

    TODO: keyword arguments to override config settings...
    """
    def __init__(self, device_name, shot, channel):
        self.device_name = device_name
        self.shot_number = shot

    def getdata(self):
        """Get the data and return prescribed subclass of BaseData."""
        return self.data_class(device_name=self.device_name,
                               shot_number=self.shot_number)
