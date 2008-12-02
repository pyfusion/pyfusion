"""
main clustering libs
"""


import pyfusion
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Float, Table, String
from sqlalchemy.orm import relation
from sqlalchemy.orm import eagerload
import pylab as pl
from numpy import mean, average, array, fft, conjugate, arange, searchsorted, argsort, dot, diag, transpose, arctan2, pi, sin, cos, take, argmin, cumsum, resize, shape, ndarray
from pyfusion.utils import r_lib
from pyfusion.visual.core import PLOT_MARKERS
from sqlalchemy import select,func

ordered_channels=[]

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
    raw_energy = Column('raw_energy', Float)
    a1 = Column('a1', Float)
# maybe one day there will be a description field, even though not all SQLs implement it
    a12 = Column('a12', Float,info={'comment':'ratio of first two SVs'})
    a13 = Column('a13', Float)
    tmid = Column('tmid',Float) # need if we access data other than from python
    dt12 = Column('dt12', Float)
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
        if do_ends:
            raise NotImplementedError            
        if not phase_method in ['inversion', 'topo']:
            raise ValueError
        if phase_method == 'topo':
            raise NotImplementedError
        elif phase_method == 'inversion':
            fs_signals = self.get_signals()
            individual_phases = [get_single_phase(fs_signals[i], array(self.svd.timebase), self.frequency) for i in range(len(fs_signals))]
            global ordered_channels
            if (pyfusion.settings.OPT < 2) or (len(ordered_channels) == 0):
                ordered_channels = [pyfusion.session.query(pyfusion.Channel).filter_by(name=name_i).one() for name_i in self.svd.used_channels]
            for ci,c in enumerate(ordered_channels[:-1]):
                tmp = DeltaPhase(flucstruc_id = self.id, channel_1_id = ordered_channels[ci].id, channel_2_id = ordered_channels[ci+1].id, d_phase = float(individual_phases[ci+1]-individual_phases[ci]))
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



def _bk_generate_flucstrucs_for_time_segment(seg,diag_inst, fs_set, store_chronos=False, threshold=pyfusion.settings.SV_GROUPING_THRESHOLD, normalise=True):
    # clear out session (dramatically improves performance)
    pyfusion.session.clear()
    sess = pyfusion.Session()
    seg._load_data()
    
    seg_svd_q = sess.query(pyfusion.MultiChannelSVD).filter_by(timesegment_id=seg.id, diagnostic_id = diag_inst.id)
    if seg_svd_q.count() == 0:
        seg_svd = pyfusion.MultiChannelSVD(timesegment=seg, diagnostic = diag_inst)
        seg_svd._do_svd(store_chronos=store_chronos, normalise=normalise)
        sess.save(seg_svd)
    else:
        # this will raise an exception if there is more than one svd for 
        # theis timesegment and diagnostic, but that's healthy as there
        # should not be more than one
        seg_svd = seg_svd_q.one()
    E = seg_svd.energy
    # sv_groupings = group_svs(seg_svd, threshold=threshold)
    sv_groupings = _new_group_svs(seg_svd)
    for svg_i, sv_group in enumerate(sv_groupings):
        energy = float(sum([sv.value**2 for sv in sv_group])/E)
        raw_energy=0 # not sure how yet
        freq = float(peak_freq(sv_group[0].chrono, seg_svd.timebase))
        tmid = float(average(seg_svd.timebase))
        a1=sv_group[0].value
        if len(sv_group)>1: a12 = sv_group[1].value/sv_group[0].value
        else:               a12=0
        if len(sv_group)>2: a13 = sv_group[2].value/sv_group[0].value
        else:               a13=0
        if pyfusion.settings.VERBOSE>2: 
            print 'svg_i %d, len=%d, fr=%.3gkHz, t0=%.3gms,' % (
                svg_i, len(sv_group), freq/1000, 1000*seg_svd.timebase[0]),
            print 'SV=[%s]'%','.join([str("%.3g") % sv.value for sv in sv_group])
        fs = FluctuationStructure(svd=seg_svd, frequency=freq, 
                                  energy=energy, gamma_threshold=threshold, 
                                  raw_energy=0, a1=a1, a12=a12, tmid=tmid, a13=a13,
                                  set_id = fs_set.id)
        sess.save(fs)
        for sv in sv_group:
            fs.svs.append(sv)
        fs.get_phases()
        sess.save_or_update(fs)
        sess.flush()
        #sess.close()

def generate_flucstrucs_for_time_segment(seg,diag_inst, fs_set, store_chronos=False, threshold=pyfusion.settings.SV_GROUPING_THRESHOLD, normalise=True):
    # clear out session (dramatically improves performance)
    #pyfusion.session.clear()
    seg._load_data()
    
    seg_svd_q = pyfusion.session.query(pyfusion.MultiChannelSVD).filter_by(timesegment_id=seg.id, diagnostic_id = diag_inst.id)
    if seg_svd_q.count() == 0:
        seg_svd = pyfusion.MultiChannelSVD(timesegment=seg, diagnostic = diag_inst)
        seg_svd._do_svd(store_chronos=store_chronos, normalise=normalise)
        pyfusion.session.save(seg_svd)
    else:
        # this will raise an exception if there is more than one svd for 
        # theis timesegment and diagnostic, but that's healthy as there
        # should not be more than one
        seg_svd = seg_svd_q.one()
    E = seg_svd.energy
    # sv_groupings = group_svs(seg_svd, threshold=threshold)
    sv_groupings = _new_group_svs(seg_svd)
    for svg_i, sv_group in enumerate(sv_groupings):
        energy = float(sum([sv.value**2 for sv in sv_group])/E)
        raw_energy=0 # not sure how yet
        freq = float(peak_freq(sv_group[0].chrono, seg_svd.timebase))
        tmid = float(average(seg_svd.timebase))
        a1=sv_group[0].value
        if len(sv_group)>1: a12 = sv_group[1].value/sv_group[0].value
        else:               a12=0
        if len(sv_group)>2: a13 = sv_group[2].value/sv_group[0].value
        else:               a13=0
        if pyfusion.settings.VERBOSE>2: 
            print 'svg_i %d, len=%d, fr=%.3gkHz, t0=%.3gms,' % (
                svg_i, len(sv_group), freq/1000, 1000*seg_svd.timebase[0]),
            print 'SV=[%s]'%','.join([str("%.3g") % sv.value for sv in sv_group])
        fs = FluctuationStructure(svd=seg_svd, frequency=freq, 
                                  energy=energy, gamma_threshold=threshold, 
                                  raw_energy=0, a1=a1, a12=a12, tmid=tmid, a13=a13,
                                  set_id = fs_set.id)
        pyfusion.session.save(fs)
        for sv in sv_group:
            fs.svs.append(sv)
        fs.get_phases()
        pyfusion.session.save_or_update(fs)
        #pyfusion.session.flush()
        #sess.flush()
        #sess.close()


def generate_flucstrucs(shot, diag_name, fs_set_name, store_chronos=False, threshold=pyfusion.settings.SV_GROUPING_THRESHOLD, normalise=True, data_summary_channels = []):
    # get fs_set or register a new one
    try:
        fs_set = pyfusion.session.query(FluctuationStructureSet).filter_by(name=fs_set_name).one()
    except:
        fs_set = FluctuationStructureSet(name = fs_set_name)
        pyfusion.session.save(fs_set)
    segs = pyfusion.get_time_segments(shot, diag_name)
    diag_inst = pyfusion.session.query(pyfusion.Diagnostic).filter(pyfusion.Diagnostic.name == diag_name).one()
    for seg_i, seg in enumerate(segs[::-1]):
        generate_flucstrucs_for_time_segment(seg, diag_inst, fs_set, store_chronos=store_chronos, threshold=threshold, normalise=normalise)
        for ch_name in data_summary_channels:
            seg.generate_data_summary(ch_name,channel=True)
            
    


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
        tmp_cp = [mean(abs(cps(remaining_svs[0].chrono, sv.chrono)))**2/(remaining_svs[0].self_cps*sv.self_cps) for sv in remaining_svs]
        # elements of tmp_cp which pass the threshold values
        filtered_elements = [i for [i,val] in enumerate(tmp_cp) if val > threshold]
        
        # append the new flucstruc, defined by SV numbers
        output_fs_list.append([remaining_svs[i] for i in filtered_elements])
        # remove the newly assigned SV from the remaining SV list so they don't get assigned again
        for i in output_fs_list[-1]: remaining_svs.remove(i)

    return output_fs_list
        

def _new_group_svs(input_SVD):
    """
    input_SVD is an MCSVDData object
    in this function we implicity assume that SVs are sorted from largest to smallest (as returned by most SVD libs)
    """

    output_fs_list = []
    sv_query = pyfusion.session.query(pyfusion.SingularValue).filter_by(svd = input_SVD).order_by(pyfusion.SingularValue.number)

    remaining_svs = [i for i in sv_query]
    E = input_SVD.energy
    remaining_svs_norm_energy = array([i.value**2 for i in remaining_svs])/E
    if pyfusion.settings.ENERGY_THRESHOLD < 1:
        max_element = searchsorted(cumsum(remaining_svs_norm_energy),
                                          pyfusion.settings.ENERGY_THRESHOLD)
        if (pyfusion.settings.VERBOSE>5):
            if max_element < (len(remaining_svs_norm_energy)-1):
                print "Cut: remaining_svs_norm_energy %s || %s" % (
                    str(remaining_svs_norm_energy[:max_element+1]), 
                    str(remaining_svs_norm_energy[max_element+1:]))
            else:   print "Remaining_svs_norm_energy", remaining_svs_norm_energy

        remaining_svs = remaining_svs[:max_element+1]
        remaining_svs_norm_energy = remaining_svs_norm_energy[:max_element+1]   

    for i,_sv in enumerate(remaining_svs):
        remaining_svs[i].self_cps = mean(cps(_sv.chrono,_sv.chrono))
    if pyfusion.settings.VERBOSE>6: 
        print "ENERGY_THRESHOLD = %.3g"% pyfusion.settings.ENERGY_THRESHOLD,
        print "svs.selfcps=%s" % ','.join(
            [str("%.3g") % (rs.self_cps) for rs in remaining_svs])
    while len(remaining_svs) > 1:
        tmp_cp = [mean(abs(cps(remaining_svs[0].chrono, sv.chrono)))**2/(remaining_svs[0].self_cps*sv.self_cps) for sv in remaining_svs]
        tmp_cp_argsort = array(tmp_cp).argsort()[::-1]
        sort_cp = take(tmp_cp,tmp_cp_argsort)
        delta_cp = sort_cp[1:]-sort_cp[:-1]
        if pyfusion.settings.VERBOSE>5: 
            print "svs.cross_cps=%s" % ','.join(
                [str("%.3g") % (cp) for cp in tmp_cp])
            print "svs.cross_sort_cps=%s" % ','.join(
                [str("%.3g") % (cp) for cp in sort_cp])
            print "svs.cross_delta_cps=%s" % ','.join(
                [str("%.3g") % (cp) for cp in delta_cp])
            print "indices to be appended", tmp_cp_argsort[:argmin(delta_cp)+1]
        output_fs_list.append([remaining_svs[i] for i in tmp_cp_argsort[:argmin(delta_cp)+1]])

        # remove the newly assigned SV from the remaining SV list so they don't get assigned again
        for i in output_fs_list[-1]: remaining_svs.remove(i)
    if len(remaining_svs) == 1:
        output_fs_list.append(remaining_svs)

    if pyfusion.settings.VERBOSE>3: 
        print('%d flucstrucs from new_group_svs' % len(output_fs_list))

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
    name = Column("name", String(500), unique=True)
    clustersets = relation("ClusterSet", backref="clusterdataset")
    def plot_BIC(self, loglik=False,log_ncl=False, grid=True):
        import pylab as pl
        model_data = {}
        for cl in self.clustersets:
            if not cl.modelname in model_data.keys():
                model_data[cl.modelname] = {'ncl':[], 'bic':[], 'loglik':[]}
            model_data[cl.modelname]['ncl'].append(cl.n_clusters)
            model_data[cl.modelname]['bic'].append(cl.bic)
            model_data[cl.modelname]['loglik'].append(cl.loglik)
        
        for modelname_i, modelname in enumerate(model_data.keys()):
            if log_ncl != False:
                pl.semilogx(model_data[modelname]['ncl'],model_data[modelname]['bic'],PLOT_MARKERS[modelname_i],label=modelname)
            else:
                pl.plot(model_data[modelname]['ncl'],model_data[modelname]['bic'],PLOT_MARKERS[modelname_i],label=modelname)
            if loglik:
                if log_ncl != False:
                    pl.semilogx(model_data[modelname]['ncl'],model_data[modelname]['loglik'],'k.')
                else:
                    pl.plot(model_data[modelname]['ncl'],model_data[modelname]['loglik'],'k.')

        pl.xlabel('Number of Clusters')
        pl.ylabel('Bayesian Information Classifier (BIC)')
        pl.title('Cluster Dataset: %s' %self.name)
        pl.legend(loc='upper right')
        if grid==True:
            pl.grid()
        pl.show()

    def plot_N_clusters(self,N_clusters,title=""):
        """ Simple f-t plot of this ClusterDataSet for a given N_clusters
        """
        clusterset = pyfusion.session.query(ClusterSet).filter_by(clusterdataset_id=self.id).filter_by(n_clusters=N_clusters).all()   #one() - be more flexible -bdb
        if len(clusterset)>1: 
            len_cset=len(clusterset)
            print("More than one clusterset in %s with %d elements - choosing #%d!!" % 
                  (self.name, len_cset, clusterset.id))
                                    
        clusterset=clusterset[0]  # needed as we now look for all()
        print "**** clusters: ", clusterset.clusters
        for cl in clusterset.clusters:
            t0_freq_list = [[i.svd.timebase[0],i.frequency] for i in cl.flucstrucs]
            pl.plot([i[0] for i in t0_freq_list], [i[1] for i in t0_freq_list],'o')
            pl.title(title+' coloured according to cluster, cset id '+
                     str(self.id)+':'+str(self.name))
        pl.show()

    def plot_N_cumu_phase(self,N_clusters):
        """ Show mean phases and sds like fig 5.X in Dave Pretty thesis
        not finished...
        """
        pass
        clusterset = pyfusion.session.query(ClusterSet).filter_by(clusterdataset_id=self.id).filter_by(n_clusters=N_clusters).one()
        for cl in clusterset.clusters:
            t0_freq_list = [[i.svd.timebase[0],i.frequency] for i in cl.flucstrucs]
            pl.plot([i[0] for i in t0_freq_list], [i[1] for i in t0_freq_list],'o')
        pl.show()

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
    mean_phase_var = Column("mean_phase_var", Float)

    def get_dphase_channel_ids(self):
        """
        Return channel ids for delta phases in the same order as for get_phases() 
        """
        joined_table = Cluster.__table__.join(cluster_flucstrucs).join(
            FluctuationStructure.__table__).join(DeltaPhase.__table__)

        phase_select = select([DeltaPhase.channel_1_id, DeltaPhase.channel_2_id],
                              from_obj=[joined_table]).where(Cluster.id==self.id).group_by(
            DeltaPhase.channel_1_id,DeltaPhase.channel_2_id)
        
        data = array(pyfusion.session.execute(phase_select).fetchall(),dtype='int')

        return data

    def get_dphase_channel_names(self):
        """
        Return channel names for delta phases in the same order as for get_phases() 
        """
        
        channel_id_pairs = self.get_dphase_channel_ids()
        ch_query = pyfusion.q(pyfusion.Channel)
        channel_names = [[ch_query.get(i[0]).name, ch_query.get(i[1]).name] for i in channel_id_pairs]

        return channel_names
        

    def get_phases(self):
        """
        retrieve phase information from fluctuation structres in this cluster
        returns a N_fs x N_phase array, where flucstruc rows are ordered by flucstruc id
        and d_phase columns are ordered by channel1.id, channel2.id
        WARNING: there is no checking to make sure each flucstruc has the same phase channels
        """
        joined_table = Cluster.__table__.join(cluster_flucstrucs).join(
            FluctuationStructure.__table__).join(DeltaPhase.__table__)

        phase_select = select([DeltaPhase.d_phase],from_obj=[joined_table]).where(
            Cluster.id==self.id).group_by(FluctuationStructure.id,DeltaPhase.channel_1_id,DeltaPhase.channel_2_id)

        nfs = len(self.flucstrucs)
        data = array(pyfusion.session.execute(phase_select).fetchall(),dtype='float')

        reshaped_data = data.reshape([nfs,data.shape[0]/nfs])

        return reshaped_data

    def get_sin_cos_phases(self):
        """
        return sin() and cos() components of cluster phases. 
        the array returned from get_phases() is transformed as, for example:
        |a00 a01|     |sin(a00) cos(a00) sin(a01) cos(a01)|
        |a10 a11| --> |sin(a10) cos(a10) sin(a11) cos(a11)|
        |a20 a21|     |sin(a20) cos(a20) sin(a21) cos(a21)|
        """
        cl_ph = self.get_phases()
        cl_cs_phases = ndarray(shape=(cl_ph.shape[0],2*cl_ph.shape[1]))
        cl_cs_phases[:,::2] = sin(cl_ph)
        cl_cs_phases[:,1::2] = cos(cl_ph)
        return cl_cs_phases

    def get_time_flucstuc_properties(self,fs_props=['frequency']):
        joined_table = Cluster.__table__.join(cluster_flucstrucs).join(
            FluctuationStructure.__table__).join(pyfusion.MultiChannelSVD.__table__)
        
        select_list = [pyfusion.MultiChannelSVD.timebase]
        for fs_p in fs_props:
            select_list.append(FluctuationStructure.__dict__[fs_p])

        data_select = select(select_list,from_obj=[joined_table]).where(
            Cluster.id==self.id).group_by(FluctuationStructure.id) 

        data = pyfusion.session.execute(data_select).fetchall()
       
        # take first element of timebase
        data_t0 = map(lambda x: [x[0][0]]+list(x)[1:],data)

        return data_t0

cluster_flucstrucs = Table('cluster_flucstrucs', pyfusion.Base.metadata,
                      Column('cluster_id', Integer, ForeignKey('dm_clusters.id')),
                      Column('flucstruc_id', Integer, ForeignKey('dm_fs.id')))

pyfusion.Base.metadata.create_all()
Cluster.flucstrucs = relation(FluctuationStructure, secondary=cluster_flucstrucs)



def get_sin_cos_phase_for_channel_pairs(fs_list, channel_pairs):
    print "Warning:  not checking channel_pairs!!"
    import time
    data_array = []
    used_fs = []
    t0 = time.time()
    for fsi,fs in enumerate(fs_list):
        if pyfusion.settings.VERBOSE>2: 
            print "getting phases: %d of %d. %.2f secs" % (
                fsi+1, len(fs_list), time.time()-t0)
        tmp_data = []
        tmp = pyfusion.session.query(DeltaPhase).filter_by(flucstruc_id=fs.id).group_by(DeltaPhase.channel_1_id, DeltaPhase.channel_2_id).all()
        for ii in tmp:
            tmp_data.append(sin(ii.d_phase))
            tmp_data.append(cos(ii.d_phase))
        if len(tmp_data) == 2*len(channel_pairs):
            data_array.append(tmp_data)
            used_fs.append(fs)
        else:
            print "maybe error...", len(tmp_data), len(channel_pairs),'fs.id=',fs.id,"!!"
    return [data_array, used_fs]

def _old_get_sin_cos_phase_for_channel_pairs(fs_list, channel_pairs):
    import time
    data_array = []
    used_fs = []
    t0 = time.time()
    for fsi,fs in enumerate(fs_list):
        if pyfusion.settings.VERBOSE>2: 
            print "getting phases: %d of %d. %.2f secs" % (
                fsi+1, len(fs_list), time.time()-t0)
        tmp_data = []
        for chpair in channel_pairs:
            tmp = pyfusion.session.query(DeltaPhase).filter_by(flucstruc_id=fs.id, channel_1_id=chpair[0].id, channel_2_id = chpair[1].id).all()
            if len(tmp) == 1:
                tmp_data.append(sin(tmp[0].d_phase))
                tmp_data.append(cos(tmp[0].d_phase))
        if len(tmp_data) == 2*len(channel_pairs):
            data_array.append(tmp_data)
            used_fs.append(fs)
    return [data_array, used_fs]

def get_clusters(fs_list, channel_pairs, clusterdatasetname,  n_cluster_list = range(2,11), modelnames=None, input_data = None):
    """
    There are a couple of explicit flush() calls here. without them nothing gets saved - 
    is there an alternative way to write the code so we don't need them? this isn't
    really a performance hit, as we only get a flush when saving a clusters, which takes
    much time.
    """
    from rpy import r, RVER
    from numpy import unique  #bdb added
    
    r_lib(r,'mclust')
    
    if input_data != None:
        data_array = input_data
        used_fs = fs_list
    else:
        [data_array, used_fs] = get_sin_cos_phase_for_channel_pairs(fs_list, channel_pairs)

    try:
        clusterdataset = pyfusion.session.query(ClusterDataSet).filter_by(name=clusterdatasetname).one()
    except:
        clusterdataset = ClusterDataSet(name=clusterdatasetname)
    pyfusion.session.save_or_update(clusterdataset)
    pyfusion.session.flush()

# may need this in 2.4.1 bdb - strange behaviour otherwise?
# but occasionally generates warning:
#   clustering/core.py:338: SyntaxWarning: import * only allowed at module level
    if int(RVER) <= 2041:
        from rpy import *
        r.library('mclust')

    for n_clusters in n_cluster_list:
        try:
            if pyfusion.settings.VERBOSE>0: print 'mclust: n_clusters = %d' %n_clusters
            if modelnames:
                MX = r.Mclust(array(data_array),G=n_clusters, 
                              modelNames=modelnames, header='FALSE')
            else:
                MX = r.Mclust(array(data_array),G=n_clusters, header='FALSE')
            # seems to be special case for NCl=1:
            if n_clusters==1:
                if len(MX['bic'].keys()) != 1:
                    raise NotImplementedError
                
                mn = MX['bic'].keys()[0].split(',')[0]
                bic = MX['bic'].values()[0]
            else:
                mn = MX['modelName']
                bic=MX['bic']

            clusterset = ClusterSet(modelname=mn, bic=bic, loglik=MX['loglik'],
                                    n_clusters=n_clusters, n_flucstrucs=MX['n'])
            pyfusion.session.save(clusterset)
            clusterdataset.clustersets.append(clusterset)
            pyfusion.session.flush()
            clusters = [Cluster(clusterset=clusterset) for i in range(n_clusters)]
            cluster_labels = unique(MX['classification']).tolist()
            if len(cluster_labels) != n_clusters:
                raise ValueError, 'Clustering returned wrong number of clusters...'
            for fsi, fs in enumerate(used_fs):
                cluster_el = cluster_labels.index(MX['classification'][fsi])
                clusters[cluster_el].flucstrucs.append(fs)
            for cl in clusters:
                pyfusion.session.save(cl)
            pyfusion.session.save_or_update(clusterset)
        except:
            print "Failed for n_clusters = %d!!" %n_clusters
            raise
        pyfusion.session.save_or_update(clusterdataset)
        # make sure all clusters are saved
        pyfusion.session.flush()

def use_clustvarsel(fs_list, channel_pairs,  max_clusters = 10,max_iterations=100):
    """
    returns new set of channel_pairs as determined by clustvarsel
    """
    from rpy import r
    r_lib(r, 'clustvarsel')

    [data_array, used_fs] = get_sin_cos_phase_for_channel_pairs(fs_list, channel_pairs)

    MX = r.clustvarsel(array(data_array), G=max_clusters,itermax=max_iterations)

    # would be nice not to have to go through hoops to get back the variables...
    da0_as = argsort(data_array[0])
    da0_sorted = take(data_array[0],da0_as)
    new_var_da0_as = searchsorted(da0_sorted,MX['sel.var'][0])
    new_channel_args = take(da0_as,new_var_da0_as)

    if pyfusion.settings.VERBOSE>0:
        print 'new_channel_args:', new_channel_args
        print 'len(channel_pairs): ',len(channel_pairs)
        print 'len(da0)', len(da0_as)

    new_channel_pairs = [channel_pairs[i] for i in new_channel_args]

    return [new_channel_pairs, used_fs, MX['sel.var'], MX['steps.info']]

def get_fs_in_set(fs_set_name,min_energy = 0.0):
    fs_set = pyfusion.session.query(FluctuationStructureSet).filter_by(name=fs_set_name).one()
    fs_query = pyfusion.session.query(FluctuationStructure).filter_by(set=fs_set)
    return fs_query.filter(FluctuationStructure.energy > min_energy).all()

def get_clusters_for_fs_set(fs_set_name,cluster_dataset_name=None, min_energy = 0.0,n_cluster_list = range(2,11),modelnames=None):
    # min energy is a temporary hack - see get_fs_in_set
    if cluster_dataset_name==None: cluster_dataset_name = fs_set_name + '_clusters'
    fs_list = get_fs_in_set(fs_set_name,min_energy = min_energy)
    get_clusters_for_fs_list(fs_list, cluster_dataset_name, n_cluster_list = n_cluster_list,modelnames=modelnames)

def get_clusters_for_fs_list(fs_list, cluster_dataset_name,n_cluster_list = range(2,11),modelnames=None):
    # BAD... should ensure that all used_channels are the same - not just grab them from one FS in the set!
    # do we need to do a query here? probably not
    chs = [pyfusion.session.query(pyfusion.Channel).filter_by(name=i).one() for i in fs_list[0].svd.used_channels]
    # default channel pairs - use pairs from used_channels - assumed to be ordered - at the moment it's taken from ordeed_channel_list
    ch_pairs = [[chs[i],chs[i+1]] for i in range(len(chs)-1)]
    #cluster_dataset_name = fs_set_name + '_clusters'
    if (pyfusion.settings.VERBOSE>0) and (len(fs_list)>1000) : 
        print("a lot of flucstrucs: %d?" % len(fs_list)) 
    get_clusters(fs_list, ch_pairs, cluster_dataset_name,n_cluster_list=n_cluster_list,modelnames=modelnames)
    
