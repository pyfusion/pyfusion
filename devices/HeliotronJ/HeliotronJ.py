"""
Code specific to Heliotron J
"""
import pyfusion
from pyfusion.data_acq.HJ.HJ import HJChannel

DEFAULT_SHOT_CLASS = 'Shot'

diag_dict =  {'NBIS9I':1024,  \
              'NBIS10I':1024, \
              'NBIS910V':1024,\
              'NBIS3I':1024,  \
              'NBIS4I':1024,  \
              'NBIS34V':1024, \
              'ECHRG500':1024,\
              'ECHG2':1024,   \
              'ECHG4T':1024,  \
              'ECHG4':1024,   \
              'ECHRG500B':1024,\
              'ICRFP1':1024,  \
              'ICRFP2':1024,  \
              'ICRFP3':1024,  \
              'ICRFP4':1024,  \
              'GASPUFF#1':1024,\
              'GASPUFF#2':1024,\
              'GASPUFF#9.5':2048,\
              'GASPUFF#15.5':2048,\
              'HALPHA3.5':2048,\
              'HALPHA7.5':2048,\
              'HALPHA11.5':2048,\
              'HALPHA15.5':2048,\
              'VISIBLE1':1024,\
              'VISIBLE2':1024,\
              'VISIBLE3':1024,\
              'VISIBLE4':1024,\
              'VISIBLEMONITOR':1024,\
              'BOLOMETER14':1024,\
              'BOLOMETER26':1024,\
              'AXUV':1024,\
              'SX1.6AL':1024,\
              'SX6AL':1024,\
              'SXTEMP':1024,\
              'IS9FAST':1024*256,\
              'VF11FAST':1024*256,\
              'DP-2RLP':1024*256,\
              'DP-2RLP':1024*256,\
              'MP1':1024*256,\
              'MP2':1024*256,\
              'MP3':1024*256,\
              'MP4':1024*256,\
              'PMP1':1024*256,\
              'PMP2':1024*256,\
              'PMP3':1024*256,\
              'PMP4':1024*256,\
              'PMP5':1024*256,\
              'PMP6':1024*256,\
              'PMP7':1024*256,\
              'PMP8':1024*256,\
              'PMP9':1024*256,\
              'PMP10':1024*256,\
              'PMP11':1024*256,\
              'PMP12':1024*256,\
              'PMP13':1024*256,\
              'PMP14':1024*256,\
              'ECE1FAST':1024*16,\
              'ECE2FAST':1024*16,\
              'ECE3FAST':1024*16,\
              'ECE4FAST':1024*16,\
              'ECE5FAST':1024*16,\
              'ECE6FAST':1024*16,\
              'ECE7FAST':1024*16,\
              'ECE8FAST':1024*16,\
              'ECE9FAST':1024*16,\
              'ECE10FAST':1024*16,\
              'ECE11FAST':1024*16,\
              'ECE12FAST':1024*16,\
              'ECE13FAST':1024*16,\
              'ECE14FAST':1024*16,\
              'ECE15FAST':1024*16,\
              'ECE16FAST':1024*16,\
              'SXR001':1024,\
              'SXR002':1024,\
              'SXR003':1024,\
              'SXR004':1024,\
              'SXR005':1024,\
              'SXR006':1024,\
              'SXR007':1024,\
              'SXR008':1024,\
              'SXR009':1024,\
              'SXR010':1024,\
              'SXR011':1024,\
              'SXR012':1024,\
              'SXR013':1024,\
              'SXR014':1024,\
              'SXR015':1024,\
              'SXR016':1024,\
              'SXR017':1024,\
              'SXR018':1024,\
              'SXR019':1024,\
              'SXR020':1024 \
              }
              
PMP_diagnostic = pyfusion.Diagnostic(name='PMP')

PMP1 = HJChannel(name='PMP1', length=diag_dict['PMP1'])
PMP2 = HJChannel(name='PMP2', length=diag_dict['PMP2'])
PMP3 = HJChannel(name='PMP3', length=diag_dict['PMP3'])
PMP4 = HJChannel(name='PMP4', length=diag_dict['PMP4'])
PMP5 = HJChannel(name='PMP5', length=diag_dict['PMP5'])
PMP6 = HJChannel(name='PMP6', length=diag_dict['PMP6'])
PMP7 = HJChannel(name='PMP7', length=diag_dict['PMP7'])
PMP8 = HJChannel(name='PMP8', length=diag_dict['PMP8'])
PMP9 = HJChannel(name='PMP9', length=diag_dict['PMP9'])
PMP10 = HJChannel(name='PMP10', length=diag_dict['PMP10'])
PMP11 = HJChannel(name='PMP11', length=diag_dict['PMP11'])
PMP12 = HJChannel(name='PMP12', length=diag_dict['PMP12'])
PMP13 = HJChannel(name='PMP13', length=diag_dict['PMP13'])
PMP14 = HJChannel(name='PMP14', length=diag_dict['PMP14'])

for ch in [PMP1, PMP2, PMP3, PMP4, PMP5, PMP6, PMP7, PMP8, PMP9, PMP10, PMP11, PMP12, PMP13, PMP14]:
    PMP_diagnostic.add_channel(ch)

class HeliotronJ(pyfusion.Device):
    def __init__(self):
        self.name = 'HeliotronJ'
        
HJinst = HeliotronJ()
