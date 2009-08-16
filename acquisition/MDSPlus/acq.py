"""MDSPlus acquisition."""


from pyfusion.acquisition.base import BaseAcquisition

class MDSPlusAcquisition(BaseAcquisition):
    def __init__(self, server=None, *args, **kwargs):
        from MDSplus import Data
        self._Data = Data
        super(MDSPlusAcquisition, self).__init__(*args, **kwargs)

