"""
The core components of PyFusion. 
The classes and functions here are imported by pyfusion/__init__.py

requirements:
numpy
sqlalchemy version >= 0.4.4 (version 0.4.4 is required for the declarative extension)
"""

from numpy import array,mean,ravel,transpose,arange,var,log, take, shape, ones
from numpy.dual import svd
from utils import local_import, get_conditional_select, check_same_timebase
import settings 

from sqlalchemy import Column, Integer, ForeignKey, exceptions, PickleType, Float, Boolean#, Numeric
from sqlalchemy.orm import relation
import pyfusion


def get_shot(shot_number):    
    try:
        existing_shot = pyfusion.session.query(Shot).filter(Shot.device_id == pyfusion._device.id).filter(Shot.shot == shot_number).one()
        return existing_shot
    except:
        print "Creating shot %s:%d" %(pyfusion._device.name, shot_number)    
        s = Shot(shot_number)
        return s
    

class Shot(pyfusion.Base):
    """
    The class to represent any shot-specific data.    
    """
    __tablename__ = "shots"
    id = Column('id', Integer, primary_key=True)
    shot = Column('shot', Integer)
    device_id = Column('device_id', Integer, ForeignKey('devices.id'))
    device = relation(pyfusion.Device, primaryjoin=device_id==pyfusion.Device.id, backref="shots")    
    data = {}
    def __init__(self, sn):
        """
        sn: shot number (integer)
        """
        self.shot = sn
        self.device_id = pyfusion._device.id
        self.metadata.create_all()
        pyfusion.session.save_or_update(self)
        pyfusion.session.commit()


    def load_diag(self, diagnostic, ignore_channels=[]):
        print "Only MultiChannel Timeseries data works for now"
        diag = pyfusion.session.query(pyfusion.Diagnostic).filter(pyfusion.Diagnostic.name==diagnostic)[0]
        channel_list = []
        print diag
        print diag.ordered_channel_list
        for ch in diag.ordered_channel_list:
            if ch not in ignore_channels:
                channel_list.append(ch)
        for chi, chn in enumerate(channel_list):
            ch = pyfusion.session.query(pyfusion.Channel).filter(pyfusion.Channel.name==chn)[0]
            _ProcessData = __import__('pyfusion.data_acq.%s.%s' %(ch.data_acq_type,ch.data_acq_type), globals(), locals(), ['ProcessData']).ProcessData()
            if chi==0:
                channel_MCT = _ProcessData.load_channel(ch, self.shot)
            else:
                _tmp = _ProcessData.load_channel(ch, self.shot)
                channel_MCT.add_multichannel(_tmp)
        self.data[diagnostic] = channel_MCT

    def define_time_segments(self, diag, n_samples = settings.N_SAMPLES_TIME_SEGMENT, include_remainder = False):
        """
        Create a list of time segments defined with width n_samples for primary_diag. 
        gives self.time_segments = [elements, times]. elements[:-1] and elements[1:] respectively provide lists for t0 and t1 elements for segements. Likewise, times[:-1] and times[1:] give t0 and t1 time lists
        @param n_samples: width of time segment (using sample rate of primary_diag)
        @param include_remainder: choose how to treat remainder if len(signal) / n_samples is not integer. if True, self.time_segments will include the final segment even if it has length other than n_samples. If False, trailing data will be ignored
        """
        len_timebase = len(self.data[diag].timebase)
        element_list = range(0,len_timebase,n_samples)
        times_list = take(self.data[diag].timebase, element_list).tolist()
        if (len_timebase%n_samples == 0) or include_remainder:
            element_list.append(len_timebase)
            times_list.append(self.data[diag].timebase[-1])
	self.time_segments = [[element_list[i], times_list[i]] for i in range(len(element_list))]

    def time_segment(self, segment_number, diag = ''):
        """
        return time segment for diag. 
        @param segment_number: segment is defined by self.time_segments[0][segment_number] : self.time_segments[0][segment_number+1] (or time_segments[0] -> time_segments[1])
        """
        if diag == '':
            diag = self.primary_diag

        if diag == self.primary_diag:
            # skip timebase test
            [e0,e1] = [self.time_segments[0][segment_number], self.time_segments[0][segment_number+1]]
            return self.data[diag].timesegment(e0,e1-e0, use_samples=[True, True])
        elif check_same_timebase(self.data[diag],self.data[self.primary_diag]):
            [e0,e1] = [self.time_segments[0][segment_number], self.time_segments[0][segment_number+1]]
            return self.data[diag].timesegment(e0,e1-e0, use_samples=[True, True])
        else:
            [t0,t1] = [self.time_segments[1][segment_number], self.time_segments[1][segment_number+1]]
            return self.data[diag].timesegment(t0,t1-t0, use_samples=[False, False])


class MultiChannelTimeseries(object):
    """
    A class to hold multichannel data. 
    """
    def __init__(self,timebase, parent_element = 0):
        """
        initiate with the timebase
        parent_element is to help keep track of where splitting occurs...
        """
        timebase = array(timebase)
        # check timebase is monotonically increasing
        if min(timebase[1:]-timebase[:-1]) <= 0:
            raise ValueError, "timebase is not monotonically increasing"
        self.timebase = timebase
        self.len_timebase = len(timebase)
        self.nyquist = 0.5/mean(self.timebase[1:]-self.timebase[:-1])
        self.signals = {}
        self.parent_element = parent_element
        self.t0 = min(timebase)
        self.norm_info = {} # raw (not normalised) data has empty dict.
        self.ordered_channel_list = [] # keep the order in which channels are added - use this ordering for SVD, etc

    def add_channel(self,signal,channel_name):
        signal = array(signal)
        if len(signal) == self.len_timebase:
            self.signals[str(channel_name)] = signal
            self.ordered_channel_list.append(str(channel_name))
        else:
            print "Signal '%s' not same length as timebase. Not adding to multichannel data" %channel_name

    def add_multichannel(self, multichanneldata):
        """
        join another MultiChannelTimeseries object to this one
        """
        if check_same_timebase(self, multichanneldata):
            for channel_name in multichanneldata.ordered_channel_list:
                self.add_channel(multichanneldata.signals[channel_name], channel_name)
        else:
            print "Timebase not the same. Not joining multichannel data"
    
        
    #def ica(self,selected_channels = [], exclude_selected=True):
    #    """
    #    Independent Component Analysis
    #    """
    #    import mdp
    #    use_channels = get_conditional_select(self.signals.keys(), selected_channels, exclude_selected
    #
    #    use_channel_data = array([self.signals[i] for i in use_channels])
    #    ica_out = mdp.fastica(transpose(use_channel_data),failures=10)
    #
    #    return ica_out

    #def normalise(self, norm = 'var', remove_baseline = True, seperate_channels = True):
    #    """
    #    normalise signals. use undo_normalisation to reverse the process.
    #    """
    #    if not [norm, remove_baseline, seperate_channels] == ['var', True, True]:
    #        print 'Not normalising: arguments not implemented yet: ', norm, remove_baseline, seperate_channels
    #    else:
    #        self.norm_info['channels'] = self.signals.keys()
    #        self.norm_info['baseline'] = {}
    #        self.norm_info['type'] = norm
    #        self.norm_info['norms'] = {}
    #        
    #        if remove_baseline:
    #            for ch_i, ch in enumerate(self.norm_info['channels']):
    #                baseline = mean(self.signals[ch])
    #                self.norm_info['baseline'][ch] = baseline
    #                self.signals[ch] = self.signals[ch]-baseline
    #        if norm == 'var':
    #            for ch_i, ch in enumerate(self.norm_info['channels']):
    #                var_val = self.signals[ch].var()
    #                self.norm_info['norms'][ch] = var_val
    #                self.signals[ch] = self.signals[ch]/var_val
                
                

    #def undo_normalise(self):
    #    if self.norm_info == {}:
    #        print 'Data not normalised'
    #    else:
    #        print 'undo_normalise not implemented yet'


    def timesegment(self, t0, dt, use_samples=[False, False]):
        """
        return a reduced-time copy of the current MultiChannelTimeseries object
        @param t0: start time of segment (if use_samples[0] = True, then t0 is sample number rather than time)
        @param dt: width (t1-t0) of segment (if use_samples[1] = True, then dt is number of samples rather than length of time)
        @param use_samples: interpret t0, dt as samples instead of time.
        """
        # element for t0
        if use_samples[0]:
            e0 = t0
        else:
            e0 = self.timebase.searchsorted(t0)
        
        if use_samples[1]:
            e1 = t0+dt
        else:
            e1 = self.timebase.searchsorted(self.timebase[e0] + dt)
        
        new_mc_data = MultiChannelTimeseries(self.timebase[e0:e1], parent_element=e0)
        
        for ch in self.ordered_channel_list:
            new_mc_data.add_channel(self.signals[ch][e0:e1],ch)
        return new_mc_data

    
class TimeSegment(pyfusion.Base):    
    __tablename__ = 'timesegments'
    id = Column('id', Integer, primary_key=True)
    shot_id = Column('shot_id', Integer, ForeignKey('shots.id'))
    shot = relation(Shot, primaryjoin=shot_id==Shot.id)    
    primary_diagnostic_id = Column('primary_diagnostic_id', Integer, ForeignKey('diagnostics.id'))
    parent_min_sample = Column('parent_min_sample', Integer)
    n_samples = Column('s_samples', Integer)
    data = {}
    def _load_data(self):
        for diag in self.shot.data.keys():
            self.data[diag] = self.shot.data[diag].timesegment(self.parent_min_sample, self.n_samples, use_samples=[True, True])

class MultiChannelSVD(pyfusion.Base):
    __tablename__ = 'svds'
    id = Column('id', Integer, primary_key=True)    
    timesegment_id = Column('timesegment_id', Integer, ForeignKey('timesegments.id'))
    timesegment = relation(TimeSegment, primaryjoin=timesegment_id==TimeSegment.id, backref='svd')
    diagnostic_id = Column('diagnostic_id', Integer, ForeignKey('diagnostics.id'))
    diagnostic = relation(pyfusion.Diagnostic, primaryjoin=diagnostic_id==pyfusion.Diagnostic.id)
    svs = relation("SingularValue", backref='svd')
    entropy = Column('entropy', Float)
    energy = Column('energy', Float)
    timebase = Column('timebase', PickleType)
    channel_norms = Column('channel_norms', PickleType)
    normalised = Column('normalised', Boolean)
    def _do_svd(self, store_chronos=False, normalise = False):
        data = array([self.timesegment.data[self.diagnostic.name].signals[c] for c in self.timesegment.data[self.diagnostic.name].ordered_channel_list])
        self.timebase = self.timesegment.data[self.diagnostic.name].timebase.tolist()
        if normalise == True:
            self.normalised = True
            norm_list = []
            for ci,c in enumerate(data):
                normval = c.var()
                norm_list.append(normval)
                data[ci] /= norval
            self.channel_norms = norm_list
        else:
            self.normalised = False
            self.channel_norms = []
        [tmp,svs,chronos] = svd(data,0)
        topos = transpose(tmp)
        print 'done svd for %s' %(str(self.id))
        for svi,sv in enumerate(svs):
            if store_chronos:
                tmp1 = SingularValue(svd_id = self.id, number=svi, value=sv, chrono=chronos[svi].tolist(), topo=topos[svi].tolist())
            else:
                tmp1 = SingularValue(svd_id = self.id, number=svi, value=sv, chrono=None, topo=topos[svi].tolist())
            pyfusion.session.save(tmp1)
            self.svs.append(tmp1)
        ### (I read somewhere that x*x is faster than x**2)
        sv_sq = svs*svs
        
        ### total energy of singular values
        self.energy = sum(sv_sq)
        
        ### normalised energy of singular values
        p = sv_sq/self.energy

        ### entropy of singular values
        self.entropy = (-1./log(len(svs)))*sum(p*log(p))

    
class SingularValue(pyfusion.Base):
    __tablename__ = 'svs'
    id = Column('id', Integer, primary_key=True)        
    svd_id = Column('svd_id', Integer, ForeignKey('svds.id'))
    number = Column('number', Integer)
    value = Column('value', Float)
    chrono = Column('chrono', PickleType)
    topo = Column('topo', PickleType)




def get_time_segments(shot, primary_diag, n_samples = settings.N_SAMPLES_TIME_SEGMENT):
    shot.define_time_segments(primary_diag, n_samples = n_samples)
    output_list = []
    diag_inst = pyfusion.session.query(pyfusion.Diagnostic).filter_by(name = primary_diag).one()
    for seg_i, seg_min in enumerate(shot.time_segments):
        try:
            seg = pyfusion.session.query(TimeSegment).filter_by(shot = shot, primary_diagnostic_id=diag_inst.id, parent_min_sample=seg_min[0], n_samples=n_samples).one()
        except:# exceptions.InvalidRequestError:
            print "Creating segment %d" %seg_i
            seg  = TimeSegment(shot=shot, primary_diagnostic_id = diag_inst.id, n_samples = n_samples, parent_min_sample = seg_min[0])
        seg._load_data()
        output_list.append(seg)
        pyfusion.session.save_or_update(seg)
    pyfusion.session.flush()
    return output_list

