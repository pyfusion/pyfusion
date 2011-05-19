"""MDSPlus acquisition."""
import warnings, os
from pyfusion.acquisition.base import BaseAcquisition
try:
    import MDSplus
except:
    print "MDSplus python package not found"

class MDSPlusAcquisition(BaseAcquisition):
    """Acquisition class for MDSplus data systems.

    If a 'server' configuration  parameter is provided, a connection for
    thin  client  access  will  be  provided.  Also,  any  configuration
    parameters  which   end  with  '_path'  will  be   loaded  into  the
    environment.
    """
    def __init__(self, *args, **kwargs):
        super(MDSPlusAcquisition, self).__init__(*args, **kwargs)

        if hasattr(self, 'server'):
            self.connection = MDSplus.Connection(self.server)
        
        for attr_name, attr_value in self.__dict__.items():
            if attr_name.endswith('_path'):
                os.environ['%s' %(attr_name)] = attr_value

    def __del__(self):
        # TODO: How do I do an  MDS disconnect using this API? do I need
        # to? Is  the following pointless is  self.connection is deleted
        # when the  parent object  is deleted? I'll  leave it here  as a
        # reminder
        if hasattr(self, 'connection'):
            del self.connection
