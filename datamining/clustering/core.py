"""
main clustering libs
"""


import pyfusion
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Float, Table, String
from sqlalchemy.orm import relation
from sqlalchemy.orm import eagerload
import pylab as pl
from numpy import mean, array, fft, conjugate, arange, searchsorted, argsort, dot, diag, transpose, arctan2, pi, sin, cos


class DeltaPhase(pyfusion.Base):
    __tablename__ = 'dm_dphase'
    id = Column('id', Integer, primary_key=True)
    flucstruc_id = Column('flucstruc_id', Integer, ForeignKey('dm_fs.id'))
    channel_1_id = Column('channel_1_id', Integer, ForeignKey('channels.id'))
    channel_2_id = Column('channel_2_id', Integer, ForeignKey('channels.id'))
    d_phase = Column('d_phase', Float)


class FluctuationStructure(pyfusion.Base):
    __tablename__ = 'dm_fs'
    id = Column('id', Integer, primary_key=True)
    svd_id = Column('svd_id', Integer, ForeignKey('svds.id'))
    svd = relation(pyfusion.MultiChannelSVD, primaryjoin=svd_id==pyfusion.MultiChannelSVD.id, backref="flucstruc")    
    frequency = Column('frequency', Float)
    energy = Column('energy', Float)
    gamma_threshold = Column('gamma_threshold', Numeric)
    phases = relation("DeltaPhase", backref='flucstruc')
    set_id = Column('set_id', Integer, ForeignKey('dm_fs_set.id'))
    def get_signals(self):
        sv_chrono_arr = array([i.chrono for i in self.svs])
        sv_val_arr = diag(array([i.value for i in self.svs]))
        sv_topo_arr = transpose(array([i.topo for i in self.svs]))
        fs_signals = dot(sv_topo_arr,dot(sv_val_arr, sv_chrono_arr))
        return fs_signals
    def get_phases(self, phase_method = 'inversion', do_ends = False):
        # flush so we have self.svd.timebase....
        pyfusion.session.flush()
        if do_ends:
            raise NotImplementedError            
        if not phase_method in ['inversion', 'topo']:
            raise ValueError
        if phase_method == 'topo':
            raise NotImplementedError
        elif phase_method == 'inversion':
            fs_signals = self.get_signals()
            individual_phases = [get_single_phase(fs_signals[i], array(self.svd.timebase), self.frequency) for i in range(len(fs_signals))]
            ordered_channels = [pyfusion.session.query(pyfusion.Channel).filter_by(name=name_i).one() for name_i in self.svd.used_channels]
            for ci,c in enumerate(ordered_channels[:-1]):
                tmp = DeltaPhase(flucstruc_id = self.id, channel_1_id = ordered_channels[ci].id, channel_2_id = ordered_channels[ci+1].id, d_phase = individual_phases[ci+1]-individual_phases[ci])
                self.phases.append(tmp)
            

flucstruc_svs = Table('flucstruc_svs', pyfusion.Base.metadata,
                      Column('flucstruc_id', Integer, ForeignKey('dm_fs.id')),
                      Column('sv_id', Integer, ForeignKey('svs.id')))

class FluctuationStructureSet(pyfusion.Base):
    __tablename__ = 'dm_fs_set'
    id = Column('id', Integer, primary_key=True)
    name = Column("name", String(100), unique=True)
    flucstrucs = relation("FluctuationStructure", backref='set')


pyfusion.Base.metadata.create_all()
FluctuationStructure.svs = relation(pyfusion.SingularValue, secondary=flucstruc_svs)


def get_single_phase(data,timebase,freq):
	sample_freq = 1./mean(timebase[1:]-timebase[:-1])
	data_fft = fft.fft(data)
	# fft goes up to sample freq (mirror-like about Nyquist)
	freq_array = sample_freq*arange(len(data_fft))/(len(data_fft)-1)
	freq_elmt = searchsorted(freq_array,freq)
	a = data_fft[freq_elmt].real
	b = data_fft[freq_elmt].imag
	phase_val = arctan2(a,b)
	return phase_val




def generate_flucstrucs(shot, diag_name, fs_set_name, store_chronos=False, threshold=pyfusion.settings.SV_GROUPING_THRESHOLD, normalise=True):
    # register the fs_set name
    fs_set = FluctuationStructureSet(name = fs_set_name)
    # get id ofr fs_set    
    pyfusion.session.save(fs_set)
    pyfusion.session.commit()
    import datetime
    segs = pyfusion.get_time_segments(shot, diag_name)
    diag_inst = pyfusion.session.query(pyfusion.Diagnostic).filter(pyfusion.Diagnostic.name == diag_name).one()
    for seg_i, seg in enumerate(segs[::-1]):
        # clear out session (dramatically improves performance)
        pyfusion.session.clear()
        seg._load_data()
        try:
            seg_svd = pyfusion.session.query(pyfusion.MultiChannelSVD).filter_by(timesegment_id=seg.id, diagnostic_id = diag_inst.id).one()
        except:
            seg_svd = pyfusion.MultiChannelSVD(timesegment_id=seg.id, diagnostic_id = diag_inst.id)
            pyfusion.session.save(seg_svd)
            pyfusion.session.flush()
            seg_svd._do_svd(store_chronos=store_chronos, normalise=normalise)
            pyfusion.session.flush()
        E = seg_svd.energy
        sv_groupings = group_svs(seg_svd, threshold=threshold)
        for sv_group in sv_groupings:
            energy = sum([sv.value**2 for sv in sv_group])/E
            freq = peak_freq(sv_group[0].chrono, seg_svd.timebase)
            fs = FluctuationStructure(svd_id=seg_svd.id, frequency=freq, energy=energy, gamma_threshold=threshold, set_id = fs_set.id)
            pyfusion.session.save(fs)
            for sv in sv_group:
                fs.svs.append(sv)
            fs.get_phases()

            
    


def group_svs(input_SVD, threshold = pyfusion.settings.SV_GROUPING_THRESHOLD):
    """
    input_SVD is an MCSVDData object
    in this function we implicity assume that SVs are sorted from largest to smallest (as returned by most SVD libs)
    """
    #check_inputtype(self,input_SVD,'MultiChannelSVD')
    
    output_fs_list = []
    sv_query = pyfusion.session.query(pyfusion.SingularValue).filter_by(svd = input_SVD).order_by(pyfusion.SingularValue.number)
    
    remaining_svs = [i for i in sv_query]
    for i,_sv in enumerate(remaining_svs):
        remaining_svs[i].self_cps = mean(cps(_sv.chrono,_sv.chrono))

    while len(remaining_svs) > 0:
        tmp_cp = [mean(abs(cps(remaining_svs[0].chrono, sv.chrono)))/(remaining_svs[0].self_cps*sv.self_cps) for sv in remaining_svs]
        # elements of tmp_cp which pass the threshold values
        filtered_elements = [i for [i,val] in enumerate(tmp_cp) if val > threshold]
        
        # append the new flucstruc, defined by SV numbers
        output_fs_list.append([remaining_svs[i] for i in filtered_elements])
        # remove the newly assigned SV from the remaining SV list so they don't get assigned again
        for i in output_fs_list[-1]: remaining_svs.remove(i)

    return output_fs_list
        


def peak_freq(signal,timebase,minfreq=0,maxfreq=1.e18):
	"""
	TODO: old code: needs review
	"""
	timebase = array(timebase)
	sig_fft = fft.fft(signal)
	sample_time = float(mean(timebase[1:]-timebase[:-1]))
	fft_freqs = (1./sample_time)*arange(len(sig_fft)).astype(float)/(len(sig_fft)-1)
	# only show up to nyquist freq
	new_len = len(sig_fft)/2
	sig_fft = sig_fft[:new_len]
	fft_freqs = fft_freqs[:new_len]
	[minfreq_elmt,maxfreq_elmt] = searchsorted(fft_freqs,[minfreq,maxfreq])
	sig_fft = sig_fft[minfreq_elmt:maxfreq_elmt]
	fft_freqs = fft_freqs[minfreq_elmt:maxfreq_elmt]

	peak_elmt = (argsort(abs(sig_fft)))[-1]
	return fft_freqs[peak_elmt]


def cps(a,b):
	return fft.fft(a)*conjugate(fft.fft(b))

class ClusterDataSet(pyfusion.Base):
    __tablename__ = 'dm_cluster_datasets'
    id = Column('id', Integer, primary_key=True)
    name = Column("name", String(20), unique=True)
    clustersets = relation("ClusterSet", backref="clusterdataset")
    

class ClusterSet(pyfusion.Base):
    __tablename__ = 'dm_cluster_sets'
    id = Column('id', Integer, primary_key=True)
    clusters = relation("Cluster", backref="clusterset")
    modelname = Column("model_name", String(10))
    bic = Column("bic", Float)
    loglik = Column("loglik", Float)
    n_clusters = Column("n_clusters", Integer)
    n_flucstrucs = Column("n_flucstrucs", Integer)
    clusterdataset_id = Column("clusterdataset_id", Integer, ForeignKey('dm_cluster_datasets.id'))

class Cluster(pyfusion.Base):
    __tablename__ = 'dm_clusters'
    id = Column('id', Integer, primary_key=True)
    clusterset_id = Column("clusterset_id", Integer, ForeignKey('dm_cluster_sets.id'))

cluster_flucstrucs = Table('cluster_flucstrucs', pyfusion.Base.metadata,
                      Column('cluster_id', Integer, ForeignKey('dm_clusters.id')),
                      Column('flucstruc_id', Integer, ForeignKey('dm_fs.id')))

pyfusion.Base.metadata.create_all()
Cluster.flucstrucs = relation(FluctuationStructure, secondary=cluster_flucstrucs)



def get_clusters(fs_list, channel_pairs, clusterdatasetname,  n_cluster_list = range(2,11)):
    from rpy import *
    try:
        r.library('mclust')
    except:
        raw_input("\nR library 'mclust' not found: press Enter to install...\n")
        r("install.packages('mclust')")
        r.library('mclust')
    
    data_array = []
    used_fs = []
    for fs in fs_list:
        tmp_data = []
        for chpair in channel_pairs:
            tmp = pyfusion.session.query(DeltaPhase).filter_by(flucstruc_id=fs.id, channel_1_id=chpair[0].id, channel_2_id = chpair[1].id).all()
            if len(tmp) == 1:
                tmp_data.append(sin(tmp[0].d_phase))
                tmp_data.append(cos(tmp[0].d_phase))
        if len(tmp_data) == 2*len(channel_pairs):
            data_array.append(tmp_data)
            used_fs.append(fs)
    clusterdataset = ClusterDataSet(name=clusterdatasetname)
    pyfusion.session.save(clusterdataset)
    pyfusion.session.flush()
    
    for n_clusters in n_cluster_list:
        print 'n_clusters = %d' %n_clusters
        MX = r.Mclust(array(data_array),G=n_clusters, header='FALSE')
        clusterset = ClusterSet(modelname=MX['modelName'], bic=MX['bic'], loglik=MX['loglik'], n_clusters=n_clusters, n_flucstrucs=MX['n'])
        pyfusion.session.save(clusterset)
        clusterdataset.clustersets.append(clusterset)
        # to get id...
        pyfusion.session.flush()
        clusters = [Cluster(clusterset_id=clusterset.id) for i in range(n_clusters)]
        cluster_labels = unique(MX['classification']).tolist()
        if len(cluster_labels) != n_clusters:
            raise ValueError, 'Clustering returned wrong number of clusters...'
        for fsi, fs in enumerate(used_fs):
            cluster_el = cluster_labels.index(MX['classification'][fsi])
            clusters[cluster_el].flucstrucs.append(fs)
        for cl in clusters:
            pyfusion.session.save(cl)
    pyfusion.session.flush()
