"""
The core components of PyFusion. 
The classes and functions here are imported by pyfusion/__init__.py
"""

from numpy import array,mean,ravel,transpose,arange,var,log, take, shape, ones, searchsorted, load, version as numpy_version, sqrt
from numpy.dual import svd
if int(numpy_version.version.replace('.','')) >= 110: from numpy import savez

from sqlalchemy import Column, Integer, ForeignKey, exceptions, PickleType, Float, Boolean, String, DateTime
from sqlalchemy.orm import relation, synonym

import pyfusion
from pyfusion.coords import Coordinates
from pyfusion.utils import local_import, get_conditional_select, check_same_timebase, delta_t, linear_interpolate_resample

class Device(pyfusion.Base):
    """
    The Device class is used to represent a fusion experiment device, such as JET, LHD, etc...
    An instance of this class, or a class which inherits this class, must reside in pyfusion/devices/DEVICE/DEVICE.py
    where DEVICE is defined in the pyfusion settings
    """
    __tablename__ = "devices"
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(50), nullable=False, unique=True)

class Diagnostic(pyfusion.Base):
    """
    The Diagnostic class is basically just a collection of channels. 
    Diagnostic.channels is defined through a back-reference in the Channel class definition
    """
    __tablename__ = "diagnostics"
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(50), nullable=False, unique=True)
    # this ordered_channel_list guarantees a specific ordering of the channels (defined by
    # the order in which they are added to the diagnostic). This is used for
    # determining the default nearest neighbour channels, etc. This may be 
    # replaced with a numeric value on the channel which would give more
    # rigour to the channel ordering process.
    ordered_channel_list = Column('ordered_channel_list', PickleType)

    def __init__(self, name):
        self.name= name
        self.ordered_channel_list = []
        if pyfusion.settings.VERBOSE>2:
            print('Class Diagnostic __init__ %s') % self.name

    def add_channel(self, channel):
        self.ordered_channel_list.append(channel.name)
        self.channels.append(channel)

    def ordered_channels(self):
        """
        return a list of channel instances corresponding to the names
        in ordered_channel_list
        """
        if len(self.channels) != len(self.ordered_channel_list): 
            print('******** Inconsistency in ordered channels %d != %d!!') % (len(self.channels), len(self.ordered_channel_list))
        outlist = []
        for oc in self.ordered_channel_list:
            outlist.append(pyfusion.session.query(Channel).filter_by(name=oc, diagnostic_id=self.id).one())
        return outlist

class Channel(pyfusion.Base):
    __tablename__ = "channels"
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(50), nullable=False, unique=True)
    data_acq_type = Column('data_acq_type', String(50))
    __mapper_args__ = {'polymorphic_on':data_acq_type}
    diagnostic_id = Column('diagnostic_id', Integer, ForeignKey('diagnostics.id'))
    diagnostic = relation(Diagnostic, primaryjoin=diagnostic_id==Diagnostic.id, backref="channels")
    processdata_override = Column('processdata_override', PickleType, nullable=True)
    coord_id = Column('coord_id', Integer, ForeignKey('coords.id'))
    coords = relation(Coordinates, primaryjoin=coord_id==Coordinates.id)    


class Shot(pyfusion.Base):
    """
    The class to represent any shot-specific data.    
    """
    __tablename__ = "shots"
    id = Column('id', Integer, primary_key=True, index=True)
    shot = Column('shot', Integer)
    device_id = Column('device_id', Integer, ForeignKey('devices.id'))
    device = relation(Device, primaryjoin=device_id==Device.id, backref="shots")    
    shot_type = Column('shot_type', String(50)) ## want something to map...
    date = Column('date',DateTime, default=pyfusion.settings.DEFAULT_SHOT_DATE)
    pulse_start = Column('pulse_start',Float, default=pyfusion.settings.SHOT_PULSE_START)
    __mapper_args__ = {'polymorphic_on':shot_type}
    data = {}
    channels = {}
    def __init__(self, sn):
        """
        sn: shot number (integer)
        """
        self.shot = sn
        self.device_id = pyfusion._device.id
        self.metadata.create_all()
        self.fetch_shot_datetime()
        pyfusion.session.save_or_update(self)

    def fetch_shot_datetime(self):
        try:
            self.date = pyfusion._device_module.get_shot_datetime(self.shot)
        except:
            print 'Failed to get date/time for shot using "get_shot_datetime" in device module!!'

    def load_diag(self, diagnostic, ignore_channels=[], skip_timebase_check = False,savelocal=False,ignorelocal=False, allow_null_return=False, downsample=None):
        if pyfusion.settings.VERBOSE > 0:
            print "Only MultiChannel Timeseries data works for now" 
        diag = pyfusion.session.query(Diagnostic).filter(Diagnostic.name==diagnostic)[0]
        channel_list = []
        if pyfusion.settings.VERBOSE > 0:
            print('tmin=%.4g, tmax=%.4g') % (pyfusion.settings.SHOT_T_MIN, pyfusion.settings.SHOT_T_MAX)
            print "looked up " + diagnostic
            print diag.ordered_channel_list
            
        for ch in diag.ordered_channel_list:
            if ch not in ignore_channels:
                channel_list.append(ch)
        for chi, chn in enumerate(channel_list):
            _tmp = load_channel(self.shot,chn,savelocal=savelocal,ignorelocal=ignorelocal, allow_null_return=allow_null_return)
            if chi==0:
                channel_MCT = _tmp
            else:
                channel_MCT.add_multichannel(_tmp,skip_timebase_check=skip_timebase_check, downsample=downsample)
        self.data[diagnostic] = channel_MCT

    def load_ch(self, chn, skip_timebase_check = False,savelocal=False,ignorelocal=False,allow_null_return=False):
        if pyfusion.settings.VERBOSE > 0:
            print "Only MultiChannel Timeseries data works for now" 
        _tmp = load_channel(self.shot,chn,savelocal=savelocal,ignorelocal=ignorelocal,allow_null_return=allow_null_return)
        channel_MCT = _tmp
        self.channels[chn] = channel_MCT
        


    def define_time_segments(self, diag, n_samples = False, overlap=False):
        """
        Create a list of time segments defined with width n_samples for primary_diag. 
        gives self.time_segments = [elements, times]. elements[:-1] and 
        elements[1:] respectively provide lists for t0 and t1 elements for 
        segments. Likewise, times[:-1] and times[1:] give t0 and t1 time lists
        bdb: Not implemented in exactly this way - in fact n_samples is fixed
        and the interval starts from t0 and is n_samples long.  Due to Dave's 
        foresight, this makes it easy to implement overlap.  If the sample 
        segment length is fixed, then the frequency resolution is fixed, so
        this is a good choice.  
        overlap=0 means no overlap, and overlap=1 means that the entire segment
        is overlapped with its neighbours, half to the preceding segment and 
        half to the succeeding segment thus:
        ================
               =================
                        ================
        overlap=2 is the limit when the segments do not advance in time.
        Takes approx 2/(2-overlap) as long as no overlap.
        @param overlap: 0 (default) for contiguous segments, 1 50% each end, <2 max
        @param n_samples: width of time segment (using sample rate of primary_diag)
        """
        # see note about N_SAMPLES_TIME_SEGMENT in get_time_segments        
        if n_samples == False: n_samples=pyfusion.settings.N_SAMPLES_TIME_SEGMENT
        if overlap == False: overlap=pyfusion.settings.SEGMENT_OVERLAP
        if overlap > 1.99: raise Exception, str('overlap (%.4g) must be < 2, advise < 1.8 !!') % overlap
        len_timebase = len(self.data[diag].timebase)
        overlapped_samples = int((overlap*n_samples)/2)
        if pyfusion.settings.VERBOSE >0: 
            print ("%d samples, %d overlapped") % (n_samples, overlapped_samples)
#        element_list = range(0,len_timebase,n_samples)
# should check the routine that uses the following list (get_time_segment)
# and make sure index error not possible on the last segment
        element_list = range(0,len_timebase-overlapped_samples,n_samples-overlapped_samples)
        times_list = take(self.data[diag].timebase, element_list).tolist()
        #if (len_timebase%n_samples != 0) and zeropad:
        #    element_list.append(len_timebase)
        #    times_list.append(self.data[diag].timebase[-1])
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

class ChannelBaseline(pyfusion.Base):
    __tablename__ = "channel_baselines"
    id = Column('id', Integer, primary_key=True)
    channel_id = Column('channel_id', Integer, ForeignKey('channels.id'))
    channel = relation(Channel, primaryjoin=channel_id==Channel.id)
    shot_id = Column('shot_id', Integer, ForeignKey('shots.id'))
    shot = relation(Shot, primaryjoin=shot_id==Shot.id)
    value = Column('value',Float)



def get_shot(shot_number,shot_class = None):
    if shot_class == None:
        default_shot_class = pyfusion._device_module.DEFAULT_SHOT_CLASS
        if default_shot_class == 'Shot':
            shot_class = Shot
        else:
            try:
                shot_class = pyfusion._device_module.__getattribute__(default_shot_class)
            except:
                raise ValueError,'Cannot load default shot class: %s!!' %default_shot_class
    try:
        existing_shot = pyfusion.session.query(shot_class).filter_by(device_id = pyfusion._device.id, shot = shot_number).one()
        return existing_shot
    except:
        print "Creating shot %s:%d, %s" %(
            pyfusion._device.name, shot_number,
            pyfusion.utils.delta_t('next_shot'))    
        s = shot_class(shot_number)
        return s

def last_shot():
    return pyfusion._device_module.last_shot()

def load_channel(shot_number,channel_name,savelocal=False,ignorelocal=False, allow_null_return=False, ignore_shot_lims = False):
    from os.path import exists
    if ignore_shot_lims:
        ignorelocal=True
        savelocal=False
        tmp_lims = [pyfusion.settings.SHOT_T_MIN, pyfusion.settings.SHOT_T_MAX]
        pyfusion.settings.SHOT_T_MIN = -pyfusion.settings.BIG_FLOAT
        pyfusion.settings.SHOT_T_MAX = pyfusion.settings.BIG_FLOAT
        
    ch = pyfusion.session.query(Channel).filter_by(name=channel_name)[0]
    localfilename = pyfusion.settings.getlocalfilename(shot_number, channel_name)
    if exists(localfilename) and not ignorelocal:
        localdata = load(localfilename)
        # allow for tiny rounding errors
        eps=(localdata['timebase'][-1] - localdata['timebase'][0])/len(localdata['timebase'])
        if pyfusion.settings.SHOT_T_MIN < (localdata['timebase'][0]-eps) \
           or pyfusion.settings.SHOT_T_MAX > (localdata['timebase'][-1]+eps):
            print("localdatatimebase = %g to %g") % (
                localdata['timebase'][0], localdata['timebase'][-1])
            raise ValueError, "SHOT_T_MIN/MAX lie outside the timebase of locally saved data. Either use ignorelocal=True or change pyfusion.settings.SHOT_T_MIN / MAX. While you decide what to do, I'm going to raise an exception and find myself some sangria...!!"
        t_lim = searchsorted(localdata['timebase'],[pyfusion.settings.SHOT_T_MIN,pyfusion.settings.SHOT_T_MAX])            
        loaded_MCT = MultiChannelTimeseries(localdata['timebase'][t_lim[0]:t_lim[1]],parent_element=int(localdata['parent_element']+t_lim[0]))
        loaded_MCT.add_channel(localdata['signal'][t_lim[0]:t_lim[1]],channel_name)
        return loaded_MCT

    if ch.processdata_override:
        _ProcessData = pyfusion._device_module.ProcessData(data_acq_type = ch.data_acq_type, processdata_override = ch.processdata_override)
    else:
        _ProcessData = __import__('pyfusion.data_acq.%s.%s' %(ch.data_acq_type,ch.data_acq_type), globals(), locals(), ['ProcessData']).ProcessData()
    # We trap data item not found exceptions at this level
    # -  advantage is it catches all data systems,
    # -  but the problem is that specific info like MDS stuff (tree, etc) 
    #    can't be easily accessed, and other errors are not traced -  bdb
    #  - Solution - for mid-high VERBOSE levels, try again without handling by "try"
    try:
        _tmp = _ProcessData.load_channel(ch, shot_number)
        if savelocal:
            print ("savelocal to file %s") % (localfilename)
            if int(numpy_version.version.replace('.','')) >= 110:
                savez(localfilename,timebase=_tmp.timebase,
                      signal=_tmp.signals[channel_name],
                      parent_element=_tmp.parent_element)
            else: print("**Warning - not saving - need numpy 1.1.0 or higher!!")
        if ignore_shot_lims:
            pyfusion.settings.SHOT_T_MIN = tmp_lims[0]
            pyfusion.settings.SHOT_T_MAX = tmp_lims[1]
        return _tmp
    except:
        msg=str('Failed to retrieve data from %s, shot %d') % (ch.name, shot_number)
        if allow_null_return:
            _tmp = MultiChannelTimeseries([])
            _tmp.add_channel([], channel_name)
            if ignore_shot_lims:
                pyfusion.settings.SHOT_T_MIN = tmp_lims[0]
                pyfusion.settings.SHOT_T_MAX = tmp_lims[1]
            return _tmp
        if pyfusion.settings.VERBOSE>2:
            print (msg + ': Trying again without catching exception!!')
            _tmp = _ProcessData.load_channel(ch, shot_number)
            if ignore_shot_lims:
                pyfusion.settings.SHOT_T_MIN = tmp_lims[0]
                pyfusion.settings.SHOT_T_MAX = tmp_lims[1]
            raise LookupError, msg
        
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
            raise ValueError, "timebase is not monotonically increasing!!"
        self.timebase = timebase
        self.len_timebase = len(timebase)
        self.nyquist = 0.5/mean(self.timebase[1:]-self.timebase[:-1])
        self.signals = {}
        self.parent_element = parent_element
        self.t0 = min(timebase)
        if pyfusion.settings.VERBOSE>4: print('timebase from %g, nyq=%g' % (
                self.t0, self.nyquist))
        self.norm_info = {} # raw (not normalised) data has empty dict.
        self.ordered_channel_list = [] # keep the order in which channels are added - use this ordering for SVD, etc

    def t_to_element(self, time_list):
        return searchsorted(self.timebase,time_list)

    def add_channel(self,signal,channel_name): 
        signal = array(signal)
        if len(signal) == self.len_timebase:
            self.signals[str(channel_name)] = signal
            self.ordered_channel_list.append(str(channel_name))
        else:
            print "Signal '%s' not same length as timebase. Not adding to multichannel data!!" %channel_name

    def add_multichannel(self, multichanneldata, skip_timebase_check = False, downsample = None,zeropad=True):
        """
        join another MultiChannelTimeseries object to this one
        """
        if downsample != None and multichanneldata.nyquist != self.nyquist:
            for channel_name in multichanneldata.ordered_channel_list:
                resampled_sig = linear_interpolate_resample(multichanneldata.signals[channel_name], multichanneldata.timebase, self.timebase, zeropad=zeropad)
                self.add_channel(resampled_sig, channel_name)
        else:
            
            if skip_timebase_check or check_same_timebase(self, multichanneldata):
                allow_add = True
            else:
                allow_add = False
            if allow_add:
                for channel_name in multichanneldata.ordered_channel_list:
                    self.add_channel(multichanneldata.signals[channel_name], channel_name)
            else:
                print "Timebase not the same. Not joining multichannel data!!"
    
    def export(self, filename, compression = 'bzip2', filetype = 'csv'):
        if compression != 'bzip2':
            raise NotImplementedError
        if filetype != 'csv':
            raise NotImplementedError
        import bz2
        if filename[-4:] != '.bz2':
            filename = filename + '.bz2'
        outfile = bz2.BZ2File(filename,'w')
        header_line = 't'
        for chname in self.ordered_channel_list:
            header_line = header_line + ', %s' %chname
        outfile.write(header_line+'\n')
        for i in range(len(self.timebase)):
            line = str(self.timebase[i])
            for chname in self.ordered_channel_list:
                line = line + ', '+str(self.signals[chname][i])
            outfile.write(line+'\n')
        outfile.close()

    def timesegment(self, t0, dt, use_samples=[False, False], reference_timebase = None):
        """
        return a reduced-time copy of the current MultiChannelTimeseries object
        @param t0: start time of segment (if use_samples[0] = True, then t0 is sample number rather than time)
        @param dt: width (t1-t0) of segment (if use_samples[1] = True, then dt is number of samples rather than length of time)
        @param use_samples: interpret t0, dt as samples instead of time.
        """
        if reference_timebase != None:
            # eek bad code
            if use_samples[0]:
                _t0 = self.timebase.searchsorted(reference_timebase[t0])
                if use_samples[1]:
                    dt = self.timebase.searchsorted(reference_timebase[t0+dt]) - _t0
                t0=_t0

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

    def plot(self, title="",saveas="", xlim=[None, None], 
             ylim=[None, None], hold=False, marker='None', markersize=1,linestyle='-'):
        from matplotlib.ticker import NullFormatter
        import pylab as pl
# change the order so that the first (now lowermost)channel 
#    can act as a template for other xaxes.  Turns out that you can 
#    zoom the x-axis on any equally well.
        num_ch = len(self.ordered_channel_list)
        for ch_i, ch in enumerate(self.ordered_channel_list):
            if ch_i==0: 
                ax1=pl.subplot(num_ch,1,num_ch-ch_i)
            else:
                axn=pl.subplot(num_ch,1, num_ch-ch_i,sharex=ax1)
# both these attempts to suppress the labels affect ALL, as the axes are linked 
# This (sharex) is a nice feature.  An alternative is to unlink axes, and use SpanSelector
#                pl.setp(axn, 'xticklabels', [])
#                axn.xaxis.set_major_formatter(NullFormatter())
            pl.plot(self.timebase,self.signals[ch],hold=hold, marker=marker, markersize=markersize, linestyle=linestyle)
            if pyfusion.settings.VERBOSE>3:
                print("plotting ch %d -> %s" % (ch_i, ch))
            pl.ylabel(ch)
            if xlim[1]!=None : pl.xlim(xlim)    
            if ylim[1]!=None : pl.ylim(ylim)    

        if title:
            try:        # earlier matplotlib doesn't have suptitle
                pl.suptitle(title)
            except:
                pl.xlabel(title)
                
        if saveas:
            pl.savefig(saveas)
        else:
            pl.show()


    def spectrogram(self, max_freq = -1, noverlap=0, NFFT=1024, title="",
                    saveas="", funits='kHz', colorbar=False, figure=None, **kwargs):
        import pylab as pl
        if funits == 'kHz': ffact=1e-3; tunits='ms'
        elif funits == 'MHz': ffact=1e-6; tunits='us'
        else: ffact=1; tunits='sec'
        if (figure): figure(figure.number)
        for ch_i, ch in enumerate(self.ordered_channel_list):
            pl.subplot(len(self.ordered_channel_list),1,ch_i+1)
            Pxx, freqs, bins, im = pl.specgram(self.signals[ch], NFFT=NFFT,
                                               Fs=2.*self.nyquist*ffact,
                                               noverlap=noverlap, **kwargs)
            pl.ylabel(ch+' ('+funits+')')
            if max_freq> 0:
                pl.ylim(0,max_freq)
            pl.xlabel('('+tunits+')')
        if title:
            pl.title(title)
        if colorbar:
            pl.colorbar()
        if saveas:
            pl.savefig(saveas)
        else:
            pl.show()
            
class TimeSegment(pyfusion.Base):
    __tablename__ = 'timesegments'
    id = Column('id', Integer, primary_key=True, index=True)
    shot_id = Column('shot_id', Integer, ForeignKey('shots.id'))
    shot = relation(Shot, primaryjoin=shot_id==Shot.id)    
    primary_diagnostic_id = Column('primary_diagnostic_id', Integer, ForeignKey('diagnostics.id'))
    parent_min_sample = Column('parent_min_sample', Integer)
    n_samples = Column('n_samples', Integer)
    data = {}
    channel_data = {}
    def get_primary_diagnostic(self):
        return pyfusion.session.query(Diagnostic).get(self.primary_diagnostic_id)
    def _load_data(self, diag = None, channel=None, all_diags=False,savelocal=False,ignorelocal=False):
        # if there is no data in the shot (ie - reading from previous run) then try loading the primary diagnostic
        #need to update session - we may have called the time segment from another session ...
        pyfusion.session.save_or_update(self)
        pd = self.get_primary_diagnostic()
        pyfusion.session.flush()
        #print "-------", self.shot
        loaded_diags = self.shot.data.keys()
        loaded_channels = self.shot.channels.keys()
        #print 'loaded_diags', loaded_diags
        #print 'loaded_channels',loaded_channels
        if diag:
            if not diag in loaded_diags:
                self.shot.load_diag(diag, allow_null_return=True)
            # need pd for timebase anyway, although we need only one channel...
            if not pd.name in loaded_diags:
                self.shot.load_diag(pd.name,ignore_channels=pd.ordered_channel_list[1:],ignorelocal=ignorelocal)
            elif pd.ordered_channel_list[0] not in self.shot.data[pd.name].signals.keys():
                self.shot.load_diag(pd.name,ignore_channels=pd.ordered_channel_list[1:],ignorelocal=ignorelocal)                
        elif channel:
            if not channel in loaded_channels:
                self.shot.load_ch(channel, allow_null_return=True)
            if not pd.name in loaded_diags:
                self.shot.load_diag(pd.name,ignore_channels=pd.ordered_channel_list[1:],ignorelocal=ignorelocal)
            elif pd.ordered_channel_list[0] not in self.shot.data[pd.name].signals.keys():
                self.shot.load_diag(pd.name,ignore_channels=pd.ordered_channel_list[1:],ignorelocal=ignorelocal)                
            
        else:
            if not pd.name in loaded_diags:
                self.shot.load_diag(pd.name)

        use_samples = [True, True]

        if not channel:
            if all_diags:
                load_list = self.shot.data.keys()
            elif diag:
                load_list = [diag]
            else:
                load_list = [pd.name]

            for diag_i in load_list:
                if diag_i == pd.name:
                    reference_timebase = None
                else:
                    # TODO: this means that parent_min_sample must refer to the original shot timebase...
                    #_tmp = load_channel(self.shot.shot,pd.ordered_channel_list[0],savelocal=savelocal, ignorelocal=ignorelocal)
                    reference_timebase = self.shot.data[pd.name].timebase
                self.data[diag_i] = self.shot.data[diag_i].timesegment(self.parent_min_sample, 
                                                                       self.n_samples, use_samples=use_samples, reference_timebase=reference_timebase)
        else:
            #ch_data = load_channel(self.shot.shot, channel)
            reference_timebase = self.shot.data[pd.name].timebase
            self.channel_data[channel] = self.shot.channels[channel].timesegment(self.parent_min_sample, 
                                                                                 self.n_samples, use_samples=use_samples, reference_timebase=reference_timebase)
            
    def generate_data_summary(self,diag_name,channel=False, savelocal=False,ignorelocal=False,save=True):
        """
        generate a TimeSegmentDataSummary for this timesegment and channels in diag
        TODO: don't reload data if it's already there
        temporary hack: if channel==True, then diag_name is interpreted as a channel name - will fix but don't want to break much right now
        """
        try:
            output = []
            if channel:
                self._load_data(channel=diag_name,ignorelocal=ignorelocal, savelocal=savelocal)
                ch = pyfusion.session.query(Channel).filter_by(name=diag_name).one()
                _data = self.channel_data[diag_name].signals[diag_name]
                if len(_data)>0:
                    try:
                        cb = pyfusion.session.query(ChannelBaseline).filter_by(shot_id=self.shot_id, channel_id=ch.id).one()
                    except:
                        _full_channel_data = load_channel(self.shot.shot,ch.name,ignore_shot_lims=True)
                        t0el = searchsorted(_full_channel_data.timebase,self.shot.pulse_start)
                        print 'REMOVE THIS HACK!'
                        _tmp = 0
                        # _tmp = float(mean(_full_channel_data.signals[ch.name][:t0el]))
                        if not _tmp < pyfusion.settings.BIG_FLOAT:
                            raise ValueError, 'cannot calculate baseline'
                        cb = ChannelBaseline(shot_id=self.shot_id, channel_id=ch.id, value=_tmp)
                    _mean = mean(_data)
                    _rms = sqrt(mean((_data-_mean)**2))
                    _var = var(_data)
                    tsds = TimeSegmentDataSummary(timesegment_id=self.id, channel_id=ch.id, mean=_mean, rms=_rms, var=_var, baseline=cb)
                    if save:
                        #print 'added tsds'
                        pyfusion.session.save(tsds)
                    output.append(tsds)
                else:
                    print "_data is empty!!"
            else:
                self._load_data(diag=diag_name,ignorelocal=ignorelocal, savelocal=savelocal)
                diag = pyfusion.session.query(Diagnostic).filter(Diagnostic.name==diag_name).one()
                for ch in diag.channels:
                    _data = self.data[diag_name].signals[ch.name]
                    try:
                        cb = pyfusion.session.query(ChannelBaseline).filter_by(shot_id=self.shot_id, channel_id=ch.id).one()
                    except:
                        _full_channel_data = load_channel(self.shot.shot,ch.name,ignore_shot_lims=True)
                        t0el = searchsorted(_full_channel_data.timebase,self.shot.pulse_start)
                        cb = ChannelBaseline(shot_id=self.shot_id, channel_id=ch.id, value=float(mean(_full_channel_data.signals[ch.name][:t0el])))
                    _mean = mean(_data)
                    _rms = sqrt(mean((_data-_mean)**2))
                    _var = var(_data)
                    tsds = TimeSegmentDataSummary(timesegment_id=self.id, channel_id=ch.id, mean=_mean, rms=_rms, var=_var, baseline=cb)
                    if save:
                        pyfusion.session.save(tsds)
                    output.append(tsds)
            return output
        except IndexError:
            # TODO: this exception should be handled in _load_data....
            print 'Data is out of range for timesegment: %d, diagnostic: %s!!' %(self.id, diag_name)
            return False

class TimeSegmentDataSummary(pyfusion.Base):
    __tablename__ = 'timesegment_data_summary'
    id = Column('id',Integer,primary_key=True)
    timesegment_id = Column('timesegment_id', Integer, ForeignKey('timesegments.id'))
    timesegment = relation(TimeSegment, primaryjoin=timesegment_id==TimeSegment.id)
    channel_id = Column('channel_id', Integer, ForeignKey('channels.id'))
    channel = relation(Channel, primaryjoin=channel_id==Channel.id)
    baseline_id = Column('baseline_id', Integer, ForeignKey('channel_baselines.id'))
    baseline = relation(ChannelBaseline, primaryjoin=baseline_id==ChannelBaseline.id)
    mean = Column('mean',Float)
    # RMS after baseline is removed
    rms = Column('rms',Float)
    # variance
    var = Column('var',Float)

class MultiChannelSVD(pyfusion.Base):
    __tablename__ = 'svds'
    id = Column('id', Integer, primary_key=True, index=True)    
    timesegment_id = Column('timesegment_id', Integer, ForeignKey('timesegments.id'))
    timesegment = relation(TimeSegment, primaryjoin=timesegment_id==TimeSegment.id, backref='svd')
    diagnostic_id = Column('diagnostic_id', Integer, ForeignKey('diagnostics.id'))
    diagnostic = relation(Diagnostic, primaryjoin=diagnostic_id==Diagnostic.id)
    svs = relation("SingularValue", backref='svd')
    entropy = Column('entropy', Float)
    energy = Column('energy', Float)
    raw_energy = Column('raw_energy', Float) # Dave wants this - not sure how to calc
    timebase = Column('timebase', PickleType)
    channel_norms = Column('channel_norms', PickleType)
    used_channels = Column('used_channels', PickleType)
    normalised = Column('normalised', Boolean)
    def _get_chrono(self, chrono_number):
        #print '---'
        #print self.timesegment.data.keys()
        #data = array([self.timesegment.data[self.diagnostic.name].signals[c] for c in self.timesegment.data[self.diagnostic.name].ordered_channel_list])
        #data = []
        if not self.diagnostic.name in self.timesegment.data.keys():
            self.timesegment._load_data(diag=self.diagnostic.name)
        data = array([self.timesegment.data[self.diagnostic.name].signals[c] for c in self.timesegment.data[self.diagnostic.name].ordered_channel_list])
        #for c in self.timesegment.data[self.diagnostic.name].ordered_channel_list:
        #    if not c in self.timesegment.data.keys():
                
        #self.timebase = self.timesegment.data[self.diagnostic.name].timebase.tolist()
        #self.used_channels = self.timesegment.data[self.diagnostic.name].ordered_channel_list
        if self.normalised == True:
            #norm_list = []
            for ci,c in enumerate(data):
                #normval = c.var()
                #norm_list.append(normval)
                data[ci] /= self.channel_norms[ci]
            #self.channel_norms = norm_list
        #else:
        #    self.normalised = False
        #    self.channel_norms = []
        [tmp,svs,chronos] = svd(data,0)
        return chronos[chrono_number]

    def _do_svd(self, store_chronos=False, normalise = False, remove_baseline=True):
        data = array([self.timesegment.data[self.diagnostic.name].signals[c] for c in self.timesegment.data[self.diagnostic.name].ordered_channel_list])
        self.timebase = self.timesegment.data[self.diagnostic.name].timebase.tolist()
        self.used_channels = self.timesegment.data[self.diagnostic.name].ordered_channel_list
        if remove_baseline == True:
            data = array([x-mean(x) for x in data])
        if normalise == True:
            self.normalised = True
            norm_list = []
            for ci,c in enumerate(data):
                normval = c.std()
                norm_list.append(normval)
                data[ci] /= normval
            self.channel_norms = norm_list
        else:
            self.normalised = False
            self.channel_norms = []
        
        [tmp,svs,chronos] = svd(data,0)
        topos = transpose(tmp)
        if pyfusion.settings.VERBOSE >= 3: print 'done svd seg %s, %s' %(str(self.id), delta_t("svd"))
        for svi,_sv in enumerate(svs):
            # enforce float to avoid problems with
            # mysql backend saving numpy types
            sv = float(_sv)
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

        self.raw_energy = 0  # dont know how to calc yet.
        
        ### normalised energy of singular values
        p = sv_sq/self.energy

        ### entropy of singular values
        # enforce <type 'float'>, otherwise we get errors trying to save <type 'numpy.float64'>
        self.entropy = float((-1./log(len(svs)))*sum(p*log(p)))


    def plot(self):
        from pyfusion.visual import interactive_svd_plot
        interactive_svd_plot(self)

class SingularValue(pyfusion.Base):
    __tablename__ = 'svs'
    id = Column('id', Integer, primary_key=True)        
    svd_id = Column('svd_id', Integer, ForeignKey('svds.id'))
    number = Column('number', Integer)
    store_chrono = Column('store_chrono', Boolean)
    value = Column('value', Float)
    _chrono = Column('_chrono', PickleType)
    # if we don't store the chrono in sql, keep it here for as long as the object instance lasts..
    _tmp_chrono = []
    topo = Column('topo', PickleType)
    def _reload_chrono(self):
        parent_svd = pyfusion.session.query(MultiChannelSVD).get(self.svd_id)
        self._tmp_chrono = parent_svd._get_chrono(self.number)
        return self._tmp_chrono
    
    def _get_chrono(self):
        if self.store_chrono:
            return self._chrono
        else:
            try:
                if len(self._tmp_chrono) > 0:
                    return self._tmp_chrono
                else:
                    return self._reload_chrono()
            except:
                return self._reload_chrono()

    def _set_chrono(self, chr):
        if self.store_chrono:
            self._chrono = chr
            self._tmp_chrono = []
        else:
            self._chrono = []
            self._tmp_chrono = chr
        
    chrono = synonym('_chrono', descriptor=property(_get_chrono, _set_chrono))


def get_time_segments(shot, primary_diag, n_samples = False):
    # Note: using a default in the arglist uses the value at instantation - 
    # so process_cmd_line_args fails to update that value of the setting
    if n_samples==False: n_samples=pyfusion.settings.N_SAMPLES_TIME_SEGMENT
    shot.define_time_segments(primary_diag, n_samples = n_samples)
    output_list = []
    diag_inst = pyfusion.session.query(Diagnostic).filter_by(name = primary_diag).one()
    for seg_i, seg_min in enumerate(shot.time_segments):
        try:
            seg = pyfusion.session.query(TimeSegment).filter_by(shot = shot, primary_diagnostic_id=diag_inst.id, parent_min_sample=seg_min[0], n_samples=n_samples).one()
        except:# exceptions.InvalidRequestError:
            if pyfusion.settings.VERBOSE >= 4: print "Creating segment %d" % seg_i
            seg  = TimeSegment(shot=shot, primary_diagnostic_id = diag_inst.id, n_samples = n_samples, parent_min_sample = seg_min[0])
        pyfusion.session.save_or_update(seg)
        output_list.append(seg)
    return output_list


def new_timesegment(shot_instance, primary_diagnostic_name, t0, t1):
    diag_inst = pyfusion.session.query(Diagnostic).filter(Diagnostic.name == primary_diagnostic_name).one()
    t_els = shot_instance.data[primary_diagnostic_name].t_to_element([t0,t1])
    ts = TimeSegment(shot_id=shot_instance.id, primary_diagnostic_id=diag_inst.id, parent_min_sample = t_els[0],n_samples = t_els[1]-t_els[0])
    pyfusion.session.save(ts)
    ts._load_data()
    return ts

def new_svd(timesegment_instance, diagnostic_id = -1, normalise=False, remove_baseline=True):
    if diagnostic_id < 0:
        diagnostic_id = timesegment_instance.primary_diagnostic_id
    new_svd = MultiChannelSVD(timesegment_id=timesegment_instance.id, diagnostic_id = diagnostic_id)
    pyfusion.session.save(new_svd)
    pyfusion.session.flush()
    new_svd._do_svd(normalise=normalise, remove_baseline=remove_baseline)
    return new_svd
