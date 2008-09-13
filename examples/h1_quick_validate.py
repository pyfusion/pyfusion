"""
Test several routines on a minimal data set: do this before committing changes
Initially just the simpler routines:
This one is specific to H1, includes timing on real data.

See examples/Boyds for a more complete script to check functionality
Can see phases afterwards if in ipython:
    run examples/Boyds/freq_phase_time_energy.py shots=[58122]

Timing: Ath64X2,2GHz
flucstruc     5.3
total         8.0
Notes: 58123, 20-60ms, 1024, 10 clusts
a file called 'pyfusion_local_settings.py' exists in the python path, with contents:
DEVICE='H1'
"""

from utils import delta_t
import pyfusion

#nice idea, but databse is already open by the time we get here.....
#pyfusion.settings.SQL_SERVER='sqlite:///:memory:'

# about the minimum data that will cluster, maybe not enough to make sense
diag_name = 'mirnov_small'
shot_number = 58122  # shot in CPC paper
pyfusion.settings.SHOT_T_MIN=0.02
pyfusion.settings.SHOT_T_MAX=0.06

# Note - as of r124, needed 20-60ms instead of 40-60ms to get >4 clusters

# tweak parameters according to command line args
execfile('process_cmd_line_args.py')

s = pyfusion.get_shot(shot_number)
s.load_diag(diag_name)

from pyfusion.datamining.clustering.core import generate_flucstrucs

generate_flucstrucs(s, diag_name, 'test_flucstrucs', store_chronos=True)
print "flucstrucs -> "+ delta_t("flucstrucs", total=True)

from pyfusion.datamining.clustering.core import get_clusters_for_fs_set

get_clusters_for_fs_set('test_flucstrucs')

import pylab as pl
from pyfusion.datamining.clustering.core import ClusterDataSet

clusterdataset = pyfusion.session.query(ClusterDataSet).filter_by(name='test_flucstrucs_clusters').one()

#clusterdataset.plot_BIC()

print delta_t("total", total=True)
clusterdataset.plot_N_clusters(4)
info=str("shot %d %s" % (shot_number, pyfusion.utils.get_revision() ))
pl.suptitle(info)
