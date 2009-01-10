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
              'HAARRAY01':20000,\
              'HAARRAY02':20000,\
              'HAARRAY03':20000,\
              'HAARRAY04':20000,\
              'HAARRAY05':20000,\
              'HAARRAY06':20000,\
              'HAARRAY07':20000,\
              'HAARRAY08':20000,\
              'HAARRAY09':20000,\
              'HAARRAY10':20000,\
              'HAARRAY11':20000,\
              'HAARRAY12':20000,\
              'HAARRAY13':20000,\
              'HAARRAY14':20000,\
              'HAARRAY15':20000,\
              'HAARRAY16':20000,\
              'HAARRAY17':20000,\
              'HAARRAY18':20000,\
              'HAARRAY19':20000,\
              'HAARRAY20':20000,\
              'HAARRAY21':20000,\
              'HAARRAY22':20000,\
              'HAARRAY23':20000,\
              'HAARRAY24':20000,\
              'HAARRAY25':20000,\
              'HAARRAY26':20000,\
              'HAARRAY27':20000,\
              'HAARRAY28':20000,\
              'HAARRAY29':20000,\
              'HAARRAY30':20000,\
              'HAARRAY31':20000,\
              'HAARRAY32':20000,\
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
              'MICRO01':8192,\
              'MICROFAST':256*1024,\
              'AXUV':1024,\
              'AXUV1':2048,\
              'AXUV2':2048,\
              'AXUV3':2048,\
              'AXUV4':2048,\
              'AXUV5':2048,\
              'AXUV6':2048,\
              'AXUV7':2048,\
              'AXUV8':2048,\
              'AXUV9':2048,\
              'AXUV10':2048,\
              'AXUV11':2048,\
              'AXUV12':2048,\
              'AXUV13':2048,\
              'AXUV14':2048,\
              'AXUV15':2048,\
              'AXUV16':2048,\
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

MP_ALL_diagnostic = pyfusion.Diagnostic(name='MP_ALL')

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
    MP_ALL_diagnostic.add_channel(ch)

MP_diagnostic = pyfusion.Diagnostic(name='MP')
MP1 = HJChannel(name='MP1', length=diag_dict['MP1'])
MP2 = HJChannel(name='MP2', length=diag_dict['MP2'])
MP3 = HJChannel(name='MP3', length=diag_dict['MP3'])
MP4 = HJChannel(name='MP4', length=diag_dict['MP4'])
for ch in [MP1, MP2, MP3, MP4]:
    MP_diagnostic.add_channel(ch)
    MP_ALL_diagnostic.add_channel(ch)

HAARRAY_diagnostic = pyfusion.Diagnostic(name='HA')
HA01 = HJChannel(name='HAARRAY01', length=diag_dict['HAARRAY01'])
HA02 = HJChannel(name='HAARRAY02', length=diag_dict['HAARRAY02'])
HA03 = HJChannel(name='HAARRAY03', length=diag_dict['HAARRAY03'])
HA04 = HJChannel(name='HAARRAY04', length=diag_dict['HAARRAY04'])
HA05 = HJChannel(name='HAARRAY05', length=diag_dict['HAARRAY05'])
HA06 = HJChannel(name='HAARRAY06', length=diag_dict['HAARRAY06'])
HA07 = HJChannel(name='HAARRAY07', length=diag_dict['HAARRAY07'])
HA08 = HJChannel(name='HAARRAY08', length=diag_dict['HAARRAY08'])
HA09 = HJChannel(name='HAARRAY09', length=diag_dict['HAARRAY09'])
HA10 = HJChannel(name='HAARRAY10', length=diag_dict['HAARRAY10'])
HA11 = HJChannel(name='HAARRAY11', length=diag_dict['HAARRAY11'])
HA12 = HJChannel(name='HAARRAY12', length=diag_dict['HAARRAY12'])
HA13 = HJChannel(name='HAARRAY13', length=diag_dict['HAARRAY13'])
HA14 = HJChannel(name='HAARRAY14', length=diag_dict['HAARRAY14'])
HA15 = HJChannel(name='HAARRAY15', length=diag_dict['HAARRAY15'])
HA16 = HJChannel(name='HAARRAY16', length=diag_dict['HAARRAY16'])
HA17 = HJChannel(name='HAARRAY17', length=diag_dict['HAARRAY17'])
HA18 = HJChannel(name='HAARRAY18', length=diag_dict['HAARRAY18'])
HA19 = HJChannel(name='HAARRAY19', length=diag_dict['HAARRAY19'])
HA20 = HJChannel(name='HAARRAY20', length=diag_dict['HAARRAY20'])
HA21 = HJChannel(name='HAARRAY21', length=diag_dict['HAARRAY21'])
HA22 = HJChannel(name='HAARRAY22', length=diag_dict['HAARRAY22'])
HA23 = HJChannel(name='HAARRAY23', length=diag_dict['HAARRAY23'])
HA24 = HJChannel(name='HAARRAY24', length=diag_dict['HAARRAY24'])
HA25 = HJChannel(name='HAARRAY25', length=diag_dict['HAARRAY25'])
HA26 = HJChannel(name='HAARRAY26', length=diag_dict['HAARRAY26'])
HA27 = HJChannel(name='HAARRAY27', length=diag_dict['HAARRAY27'])
HA28 = HJChannel(name='HAARRAY28', length=diag_dict['HAARRAY28'])
HA29 = HJChannel(name='HAARRAY29', length=diag_dict['HAARRAY29'])
HA30 = HJChannel(name='HAARRAY30', length=diag_dict['HAARRAY30'])
HA31 = HJChannel(name='HAARRAY31', length=diag_dict['HAARRAY31'])
HA32 = HJChannel(name='HAARRAY32', length=diag_dict['HAARRAY32'])

for ch in [HA01, HA02, HA03, HA04, HA05, HA06, HA07, HA08, HA09, HA10, 
           HA11, HA12, HA13, HA14, HA15, HA16, HA17, HA18, HA19, HA20, 
           HA21, HA22, HA23, HA24, HA25, HA26, HA27, HA28, HA29, HA30, 
           HA31, HA32 ]:
    HAARRAY_diagnostic.add_channel(ch)

MISC_diagnostic = pyfusion.Diagnostic(name='MISC')
MICRO01 = HJChannel(name='MICRO01', length=diag_dict['MICRO01'])
MICROFAST = HJChannel(name='MICROFAST', length=diag_dict['MICROFAST'])

# can't put both here, different time base
for ch in [MICROFAST]:
    MISC_diagnostic.add_channel(ch)

AXUV_diagnostic = pyfusion.Diagnostic(name='AXUV')
AXUV1 = HJChannel(name='AXUV1', length=diag_dict['AXUV1'])
AXUV2 = HJChannel(name='AXUV2', length=diag_dict['AXUV2'])
AXUV3 = HJChannel(name='AXUV3', length=diag_dict['AXUV3'])
AXUV4 = HJChannel(name='AXUV4', length=diag_dict['AXUV4'])
AXUV5 = HJChannel(name='AXUV5', length=diag_dict['AXUV5'])
AXUV6 = HJChannel(name='AXUV6', length=diag_dict['AXUV6'])
AXUV7 = HJChannel(name='AXUV7', length=diag_dict['AXUV7'])
AXUV8 = HJChannel(name='AXUV8', length=diag_dict['AXUV8'])
AXUV9 = HJChannel(name='AXUV9', length=diag_dict['AXUV9'])
AXUV10 = HJChannel(name='AXUV10', length=diag_dict['AXUV10'])
AXUV11 = HJChannel(name='AXUV11', length=diag_dict['AXUV11'])
AXUV12 = HJChannel(name='AXUV12', length=diag_dict['AXUV12'])
AXUV13 = HJChannel(name='AXUV13', length=diag_dict['AXUV13'])
AXUV14 = HJChannel(name='AXUV14', length=diag_dict['AXUV14'])
AXUV15 = HJChannel(name='AXUV15', length=diag_dict['AXUV15'])
AXUV16 = HJChannel(name='AXUV16', length=diag_dict['AXUV16'])

for ch in [
   AXUV1, AXUV2, AXUV3, AXUV4, AXUV5, AXUV6, AXUV7, AXUV8, AXUV9, AXUV10, 
   AXUV11, AXUV12, AXUV13, AXUV14, AXUV15, AXUV16]:
    AXUV_diagnostic.add_channel(ch)

class HeliotronJ(pyfusion.Device):
    def __init__(self):
        self.name = 'HeliotronJ'
        
HJinst = HeliotronJ()
