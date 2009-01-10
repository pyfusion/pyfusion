"""  Module implemented by a choice of two dodgy modules
Choice is MDSmod='MDSplus' or 'pmds'
pmds: OK, but hard to find new version, hard to compile on W32 
     Advantage: thin client, so works on any MDSIP server
     Disavantage: Speed may be reduced because of client-server arch
MDSplus: superseded embryonic object implementation by Tom Fredian
     Advantage: Should be faster, links to standard MDSplus distro.
     In principle should be able to do thin client, but I didn't test it.
"""

import pyfusion
from sqlalchemy import Column, Integer, String, ForeignKey
from numpy import array, searchsorted

def _loadmds(mdsch,shot, invert=False):
    MDSmod='MDSplus'
    if MDSmod=='pmds': from mdsutils import pmds
    else: import MDSplus as M
    # This exception handler seems to be intercepted by the one in load_diag
    #   so we print the message as well!

# this try/except covers too much - need to break it up
    try:
        if MDSmod=='pmds':  
            pmds.mdsconnect(mdsch.mds_server)
            pmds.mdsopen(mdsch.mds_tree, int(shot))
        else:
            # at present, only access local data through the library 
            print('W: module MDSplus accessing local MDS only, request was %s ' % 
                  mdsch.mds_server)
            M.TreeOpen(mdsch.mds_tree, int(shot))
        
        if MDSmod=='pmds':
            data = array(pmds.mdsvalue(mdsch.mds_path))
        else:
            bounds=str("[%f:%f]") % (pyfusion.settings.SHOT_T_MIN, 
                                     pyfusion.settings.SHOT_T_MAX)
            print mdsch.mds_path+bounds
            sig = M.TdiExecute(mdsch.mds_path+bounds)
            if pyfusion.settings.VERBOSE>4: print sig
            data = sig.data()
            if pyfusion.settings.VERBOSE>10: 
                import pylab as pl
                pl.plot(sig.data())
                pl.title('mdsch.mds_path+bounds')
                pl.show()

        if MDSmod=='pmds':
            sigdim = array(pmds.mdsvalue('dim_of(' + mdsch.mds_path+bounds))
        else:
            sigdim = M.TdiExecute('dim_of(' + mdsch.mds_path+bounds+')')

        dim_data = sigdim.data()
        if MDSmod=='pmds':
            pmds.mdsclose(mdsch.mds_tree, shot)
            pmds.mdsdisconnect()
        else:
            M.TreeClose(mdsch.mds_tree, int(shot))

    except:
  # using the jScope/mdsdcl convention for "full path" here - hope it is right!
  #  mirnov_dtacq ideally should be preceded by a : 
  # (dgp: mirnov_dtacq is H-1 specific - any mirnov_dtacq customisations would go in devices/H1)
        msg=str(('Error accessing server %s: Shot %d, \\%s::top%s') % 
                (mdsch.mds_server, shot, mdsch.mds_tree, mdsch.mds_path))
        print(msg)
        raise LookupError, msg
    if invert:
        data = -data
    return [dim_data,data]

class ProcessData:
    def load_channel(self, mdsch, shot, invert=False):        
        [dim_data,data] = _loadmds(mdsch,shot,invert=invert)
        t_lim = searchsorted(dim_data,[pyfusion.settings.SHOT_T_MIN, pyfusion.settings.SHOT_T_MAX])
        if pyfusion.settings.VERBOSE>4: 
            print('choosing data indices %d to %d') % (t_lim[0],t_lim[1])
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

