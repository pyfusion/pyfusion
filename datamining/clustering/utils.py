"""
utilities for datamining/clustering
"""
from numpy import sin,cos, array, pi, mean, argmax, abs, std, transpose, random
from pyfusion.datamining.clustering.core import FluctuationStructure, flucstruc_svs, Cluster
import pyfusion
from sqlalchemy.sql import select

def generic_cluster_input(cluster_input):
    """
    Determine if cluster_input is ClusterSet, or a list of Clusters or a list of Cluster
    """
    try:
        return cluster_input.clusters()
    except AttributeError:
        output = []
        for i in cluster_input:
            if 'Cluster' in i.__str__():
                output.append(i)
            elif type(i) == type(1):
                output.append(pyfusion.q(Cluster).get(i))
            else:
                raise TypeError, "I don't know what you're feeding me. Is it some kind of cluster thing?"
        return output

def get_shot_attributes_for_fsid_list(fsid_list, attr='shot',customshot=None, return_fsid=False):
    """
    returns list of given Shot attribute for each flucstruc with id in fsid_list
    use this to aviod loading SVDs (i.e.: flucstruc.svd.timesegment.shot.attr)
    arguments: 
    fsid_list -- list of integers corresponding to FluctuationStructure.id
    attr -- attribute of Shot to retuen
    customshot -- a subclass of Shot (which might have different attributes to Shot)
    """
    joined_table = FluctuationStructure.__table__.join(
        pyfusion.MultiChannelSVD.__table__).join(pyfusion.TimeSegment.__table__).join(pyfusion.Shot.__table__)
    if customshot != None:
        joined_table = joined_table.join(customshot.__table__)

    sel_list = []
    if return_fsid:
        sel_list.append(FluctuationStructure.id)
    if customshot:
        sel_list.append(customshot.__dict__[attr])
    else:
        sel_list.append(pyfusion.Shot.__dict__[attr])

    phase_select = select(sel_list,from_obj=[joined_table]).where(FluctuationStructure.__table__.c.id.in_(fsid_list))
    
    result = pyfusion.session.execute(phase_select).fetchall()

    if len(sel_list) == 1:
        data = [i[0] for i in result]
    else:
        data = result
    return data


def update_cluster_mean_phase_var(cl):
    """
    for a cluster, calculate the mean (across all dimensions) of the variance of fs d_phase values 
    and add to cluster table
    """
    cl_phase_info = get_phase_info_for_fs_list(cl.flucstrucs)
    cl_mean_var = mean([i[1] for i in cl_phase_info[0]])
    cl.mean_phase_var = cl_mean_var
    pyfusion.session.save_or_update(cl)


def add_timesegmentdatasummary_for_fs_list(fs_list, diag_name, ts_exist_check='any',savelocal=False, ignorelocal=False):
    """
    for a list of flucstrucs, add TimeSegmentDataSummary to their TimeSegments
    """
    from pyfusion.utils import add_timesegmentdatasummary_for_ts_list
    ts_list = []
    for fs in fs_list:
        if not fs.svd.timesegment in ts_list:
            ts_list.append(fs.svd.timesegment)
    print 'Number of Fluctuation Structures: %d' %(len(fs_list))
    print 'Number of Time Segments: %d' %(len(ts_list))

    add_timesegmentdatasummary_for_ts_list(ts_list, diag_name, exist_check=ts_exist_check, savelocal=savelocal, ignorelocal=ignorelocal)

def get_periodic_mean(input_data, rad=True):
    input_data = array(input_data)
    if not rad:
        input_data *= pi/180
    tmp_stddev = 1.e6
    delta_stddev = -1.
    tmp_data = input_data
    while delta_stddev < 0:
        stddev_val = tmp_stddev
        tmp_mean = mean(tmp_data)
        furthest_el = argmax(abs(tmp_data-tmp_mean))
        if tmp_data[furthest_el] < tmp_mean:
            tmp_data[furthest_el] += 2.*pi
        else:
            tmp_data[furthest_el] -= 2.*pi
        tmp_stddev = std(tmp_data)
        delta_stddev = tmp_stddev - stddev_val
    
    if not rad:
        output_factor = 180./pi
    else:
        output_factor = 1.0
    return [output_factor*mean(tmp_data), output_factor*stddev_val]


def get_phase_info_for_fs_list(fs_list):
    """
    WARNING: we assume all flustrucs have use the same ordered_channel_list
    """
    from pyfusion.datamining.clustering.core import DeltaPhase, FluctuationStructure
    ordered_channel_list = fs_list[0].svd.diagnostic.ordered_channel_list
    output_list = []
    _phases = []
    for i,fs in enumerate(fs_list):
        _phases.append([i.d_phase for i in fs.phases])
    _t_phases = transpose(array(_phases))
    x = 0
    for ch_pair_phases in _t_phases:
        x+=1
        output_list.append(get_periodic_mean(ch_pair_phases))
    return [output_list, ordered_channel_list]


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


def fs_to_arff(fs_list, filename=None, noise_stddev = 0):
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
            dp = ph.d_phase
            if noise_stddev > 0:
                rn = random.normal(loc=0.0,scale=noise_stddev,size=2)
                outstr = outstr+"%f, %f ," %(rn[0]+sin(dp),rn[1]+cos(dp))
            else:
                outstr = outstr+"%f, %f ," %(sin(dp),cos(dp))
        f.write(outstr[:-2]+'\n')
    f.close()
