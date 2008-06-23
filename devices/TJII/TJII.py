"""
Device class for the TJ-II heliac
"""

import pyfusion
from pyfusion.data_acq.TJII.TJII import TJIIChannel

mirnov_test = TJIIChannel(senal='MID5P10',name = 'testmirnov')
mirnov_test2 = TJIIChannel(senal='MID5P11',name = 'testmirnov2')

test_diag = pyfusion.Diagnostic(name='testtjii')
test_diag.add_channel(mirnov_test)
test_diag.add_channel(mirnov_test2)

class TJII(pyfusion.Device):
    def __init__(self):
        self.name = 'TJII'

TJIIinst = TJII()
       
