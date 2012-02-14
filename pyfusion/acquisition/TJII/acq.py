"""TJ-II acquisition."""
from pyfusion.acquisition.base import BaseAcquisition

try:
    import tjiidata
except:
    # don't raise an exception - otherwise tests will fail.
    # TODO: this should go into logfile
    print  "Can't import TJ-II data aquisition library"

# to use tjii local_data, create a zero length file tjiidata.py (don't add to SVN!)

class TJIIAcquisition(BaseAcquisition):
    """Acquisition class for TJII data system.

    """
    def __init__(self, *args, **kwargs):
        super(TJIIAcquisition, self).__init__(*args, **kwargs)

