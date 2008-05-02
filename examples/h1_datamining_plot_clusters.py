"""
"""

import pyfusion
import pylab as pl
from pyfusion.datamining.clustering.core import ClusterDataSet
cluster_dataset = 1

clusterdataset = pyfusion.session.query(ClusterDataSet).filter_by(id=cluster_dataset).one()

for csi, cs in enumerate(clusterdataset.clustersets[:3]):
    for cli,cl in  enumerate(cs.clusters):
        pl.subplot(4,4,cli+1)
        t0 = [i.svd.timebase[0] for i in cl.flucstrucs]
        freqs = [i.frequency for i in cl.flucstrucs]
        pl.plot(t0,freqs,'o')
    pl.show()
