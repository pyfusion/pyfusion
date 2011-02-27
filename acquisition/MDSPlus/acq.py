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
    """
    # shouldn't need this, as BaseAcquisition now passes itself to
    #    data fetcher
    def getdata(self, shot, *args, **kwargs):
        kwargs.update({'_Data':self._Data})
        return super(MDSPlusAcquisition, self).getdata(shot,*args, **kwargs)
    """


class MDSPlusLocalAcquisition(BaseAcquisition):
    pass
