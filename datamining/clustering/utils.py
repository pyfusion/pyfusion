"""
utilities for datamining/clustering
"""

import pyfusion

def get_full_channel_pairs_from_fs(fs,join_ends = False):
    chs = [pyfusion.session.query(pyfusion.Channel).filter_by(name=i).one() for i in fs.svd.used_channels]
    channel_pairs = [[chs[i],chs[i+1]] for i in range(len(chs)-1)]
    if join_ends:
        channel_pairs.append([chs[-1],chs[0]])
    return channel_pairs

def test_clustvarsel(fs_list, max_clusters, clusterdataset_prefix):
    """
    run clustvarsel to reduce number of clustering dimensions, and 
    compare clustering results to those from the full dimension space.    
    
    quick and dirty timing...

    """
    import time
    channel_pairs = get_full_channel_pairs_from_fs(fs_list[0])
    
    # clusters without clustvarsel
    from core import get_clusters
    t0 = time.time()
    get_clusters(fs_list, channel_pairs, clusterdataset_prefix+'_no_clustvarsel',n_cluster_list=range(2,max_clusters+1))
    t1 = time.time()
    print 'time for clustering without variable selection: ', t1-t0

    # do clustvarsel
    from core import use_clustvarsel
    cvsel_data = use_clustvarsel(fs_list, channel_pairs, max_clusters = max_clusters)
    t2 = time.time()

    print 'time for variable selection: ', t2-t1
    # run get_clusters with new reduced dim
    get_clusters(cvsel_data[1], cvsel_data[0], clusterdataset_prefix+'_with_clustvarsel',n_cluster_list=range(2,max_clusters+1))
    t3 = time.time()
    print 'time for reduced dimension clustering: ', t3-t2

    print t1-t0, t2-t1,t3-t2


def test_clustvarsel_for_shot(shot_number, diag_name, max_clusters, clusterdataset_prefix, min_energy=0.2):
    from pyfusion.utils import timestamp
    fs_set_name = '%d_%s_%s' %(shot_number, diag_name, timestamp())
    s = pyfusion.get_shot(shot_number)
    s.load_diag(diag_name)

    from pyfusion.datamining.clustering.core import generate_flucstrucs
    generate_flucstrucs(s, diag_name, fs_set_name, store_chronos=False)

    from pyfusion.datamining.clustering.core import get_fs_in_set:
    fs_list = get_fs_in_set(fs_set_name, min_energy = min_energy)
    
    test_clustvarsel(fs_list, max_clusters, clusterdataset_prefix)


def compare_clustersets():
    pass
