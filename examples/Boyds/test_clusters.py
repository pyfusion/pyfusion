import pyfusion
from pyfusion.datamining.clustering.core import FluctuationStructureSet, get_clusters

flucstruc_set_name = 'test_flucstrucs'
diag_name = 'mirnovbeans'

execfile('process_cmd_line_args.py')

#fs_set = pyfusion.session.query(FluctuationStructureSet).filter_by(name=flucstruc_set_name)
fs_set = pyfusion.session.query(FluctuationStructureSet)

cnt=fs_set.count()
if (cnt == 0): 
    raise Exception, 'no flucstruc_set named '+ flucstruc_set_name
if (cnt > 1): 
    print('Choosing the first of %d sets from %s') % (cnt, flucstruc_set_name)
fs_list = fs_set[0].flucstrucs
print('extracted %d flucstrucs') % len(fs_set[0].flucstrucs)

diag_set = pyfusion.session.query(pyfusion.Diagnostic).filter_by(name=diag_name)
dcnt=diag_set.count()
if dcnt == 0: raise Exception, ' No diagnostics found matching ' + diag_name
diag=diag_set.first()

diag = pyfusion.session.query(pyfusion.Diagnostic).filter_by(name=diag_name).one()
#diag_ordered_channels = diag.ordered_channels()
diag_ordered_channels=diag.ordered_channel_list

channel_pairs = []
for oc_i, i in enumerate(diag_ordered_channels[:-1]):
    channel_pairs.append([diag_ordered_channels[oc_i], diag_ordered_channels[oc_i+1]])

cluster_dataset_name = 'testclusters1'

get_clusters(fs_list, channel_pairs, cluster_dataset_name, n_cluster_list=[2,3,4])

## save the file as test_clusters.py and run it from the terminal:
## python test_clusters.py

## This will generate clusters for n_clusters=2,3,4,5. Now we'll make a simple plot showing the clusters:

from pyfusion.datamining.clustering.plots import simple_cluster_plot, cluster_phase_plot

clusteringdatasetname = 'testclusters1'


cluster_phase_plot(clusteringdatasetname) ##, figurename='mytestclusters.png')
# data seems to "hang over" from simple_cluster_plot - maybe need a new figure?
simple_cluster_plot(clusteringdatasetname) ##, figurename='mytestclusters.png')


#simple_cluster_plot(clusteringdatasetname, xlims=[150,320], ylims = [0,500]) ##, figurename='mytestclusters.png')

## You should now have a simple figure mytestclusters.png showing the clusters.
