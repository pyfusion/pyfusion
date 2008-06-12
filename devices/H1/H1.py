"""
Device class for the H-1 heliac
"""

import pyfusion
from pyfusion.data_acq.MDSPlus.MDSPlus import MDSPlusChannel
from pyfusion.settings import H1_MDS_SERVER

mirnov_1_1 = MDSPlusChannel(name = 'mirnov_1_1', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_14:input_1')
mirnov_1_2 = MDSPlusChannel(name = 'mirnov_1_2', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_14:input_2')
mirnov_1_3 = MDSPlusChannel(name = 'mirnov_1_3', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_14:input_3')
mirnov_1_4 = MDSPlusChannel(name = 'mirnov_1_4', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_14:input_4')
mirnov_1_7 = MDSPlusChannel(name = 'mirnov_1_7', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_14:input_6')
mirnov_1_8 = MDSPlusChannel(name = 'mirnov_1_8', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_15:input_1')
mirnov_1_9 = MDSPlusChannel(name = 'mirnov_1_9', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_15:input_2')
mirnov_1_10 = MDSPlusChannel(name = 'mirnov_1_10', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_15:input_3')
mirnov_1_15 = MDSPlusChannel(name = 'mirnov_1_15', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_16:input_2')
mirnov_1_16 = MDSPlusChannel(name = 'mirnov_1_16', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_16:input_3')
mirnov_1_17 = MDSPlusChannel(name = 'mirnov_1_17', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_16:input_4')
mirnov_1_18 = MDSPlusChannel(name = 'mirnov_1_18', mds_server = H1_MDS_SERVER, mds_tree='H1DATA', mds_path='.operations.mirnov:a14_16:input_6')

mirnovbean1 = pyfusion.Diagnostic(name='mirnovbean1')

for ch in [mirnov_1_1, mirnov_1_2,mirnov_1_3,mirnov_1_4,mirnov_1_7,mirnov_1_8,mirnov_1_9,mirnov_1_10, mirnov_1_15 ,mirnov_1_16 ,mirnov_1_17,mirnov_1_18]:
    mirnovbean1.add_channel(ch)


class H1(pyfusion.Device):
    def __init__(self):
        self.name = 'H1'

H1inst = H1()
       
