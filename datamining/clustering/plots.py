"""
plots for clustering

yes, it's a mess.
"""

import pyfusion
import pylab as pl
from pyfusion.datamining.clustering.core import FluctuationStructure,FluctuationStructureSet, ClusterDataSet, Cluster, ClusterSet
from pyfusion.datamining.clustering.utils import get_phase_info_for_fs_list
from numpy import array,transpose, argsort, min, max, average, shape, mean, cumsum, unique, sqrt, intersect1d
from pyfusion.visual.core import ScatterPlot, golden_ratio

from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relation


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


def dendro_coords(ncl, cl, max_ncl, h_sp, v_sp, aspect, margins = [1,1,1,1]):
    # assume horizontal subplot length = 1
    # margins = [l,r,t,b]
    # cl starts at 1 not 0
    pl_height = max_ncl*aspect + (max_ncl-1)*v_sp
    delta_h = pl_height/ncl
    x_loc = margins[0] + ncl-1 + (ncl-2)*h_sp
    y_loc = margins[3] + pl_height - (cl-0.5)*delta_h  
    return [x_loc, y_loc]



class Dendrogram(pyfusion.Base):
    """
    class to produce a dendrogram for a ClusterDataSet
    """
    __tablename__ = "dm_plots_dendrogram"
    id = Column('id', Integer, primary_key=True)
    head_cluster_id = Column('head_cluster_id', Integer, ForeignKey('dm_clusters.id'))
    head_cluster = relation(Cluster, primaryjoin=head_cluster_id==Cluster.id)
    def __init__(self, head_cluster):
        self.head_cluster = head_cluster
        # get n_clusters of head_cluster
        self.head_clusterset = self.head_cluster.clusterset
        if self.head_clusterset.n_clusters != 1:
            print "Warning: Not starting from n_clusters = 1, results may be strange"
        self.cluster_dataset = self.head_clusterset.clusterdataset
        self.max_n_clusters = max([cs.n_clusters for cs in self.cluster_dataset.clustersets])
        
    def get_links(self):
        parent_clusters = [self.head_cluster]
        for n_cl in range(self.head_clusterset.n_clusters+1, self.max_n_clusters+1):
            child_clusterset = pyfusion.q(ClusterSet).filter_by(clusterdataset_id=self.cluster_dataset.id, n_clusters=n_cl).one()
            child_clusters = child_clusterset.clusters
            for parent in parent_clusters:
                for child in child_clusters:
                    if pyfusion.q(DendrogramLink).filter_by(parent=parent,child=child).count() == 0:
                        fs_intersection  = len(intersect1d(parent.flucstrucs, child.flucstrucs))
                        frac = float(fs_intersection)/len(parent.flucstrucs)
                        _tmp = DendrogramLink(parent_id=parent.id, child_id=child.id, fraction = frac, fs_intersection=fs_intersection)
                        pyfusion.session.save_or_update(_tmp)
            #pyfusion.session.flush()
            #pyfusion.session.commit()
            parent_clusters = child_clusters
    def simple_plot(self):
        # testing code - will make variables available outside of method later...
        # subplot with is defined as 1, everything else scaled accordingly
        subplot_aspect = golden_ratio**-1 # ratio of height/width
        horizontal_subplot_spacing = 0.3
        vertical_subplot_spacing = horizontal_subplot_spacing*subplot_aspect
        main_plot_left_margin =3*horizontal_subplot_spacing
        main_plot_right_margin = horizontal_subplot_spacing
        main_plot_top_margin = 3*vertical_subplot_spacing
        main_plot_bottom_margin = vertical_subplot_spacing
        
        x_subplot_offset = -0.7
        y_subplot_offset = -0.3

        main_plot_height = (self.max_n_clusters-1)*vertical_subplot_spacing + self.max_n_clusters*subplot_aspect + main_plot_bottom_margin + main_plot_top_margin
        n_cl_width = (self.max_n_clusters-self.head_clusterset.n_clusters + 1)
        main_plot_width = n_cl_width + (n_cl_width - 1)*horizontal_subplot_spacing + main_plot_left_margin + main_plot_right_margin
        plot_coords = {}
        plot_coords[str(self.head_cluster.id)] = dendro_coords(1, 1, self.max_n_clusters, horizontal_subplot_spacing, vertical_subplot_spacing, subplot_aspect, [main_plot_left_margin, main_plot_right_margin, main_plot_top_margin, main_plot_bottom_margin])
        clustersets = self.cluster_dataset.clustersets
        clustersets_ncl = [i.n_clusters for i in clustersets]
        
        fig = pl.figure()

        main_axes = pl.axes([0,0,1,1])
        pl.axis([-main_plot_left_margin, main_plot_left_margin+main_plot_width, -main_plot_bottom_margin, main_plot_height - main_plot_bottom_margin],'off')
        main_axis = pl.gca()
        #pl.xlim(-main_plot_left_margin, main_plot_left_margin+main_plot_width)
        #pl.ylim(-main_plot_bottom_margin, main_plot_height - main_plot_bottom_margin)
        pl.setp(main_axis, xticks=[],yticks=[])

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
                    c1 = dendro_coords(child_cl_set.n_clusters, child_cli, self.max_n_clusters, horizontal_subplot_spacing, vertical_subplot_spacing, subplot_aspect, [main_plot_left_margin, main_plot_right_margin, main_plot_top_margin, main_plot_bottom_margin])
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

                    
                    
            #plot_coords = minimise_crossing(plot_coords, all_links)
            # plot all links
            
            for cli,cl in enumerate(new_pcls):
                links = all_links[cli]
                for li,l in enumerate(links):
                    c0 = plot_coords[str(cl.id)]
                    c1 = plot_coords[str(l.child.id)]
                    pl.plot([c0[0],c1[0]], [c0[1],c1[1]],lw=20.*l.fs_intersection/len(self.head_cluster.flucstrucs),color='k')
                    #pl.text(c1[0],c1[1],str(l.child_id),color='r')
        for clidstri,clidstr in enumerate(plot_coords.keys()):
            print "cl %d of %d" %(clidstri+1, len(plot_coords.keys()))
            pl.axes(main_axis)
            clco = plot_coords[clidstr]
            #local_axes = pl.axes([clco[0],clco[1],1,subplot_aspect],transform=fig.transFigure)
            local_axes = pl.axes([(clco[0]+main_plot_left_margin+x_subplot_offset)/main_plot_width,(clco[1]+main_plot_bottom_margin+y_subplot_offset)/main_plot_height,1./(main_plot_width-main_plot_left_margin-main_plot_right_margin),subplot_aspect/(main_plot_height-main_plot_bottom_margin-main_plot_top_margin)],transform=fig.transFigure)
            cl = pyfusion.q(Cluster).filter_by(id=int(clidstr)).one()
            tfplot = ScatterPlot(cl.flucstrucs, ['svd.timesegment.shot.kappa_h'], ['frequency'],xlabel='',ylabel='',title='Cl %d (%d)' %(cl.id, len(cl.flucstrucs)))
            pl.setp(local_axes,xlim=(0,1.1),ylim=(0,120000),xticks=[0.2,0.4,0.6,0.8,1.0],xticklabels=[],yticks=[])

        pl.axes(main_axis)

        pl.xlim(-main_plot_left_margin, main_plot_left_margin+main_plot_width)
        pl.ylim(-main_plot_bottom_margin, main_plot_height - main_plot_bottom_margin)

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


def plot_flucstrucs_for_set(set_name, size_factor = 30.0, colour_factor = 30.0, frequency_range = [False,False], time_range=[False,False], savefile = ''):
    #fs_list = pyfusion.session.query(FluctuationStructure).join(['svd','timesegment','shot']).join(['svd','diagnostic']).filter(FluctuationStructureSet.name == set_name).all()
    fs_list = pyfusion.session.query(FluctuationStructure).join(['set']).filter(FluctuationStructureSet.name == set_name).all()
    plot_flucstrucs(fs_list, size_factor = size_factor, colour_factor=colour_factor, frequency_range = frequency_range, time_range=time_range, savefile = savefile)
    

def plot_flucstrucs_for_shot(shot_number, diag_name, size_factor = 30.0, colour_factor = 30.0, frequency_range = [False,False], time_range=[False,False], savefile = ''):
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
    plot_flucstrucs(fs_list, size_factor = size_factor, colour_factor=colour_factor, frequency_range = frequency_range, time_range=time_range, savefile = savefile)

def plot_flucstrucs(fs_list, size_factor = 30.0, colour_factor = 30.0, frequency_range = [False,False], time_range=[False,False], savefile = ''):
    data = transpose(array([[f.svd.timebase[0], f.frequency, f.energy] for f in fs_list]))
    pl.scatter(data[0],data[1],size_factor*data[2], colour_factor*data[2])
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
            
