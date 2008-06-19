"""
"""

import pyfusion
from sqlalchemy import Column, Integer, String, ForeignKey
from numpy import array, searchsorted

def _loadmds(mdsch,shot, invert=False):
    from mdsutils import pmds
    # This exception handler seems to be intercepted by the higher one in load_diag
    #   so we print the message as well!
    try:
        pmds.mdsconnect(mdsch.mds_server)
        pmds.mdsopen(mdsch.mds_tree, int(shot))
        data = array(pmds.mdsvalue(mdsch.mds_path))
        dim_data = array(pmds.mdsvalue('dim_of(' + mdsch.mds_path+')'))
        pmds.mdsclose(mdsch.mds_tree, shot)
        pmds.mdsdisconnect()
    except:
        # using the jScope/mdsdcl convention for "full path" here - hope it is right!
        #  mirnov_dtacq ideally should be preceded by a : 
        # (dgp: mirnov_dtacq is H-1 specific - any mirnov_dtacq customisations would go in devices/H1)
        msg=str('Error accessing server %s: Shot %d, \\%s::top%s') % (mdsch.mds_server, shot, mdsch.mds_tree, mdsch.mds_path)
        print(msg)
        raise LookupError, str
    if invert:
        data = -data
    return [dim_data,data]

class ProcessData:
    def load_channel(self, mdsch, shot, invert=False):        
        [dim_data,data] = _loadmds(mdsch,shot,invert=invert)
        t_lim = searchsorted(dim_data,[pyfusion.settings.SHOT_T_MIN, pyfusion.settings.SHOT_T_MAX])
        output_MCT = pyfusion.MultiChannelTimeseries(dim_data[t_lim[0]:t_lim[1]])
        output_MCT.add_channel(data[t_lim[0]:t_lim[1]], mdsch.name)
        return output_MCT

class MDSPlusChannel(pyfusion.Channel):
    __tablename__ = 'mdspluschannels'
    __mapper_args__ = {'polymorphic_identity':'MDSPlus'}
    id = Column('id', Integer, ForeignKey('channels.id'), primary_key=True)
    mds_server = Column('mds_server', String(50))
    mds_tree = Column('mds_tree', String(50))
    mds_path = Column('mds_path', String(50))

