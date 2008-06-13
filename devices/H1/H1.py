"""
Device class for the H-1 heliac
"""

import pyfusion
from pyfusion.data_acq.MDSPlus.MDSPlus import MDSPlusChannel
from pyfusion.settings import H1_MDS_SERVER
from h1data_dtacq_shot_offset import h1data_dtacq_mapping

class ProcessData:
    def __init__(self, data_acq_type = '', processdata_override = ''):
        self.data_acq_type = data_acq_type
        self.processdata_override = processdata_override


    def load_channel(self, mdsch, shot):
        if self.data_acq_type == 'MDSPlus':
            if 'DTACQ' in self.processdata_override:
                _shot = h1data_dtacq_mapping[str(shot)]
                print 'got shot from dtacq:', mdsch.name, shot, _shot
            else:
                _shot = shot
            if 'INVERT' in self.processdata_override:
                invert_signal = True
            else:
                invert_signal = False
            from pyfusion.data_acq.MDSPlus.MDSPlus import ProcessData as _ProcessData
            pd = _ProcessData()
            return pd.load_channel(mdsch, _shot, invert=invert_signal)


mirnov_1_1  = MDSPlusChannel(name = 'mirnov_1_1',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_14:input_1')
mirnov_1_2  = MDSPlusChannel(name = 'mirnov_1_2',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_14:input_2')
mirnov_1_3  = MDSPlusChannel(name = 'mirnov_1_3',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_14:input_3')
mirnov_1_4  = MDSPlusChannel(name = 'mirnov_1_4',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_14:input_4')
mirnov_1_7  = MDSPlusChannel(name = 'mirnov_1_7',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_14:input_6')
mirnov_1_8  = MDSPlusChannel(name = 'mirnov_1_8',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_15:input_1')
mirnov_1_9  = MDSPlusChannel(name = 'mirnov_1_9',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_15:input_2')
mirnov_1_10 = MDSPlusChannel(name = 'mirnov_1_10', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_15:input_3')
mirnov_1_15 = MDSPlusChannel(name = 'mirnov_1_15', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_16:input_2')
mirnov_1_16 = MDSPlusChannel(name = 'mirnov_1_16', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_16:input_3')
mirnov_1_17 = MDSPlusChannel(name = 'mirnov_1_17', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_16:input_4')
mirnov_1_18 = MDSPlusChannel(name = 'mirnov_1_18', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_16:input_6')

mirnov_2_1  = MDSPlusChannel(name = 'mirnov_2_1',  mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', mds_path='acq216_026:input_01', processdata_override=['DTACQ', 'INVERT'])
mirnov_2_2  = MDSPlusChannel(name = 'mirnov_2_2',  mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', mds_path='acq216_026:input_02', processdata_override=['DTACQ', 'INVERT'])
mirnov_2_3  = MDSPlusChannel(name = 'mirnov_2_3',  mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', mds_path='acq216_026:input_03', processdata_override=['DTACQ', 'INVERT'])
mirnov_2_5  = MDSPlusChannel(name = 'mirnov_2_5',  mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', mds_path='acq216_026:input_05', processdata_override=['DTACQ', 'INVERT'])
mirnov_2_7  = MDSPlusChannel(name = 'mirnov_2_7',  mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', mds_path='acq216_026:input_07', processdata_override=['DTACQ', 'INVERT'])
mirnov_2_8  = MDSPlusChannel(name = 'mirnov_2_8',  mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', mds_path='acq216_026:input_08', processdata_override=['DTACQ', 'INVERT'])
mirnov_2_9  = MDSPlusChannel(name = 'mirnov_2_9',  mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', mds_path='acq216_026:input_09', processdata_override=['DTACQ', 'INVERT'])
mirnov_2_10 = MDSPlusChannel(name = 'mirnov_2_10', mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', mds_path='acq216_026:input_10', processdata_override=['DTACQ', 'INVERT'])
mirnov_2_15 = MDSPlusChannel(name = 'mirnov_2_15', mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', mds_path='acq216_026:input_06', processdata_override=['DTACQ', 'INVERT'])
mirnov_2_17 = MDSPlusChannel(name = 'mirnov_2_17', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.electr_dens.camac:a14_5:input_3', processdata_override=['INVERT'])
mirnov_2_18 = MDSPlusChannel(name = 'mirnov_2_18', mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', mds_path='acq216_026:input_14', processdata_override=['DTACQ', 'INVERT'])
mirnov_2_19 = MDSPlusChannel(name = 'mirnov_2_19', mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', mds_path='acq216_026:input_13', processdata_override=['DTACQ', 'INVERT'])
mirnov_2_20 = MDSPlusChannel(name = 'mirnov_2_20', mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', mds_path='acq216_026:input_15', processdata_override=['DTACQ', 'INVERT'])


mirnovbeans = pyfusion.Diagnostic(name='mirnovbeans')

for ch in [mirnov_1_1, mirnov_1_2,mirnov_1_3,mirnov_1_4,mirnov_1_7,mirnov_1_8,mirnov_1_9,mirnov_1_10, mirnov_1_15 ,mirnov_1_16 ,mirnov_1_17,mirnov_1_18, mirnov_2_1, mirnov_2_2, mirnov_2_3, mirnov_2_5, mirnov_2_7, mirnov_2_8, mirnov_2_9, mirnov_2_10, mirnov_2_15, mirnov_2_17, mirnov_2_18, mirnov_2_19, mirnov_2_20]:
    mirnovbeans.add_channel(ch)

testchannel_1 = MDSPlusChannel(name = 'testchannel_1',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_14:input_1')
testchannel_1_inverted = MDSPlusChannel(name = 'testchannel_1_inverted',  mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_14:input_1', processdata_override=['INVERT'])
testchannel_2_no_dtacq_map  = MDSPlusChannel(name = 'testchannel_2_no_dtacq_map',  mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', mds_path='acq216_026:input_01')
testchannel_2_with_dtacq_map  = MDSPlusChannel(name = 'testchannel_2_with_dtacq_map',  mds_server = H1_MDS_SERVER, mds_tree='MIRNOV_DTACQ', mds_path='acq216_026:input_01', processdata_override=['DTACQ'])


test_processdata_override = pyfusion.Diagnostic(name='test_processdata_override')
for ch in [testchannel_1, testchannel_1_inverted, testchannel_2_no_dtacq_map, testchannel_2_with_dtacq_map]:
    test_processdata_override.add_channel(ch)


class H1(pyfusion.Device):
    def __init__(self):
        self.name = 'H1'

H1inst = H1()
       
