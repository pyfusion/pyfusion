"""Base data classes."""

class BaseData:
    def __init__(self, device_name, shot_number):
        self.device_name = device_name
        self.shot_number = shot_number
