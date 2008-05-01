"""
Metaclasses, etc which are useful for multiple devices.
depreciated
"""

#from pyfusion.core import Device
#import pyfusion

#class MDSPlusDevice(pyfusion.Device):
#    """
#    require Tom Osbourne's MDSPlus python libs to be installed in your PYTHONPATH
#    TODO: use more recent version
#    diagnostics example: 
#    mds_info = {'server':mds_server, 'tree':mds_tree, 'path':mds_path}
#    diagnostics['diag_name']['mds'] = mds_info : here, mds_server, etc are strings which can include python string variables. e.g. mds_path="A14:%d"
#    diagnostics['diag_name']['channels'] = [channel_1_name, channel_2_name,...]
#
#    for the channels, mds_server, etc are sets of values to fill in variables in diagnostics['diag_name']['mds'] strings
#
#    For now, data is assumed to be timeseries - TO DO: fix code to figure out data type from mds
#    also TO DO: should be able to maintain a connection and not reconnect for each channel...
#    """
#    from mdsutils import pmds
#    from types import StringType, UnicodeType, TupleType
#
#    diagnostics = {}
#    
#    def get_mds_for_channel(self,diag, channel):
#        """
#        Not fully functional yet, but works for me...
#        """
#        output_list = []
#        for mds_string in ['mds_server', 'mds_tree', 'mds_path']:
#            if self.diagnostics[diag][channel].has_key(mds_string):
#                if type(self.diagnostics[diag][channel][mds_string]) in [self.StringType, self.UnicodeType]:
#                    output_list.append(self.diagnostics[diag][channel][mds_string])
#                elif type(self.diagnostics[diag][channel][mds_string]) == self.TupleType:
#                    output_list.append(self.diagnostics[diag]['mds'][mds_string] %self.diagnostics[diag][channel][mds_string])
#                else:
#                    raise TypeError
#            else:
#                output_list.append(self.diagnostics[diag]['mds'][mds_string])
#        return output_list
#
#    def load_diag(self, diag_name, ignore_channels=[]):
#        # require ignore_channels elements to be strings (or unicode)
#        for i in ignore_channels:
#            if type(i) not in [self.StringType, self.UnicodeType]:
#                raise TypeError, 'any ignore_channels list elements must be strings (or unicode)'
#
#        # get list of channels to use
#        use_channels = []
#        for ch in self.diagnostics[diag_name]['channels']:
#            if not ch in ignore_channels:
#                use_channels.append(ch)
#
#        if len(use_channels) < 2:
#            raise ValueError, 'Single channel data not yet implemented'
#
#
#        for ch_i, ch in enumerate(use_channels):
#            mds_strings = self.get_mds_for_channel(diag_name, ch)
#            self.pmds.mdsconnect(mds_strings[0])
#            # self.shot comes from Shot() instance
#            self.pmds.mdsopen(mds_strings[1], self.shot)
#            data = self.pmds.mdsvalue(mds_strings[2])
#            dim_data = self.pmds.mdsvalue('dim_of(' + mds_strings[2]+')')
#            self.pmds.mdsclose(mds_strings[1], self.shot)
#            self.pmds.mdsdisconnect()
#            if ch_i == 0:
#                output_MCT = pyfusion.MultiChannelTimeseries(dim_data)
#            output_MCT.add_channel(data, ch)
#        
#        return output_MCT
#        
#class BasicLocalDataDevice(pyfusion.Device):
#    diagnostics = {}
#
#
