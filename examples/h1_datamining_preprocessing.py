"""
An example of how to use the pyfusion code for preprocessing of Mirnov data for clustering.

a file called 'pyfusion_local_settings.py' exists in the python path, with contents:
DEVICE='H1'

"""

import pyfusion
import pylab as pl
diag_name = 'mirnovbean1'

s = pyfusion.get_shot(58111)
s.load_diag(diag_name)

from pyfusion.datamining.clustering.core import generate_flucstrucs


#print s.id


generate_flucstrucs(s, diag_name, store_chronos=True)




#seg = pyfusion.session.query(pyfusion.TimeSegment).filter_by(shot = s, diag_name=).filter(pyfusion.TimeSegment.primary_diagnostic.name == diag_inst.id).all()#.filter(TimeSegment.parent_min_sample == seg_min[0]).filter(TimeSegment.n_samples == n_samples).one()
#print seg
#t = pyfusion.get_time_segments(s, diag_name)



#n_sam = 1000

#pl.plot(s.data[diag_name].timebase[:n_sam], s.data[diag_name].signals['mirnov_1_1'][:n_sam])

#pl.show()


