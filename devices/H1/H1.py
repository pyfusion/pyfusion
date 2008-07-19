"""
Device class for the H-1 heliac
"""

import pyfusion
from pyfusion.data_acq.MDSPlus.MDSPlus import MDSPlusChannel
#from pyfusion.settings import H1_MDS_SERVER
from h1data_dtacq_shot_offset import h1data_dtacq_mapping
from numpy import searchsorted
from sqlalchemy import Column, Float, Integer, ForeignKey
from pyfusion.core import Shot

H1_MDS_SERVER = pyfusion.settings.H1_MDS_SERVER

class H1Shot(Shot):
    __tablename__ = 'h1_customshot'
    __mapper_args__ = {'polymorphic_identity':'H1'}
    id = Column('id', Integer, ForeignKey('shots.id'), primary_key=True)
    kappa_h = Column('kappa_h',Float)

class ProcessData:
    def __init__(self, data_acq_type = '', processdata_override = ''):
        self.data_acq_type = data_acq_type
        self.processdata_override = processdata_override


    def load_channel(self, mdsch, shot):
        if self.data_acq_type == 'MDSPlus':
            if 'INVERT' in self.processdata_override:
                invert_signal = True
            else:
                invert_signal = False
            if 'DTACQ' in self.processdata_override:
                [_shot,dtacq_shift] = h1data_dtacq_mapping[str(shot)]
                from pyfusion.data_acq.MDSPlus.MDSPlus import _loadmds
                [dim_data,data] = _loadmds(mdsch, _shot, invert=invert_signal)
                if dtacq_shift > 0:
                    dim_data = dim_data[dtacq_shift:]
                    data = data[:-dtacq_shift]
                elif dtacq_shift < 0:
                    dim_data = dim_data[:dtacq_shift]
                    data = data[-dtacq_shift:]
                t_lim = searchsorted(dim_data,[pyfusion.settings.SHOT_T_MIN, pyfusion.settings.SHOT_T_MAX])
                output_MCT = pyfusion.MultiChannelTimeseries(dim_data[t_lim[0]:t_lim[1]])
                output_MCT.add_channel(data[t_lim[0]:t_lim[1]], mdsch.name)
                return output_MCT    
            else:
                _shot = shot
            from pyfusion.data_acq.MDSPlus.MDSPlus import ProcessData as _ProcessData
            pd = _ProcessData()
            return pd.load_channel(mdsch, _shot, invert=invert_signal)


mirnov_1_1  = MDSPlusChannel(name = 'mirnov_1_1', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
                             mds_path='.operations.mirnov:a14_14:input_1', 
                             coords = pyfusion.CylindricalCoordinates(r=1.114, phi=0.7732, z=0.355))

mirnov_1_2  = MDSPlusChannel(name = 'mirnov_1_2',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
                             mds_path='.operations.mirnov:a14_14:input_2',
                             coords = pyfusion.CylindricalCoordinates(r=1.185, phi=0.7732, z=0.289))

mirnov_1_3  = MDSPlusChannel(name = 'mirnov_1_3',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
                             mds_path='.operations.mirnov:a14_14:input_3',
                             coords = pyfusion.CylindricalCoordinates(r=1.216, phi=0.7732, z=0.227))

mirnov_1_4  = MDSPlusChannel(name = 'mirnov_1_4',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
                             mds_path='.operations.mirnov:a14_14:input_4',
                             coords = pyfusion.CylindricalCoordinates(r=1.198, phi=0.7732, z=0.137))

#mirnov_1_5  = MDSPlusChannel(name = 'mirnov_1_5',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
#                             mds_path='',
#                             coords = pyfusion.CylindricalCoordinates(r=1.129, phi=0.7732, z=0.123))

#mirnov_1_6  = MDSPlusChannel(name = 'mirnov_1_6',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
#                             mds_path='',
#                             coords = pyfusion.CylindricalCoordinates(r=1.044, phi=0.7732, z=0.128))

mirnov_1_7  = MDSPlusChannel(name = 'mirnov_1_7',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
                             mds_path='.operations.mirnov:a14_14:input_6',
                             coords = pyfusion.CylindricalCoordinates(r=0.963, phi=0.7732, z=0.112))

mirnov_1_8  = MDSPlusChannel(name = 'mirnov_1_8',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
                             mds_path='.operations.mirnov:a14_15:input_1',
                             coords = pyfusion.CylindricalCoordinates(r=0.924, phi=0.7732, z=0.087))

mirnov_1_9  = MDSPlusChannel(name = 'mirnov_1_9',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
                             mds_path='.operations.mirnov:a14_15:input_2',
                             coords = pyfusion.CylindricalCoordinates(r=0.902, phi=0.7732, z=0.052))

mirnov_1_10 = MDSPlusChannel(name = 'mirnov_1_10', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
                             mds_path='.operations.mirnov:a14_15:input_3',
                             coords = pyfusion.CylindricalCoordinates(r=0.900, phi=0.7732, z=-0.008))

#mirnov_1_11 = MDSPlusChannel(name = 'mirnov_1_11', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
#                             mds_path='',
#                             coords = pyfusion.CylindricalCoordinates(r=0.925, phi=0.7732, z=-0.073))

#mirnov_1_12 = MDSPlusChannel(name = 'mirnov_1_12', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
#                             mds_path='',
#                             coords = pyfusion.CylindricalCoordinates(r=0.964, phi=0.7732, z=-0.169))

#mirnov_1_13 = MDSPlusChannel(name = 'mirnov_1_13', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
#                             mds_path='',
#                             coords = pyfusion.CylindricalCoordinates(r=0.897, phi=0.7732, z=-0.238))

#mirnov_1_14 = MDSPlusChannel(name = 'mirnov_1_14', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
#                             mds_path='',
#                             coords = pyfusion.CylindricalCoordinates(r=0.821, phi=0.7732, z=-0.221))
                             
mirnov_1_15 = MDSPlusChannel(name = 'mirnov_1_15', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
                             mds_path='.operations.mirnov:a14_16:input_2',
                             coords = pyfusion.CylindricalCoordinates(r=0.696, phi=0.7732, z=-0.106))
                             
mirnov_1_16 = MDSPlusChannel(name = 'mirnov_1_16', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
                             mds_path='.operations.mirnov:a14_16:input_3',
                             coords = pyfusion.CylindricalCoordinates(r=0.652, phi=0.7732, z=0.036))

mirnov_1_17 = MDSPlusChannel(name = 'mirnov_1_17', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
                             mds_path='.operations.mirnov:a14_16:input_4',
                             coords = pyfusion.CylindricalCoordinates(r=0.676, phi=0.7732, z=0.193))

mirnov_1_18 = MDSPlusChannel(name = 'mirnov_1_18', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
                             mds_path='.operations.mirnov:a14_16:input_6',
                             coords = pyfusion.CylindricalCoordinates(r=0.790, phi=0.7732, z=0.326))

#mirnov_1_19 = MDSPlusChannel(name = 'mirnov_1_19', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
#                             mds_path='',
#                             coords = pyfusion.CylindricalCoordinates(r=0.806, phi=0.7732, z=0.336))

#mirnov_1_20 = MDSPlusChannel(name = 'mirnov_1_20', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
#                             mds_path='',
#                             coords = pyfusion.CylindricalCoordinates(r=0.934, phi=0.7732, z=0.383))


mirnov_2_1  = MDSPlusChannel(name = 'mirnov_2_1',  mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', 
                             mds_path='acq216_026:input_01', processdata_override=['DTACQ', 'INVERT'],
                             coords = pyfusion.CylindricalCoordinates(r=1.114, phi=4.962, z=0.355))
                             
mirnov_2_2  = MDSPlusChannel(name = 'mirnov_2_2',  mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', 
                             mds_path='acq216_026:input_02', processdata_override=['DTACQ', 'INVERT'],
                             coords = pyfusion.CylindricalCoordinates(r=1.185, phi=4.962, z=0.289))

mirnov_2_3  = MDSPlusChannel(name = 'mirnov_2_3',  mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', 
                             mds_path='acq216_026:input_03', processdata_override=['DTACQ', 'INVERT'],
                             coords = pyfusion.CylindricalCoordinates(r=1.216, phi=4.962, z=0.227))

#mirnov_2_4  = MDSPlusChannel(name = 'mirnov_2_4',  mds_server = H1_MDS_SERVER, mds_tree='', 
#                             mds_path='', processdata_override=['INVERT'],
#                             coords = pyfusion.CylindricalCoordinates(r=1.198, phi=4.962, z=0.137))

mirnov_2_5  = MDSPlusChannel(name = 'mirnov_2_5',  mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', 
                             mds_path='acq216_026:input_05', processdata_override=['DTACQ', 'INVERT'],
                             coords = pyfusion.CylindricalCoordinates(r=1.129, phi=4.962, z=0.123))

#mirnov_2_6  = MDSPlusChannel(name = 'mirnov_2_6',  mds_server = H1_MDS_SERVER, mds_tree='', 
#                             mds_path='', processdata_override=['INVERT'],
#                             coords = pyfusion.CylindricalCoordinates(r=1.044, phi=4.962, z=0.128))
                             
mirnov_2_7  = MDSPlusChannel(name = 'mirnov_2_7',  mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', 
                             mds_path='acq216_026:input_07', processdata_override=['DTACQ', 'INVERT'],
                             coords = pyfusion.CylindricalCoordinates(r=0.963, phi=4.962, z=0.112))
                             
mirnov_2_8  = MDSPlusChannel(name = 'mirnov_2_8',  mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', 
                             mds_path='acq216_026:input_08', processdata_override=['DTACQ', 'INVERT'],
                             coords = pyfusion.CylindricalCoordinates(r=0.924, phi=4.962, z=0.087))

mirnov_2_9  = MDSPlusChannel(name = 'mirnov_2_9',  mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', 
                             mds_path='acq216_026:input_09', processdata_override=['DTACQ', 'INVERT'],
                             coords = pyfusion.CylindricalCoordinates(r=0.902, phi=4.962, z=0.052))

mirnov_2_10 = MDSPlusChannel(name = 'mirnov_2_10', mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', 
                             mds_path='acq216_026:input_10', processdata_override=['DTACQ', 'INVERT'],
                             coords = pyfusion.CylindricalCoordinates(r=0.900, phi=4.962, z=-0.008))

#mirnov_2_11 = MDSPlusChannel(name = 'mirnov_2_11', mds_server = H1_MDS_SERVER, mds_tree='', 
#                             mds_path='', processdata_override=['INVERT'],
#                             coords = pyfusion.CylindricalCoordinates(r=0.925, phi=4.962, z=-0.073))

#mirnov_2_12 = MDSPlusChannel(name = 'mirnov_2_12', mds_server = H1_MDS_SERVER, mds_tree='', 
#                             mds_path='', processdata_override=['INVERT'],
#                             coords = pyfusion.CylindricalCoordinates(r=0.964, phi=4.962, z=-0.169))

#mirnov_2_13 = MDSPlusChannel(name = 'mirnov_2_13', mds_server = H1_MDS_SERVER, mds_tree='', 
#                             mds_path='', processdata_override=['INVERT'],
#                             coords = pyfusion.CylindricalCoordinates(r=0.897, phi=4.962, z=-0.238))

#mirnov_2_14 = MDSPlusChannel(name = 'mirnov_2_14', mds_server = H1_MDS_SERVER, mds_tree='', 
#                             mds_path='', processdata_override=['INVERT'],
#                             coords = pyfusion.CylindricalCoordinates(r=0.821, phi=4.962, z=-0.221))

mirnov_2_15 = MDSPlusChannel(name = 'mirnov_2_15', mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', 
                             mds_path='acq216_026:input_06', processdata_override=['DTACQ', 'INVERT'],
                             coords = pyfusion.CylindricalCoordinates(r=0.696, phi=4.962, z=-0.106))
                             
#mirnov_2_16 = MDSPlusChannel(name = 'mirnov_2_16', mds_server = H1_MDS_SERVER, mds_tree='', 
#                             mds_path='', processdata_override=['INVERT'],
#                             coords = pyfusion.CylindricalCoordinates(r=0.652, phi=4.962, z=0.036))
                             
mirnov_2_17 = MDSPlusChannel(name = 'mirnov_2_17', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
                             mds_path='.electr_dens.camac:a14_5:input_3', processdata_override=['INVERT'],
                             coords = pyfusion.CylindricalCoordinates(r=0.676, phi=4.962, z=0.193))
                             
mirnov_2_18 = MDSPlusChannel(name = 'mirnov_2_18', mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', 
                             mds_path='acq216_026:input_14', processdata_override=['DTACQ', 'INVERT'],
                             coords = pyfusion.CylindricalCoordinates(r=0.790, phi=4.962, z=0.326))
                             
mirnov_2_19 = MDSPlusChannel(name = 'mirnov_2_19', mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', 
                             mds_path='acq216_026:input_13', processdata_override=['DTACQ', 'INVERT'],
                             coords = pyfusion.CylindricalCoordinates(r=0.806, phi=4.962, z=0.336))
                             
mirnov_2_20 = MDSPlusChannel(name = 'mirnov_2_20', mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', 
                             mds_path='acq216_026:input_15', processdata_override=['DTACQ', 'INVERT'],
                             coords = pyfusion.CylindricalCoordinates(r=0.934, phi=4.962, z=0.383))


#mirnov_linear_1 = MDSPlusChannel(name = 'mirnov_linear_1', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
#                                 mds_path='',
#                                 coords = pyfusion.CylindricalCoordinates(r=0.98, phi=0.6109, z=0.4))

mirnov_linear_2 = MDSPlusChannel(name = 'mirnov_linear_2', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
                                 mds_path='.electr_dens.camac:a14_5:input_4',
                                 coords = pyfusion.CylindricalCoordinates(r=0.99, phi=0.6109, z=0.4))
                                 
#mirnov_linear_3 = MDSPlusChannel(name = 'mirnov_linear_3', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
#                                 mds_path='',
#                                 coords = pyfusion.CylindricalCoordinates(r=1.01, phi=0.6109, z=0.4))
                                 
mirnov_linear_4 = MDSPlusChannel(name = 'mirnov_linear_4', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
                                 mds_path='.electr_dens.camac:a14_5:input_6',
                                 coords = pyfusion.CylindricalCoordinates(r=1.04, phi=0.6109, z=0.4))

mirnov_linear_5 = MDSPlusChannel(name = 'mirnov_linear_5', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', 
                                 mds_path='.electr_dens.camac:a14_5:input_5',
                                 coords = pyfusion.CylindricalCoordinates(r=1.08, phi=0.6109, z=0.4))


mirnovbeans = pyfusion.Diagnostic(name='mirnovbeans')
mirnov_all = pyfusion.Diagnostic(name='mirnov_all')

for ch in [mirnov_1_1, mirnov_1_2,mirnov_1_3,mirnov_1_4,mirnov_1_7,mirnov_1_8,mirnov_1_9,mirnov_1_10, mirnov_1_15 ,mirnov_1_16 ,mirnov_1_17,mirnov_1_18, mirnov_2_1, mirnov_2_2, mirnov_2_3, mirnov_2_5, mirnov_2_7, mirnov_2_8, mirnov_2_9, mirnov_2_10, mirnov_2_15, mirnov_2_17, mirnov_2_18, mirnov_2_19, mirnov_2_20]:
    mirnovbeans.add_channel(ch)
    mirnov_all.add_channel(ch)

for ch in [mirnov_linear_2,mirnov_linear_4,mirnov_linear_5]:
    mirnov_all.add_channel(ch)

mirnovbean1 = pyfusion.Diagnostic(name='mirnovbean1')

for ch in [mirnov_1_1, mirnov_1_2,mirnov_1_3,mirnov_1_4,mirnov_1_7,mirnov_1_8,mirnov_1_9,mirnov_1_10, mirnov_1_15 ,mirnov_1_16 ,mirnov_1_17,mirnov_1_18]:
    mirnovbean1.add_channel(ch)

# just the really strong ones, also speeds up code for debugging
mirnov_small = pyfusion.Diagnostic(name='mirnov_small')

for ch in [mirnov_1_4,mirnov_1_7,mirnov_1_8,mirnov_1_9]:
    mirnov_small.add_channel(ch)

"""
testchannel_1 = MDSPlusChannel(name = 'testchannel_1',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_14:input_1')
testchannel_1_inverted = MDSPlusChannel(name = 'testchannel_1_inverted',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_14:input_1', processdata_override=['INVERT'])
testchannel_2_no_dtacq_map  = MDSPlusChannel(name = 'testchannel_2_no_dtacq_map',  mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', mds_path='acq216_026:input_01')
testchannel_2_with_dtacq_map  = MDSPlusChannel(name = 'testchannel_2_with_dtacq_map',  mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', mds_path='acq216_026:input_01', processdata_override=['DTACQ'])


test_processdata_override = pyfusion.Diagnostic(name='test_processdata_override')
for ch in [testchannel_1, testchannel_1_inverted, testchannel_2_no_dtacq_map, testchannel_2_with_dtacq_map]:
    test_processdata_override.add_channel(ch)
"""

class H1(pyfusion.Device):
    def __init__(self):
        self.name = 'H1'

H1inst = H1()
       
