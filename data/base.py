"""Base data classes."""

class BaseData:
    """Base class for handling processed data.

    In general, specialised subclasses of BaseData will be used
    to handle processed data rather than BaseData itself.

    Usage: BaseData(device_name, shot_number)

    Arguments:
    device_name -- name of device as specified in configuration
      file, i.e. [Device:device_name]
    shot_number -- number of the shot from where he data was acquired.
    
    """
    def __init__(self, device_name, shot_number):
        self.device_name = device_name
        self.shot_number = shot_number
