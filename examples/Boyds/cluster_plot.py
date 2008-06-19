import pyfusion, sys
from pyfusion.datamining.clustering.core import FluctuationStructureSet, get_clusters

execfile('process_cmd_line_args.py')

from pyfusion.datamining.clustering.plots import simple_cluster_plot

clusteringdatasetname = 'testclusters1'

simple_cluster_plot(clusteringdatasetname,figurename='')

#simple_cluster_plot(clusteringdatasetname, xlims=[150,320], ylims = [0,500]) ##, figurename='mytestclusters.png')

## You should now have a simple figure mytestclusters.png showing the clusters.
