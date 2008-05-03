"""
Code specific to Heliotron J
"""
import pyfusion

class HeliotronJ(pyfusion.Device):
    def __init__(self):
        self.name = 'HeliotronJ'
        
HJinst = HeliotronJ()
