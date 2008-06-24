"""
Device class for the TJ-II heliac
"""

import pyfusion
from pyfusion.data_acq.TJII.TJII import TJIIChannel



mirnov_5p_1 = TJIIChannel(senal='MID5P1',name = 'mirnov_5p_1')
mirnov_5p_2 = TJIIChannel(senal='MID5P2',name = 'mirnov_5p_2')
mirnov_5p_3 = TJIIChannel(senal='MID5P3',name = 'mirnov_5p_3')
mirnov_5p_4 = TJIIChannel(senal='MID5P4',name = 'mirnov_5p_4')
mirnov_5p_5 = TJIIChannel(senal='MID5P5',name = 'mirnov_5p_5')
mirnov_5p_6 = TJIIChannel(senal='MID5P6',name = 'mirnov_5p_6')
mirnov_5p_7 = TJIIChannel(senal='MID5P7',name = 'mirnov_5p_7')
mirnov_5p_8 = TJIIChannel(senal='MID5P8',name = 'mirnov_5p_8')
mirnov_5p_9 = TJIIChannel(senal='MID5P9',name = 'mirnov_5p_9')
mirnov_5p_10 = TJIIChannel(senal='MID5P10',name = 'mirnov_5p_10')
mirnov_5p_11 = TJIIChannel(senal='MID5P11',name = 'mirnov_5p_11')
mirnov_5p_12 = TJIIChannel(senal='MID5P12',name = 'mirnov_5p_12')
mirnov_5p_13 = TJIIChannel(senal='MID5P13',name = 'mirnov_5p_13')
mirnov_5p_14 = TJIIChannel(senal='MID5P14',name = 'mirnov_5p_14')
mirnov_5p_15 = TJIIChannel(senal='MID5P15',name = 'mirnov_5p_15')
mirnov_5p_16 = TJIIChannel(senal='MID5P16',name = 'mirnov_5p_16')
mirnov_5p_17 = TJIIChannel(senal='MID5P17',name = 'mirnov_5p_17')
mirnov_5p_18 = TJIIChannel(senal='MID5P18',name = 'mirnov_5p_18')
mirnov_5p_19 = TJIIChannel(senal='MID5P19',name = 'mirnov_5p_19')
mirnov_5p_20 = TJIIChannel(senal='MID5P20',name = 'mirnov_5p_20')
mirnov_5p_101 = TJIIChannel(senal='MID5P_01',name = 'mirnov_5p_101')
mirnov_5p_102 = TJIIChannel(senal='MID5P_02',name = 'mirnov_5p_102')
mirnov_5p_103 = TJIIChannel(senal='MID5P_03',name = 'mirnov_5p_103')
mirnov_5p_104 = TJIIChannel(senal='MID5P_04',name = 'mirnov_5p_104')
mirnov_5p_105 = TJIIChannel(senal='MID5P_05',name = 'mirnov_5p_105')


mirnov_coils = pyfusion.Diagnostic(name='mirnov_coils')
for ch in [mirnov_5p_1,mirnov_5p_2, mirnov_5p_3, mirnov_5p_4,mirnov_5p_5,mirnov_5p_6,mirnov_5p_7,mirnov_5p_8,mirnov_5p_9,mirnov_5p_10,mirnov_5p_11,mirnov_5p_12,mirnov_5p_13,mirnov_5p_14,mirnov_5p_15,mirnov_5p_16,mirnov_5p_17,mirnov_5p_18,mirnov_5p_19,mirnov_5p_20,mirnov_5p_101,mirnov_5p_102,mirnov_5p_103,mirnov_5p_104,mirnov_5p_105]:
    mirnov_coils.add_channel(ch)


class TJII(pyfusion.Device):
    def __init__(self):
        self.name = 'TJII'

TJIIinst = TJII()
       
