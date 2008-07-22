""" testsignal shot 1000 has enough noise to be non trivial, but
fluctrucs are found easily.  Shot 0-999 is harder. 
Note that correct operation is only guaranteed on an empty database:
   either drop database pyfusion_validate Careful!
   or better still use SQL_SERVER = 'sqlite://'
"""
import os
os.putenv("PYFUSION_SETTINGS_DEVICE","TestDevice")
if os.getenv("PYFUSION_SETTINGS_DEVICE") != "TestDevice":
    print "***Warning - being heavy handed with os.environ to correct DEVICE"
    os.environ.__setitem__("PYFUSION_SETTINGS_DEVICE","TestDevice")
if os.getenv("PYFUSION_SETTINGS_DEVICE") != "TestDevice":
    raise ValueError, 'PYFUSION_SETTINGS_DEVICE must be "TestDevice"'


import pyfusion
     # won't work here - too late!  pyfusion.settings.DEVICE="TestDevice"
diag_name = 'testdiag1'

s = pyfusion.get_shot(1000)
s.load_diag(diag_name)

from pyfusion.datamining.clustering.core import generate_flucstrucs

flucstruc_set_name = 'test_flucstrucs'
generate_flucstrucs(s, diag_name, flucstruc_set_name, store_chronos=True)

from pyfusion.datamining.clustering.plots import plot_flucstrucs_for_shot

plot_flucstrucs_for_shot(s.shot, diag_name, savefile='')

from pyfusion.datamining.clustering.core import get_clusters_for_fs_set

get_clusters_for_fs_set('test_flucstrucs')

import pylab as pl
from pyfusion.datamining.clustering.core import ClusterDataSet

clusterdataset = pyfusion.session.query(ClusterDataSet).filter_by(name='test_flucstrucs_clusters').one()

clusterdataset.plot_N_clusters(4)
