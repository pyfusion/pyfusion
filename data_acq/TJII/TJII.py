"""
data acquisition library for the TJ-II heliac
"""
import pyfusion
from sqlalchemy import Column, Integer, String, ForeignKey
from numpy import searchsorted, array
# import the python binding to the TJ-II data aquisition library
# try to import the module, if this fails, try to compile it
MAX_SIGNAL_LENGTH = 2**20

try:
    import tjiidata
except:
    import os
    print 'Compiling TJ-II data aquisition library, please wait...'
    cdir = os.path.dirname(os.path.abspath(__file__))
    tmp = pyfusion.settings.compile_tjiidata(cdir)
    try:
        import tjiidata
    except:
        raise ImportError, "Can't import TJ-II data aquisition library"



class ProcessData:
    def load_channel(self, tjiich, shot, invert=False):
        data_dim = tjiidata.dimens(shot,tjiich.senal)
        if data_dim[0] < MAX_SIGNAL_LENGTH:
            data_dict = tjiidata.lectur(shot, tjiich.senal, data_dim[0],data_dim[0],data_dim[1])
        else:
            raise ValueError, 'Not loading data to avoid segmentation fault in tjiidata.lectur'
        t_lim = searchsorted(data_dict['x'],[pyfusion.settings.SHOT_T_MIN, pyfusion.settings.SHOT_T_MAX])
        if pyfusion.settings.VERBOSE>4: 
            print('choosing data indices %d to %d') % (t_lim[0],t_lim[1])
        output_MCT = pyfusion.MultiChannelTimeseries(array(data_dict['x'][t_lim[0]:t_lim[1]]))
        if invert:
            output_MCT.add_channel(-array(data_dict['y'][t_lim[0]:t_lim[1]]), tjiich.name)
        else:
            output_MCT.add_channel(array(data_dict['y'][t_lim[0]:t_lim[1]]), tjiich.name)
        return output_MCT


class TJIIChannel(pyfusion.Channel):
    __tablename__ = 'tjiichannels'
    __mapper_args__ = {'polymorphic_identity':'TJII'}
    id = Column('id', Integer, ForeignKey('channels.id'), primary_key=True)
    senal = Column('senal',String(50))
