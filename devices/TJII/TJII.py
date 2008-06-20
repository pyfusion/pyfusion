"""
Device class for the TJ-II heliac
"""

import pyfusion


class TJII(pyfusion.Device):
    def __init__(self):
        self.name = 'TJII'

TJIIinst = TJII()
       
