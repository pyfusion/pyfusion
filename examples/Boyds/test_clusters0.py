import pyfusion
from pyfusion.datamining.clustering.core import FluctuationStructureSet, get_clusters

flucstruc_set_name = 'test_flucstrucs'
diag_name = 'mirnovbeans'

execfile('process_cmd_line_args.py')

fs_set = pyfusion.session.query(FluctuationStructureSet)
fs_list = fs_set[0].flucstrucs

diag_set = pyfusion.session.query(pyfusion.Diagnostic)
# the above is no use - the first defined diag shows up, which may have no data
diag_set = pyfusion.session.query(pyfusion.Diagnostic).filter_by(name=diag_name)

diag=diag_set[0]
print('fs_set: %s, diag: %s') % (fs_set[0].name, diag_set[0].name)

diag_ordered_channels = diag.ordered_channels()

channel_pairs = []
for oc_i, i in enumerate(diag_ordered_channels[:-1]):
    channel_pairs.append([diag_ordered_channels[oc_i], diag_ordered_channels[oc_i+1]])

cluster_dataset_name = 'testclusters1'

get_clusters(fs_list, channel_pairs, cluster_dataset_name, n_cluster_list=[2,3,4,5])

## save the file as test_clusters.py and run it from the terminal:
## python test_clusters.py

## This will generate clusters for n_clusters=2,3,4,5. Now we'll make a simple plot showing the clusters:

from pyfusion.datamining.clustering.plots import simple_cluster_plot

clusteringdatasetname = 'testclusters1'

simple_cluster_plot(clusteringdatasetname) ##, figurename='mytestclusters.png')

#simple_cluster_plot(clusteringdatasetname, xlims=[150,320], ylims = [0,500]) ##, figurename='mytestclusters.png')

## You should now have a simple figure mytestclusters.png showing the clusters.
