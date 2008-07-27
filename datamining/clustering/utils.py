"""
utilities for datamining/clustering
"""
from numpy import sin,cos

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


def test_clustvarsel_for_shot(shot_number, diag_name, max_clusters, clusterdataset_prefix, min_energy=0.2, load_diag_args={}):
    from pyfusion.utils import timestamp
    fs_set_name = '%d_%s_%s' %(shot_number, diag_name, timestamp())
    s = pyfusion.get_shot(shot_number)
    s.load_diag(diag_name,**load_diag_args)

    from pyfusion.datamining.clustering.core import generate_flucstrucs
    generate_flucstrucs(s, diag_name, fs_set_name, store_chronos=False)

    from pyfusion.datamining.clustering.core import get_fs_in_set
    fs_list = get_fs_in_set(fs_set_name, min_energy = min_energy)
    print 'len fs_list: %d' %len(fs_list)
    test_clustvarsel(fs_list, max_clusters, clusterdataset_prefix)


def compare_clustersets():
    pass

def fs_to_arff(fs_list, filename=None):
    """
    output flucstruc data (including phase data) to arff format http://www.cs.waikato.ac.nz/~ml/weka/arff.html
    for use with WEKA http://www.cs.waikato.ac.nz/ml/weka/
    """

    if not filename:
        filename = "pyfusion_fs_arff_"+pyfusion.utils.timestamp()+'.arff'
    f = open(filename,'w')
    f.write('@relation %s\n\n' %(filename[:-5]))
  
    # todo: put a check here so we don't assume...
    print 'Warning: assuming phases list is the same for each flucstruc...'
    for i in fs_list[0].phases:
        f.write('@attribute sin_%d_%d numeric\n' %(i.channel_1_id, i.channel_2_id))
        f.write('@attribute cos_%d_%d numeric\n' %(i.channel_1_id, i.channel_2_id))
    
    f.write('\n@data\n')
    for fs in fs_list:
        outstr = ""
        for ph in fs.phases:
            outstr = outstr+"%f, %f ," %(sin(ph.d_phase),cos(ph.d_phase))
        f.write(outstr[:-2]+'\n')
    f.close()
