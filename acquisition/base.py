"""Base classes for pyfusion data acquisition."""

from pyfusion.data.timeseries import SCTData

class BaseAcquisition:
    def __init__(self, device_name, shots, channels, data_class):
        self.data_class = data_class
        self.device_name = device_name
        self.shot_number = shots
    def getdata(self):
        return self.data_class(device_name=self.device_name, shot_number=self.shot_number)
