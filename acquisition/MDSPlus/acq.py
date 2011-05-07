"""MDSPlus acquisition."""


from pyfusion.acquisition.base import BaseAcquisition

class MDSPlusAcquisition(BaseAcquisition):
    def __init__(self, *args, **kwargs):
        from MDSplus import Data
        self._Data = Data
        super(MDSPlusAcquisition, self).__init__(*args, **kwargs)
        result=self._Data.execute("mdsconnect('%(server)s')" %{'server':self.server})
        # existing error info does not give server name
        if (result==0): print('Error connecting to %s' %
                                  ( self.server))

    def __del__(self):
        self._Data.execute("mdsdisconnect()")

class MDSPlusLocalAcquisition(BaseAcquisition):
    pass
