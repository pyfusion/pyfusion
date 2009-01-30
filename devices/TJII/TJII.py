"""
Device class for the TJ-II heliac
"""

import pyfusion
from pyfusion.data_acq.TJII.TJII import TJIIChannel
from pyfusion.data_acq.TJII import tjiidata
from pyfusion.coords import ToroidalCoordinates
from datetime import datetime
from sqlalchemy import Column, Float, Integer, ForeignKey, String, Boolean

DEFAULT_SHOT_CLASS = 'TJIIShot'

class TJIIShot(pyfusion.core.Shot):
    __tablename__ = 'tjii_customshot'
    __mapper_args__ = {'polymorphic_identity':'TJII'}
    id = Column('id', Integer, ForeignKey('shots.id'), primary_key=True, index=True)
    config = Column('config', String(20))
    iota_0 = Column('iota_0', Float)
    iota_a = Column('iota_a', Float)
    iota_2_3 = Column('iota_2_3', Float)
    volume = Column('volume', Float)
    minor_radius = Column('minor_radius', Float)
    gas = Column('gas', String(2))
    field_direction = Column('field_direction', String(4))
    nbi = Column('nbi', Boolean)

def get_shot_datetime(shot_number):
    dlist = tjiidata.fecha(shot_number)
    return datetime(dlist[3],dlist[2],dlist[1],dlist[4],dlist[5])

def get_signals_for_shot(shot_number):
    nsignals = tjiidata.nums(shot_number)
    signal_str = tjiidata.listas(shot_number, nsignals)[1]
    sig_str_list = signal_str.split('\x00')
    output = []
    for i in sig_str_list:
        if i != '':
            output.append(i)
    return output


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

cbol01 = TJIIChannel(senal='CBOL1', name = 'cbol01')
cbol02 = TJIIChannel(senal='CBOL2', name = 'cbol02')
cbol03 = TJIIChannel(senal='CBOL3', name = 'cbol03')
cbol04 = TJIIChannel(senal='CBOL4', name = 'cbol04')
cbol05 = TJIIChannel(senal='CBOL5', name = 'cbol05')
cbol06 = TJIIChannel(senal='CBOL6', name = 'cbol06')
cbol07 = TJIIChannel(senal='CBOL7', name = 'cbol07')
cbol08 = TJIIChannel(senal='CBOL8', name = 'cbol08')
cbol09 = TJIIChannel(senal='CBOL9', name = 'cbol09')
cbol10 = TJIIChannel(senal='CBOL10', name = 'cbol10')
cbol11 = TJIIChannel(senal='CBOL11', name = 'cbol11')
cbol12 = TJIIChannel(senal='CBOL12', name = 'cbol12')
cbol13 = TJIIChannel(senal='CBOL13', name = 'cbol13')
cbol14 = TJIIChannel(senal='CBOL14', name = 'cbol14')
cbol15 = TJIIChannel(senal='CBOL15', name = 'cbol15')
cbol16 = TJIIChannel(senal='CBOL16', name = 'cbol16')

mirnov_coils = pyfusion.Diagnostic(name='mirnov_coils')

# many TJII shots have Mirnov channel MID5P_02 missing, create a diagnostic without it.
mirnov_coils_sin_102 = pyfusion.Diagnostic(name='mirnov_coils_sin_102')

# early shots only had the 15 original Mirnov coils
mirnov_coils_original = pyfusion.Diagnostic(name='mirnov_coils_original')

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

mirnov_coils_channel_ordering_original = [mirnov_5p_1,
                                 mirnov_5p_2,   mirnov_5p_3,   mirnov_5p_4,
                                 mirnov_5p_5,   mirnov_5p_6,   mirnov_5p_7,
                                 mirnov_5p_8,   mirnov_5p_9,   mirnov_5p_10,
                                 mirnov_5p_11,  mirnov_5p_12,  mirnov_5p_13,
                                 mirnov_5p_14,  mirnov_5p_15]


cbol_channels = [cbol01, cbol02, cbol03, cbol04, cbol05, cbol06, cbol07, cbol08, 
                 cbol09, cbol10, cbol11, cbol12, cbol13, cbol14, cbol15, cbol16]

cbol_channels_no_sat = [cbol01, cbol02, cbol03, 
                               cbol12, cbol13, cbol14, cbol15, cbol16]

for ch in mirnov_coils_channel_ordering:
    mirnov_coils.add_channel(ch)

for ch in mirnov_coils_channel_ordering_sin_102:
    mirnov_coils_sin_102.add_channel(ch)

for ch in mirnov_coils_channel_ordering_original:
    mirnov_coils_original.add_channel(ch)



density_diag = pyfusion.Diagnostic(name='density')
densityIR_diag = pyfusion.Diagnostic(name='densityIR')
cbol_diag = pyfusion.Diagnostic(name='cbol')
cbol_diag_no_sat = pyfusion.Diagnostic(name='cbol_no_sat')

for ch in [density2]:
    density_diag.add_channel(ch)

for ch in [densityIR]:
    densityIR_diag.add_channel(ch)

#for ch in cbol_channels:
#    cbol_diag.add_channel(ch)

for ch in cbol_channels_no_sat:
    cbol_diag_no_sat.add_channel(ch)


mirnov_filter_diag = pyfusion.Diagnostic('mirnov_filter')

mirnov_small = pyfusion.Diagnostic('mirnov_small')
small_chans=5  # keep it small

for ch in [mirnov_5p_1]:
    mirnov_filter_diag.add_channel(ch)
    mirnov_small.add_channel(ch)

for c, ch in enumerate(mirnov_coils_channel_ordering_sin_102):
    if c<small_chans: mirnov_small.add_channel(ch)


class TJII(pyfusion.Device):
    def __init__(self):
        self.name = 'TJII'

TJIIinst = TJII()
       
