"""
Device class for the TJ-II heliac
"""

import pyfusion
from pyfusion.data_acq.TJII.TJII import TJIIChannel
from pyfusion.data_acq.TJII import tjiidata
from pyfusion.coords import ToroidalCoordinates

def last_shot():
    return tjiidata.last_shot()

class ProcessData:
    def __init__(self, data_acq_type = '', processdata_override = ''):
        self.data_acq_type = data_acq_type
        self.processdata_override = processdata_override


    def load_channel(self, tjiich, shot):
        if self.data_acq_type == 'TJII':
            if 'INVERT' in self.processdata_override:
                invert_signal = True
            else:
                invert_signal = False
            from pyfusion.data_acq.TJII.TJII import ProcessData as _ProcessData
            pd = _ProcessData()
            return pd.load_channel(tjiich, shot, invert=invert_signal)



mirnov_5p_105 = TJIIChannel(senal='MID5P_05',name = 'mirnov_5p_105',
                            coords = ToroidalCoordinates(r=0.17947, theta=1.37, phi=0.7854))
mirnov_5p_104 = TJIIChannel(senal='MID5P_04',name = 'mirnov_5p_104',
                            coords = ToroidalCoordinates(r=0.22611, theta=1.54, phi=0.7854))
mirnov_5p_103 = TJIIChannel(senal='MID5P_03',name = 'mirnov_5p_103',
                            coords = ToroidalCoordinates(r=0.27037, theta=1.67, phi=0.7854))
mirnov_5p_102 = TJIIChannel(senal='MID5P_02',name = 'mirnov_5p_102',
                            coords = ToroidalCoordinates(r=0.31295, theta=1.8, phi=0.7854))
mirnov_5p_101 = TJIIChannel(senal='MID5P_01',name = 'mirnov_5p_101',
                            coords = ToroidalCoordinates(r=0.35371, theta=1.91, phi=0.7854))
mirnov_5p_1 = TJIIChannel(senal='MID5P1',name = 'mirnov_5p_1',
                          coords = ToroidalCoordinates(r=0.38279, theta=2.13, phi=0.7854))
mirnov_5p_2 = TJIIChannel(senal='MID5P2',name = 'mirnov_5p_2',processdata_override=['INVERT'],
                          coords = ToroidalCoordinates(r=0.40152, theta=2.29, phi=0.7854))
mirnov_5p_3 = TJIIChannel(senal='MID5P3',name = 'mirnov_5p_3',
                          coords = ToroidalCoordinates(r=0.42098, theta=2.45, phi=0.7854))
mirnov_5p_4 = TJIIChannel(senal='MID5P4',name = 'mirnov_5p_4',
                          coords = ToroidalCoordinates(r=0.44075, theta=2.6, phi=0.7854))
mirnov_5p_5 = TJIIChannel(senal='MID5P5',name = 'mirnov_5p_5',
                          coords = ToroidalCoordinates(r=0.45977, theta=2.75, phi=0.7854))
mirnov_5p_6 = TJIIChannel(senal='MID5P6',name = 'mirnov_5p_6',
                          coords = ToroidalCoordinates(r=0.47477, theta=2.88, phi=0.7854))
mirnov_5p_7 = TJIIChannel(senal='MID5P7',name = 'mirnov_5p_7',processdata_override=['INVERT'],
                          coords = ToroidalCoordinates(r=0.48509, theta=3.01, phi=0.7854))
mirnov_5p_8 = TJIIChannel(senal='MID5P8',name = 'mirnov_5p_8',
                          coords = ToroidalCoordinates(r=0.48900, theta=3.14, phi=0.7854))
mirnov_5p_9 = TJIIChannel(senal='MID5P9',name = 'mirnov_5p_9',
                          coords = ToroidalCoordinates(r=0.48509, theta=3.27, phi=0.7854))
mirnov_5p_10 = TJIIChannel(senal='MID5P10',name = 'mirnov_5p_10',
                           coords = ToroidalCoordinates(r=0.47477, theta=3.40, phi=0.7854))
mirnov_5p_11 = TJIIChannel(senal='MID5P11',name = 'mirnov_5p_11',
                           coords = ToroidalCoordinates(r=0.45977, theta=3.54, phi=0.7854))
mirnov_5p_12 = TJIIChannel(senal='MID5P12',name = 'mirnov_5p_12',
                           coords = ToroidalCoordinates(r=0.44075, theta=3.68, phi=0.7854))
mirnov_5p_13 = TJIIChannel(senal='MID5P13',name = 'mirnov_5p_13',
                           coords = ToroidalCoordinates(r=0.42098, theta=3.83, phi=0.7854))
mirnov_5p_14 = TJIIChannel(senal='MID5P14',name = 'mirnov_5p_14',processdata_override=['INVERT'],
                           coords = ToroidalCoordinates(r=0.40152, theta=3.99, phi=0.7854))
mirnov_5p_15 = TJIIChannel(senal='MID5P15',name = 'mirnov_5p_15',
                           coords = ToroidalCoordinates(r=0.38279, theta=4.15, phi=0.7854))
mirnov_5p_16 = TJIIChannel(senal='MID5P16',name = 'mirnov_5p_16',
                           coords = ToroidalCoordinates(r=0.35371, theta=4.37, phi=0.7854))
mirnov_5p_17 = TJIIChannel(senal='MID5P17',name = 'mirnov_5p_17',
                           coords = ToroidalCoordinates(r=0.31295, theta=4.49, phi=0.7854))
mirnov_5p_18 = TJIIChannel(senal='MID5P18',name = 'mirnov_5p_18',
                           coords = ToroidalCoordinates(r=0.27037, theta=4.61, phi=0.7854))
mirnov_5p_19 = TJIIChannel(senal='MID5P19',name = 'mirnov_5p_19',
                           coords = ToroidalCoordinates(r=0.22611, theta=4.74, phi=0.7854))
mirnov_5p_20 = TJIIChannel(senal='MID5P20',name = 'mirnov_5p_20',processdata_override=['INVERT'],
                           coords = ToroidalCoordinates(r=0.17947, theta=4.91, phi=0.7854))

density2 = TJIIChannel(senal='Densidad2_', name = 'density2')
densityIR = TJIIChannel(senal='DensidadMedia_IR_', name = 'densitymediaIR')

mirnov_coils = pyfusion.Diagnostic(name='mirnov_coils')

# many TJII shots have Mirnov channel MID5P_02 missing, create a diagnostic without it.
mirnov_coils_sin_102 = pyfusion.Diagnostic(name='mirnov_coils_sin_102')

mirnov_coils_channel_ordering = [mirnov_5p_105, mirnov_5p_104, mirnov_5p_103, 
                                 mirnov_5p_102, mirnov_5p_101, mirnov_5p_1,
                                 mirnov_5p_2,   mirnov_5p_3,   mirnov_5p_4,
                                 mirnov_5p_5,   mirnov_5p_6,   mirnov_5p_7,
                                 mirnov_5p_8,   mirnov_5p_9,   mirnov_5p_10,
                                 mirnov_5p_11,  mirnov_5p_12,  mirnov_5p_13,
                                 mirnov_5p_14,  mirnov_5p_15,  mirnov_5p_16,
                                 mirnov_5p_17,  mirnov_5p_18,  mirnov_5p_19,
                                 mirnov_5p_20]

mirnov_coils_channel_ordering_sin_102 = [mirnov_5p_105, mirnov_5p_104, mirnov_5p_103, 
                                 mirnov_5p_101, mirnov_5p_1,
                                 mirnov_5p_2,   mirnov_5p_3,   mirnov_5p_4,
                                 mirnov_5p_5,   mirnov_5p_6,   mirnov_5p_7,
                                 mirnov_5p_8,   mirnov_5p_9,   mirnov_5p_10,
                                 mirnov_5p_11,  mirnov_5p_12,  mirnov_5p_13,
                                 mirnov_5p_14,  mirnov_5p_15,  mirnov_5p_16,
                                 mirnov_5p_17,  mirnov_5p_18,  mirnov_5p_19,
                                 mirnov_5p_20]

for ch in mirnov_coils_channel_ordering:
    mirnov_coils.add_channel(ch)

for ch in mirnov_coils_channel_ordering_sin_102:
    mirnov_coils_sin_102.add_channel(ch)


density_diag = pyfusion.Diagnostic(name='density')
densityIR_diag = pyfusion.Diagnostic(name='densityIR')

for ch in [density2]:
    density_diag.add_channel(ch)

for ch in [densityIR]:
    densityIR_diag.add_channel(ch)


class TJII(pyfusion.Device):
    def __init__(self):
        self.name = 'TJII'

TJIIinst = TJII()
       
