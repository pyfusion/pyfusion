"""
plots for clustering

yes, it's a mess.
"""

import pyfusion, os, pickle
import pylab as pl
from pyfusion.datamining.clustering.core import FluctuationStructure,FluctuationStructureSet, ClusterDataSet, Cluster, ClusterSet
from pyfusion.datamining.clustering.utils import get_phase_info_for_fs_list
from numpy import array,transpose, argsort, min, max, average, shape, mean, cumsum, unique, sqrt, intersect1d, take,pi, arange, mat, cov,average, trace, log, sin,cos, ndarray, var, size
from numpy.random import random_sample
from pyfusion.visual.core import ScatterPlot, golden_ratio, datamap
from numpy.random import rand
from numpy.linalg import det

from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relation
from tempfile import gettempdir



def KL_dist(input_data0,input_data1,symmetric=True):
    """
    Compute the Kullback-Leibler divergence (~distance) between two normally distributed sets of data in the same space.

    input_data0, input_data1 -- Ndp x Ndim arrays or matricies. Ndp is number of data points, Ndim is number of dimensions

    We use the form of the KL divergence for normal distributions, if the data is far from normal do not expect a useful result.
    reference: http://en.wikipedia.org/wiki/Multivariate_normal_distribution#Kullback-Leibler_divergence

    By definition, the KL divergence is not symmetric (d_KL(a,b) != d_KL(b,a)). 
    If the symmetric argument = True, KL_dist will return (d_KL(a,b)+d_KL(b,a))/2
    """
    # convert input data into numpy matrices
    data0 = mat(input_data0).T
    data1 = mat(input_data1).T

    # calulate means mu and covariance matrix S for input data
    mu0 = mat(average(data0,axis=1))
    mu1 = mat(average(data1,axis=1))
    S0 = mat(cov(data0))
    S1 = mat(cov(data1))

    N = shape(mu0)[1]
    m10 = mu1-mu0
    
    X = 0.5*( log(det(S1)/det(S0)) + trace(S1.I * S0) + m10.T * S1.I * m10 - N)
    x = array(X)[0][0]
    if symmetric:
        return 0.5*(x + KL_dist(input_data1,input_data0,symmetric=False))
    else:
        return x


def get_clusterset_net_data(clusterset, phase_data_function=None):
    """
    get phases and distances for clusterset_net plot
    """
    
    # load clusters from clusterset
    cluster_list = pyfusion.q(Cluster).filter_by(clusterset=clusterset).all()
    
    # dictionary to hold phase info for cluster flucstrucs
    cluster_phases = dict.fromkeys([str(cluster.id) for cluster in cluster_list])

    # get phase info for clusters
    for cl_i, cluster in enumerate(cluster_list):
        if pyfusion.settings.VERBOSE>1:
            print "getting phases for cluster %d, %d of %d" %(cluster.id, cl_i+1, len(cluster_list))
        if phase_data_function == None:
            cluster_phases[str(cluster.id)] = cluster.get_sin_cos_phases()
        else:
            cluster_phases[str(cluster.id)] = phase_data_function(cluster)

    # dictionary to hold distances between clusters
    cluster_dist = dict.fromkeys([str(cluster.id) for cluster in cluster_list],{})

    # get distance between each pair of clusters
    all_dists = []
    for cl1_i, cluster1 in enumerate(cluster_list):
        if pyfusion.settings.VERBOSE>1:
            print "calculating distances for cluster %d, %d of %d" %(cluster1.id, cl1_i+1, len(cluster_list))
        for _tmp_counter, cluster2 in enumerate(cluster_list[cl1_i+1:]):
            cl2_i = cl1_i+_tmp_counter+1
            cl_kl_dist = KL_dist(cluster_phases[str(cluster1.id)], cluster_phases[str(cluster2.id)])
            # check for nan (cl_kl_dist is pos def)
            if not cl_kl_dist <  pyfusion.settings.BIG_FLOAT:
                cl_kl_dist =  sqrt(pyfusion.settings.BIG_FLOAT)
            #if cl_kl_dist <  pyfusion.settings.BIG_FLOAT:
            cluster_dist[str(cluster1.id)][str(cluster2.id)] = log(cl_kl_dist)
            all_dists.append(cluster_dist[str(cluster1.id)][str(cluster2.id)])

    return [cluster_dist,all_dists]

def plot_clusterset_net(clusterset, clusterplot_func=None, clusterplot_xlim=None, clusterplot_ylim=None, phase_data_function=None):
    """
    Plot the clusters in the given clusterset as a graph. 
    Distances between clusters are defined by the Kullback-Leibier distance.
    We use graphviz (via pygraphviz) to graph the clusters as a `spring model' (using the
    Kamada-Kawai model for energy minimisation)

    arguments:
    clusterset -- a ClusterSet instance
    clusterplot_func - an optional function which takes a Cluster instance as its only arument and returns
        data [[x0,y0],[x1,y1]] for plotting for the given cluster
    clusterplot_xlim -- [min,max] for x axis of cluster subplots
    clusterplot_ylim -- [min,max] for y axis of cluster subplots
    """
    import pygraphviz
    
    [cluster_dist,all_dists] = get_clusterset_net_data(clusterset, phase_data_function=phase_data_function)

    # initialise main plot (not subplot) axes
    main_axes = pl.axes([0.,0.,1,1])

    ### compute graph coordinates
    
    G=pygraphviz.AGraph()
    
    # cluster id list, corresponding to clusterset.clusters
    clid_str_list = [str(cl.id) for cl in clusterset.clusters]

    # add cluster nodes:
    for clid_str in clid_str_list:
        G.add_node(clid_str)

    # add edges
    for cl1 in cluster_dist.keys():
        for cl2 in cluster_dist[cl1].keys():
            G.add_edge(cl1,cl2,len=str(cluster_dist[cl1][cl2]))
    G.layout()
    
    # read back the plot coordinates of the nodes (cluster locations) so we can plot our own subplots with numpy
    node_coord_list = []
    for clid_str in clid_str_list:
        n = G.get_node(clid_str)
        x = float(n.attr['pos'].split(',')[0])
        y = float(n.attr['pos'].split(',')[1])    
        node_coord_list.append([x,y])
    
    # parameters for plotting
    colourmap = pl.get_cmap('jet')
    if min(all_dists) == max(all_dists):
        raise ValueError, "cannot normalise distances between clusters"
    get_norm_dist = lambda x: (x-min(all_dists))/(max(all_dists)-min(all_dists))
    linewidth_offset = 0.2 # we plot the linewidth as inverse of distance, so let's not let it reach zero
    linewidth_scale = 5.0
    #min_alpha = 0.2

    # plot graph edges
    for cl1 in cluster_dist.keys():
        for cl2 in cluster_dist[cl1].keys():
            x0 = node_coord_list[clid_str_list.index(cl1)][0]
            y0 = node_coord_list[clid_str_list.index(cl1)][1]
            x1 = node_coord_list[clid_str_list.index(cl2)][0]
            y1 = node_coord_list[clid_str_list.index(cl2)][1]
            norm_dist = get_norm_dist(cluster_dist[cl1][cl2])
            linewidth_val = 1./(linewidth_scale*norm_dist+linewidth_offset)
            print 'norm_dist', norm_dist
            colour_val = colourmap(int(norm_dist*256))
            #alpha_val = (1-norm_dv)*(1-min_alpha)+min_alpha
            pl.plot([x0,x1],[y0,y1],color=colour_val,lw=linewidth_val)
            #pl.plot([x0,x1],[y0,y1],color=colour_val,alpha=0.5)

    # plot node plots
    pl.axes(main_axes)
    main_xlim = pl.xlim()
    main_ylim = pl.ylim()
    main_dx = main_xlim[1] - main_xlim[0]
    main_dy = main_ylim[1] - main_ylim[0]
    for clid_str_i, clid_str in enumerate(clid_str_list):
        pl.axes(main_axes)
        pl.xlim(main_xlim)
        pl.ylim(main_ylim)
        [nx,ny] = node_coord_list[clid_str_i]
        if clusterplot_func != None:
            cluster_data = clusterplot_func(clusterset.clusters[clid_str_i])
        else:
            cluster_data = clusterset.clusters[clid_str_i].get_time_flucstuc_properties(fs_props=['frequency'])
        #local_axes = pl.axes([(nx-10)/main_dx,(ny-10)/main_dy,70./main_dx,70./main_dy])
        local_axes = pl.axes([(nx-10)/main_dx,(ny-10)/main_dy,140./main_dx,140./main_dy])

        cd_t = transpose(array(cluster_data,dtype='float'))
        pl.plot(cd_t[0],cd_t[1],'.')
        if clusterplot_xlim != None:
            pl.xlim(clusterplot_xlim[0], clusterplot_xlim[1])
        if clusterplot_ylim != None:
            pl.ylim(clusterplot_ylim[0], clusterplot_ylim[1])
        pl.setp(pl.gca(),xticklabels=[],yticklabels=[])

    pl.show()


class DendrogramLink(pyfusion.Base):
    """
    information about how clusters in a dendrogram are linked together
    """
    __tablename__ = "dm_plots_dendrogram_links"
    id = Column('id', Integer, primary_key=True)
    parent_id = Column('parent_id', Integer, ForeignKey('dm_clusters.id'))
    parent = relation(Cluster, primaryjoin=parent_id==Cluster.id)
    child_id = Column('child_id', Integer, ForeignKey('dm_clusters.id'))
    child = relation(Cluster, primaryjoin=child_id==Cluster.id)
    fs_intersection = Column('fs_intersection',Integer)
    fraction = Column('fraction',Float)

def dendro_coords(ncl, cl, max_ncl,xmar,ymar):
    delta_h = (1.0-2.*ymar)/ncl
    x_loc = xmar + (ncl-1)*(1.0-2*xmar)/(max_ncl)
    y_loc = 1.0-ymar - (cl-0.5)*delta_h
    return [x_loc, y_loc]



class Dendrogram(pyfusion.Base):
    """
    class to produce a dendrogram for a ClusterDataSet
    """
    __tablename__ = "dm_plots_dendrogram"
    id = Column('id', Integer, primary_key=True)
    head_cluster_id = Column('head_cluster_id', Integer, ForeignKey('dm_clusters.id'))
    head_cluster = relation(Cluster, primaryjoin=head_cluster_id==Cluster.id)
    def __init__(self, head_cluster, max_clusters=None):
        self.head_cluster = head_cluster
        # get n_clusters of head_cluster
        self.head_clusterset = self.head_cluster.clusterset
        if self.head_clusterset.n_clusters != 1:
            print "Warning: Not starting from n_clusters = 1, results may be strange"
        self.cluster_dataset = self.head_clusterset.clusterdataset
        if max_clusters:
            self.max_n_clusters = max_clusters
        else:
            self.max_n_clusters = max([cs.n_clusters for cs in self.cluster_dataset.clustersets])
        
    def get_links(self):
        # simple hack - for some reason the DendrogramLink table wan't being created.
        # need to undertstand why
        try:
            # raises an exception if table exists
            DendrogramLink.__table__.create()
        except:
            # no harm done. 
            pass
        parent_clusters = [self.head_cluster]
        for n_cl in range(self.head_clusterset.n_clusters+1, self.max_n_clusters+1):
            child_clusterset = pyfusion.q(ClusterSet).filter_by(clusterdataset_id=self.cluster_dataset.id, n_clusters=n_cl).one()
            child_clusters = child_clusterset.clusters
            print 'n_cl, ', n_cl
            for parent in parent_clusters:
                for child in child_clusters:
                    if pyfusion.q(DendrogramLink).filter_by(parent=parent,child=child).count() == 0:
                        fs_intersection  = len(intersect1d(parent.flucstrucs, child.flucstrucs))
                        frac = float(fs_intersection)/len(parent.flucstrucs)
                        _tmp = DendrogramLink(parent_id=parent.id, child_id=child.id, fraction = frac, fs_intersection=fs_intersection)
                        pyfusion.session.save_or_update(_tmp)
            parent_clusters = child_clusters
    def simple_plot(self, clusterplot_func=None,x_lims=[0,1],y_lims=[0,1],x_space=0.2,y_space=0.2, random_sample = None, var_col=True, text_list=[], show_cluster_id=False, show_lines=False, figure_size=None, savename=None):
        """
        x_plot, y_plot = attributes of fluctuation structures to be plotted
        x_lim, y_lim, range ofr subplots
        x_space. fraction of width of subplot to have as spacing
        y_space. fraction of height of subplot to have as spacing between plots at max( n_clusters)
        """
        x_margin = 0.1
        y_margin = 0.1
        
        _fig = pl.figure(figsize=figure_size)

        max_subplot_width = (1.0-2*x_margin)/self.max_n_clusters
        max_subplot_height = (1.0-2*y_margin)/self.max_n_clusters
        subplot_height = (1.0-y_space)*max_subplot_height
        subplot_width = (1.0-x_space)*max_subplot_width #golden_ratio*subplot_height

        plot_coords = {}
        plot_coords[str(self.head_cluster.id)] = dendro_coords(1, 1, self.max_n_clusters, x_margin, y_margin)

        clustersets = self.cluster_dataset.clustersets
        clustersets_ncl = [i.n_clusters for i in clustersets]

        main_axes = pl.axes([0,0,1,1])
        
        # somehow, this bit is responsible for drawing the links... 
        for ncl in range(1,self.max_n_clusters):
            child_cl_set = clustersets[clustersets_ncl.index(ncl+1)]
            parent_cl_set = clustersets[clustersets_ncl.index(ncl)]
            child_cli = 1
            _new_pcls = parent_cl_set.clusters
            _newcls_y = [plot_coords[str(i.id)][1] for i in _new_pcls]
            _argsort_y = argsort(_newcls_y)[::-1]
            new_pcls = [_new_pcls[i] for i in _argsort_y]
            child_parent_links = []
            for ccli,ccl in enumerate(child_cl_set.clusters):
                child_parent_links.append(pyfusion.q(DendrogramLink).filter_by(child=ccl).order_by(DendrogramLink.fs_intersection).all()[-1])
            p_c_sets = []
            for pcli,cpl in enumerate(new_pcls):
                _tmp_c_links = []
                for l in child_parent_links:
                    if l.parent_id == cpl.id:
                        _tmp_c_links.append(l)
                
                tmp_c_intersec_as = argsort([i.fs_intersection for i in _tmp_c_links])[::-1]
                tmp_c_links = [_tmp_c_links[i] for i in tmp_c_intersec_as]
                p_c_sets.append(tmp_c_links)
                for li, l in enumerate(tmp_c_links):
                    c1 = dendro_coords(child_cl_set.n_clusters, child_cli, self.max_n_clusters, x_margin, y_margin)
                    plot_coords[str(l.child.id)] = c1
                    child_cli +=1
            all_links = []
            for cli,cl in enumerate(new_pcls):
                plinks = pyfusion.q(DendrogramLink).filter_by(parent=cl).order_by(DendrogramLink.fraction).all()[::-1]
                all_links.append(plinks)
            
            for pcli,pcl in enumerate(new_pcls):
                if pcli > 0:
                    _tmp_coords = plot_coords
                    # get fraction with previous parent
                    pccl_fractions = []
                    for pccli,pccl in enumerate(p_c_sets[pcli]):
                        _q = pyfusion.q(DendrogramLink).filter_by(child_id=pccl.child_id, parent_id=new_pcls[pcli-1].id)
                        if _q.count() == 0:
                            pccl_fractions.append(0)
                        else:
                            pccl_fractions.append(_q.one().fraction)
                    pccl_f_as = argsort(pccl_fractions)[::-1]
                    already_swapped = []
                    for i in range(len(pccl_f_as)):
                        if not pccl_f_as[i] == i:
                            print "%s <> %s" %(str(p_c_sets[pcli][i].child_id), str(p_c_sets[pcli][pccl_f_as[i]].child_id))
                            a = plot_coords[str(p_c_sets[pcli][i].child_id)]
                            b = plot_coords[str(p_c_sets[pcli][pccl_f_as[i]].child_id)]
                            if not a in already_swapped and not b in already_swapped:
                                _tmp_coords[str(p_c_sets[pcli][pccl_f_as[i]].child_id)] = a
                                _tmp_coords[str(p_c_sets[pcli][i].child_id)] = b
                                already_swapped.append(a)
                                already_swapped.append(b)
                                
                        plot_coords = _tmp_coords

            
            for cli,cl in enumerate(new_pcls):
                links = all_links[cli]
                for li,l in enumerate(links):
                    c0 = plot_coords[str(cl.id)]
                    c1 = plot_coords[str(l.child.id)]
                    pl.plot([c0[0],c1[0]], [c0[1],c1[1]],lw=20.*l.fs_intersection/len(self.head_cluster.flucstrucs),color='k')


        print '... loading plot data'
        cl_q = pyfusion.q(Cluster)
        pl.setp(main_axes,xlim=[0,1],ylim=[0,1])

        mean_var_list = []
        colmap = pl.get_cmap('jet')
        #colfactor = 256./(pi/2)
        colfactor = 256./0.5
        # plot the sub-plots
        for clidstri,clidstr in enumerate(plot_coords.keys()):
            print "cl %d of %d" %(clidstri+1, len(plot_coords.keys()))
            pl.axes(main_axes)
            clco = plot_coords[clidstr]
            local_axes = pl.axes([clco[0]-0.5*subplot_width,clco[1]-0.5*subplot_height,subplot_width,subplot_height])
            cl = cl_q.get(int(clidstr))
            cl_mean_var = mean(var(transpose(cl.get_sin_cos_phases()),axis=1))
            mean_var_list.append(cl_mean_var)

            if clusterplot_func != None:
                cluster_data = transpose(clusterplot_func(cl))
            else:
                cluster_data = transpose(cl.get_time_flucstuc_properties(fs_props=['frequency']))

            if len(cluster_data) == 0:
                print 'Warning, no data found for cluster %s' %clidstr 
            elif show_lines==True:
                pl.plot(cluster_data[0],cluster_data[1],color=colmap(int(colfactor*cl_mean_var)))
            else:
                pl.plot(cluster_data[0],cluster_data[1],marker='.',color=colmap(int(colfactor*cl_mean_var)), linestyle='None')
            pl.setp(local_axes,xlim=x_lims,ylim=y_lims,xticks=[],yticks=[])
            if show_cluster_id:
                pl.title(clidstr,size=8)
            pl.axes(main_axes)
        text_start_x = 0.1
        text_start_y = 0.9
        text_height = 0.05
        for line_i,line in enumerate(text_list):
            pl.text(text_start_x,text_start_y-line_i*text_height,line,size=14)
        if savename:
            pl.savefig(savename)
        else:
            pl.show()



def dens_function(fs,dens_ch):
    fsq = pyfusion.q(pyfusion.TimeSegmentDataSummary).filter(pyfusion.TimeSegmentDataSummary.timesegment==fs.svd.timesegment).filter(pyfusion.TimeSegmentDataSummary.channel==dens_ch)
    if fsq.count() == 0:
        return -1.0
    else:
        return mean([tsds.mean for tsds in fsq.all()])

def plot_phase_angle_for_fs_list(fs_list,ch_plot=None):
    phase_info = get_phase_info_for_fs_list(fs_list)
    ch_list = []
    for ch_name in phase_info[1]:
        ch_list.append(pyfusion.q(pyfusion.Channel).filter_by(name=ch_name).one())
    if ch_plot == None:
        ch_coords = arange(len(ch_list))
    else:
        ch_coords = [ch.coords.__getattribute__(ch_plot) for ch in ch_list]
    mean_phase_list = [0.0]
    for i in phase_info[0]:
        mean_phase_list.append(i[0])
    std_phase_list = [0.0]
    for i in phase_info[0]:
        std_phase_list.append(i[1])
    csmp = cumsum(mean_phase_list)
    pl.plot(ch_coords, csmp, 'ko')
    pl.plot(ch_coords, csmp, 'r')
    for i,sd in enumerate(std_phase_list):
        pl.plot([ch_coords[i], ch_coords[i]], [csmp[i]-sd, csmp[i]+sd],'b')
    if ch_plot != None:
        pl.xlabel(ch_plot)
    else:
        pl.xlabel('Channels')
    pl.ylabel('Phase')

def get_unique_shots_from_fs_list(fs_list):
    shot_list = [fs.svd.timesegment.shot.shot for fs in fs_list]
    unique_shots = unique(shot_list)
    return unique_shots


def plot_summary_info(fs_list):
    shot_list = get_unique_shots_from_fs_list(fs_list)
    pl.text(0.2,0.8, '# shots = %d' %len(shot_list))
    pl.text(0.2,0.6, 'min shot = %d' %min(shot_list))
    pl.text(0.2,0.4, 'max shot = %d' %max(shot_list))
    pl.text(0.2,0.2, '# datapoints = %d' %len(fs_list))
    pl.xlim(0,1)
    pl.ylim(0,1)
    pl.setp(pl.gca(), xticks=[], yticks=[])

def safe_inv_sqrt(i):
    if i > 0:
        return 1./sqrt(i)
    else:
        return -1.0

def cluster_detail_plot(cluster, d_names, savefig=False, tfargs={}, dfargs={}):
    dens_ch = pyfusion.q(pyfusion.Channel).filter(pyfusion.Channel.name==d_names[0]).one()
    dens_ch2 = pyfusion.q(pyfusion.Channel).filter(pyfusion.Channel.name==d_names[1]).one()
    print 'n_flucstrucs = %d' % len(cluster.flucstrucs)
    pl.subplot(221)
    pl.cla()
    tfplot = ScatterPlot(cluster.flucstrucs, ['svd.timebase[0]'], ['frequency'],xlabel='Time',ylabel='Frequency',title='Cluster %d' %cluster.id,**tfargs)
    pl.subplot(223)
    pl.cla()
    #densfreqplot = ScatterPlot(cluster.flucstrucs, lambda x: dens_function(x,dens_ch), 'frequency', xlabel='Density', ylabel='Frequency', **dfargs)
    alfvenplot = ScatterPlot(cluster.flucstrucs, [lambda x: safe_inv_sqrt(dens_function(x,dens_ch)),lambda x: safe_inv_sqrt(dens_function(x,dens_ch2))], ['frequency', 'frequency'], xlabel='Density^-1/2', ylabel='Frequency', **dfargs)
    pl.subplot(222)
    pl.cla()
    plot_phase_angle_for_fs_list(cluster.flucstrucs, ch_plot='theta')
    pl.subplot(224)
    pl.cla()
    plot_summary_info(cluster.flucstrucs)
    if savefig != False:
        pl.savefig(savefig+'_cl_%d.png' %(cluster.id))
    else:
        pl.show()


def plot_flucstrucs_for_set(set_name, size_factor = 40.0, colour_factor = 30.0, frequency_range = [False,False], time_range=[False,False], savefile = '', number=False):
    #fs_list = pyfusion.session.query(FluctuationStructure).join(['svd','timesegment','shot']).join(['svd','diagnostic']).filter(FluctuationStructureSet.name == set_name).all()
    fs_list = pyfusion.session.query(FluctuationStructure).join(['set']).filter(FluctuationStructureSet.name == set_name).all()
    plot_flucstrucs(fs_list, size_factor = size_factor, colour_factor=colour_factor, frequency_range = frequency_range, time_range=time_range, savefile = savefile, number=number)
    

def plot_flucstrucs_for_shot(shot_number, diag_name, size_factor = 40.0, colour_factor = 30.0, frequency_range = [False,False], time_range=[False,False], savefile = '', number=False):
    """
    TO DO: need to be able to separate flucstrucs from different runs, etc...
    quick fix to allow multiple shot_numbers
    allow "like" matches (still works like == if you use no % signs)
    """
    if len(shape(shot_number)) == 0:
        shot_number=[shot_number]        
        if len(diag_name) == 0: diag_name="%"    # null name returns all.....
#    fs_list = pyfusion.session.query(FluctuationStructure).join(['svd','timesegment','shot']).join(['svd','diagnostic']).filter(pyfusion.Shot.shot == shot).filter(pyfusion.Diagnostic.name == diag_name).all()
    fs_list = pyfusion.session.query(FluctuationStructure).join(['svd','timesegment','shot']).join(['svd','diagnostic']).filter(pyfusion.Shot.shot.in_(shot_number)).filter(pyfusion.Diagnostic.name.like(diag_name)).all()
    plot_flucstrucs(fs_list, size_factor = size_factor, colour_factor=colour_factor, frequency_range = frequency_range, time_range=time_range, savefile = savefile, number=number)

def plot_flucstrucs(fs_list, size_factor = 40.0, colour_factor = 30.0, frequency_range = [False,False], time_range=[False,False], savefile = '', number=False, dither=0.001):
    data = transpose(array([[f.svd.timebase[0], f.frequency, f.energy, f.a12] for f in fs_list]))
    if len(data)==0: raise LookupError, ' no data found for fs list'
#    pl.scatter(data[0],data[1],size_factor*data[2], colour_factor*data[2])
#    pl.figure()
# Use three different symbols according to a12 - side effect is to rescale the colors for
# each symbol type -> so color seems to be reset - i.e. unrelated between ranges.
# tricky way to get the remainder

    s=1 # ellipse scale factor (really want an ellipse - needs more points) - autoscaled?
    ellipse=([[0.45*s,0],[0.3*s,0.7*s], [0,1*s],[-0.3*s,0.7*s],
              [-0.45*s,0],[-0.3*s,-0.7*s],[0,-1*s],[0.3*s,-0.7*s]],0)
    thin_ellipse=([[0.2*s,0],[0.12*s,0.85*s],[0,1*s],[-0.12*s,0.85*s],
                   [-0.2*s,0],[-0.12*s,-0.85*s],[0,-1*s],[0.12*s,-0.85*s]],0)
    vertline=(2,0,0)  # polygon form - 2 sides
    singles = (data[3]==0).nonzero()
    if size(singles)>0: 
        inds=singles
        print "singles************",inds, data[2,inds].flatten()
        print data[2]
        pl.scatter(data[0,inds].flatten(),data[1,inds].flatten(),size_factor*data[2,inds].flatten(),
                   colour_factor*data[2,inds].flatten(),marker=vertline)
        
    remain_a12 = data[3]
    remain_a12[singles]=0
    circs = (remain_a12>0.7).nonzero()
    if size(circs)>0: 
        inds=circs
        remain_a12[inds]=0  # take these out of futher consideration
        print "************",inds, data[2,inds].flatten(),data[2]
        pl.scatter(data[0,inds].flatten(),data[1,inds].flatten(),size_factor*data[2,inds].flatten(), 
                   colour_factor*data[2,inds].flatten(),marker='o') #circles

    midrange = (remain_a12>0.4).nonzero()
    if size(midrange)>0: 
        inds=midrange
        remain_a12[inds]=0  # take these out of futher consideration
        print "************",inds, data[2,inds].flatten(),data[2]
        pl.scatter(data[0,inds].flatten(),data[1,inds].flatten(),0.4*size_factor*data[2,inds].flatten(), 
                   colour_factor*data[2,inds].flatten(), marker=ellipse)

    rest = (remain_a12 > 0).nonzero()
    if size(rest)>0: 
        inds=rest
        print "rest************",inds, data[0,inds].flatten()
        pl.scatter(data[0,inds].flatten(),data[1,inds].flatten(),0.45*size_factor*data[2,inds].flatten(), 
                   colour_factor*data[2,inds].flatten(), marker=thin_ellipse)

    if number:
        ndata=len(data[0])
        print "ndata=", ndata
        for i in range(0,pyfusion.utils.smaller(number, ndata)): 
            interact=pl.isinteractive()
            if interact: pl.ioff()
            if dither:
                dx=data[0,i]*dither*(random_sample()-0.5)
                dy=data[1,i]*dither*(random_sample()-0.5)
            else:
                dx=0
                dy=0
            pl.text(dx+data[0,i], dy+data[1,i], str(fs_list[i].id))
            if interact: pl.ion()
    pl.grid(True)
    if not frequency_range[0]:
        frequency_range[0] = 0
    if not frequency_range[1]:
        nyquist = 0.5/(fs_list[0].svd.timebase[1]-fs_list[0].svd.timebase[0])
        frequency_range[1] = max(data[1]) ## was nyquist
    pl.ylim(frequency_range[0],frequency_range[1])
    if not time_range[0]:
        time_range[0] = min(data[0])
    if not time_range[1]:
        time_range[1] = max(data[0])
    pl.xlim(time_range[0], time_range[1])
# need to write a function str_shot_range to compress long sequences of 
#  shot numbers....  --> [58123-26,39-45], but could do [58123...58245] 
# as a short-cut
    pl.title(str(
        ' %d Fluctuation structures, %s') % (
        len(fs_list), ' '))  #pyfusion.utils.shotrange(shot_numbers))
    # shot_numbers not defined here
    pl.xlabel('Time')
    pl.ylabel('Frequency')
    if savefile != '':
        try:
            pl.savefig(savefile)
        except:
            print 'could not save to filename %s. Please make sure filename ends with .png, .jpg, etc.'
            pl.show()
    else:
        pl.show()


def simple_cluster_plot(clusterdatasetname, xlims = [False,False], ylims =[False, False],  figurename = 'simple_cluster_plot.png'):
    from pyfusion.datamining.clustering.core import ClusterDataSet
    cluster_dataset = pyfusion.session.query(ClusterDataSet).filter_by(name=clusterdatasetname).one()
    cluster_sets =  cluster_dataset.clustersets
# next several lines is to prepare a nxm subplot area and order plots within it.
    cluster_sets_n_clusters = [i.n_clusters for i in cluster_sets]
# sort into sets of increasing n_clusters (normally like this within one clustering)
    cluster_sets_n_clusters_argsort = argsort(cluster_sets_n_clusters)
# allow for horizontal places for the highest n_clusters
    n_plots_horizontal = cluster_sets_n_clusters[cluster_sets_n_clusters_argsort[-1]]
# and vertical as the number of different n_clusters (often max(n_clusters)-1)
    n_plots_vertical = len(cluster_sets_n_clusters_argsort)
    for cs_i, cs_el in enumerate(cluster_sets_n_clusters_argsort):
        for cli, cl in enumerate(cluster_sets[cs_el].clusters):
            plot_line_number = cs_i*n_plots_horizontal + cli + 1
            pl.subplot(n_plots_vertical, n_plots_horizontal, plot_line_number)
# this line is the first to refer to clustered data
            data = transpose(array([[i.svd.timebase[0], i.frequency, i.energy] for i in cl.flucstrucs]))
            pl.plot(data[0],data[1],'.')
            if xlims[0] == False: 
                xlims[0] = min(data[0])
                xlims[1] = max(data[0])
#need to look over all data for ylims - quick fix for now
            if ylims[1] == False: 
                ylims[0] = 0
                ylims[1] = pyfusion.utils.bigger(1.1*max(data[1]),2*average(data[1]))
            pl.xlim(xlims[0], xlims[1])
            pl.ylim(ylims[0], ylims[1])
            if cs_i != len(cluster_sets_n_clusters_argsort)-1:
                pl.setp(pl.gca(), xticklabels=[])
            if cli != 0:
                pl.setp(pl.gca(), yticklabels=[])
            else:
                pl.ylabel('$N_{Cl} = %d$' %(cluster_sets_n_clusters[cluster_sets_n_clusters_argsort[cs_i]]))
    if figurename == "":
        pl.show()
    else:
        pl.savefig(figurename)
            
def cluster_phase_plot(clusterdatasetname, xlims = [False,False], ylims =[-8, 8],  figurename = 'cluster_phase_plot.png'):
    from pyfusion.datamining.clustering.core import ClusterDataSet, Cluster, DeltaPhase
    cluster_dataset = pyfusion.session.query(ClusterDataSet).filter_by(name=clusterdatasetname).one()
    cluster_sets =  cluster_dataset.clustersets
    cluster_sets_n_clusters = [i.n_clusters for i in cluster_sets]
    cluster_sets_n_clusters_argsort = argsort(cluster_sets_n_clusters)
    n_plots_horizontal = cluster_sets_n_clusters[cluster_sets_n_clusters_argsort[-1]]
    n_plots_vertical = len(cluster_sets_n_clusters_argsort)
    for cs_i, cs_el in enumerate(cluster_sets_n_clusters_argsort):
        for cli, cl in enumerate(cluster_sets[cs_el].clusters):
            plot_line_number = cs_i*n_plots_horizontal + cli + 1
            pl.subplot(n_plots_vertical, n_plots_horizontal, plot_line_number)
#            data = transpose(array([[i.svd.timebase[0], i.frequency, i.energy] for i in cl.flucstrucs]))
            phases = [i.phases[0].d_phase for i in cl.flucstrucs]
            pl.plot(phases,'.')
            pl.ylim(ylims[0], ylims[1])
            print phases
            if cs_i != len(cluster_sets_n_clusters_argsort)-1:
                pl.setp(pl.gca(), xticklabels=[])
            if cli != 0:
                pl.setp(pl.gca(), yticklabels=[])
            else:
                pl.ylabel('$N_{Cl} = %d$' %(cluster_sets_n_clusters[cluster_sets_n_clusters_argsort[cs_i]]))
    if figurename == "":
        pl.show()
    else:
        pl.savefig(figurename)
            
