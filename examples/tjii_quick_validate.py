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

import pyfusion
from pyfusion.utils import delta_t


#nice idea, but databse is already open by the time we get here.....
#pyfusion.settings.SQL_SERVER='sqlite:///:memory:'

# about the minimum data that will cluster, maybe not enough to make sense
diag_name = 'mirnov_coils'
shot_number = 18993 
min_energy = 0.2

t_min=1.030*1000
t_max=1.290*1000

# Note - as of r124, needed 20-60ms instead of 40-60ms to get >4 clusters

# tweak parameters according to command line args
execfile('process_cmd_line_args.py')
pyfusion.settings.SHOT_T_MIN=t_min
pyfusion.settings.SHOT_T_MAX=t_max

s = pyfusion.get_shot(shot_number)
s.load_diag(diag_name)

from pyfusion.datamining.clustering.core import generate_flucstrucs

generate_flucstrucs(s, diag_name, 'test_flucstrucs', store_chronos=True)
print "flucstrucs -> "+ delta_t("flucstrucs", total=True)

from pyfusion.datamining.clustering.plots import plot_flucstrucs_for_shot
plot_flucstrucs_for_shot(s.shot, diag_name, savefile='')
info=str("shot %d %s" % (shot_number, pyfusion.utils.get_revision() ))
import pylab as pl
try:    pl.suptitle(info)
except: pl.xlabel(info)

pl.figure()

from pyfusion.datamining.clustering.core import get_clusters_for_fs_set

#get_clusters_for_fs_set('test_flucstrucs')
get_clusters_for_fs_set('test_flucstrucs',min_energy=min_energy, n_cluster_list=range(1,11))

from pyfusion.datamining.clustering.core import ClusterDataSet

clusterdataset = pyfusion.session.query(ClusterDataSet).filter_by(name='test_flucstrucs_clusters').one()

#clusterdataset.plot_BIC()

print delta_t("total", total=True)
clusterdataset.plot_N_clusters(4)
pl.suptitle(info)
