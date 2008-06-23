"""
Test several routines on a minimal data set: do this before committing changes
Initially just the simpler routines:

See examples/Boyds for a more complete script to check functionality

a file called 'pyfusion_local_settings.py' exists in the python path, with contents:
DEVICE='H1'

"""

import pyfusion

#nice idea, but databse is already open by the time we get here.....
#pyfusion.settings.SQL_SERVER='sqlite:///:memory:'

# about the minimum data that will cluster, maybe not enough to make sense
diag_name = 'mirnov_small'
shot_number = 58123
pyfusion.settings.SHOT_T_MIN=0.04
pyfusion.settings.SHOT_T_MAX=0.06

# tweak parameters according to command line args
execfile('process_cmd_line_args.py')

s = pyfusion.get_shot(shot_number)
s.load_diag(diag_name)

from pyfusion.datamining.clustering.core import generate_flucstrucs

generate_flucstrucs(s, diag_name, 'test_flucstrucs', store_chronos=True)


from pyfusion.datamining.clustering.core import get_clusters_for_fs_set

get_clusters_for_fs_set('test_flucstrucs')

import pylab as pl
from pyfusion.datamining.clustering.core import ClusterDataSet

clusterdataset = pyfusion.session.query(ClusterDataSet).filter_by(name='test_flucstrucs_clusters').one()

#clusterdataset.plot_BIC()
clusterdataset.plot_N_clusters(4)
