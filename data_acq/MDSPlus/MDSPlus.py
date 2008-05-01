"""
"""

import pyfusion
from sqlalchemy import Column, Integer, String, ForeignKey

class ProcessData:
    from mdsutils import pmds

    def load_channel(self, mdsch, shot):        

        self.pmds.mdsconnect(mdsch.mds_server)
        self.pmds.mdsopen(mdsch.mds_tree, int(shot))
        data = self.pmds.mdsvalue(mdsch.mds_path)
        dim_data = self.pmds.mdsvalue('dim_of(' + mdsch.mds_path+')')
        self.pmds.mdsclose(mdsch.mds_tree, shot)
        self.pmds.mdsdisconnect()
        
        output_MCT = pyfusion.MultiChannelTimeseries(dim_data)
        output_MCT.add_channel(data, mdsch.name)
        return output_MCT

class MDSPlusChannel(pyfusion.Channel):
    __tablename__ = 'mdspluschannels'
    __mapper_args__ = {'polymorphic_identity':'MDSPlus'}
    id = Column('id', Integer, ForeignKey('channels.id'), primary_key=True)
    mds_server = Column('mds_server', String(50))
    mds_tree = Column('mds_tree', String(50))
    mds_path = Column('mds_path', String(50))

