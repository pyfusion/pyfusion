"""
plots for clustering

yes, it's a mess.
"""

import pyfusion
import pylab as pl
from pyfusion.datamining.clustering.core import FluctuationStructure,FluctuationStructureSet
from pyfusion.datamining.clustering.utils import get_phase_info_for_fs_list
from numpy import array,transpose, argsort, min, max, average, shape, mean, cumsum, unique
from pyfusion.visual.core import ScatterPlot

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

def cluster_detail_plot(clusterset, density_channel_name, savefig=False, tfargs={}, dfargs={}):
    dens_ch = pyfusion.q(pyfusion.Channel).filter(pyfusion.Channel.name==density_channel_name).one()
    for cluster in clusterset.clusters:
        print 'n_flucstrucs = %d' % len(cluster.flucstrucs)
        pl.subplot(221)
        pl.cla()
        tfplot = ScatterPlot(cluster.flucstrucs, 'svd.timebase[0]', 'frequency',xlabel='Time',ylabel='Frequency',title='Cluster %d' %cluster.id,**tfargs)
        pl.subplot(223)
        pl.cla()
        densfreqplot = ScatterPlot(cluster.flucstrucs, lambda x: dens_function(x,dens_ch), 'frequency', xlabel='Density', ylabel='Frequency', **dfargs)
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

def dendrogram(clusterdatasetname):
    pass

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
            
