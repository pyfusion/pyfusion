"""
Some un-pythonic code here (checking instance type inside
function). Need to figure out a better way to do this.
"""
from datetime import datetime
from pyfusion.debug_ import debug_
from pyfusion.utils.utils import warn
import copy
from numpy import searchsorted, arange, mean, resize, repeat, fft, conjugate, linalg, array, zeros_like, take, argmin, pi, cumsum
from numpy import correlate as numpy_correlate
import numpy as np


try:
    from scipy import signal as sp_signal
except:
    # should send message to log...
    pass

import pyfusion

DEFAULT_SEGMENT_OVERLAP = 1.0


def cps(a,b):
    return fft.fft(a)*conjugate(fft.fft(b))


filter_reg = {}


def register(*class_names):
    def reg_item(filter_method):
        for cl_name in class_names:
            if not filter_reg.has_key(cl_name):
                filter_reg[cl_name] = [filter_method]
            else:
                filter_reg[cl_name].append(filter_method)
        return filter_method
    return reg_item

"""
class MetaFilter(type):
    def __new__(cls, name, bases, attrs):
        filter_methods = filter_reg.get(name, [])
        attrs.update((i.__name__,i) for i in filter_methods)
        return super(MetaFilter, cls).__new__(cls, name, bases, attrs)
"""

def get_optimum_time_range(input_data, new_time_range):
    from pyfusion.utils.primefactors import fft_time_estimate

    nt_args = searchsorted(input_data.timebase, new_time_range)
    # try for 20 more points
    extension = ((new_time_range[1]-new_time_range[0])
                *float(20)/(nt_args[1]-nt_args[0]))
    (dum,trial_upper) = searchsorted(input_data.timebase, 
                                  [new_time_range[0],
                                   new_time_range[1]+extension])
    # if not consider using less than the original request
    trial_lower = trial_upper - 20
    times = []
    for num in range(trial_lower, trial_upper):
        times.append(fft_time_estimate(num - nt_args[0]))

    newupper = trial_lower+np.argmin(times)
    if newupper != nt_args[1]: 
        pyfusion.utils.warn('Interval fft optimized from {old} to {n} points'
                            .format(n=newupper-nt_args[0], 
                                    old=nt_args[1]-nt_args[0]))

    best_upper_time = input_data.timebase[newupper]
    new_time_range[1] = (best_upper_time 
                         - 0.5*np.average(np.diff(input_data.timebase)))
    if pyfusion.VERBOSE>0: 
        print('returning new time range={n}'.format(n=new_time_range))
    return(new_time_range)

@register("TimeseriesData", "DataSet")
def reduce_time(input_data, new_time_range, fftopt=False):
    """ reduce the time range of the input data in place(copy=False)
    or the returned Dataset (copy=True - default at present). 
    if fftopt, then extend time if possible, or if not reduce it so that
    ffts run reasonably fast. Should consider moving this to actual filters?
    But this way users can obtain optimum fft even without filters.
    The fftopt is only visited when it is a dataset, and this isn't happening
    """
    from pyfusion.data.base import DataSet
    if pyfusion.VERBOSE>1: 
        print('Entering reduce_time, fftopt={0}, isinst={1}'
              .format(fftopt,isinstance(input_data, DataSet) ))
        pyfusion.logger.warning("Testing: can I see this?")
    if isinstance(input_data, DataSet):
        if fftopt: new_time_range = get_optimum_time_range(input_data, new_time_range)

        #output_dataset = input_data.copy()
        #output_dataset.clear()
        print('****new time range={n}'.format(n=new_time_range))
        output_dataset = DataSet(input_data.label+'_reduce_time')
        for data in input_data:
            try:
                output_dataset.append(data.reduce_time(new_time_range))
            except AttributeError:
                pyfusion.logger.warning("Data filter 'reduce_time' not applied to item in dataset")
        return output_dataset

    #??? this should not need to be here - should only be called from
    # above when passed as a dataset (more efficient)
    if fftopt: new_time_range = get_optimum_time_range(input_data, new_time_range)
    new_time_args = searchsorted(input_data.timebase, new_time_range)
    input_data.timebase =input_data.timebase[new_time_args[0]:new_time_args[1]]
    if input_data.signal.ndim == 1:
        input_data.signal = input_data.signal[new_time_args[0]:new_time_args[1]]
    else:
        input_data.signal = input_data.signal[:,new_time_args[0]:new_time_args[1]]
    if pyfusion.VERBOSE>1: print('reduce_time to length {l}'
                                 .format(l=np.shape(input_data.signal))),
    return input_data


@register("TimeseriesData", "DataSet")
def segment(input_data, n_samples, overlap=DEFAULT_SEGMENT_OVERLAP):
    """Break into segments length n_samples.

    Overlap of 2.0 starts a new segment halfway into previous, overlap=1 is
    no overlap.  overlap should divide into n_samples.  Probably should
    consider a nicer definition such as in pyfusion 0
    """
    from pyfusion.data.base import DataSet
    from pyfusion.data.timeseries import TimeseriesData
    if isinstance(input_data, DataSet):
        output_dataset = DataSet()
        for ii,data in enumerate(input_data):
            try:
                output_dataset.update(data.segment(n_samples))
            except AttributeError:
                pyfusion.logger.warning("Data filter 'segment' not applied to item in dataset")
        return output_dataset
    output_data = DataSet('segmented_%s, %d samples, %.3f overlap' %(datetime.now(), n_samples, overlap))
    for el in arange(0,len(input_data.timebase), n_samples/overlap):
        if input_data.signal.ndim == 1:
            tmp_data = TimeseriesData(timebase=input_data.timebase[el:el+n_samples],
                                      signal=input_data.signal[el:el+n_samples],
                                      channels=input_data.channels, bypass_length_check=True)
        else:
            tmp_data = TimeseriesData(timebase=input_data.timebase[el:el+n_samples],
                                      signal=input_data.signal[:,el:el+n_samples],
                                      channels=input_data.channels, bypass_length_check=True)
            
        tmp_data.meta = input_data.meta.copy()
        tmp_data.history = input_data.history  # bdb - may be redundant now meta is copied
        output_data.add(tmp_data)
    return output_data

@register("DataSet")
def remove_noncontiguous(input_dataset):
    remove_list = []
    for item in input_dataset:
        if not item.timebase.is_contiguous():
            remove_list.append(item)
    for item in remove_list:
        input_dataset.remove(item)
    return input_dataset

@register("TimeseriesData", "DataSet")
def normalise(input_data, method=None, separate=False):
    """ method=None -> default, method=0 -> DON'T normalise
    """
    from numpy import mean, sqrt, max, abs, var, atleast_2d
    from pyfusion.data.base import DataSet
    # this allows method='0'(or 0) to prevent normalisation for cleaner code
    # elsewhere
    if pyfusion.DEBUG>3: print('separate = %d' % (separate))
    if (method == 0) or (method == '0'): return(input_data)
    if (method == None) or (method.lower() == "none"): method='rms'
    if isinstance(input_data, DataSet):
        output_dataset = DataSet(input_data.label+"_normalise")
        for d in input_data:
            output_dataset.add(normalise(d, method=method, separate=separate))
        return output_dataset
    if method.lower() in ['rms', 'r']:
        if input_data.signal.ndim == 1:
            norm_value = sqrt(mean(input_data.signal**2))
        else:
            rms_vals = sqrt(mean(input_data.signal**2, axis=1))
            if separate == False:
                rms_vals = max(rms_vals)
            norm_value = atleast_2d(rms_vals).T            
    elif method.lower() in ['peak', 'p']:
        if input_data.signal.ndim == 1:
            norm_value = abs(input_data.signal).max(axis=0)
        else:
            max_vals = abs(input_data.signal).max(axis=1)
            if separate == False:
                max_vals = max(max_vals)
            norm_value = atleast_2d(max_vals).T
    elif method.lower() in ['var', 'variance', 'v']:
        if input_data.signal.ndim == 1:
            norm_value = var(input_data.signal)
        else:
            var_vals = var(input_data.signal, axis=1)
            if separate == False:
                var_vals = max(var_vals)
            norm_value = atleast_2d(var_vals).T            
    input_data.signal = input_data.signal / norm_value
    #print('norm_value = %s' % norm_value)
    norm_hist = ','.join(["{0:.2g}".format(v) for v in norm_value.flatten()])
    input_data.history += "\n:: norm_value =[{0}]".format(norm_hist)
    input_data.history += ", method={0}, separate={1}".format(method, separate)
    input_data.scales = norm_value

    debug_(pyfusion.DEBUG, key='normalise',msg='about to return from normalise')
    return input_data
    
@register("TimeseriesData")
def svd(input_data):
    from timeseries import SVDData
    svddata = SVDData(input_data.timebase, input_data.channels, linalg.svd(input_data.signal, 0))
    svddata.history = input_data.history
    svddata.scales = input_data.scales # need to pass it on to caller
    if pyfusion.DEBUG>4: print("input_data.scales",input_data.scales)
    debug_(pyfusion.DEBUG, key='svd',msg='about to return from svd')
    return svddata


#@register("TimeseriesData", "SVDData")
def fs_group_geometric(input_data, max_energy = 1.0):
    """
    no filtering implemented yet
    we don't register this as a filter, because it doesn't return a Data or DataSet subclass
    TODO: write docs for how to use max_energy - not obvious if using flucstruc() filter...
    """
    from timeseries import SVDData
    #from base import OrderedDataSet

    if not isinstance(input_data, SVDData):
        input_data = input_data.subtract_mean().normalise(method="var").svd()

    output_fs_list = []#OrderedDataSet()

    if max_energy < 1.0:
        max_element = searchsorted(cumsum(input_data.p), max_energy)
        remaining_ids = range(max_element)
    else:
        remaining_ids = range(len(input_data.svs))
    
    self_cps = input_data.self_cps()

    while len(remaining_ids) > 1:
        rsv0 = remaining_ids[0]
        tmp_cp = [mean(abs(cps(input_data.chronos[rsv0], input_data.chronos[sv])))**2/(self_cps[rsv0]*self_cps[sv]) for sv in remaining_ids]
        tmp_cp_argsort = array(tmp_cp).argsort()[::-1]
        sort_cp = take(tmp_cp,tmp_cp_argsort)
        delta_cp = sort_cp[1:]-sort_cp[:-1]
        
        output_fs_list.append([remaining_ids[i] for i in tmp_cp_argsort[:argmin(delta_cp)+1]])
            

        for i in output_fs_list[-1]: remaining_ids.remove(i)
    if len(remaining_ids) == 1:
        output_fs_list.append(remaining_ids)

    return output_fs_list


#@register("SVDData")
def fs_group_threshold(input_data, threshold=0.7):   # was 0.2 in earlier version
    """
    no filtering implemented yet
    we don't register this as a filter, because it doesn't return a Data or DataSet subclass
    """
    from timeseries import SVDData

    if not isinstance(input_data, SVDData):
        input_data = input_data.subtract_mean().normalise(method="var").svd()
    
    
    #svd_data = linalg.svd(norm_data.signal,0)
    output_fs_list = []

    #svs_norm_energy = array([i**2 for i in svd_data[1]])/input_data.E

    #max_element = searchsorted(cumsum(svs_norm_energy), energy_threshold)
    #remaining_ids = range(max_element)
    remaining_ids = range(len(input_data.svs))
    
    self_cps = input_data.self_cps()

    while len(remaining_ids) > 1:
        rsv0 = remaining_ids[0]
        tmp_cp = [mean(abs(cps(input_data.chronos[rsv0], input_data.chronos[sv])))**2/(self_cps[rsv0]*self_cps[sv]) for sv in remaining_ids]
        filtered_elements = [i for [i,val] in enumerate(tmp_cp) if val > threshold]
        output_fs_list.append([remaining_ids[i] for i in filtered_elements])
            

        for i in output_fs_list[-1]: remaining_ids.remove(i)
    if len(remaining_ids) == 1:
        output_fs_list.append(remaining_ids)

    return output_fs_list

@register("TimeseriesData")
def flucstruc(input_data, min_dphase = -pi, group=fs_group_geometric, method='rms', separate=True, label=None, segment=0, segment_overlap=DEFAULT_SEGMENT_OVERLAP):
    """If segment is 0, then we dont segment the data (assume already done)"""
    from pyfusion.data.base import DataSet
    from pyfusion.data.timeseries import FlucStruc

    if label:
        fs_dataset = DataSet(label)
    else:
        fs_dataset = DataSet('flucstrucs_%s' %datetime.now())

    if segment > 0:
        for seg in input_data.segment(segment, overlap=segment_overlap):
            fs_dataset.update(seg.flucstruc(min_dphase=min_dphase, group=group, method=method, separate=separate, label=label, segment=0))
        return fs_dataset

    svd_data = input_data.subtract_mean().normalise(method, separate).svd()
    for fs_gr in group(svd_data):
        tmp = FlucStruc(svd_data, fs_gr, input_data.timebase, min_dphase=min_dphase, phase_pairs=input_data.__dict__.get("phase_pairs",None))
        tmp.meta = input_data.meta
        tmp.history = svd_data.history
        tmp.scales = svd_data.scales
        fs_dataset.add(tmp)    
    return fs_dataset


@register("TimeseriesData", "DataSet")
def subtract_mean(input_data):
    from pyfusion.data.base import DataSet
    if isinstance(input_data, DataSet):
        output_dataset = DataSet(input_data.label+"_subtract_mean")
        for d in input_data:
            output_dataset.add(subtract_mean(d))
        return output_dataset
    if input_data.signal.ndim == 1:
        mean_value = mean(input_data.signal)
        input_data.history += "\n:: mean_value\n%s" %(mean_value)
    else:
        mean_vector = mean(input_data.signal, axis=1)
        input_data.history += "\n:: mean_vector\n%s" %(mean_vector)
        mean_value = resize(repeat(mean_vector, input_data.signal.shape[1]), input_data.signal.shape)
    input_data.signal -= mean_value

    return input_data

###############################
## Wrappers to SciPy filters ##
###############################
@register("TimeseriesData")
def sp_filter_butterworth_bandpass(input_data, passband, stopband, max_passband_loss, min_stopband_attenuation,btype='bandpass'):
    """ 
      **   Warning - fails for a single signal in the enumerate step.
    This actually does ALL butterworth filters - just select bptype
    and use scalars instead of [x,y] for the passband.
     e.g df=data.sp_filter_butterworth_bandpass(2e3,4e3,2,20,btype='lowpass')
    """
    # The SciPy signal processing module uses normalised frequencies, so we need to normalise the input values
    norm_passband = input_data.timebase.normalise_freq(passband)
    norm_stopband = input_data.timebase.normalise_freq(stopband)
    ord,wn = sp_signal.filter_design.buttord(norm_passband, norm_stopband, max_passband_loss, min_stopband_attenuation)
    b, a = sp_signal.filter_design.butter(ord, wn, btype = btype)
    
    output_data = copy.deepcopy(input_data)  # was output_data = input_data

    for i,s in enumerate(output_data.signal):
        if len(output_data.signal) == 1: print('bug for a single signal')
        output_data.signal[i] = sp_signal.lfilter(b,a,s)

    return output_data

@register("TimeseriesData")
def filter_fourier_bandpass(input_data, passband, stopband, taper=None, debug=None):
    """ 
    Note: Would be MUCH (2.2x faster) more efficient to use real ffts, 
    Use a Fourier space taper/tophat or pseudo gaussian filter to perform 
    narrowband filtering (much narrower than butterworth).  
    Problem is that bursts may generate ringing. (should be better with taper=2)  
    >>> tb = dummytb(np.linspace(0,20,512))
    >>> w = 2*np.pi* 1  # 1 Hertz
    >>> dat = dummysig(tb,np.sin(w*tb.timebase)*(tb.timebase<np.max(tb.timebase)/3))
    >>> fop = filter_fourier_bandpass(dat,[0.9,1.1],[0.8,1.2],debug=2).signal[0]

    """
    if debug == None: debug = pyfusion.DEBUG
# normalising makes it easier to think about - also for But'w'h 
    norm_passband = input_data.timebase.normalise_freq(np.array(passband))
    norm_stopband = input_data.timebase.normalise_freq(np.array(stopband))
    ns = len(input_data.signal[0])
    mask = np.zeros(ns)
    # define the 4 key points 
    #         /npblow-------------npbhi\
    # ___nsbl/                          \nsbhi____
    n_sb_low = int(norm_stopband[0]*ns/2)
    n_pb_low = int(norm_passband[0]*ns/2)
    n_pb_hi = int(norm_passband[1]*ns/2)
    n_sb_hi = int(norm_stopband[1]*ns/2)

    wid = max(n_pb_low - n_sb_low,n_sb_hi - n_pb_hi)
    if wid < 4: 
        if taper == 2: 
            raise ValueError(
            'taper 2 requres a bigger margin between stop and pass') 
        elif taper == None:
            warn('defaulting taper to 1 as band edges are sharp')
            taper = 1
    else: 
        if taper == None:
            taper = 2

    if taper==1:
        for n in range(n_sb_low,n_pb_low+1):
            if n_pb_low == n_sb_low:  # allow for pass=stop on low side
                mask[n]=1.
            else:
                mask[n] = float(n - n_sb_low)/(n_pb_low - n_sb_low) # trapezoid
        for n in range(n_pb_hi,n_sb_hi+1):
            mask[n] = float(n_sb_hi - n)/(n_sb_hi - n_pb_hi) # trapezoid
        for n in range(n_pb_low,n_pb_hi+1):
            mask[n] = 1
    elif taper == 2:
        # symmetrise (so that cumsum works)

        n_pb_low = n_sb_low+wid
        n_sb_hi = n_pb_hi+wid

        for n in range(n_sb_low,n_pb_low+1):
            mask[n] = float(n - n_sb_low)/(n_pb_low - n_sb_low) # trapezoid
            mask[2*n_pb_low-n+1] = mask[n] #down ramp
        wid_up = n_sb_hi - n_pb_hi
        for n in range(n_pb_hi,n_sb_hi+1):
            mask[n] = -float(n_sb_hi - n)/(n_sb_hi - n_pb_hi) # trapezoid
            mask[2*n_pb_hi - n - 1] = mask[n]
        mask = np.cumsum(mask) # integrate
        mask = mask/np.max(mask)
    # this even and odd is not totally thought through...but it seems OK
    if np.mod(ns,2)==0: mask[:ns/2:-1] = mask[1:(ns/2)]   # even
    else:            mask[:1+ns/2:-1] = mask[1:(ns/2)] # odd 
    output_data = copy.deepcopy(input_data)  # was output_data = input_data

    for i,s in enumerate(output_data.signal):
        #if len(output_data.signal) == 1: print('bug for a single signal')
        FT = np.fft.fft(s)
        IFT = np.fft.ifft(mask*FT)
        if np.max(np.abs(IFT.imag)) > 1e-6*np.max(np.abs(IFT.real)):
            pyfusion.logger.warning("inverse fft imag part > 1e-6")

        output_data.signal[i] = IFT.real
        
    if debug>2: 
        import pylab as pl
        pl.plot(mask,'ro-')
        pl.plot(np.abs(FT)/len(mask))
        pl.plot(input_data.signal[0])
        pl.plot(output_data.signal[0])
        pl.show()
    debug_(debug, 1, key='filter_fourier')
    if np.max(mask) == 0: raise ValueError('Filter blocks all signals')
    return output_data


#########################################
## wrappers to numpy signal processing ##
#########################################
@register("TimeseriesData")
def correlate(input_data, index_1, index_2, **kwargs):
    return numpy_correlate(input_data.signal[index_1],
                           input_data.signal[index_2], **kwargs)

if __name__ == "__main__":
# this is a pain - I can see the benefit of unit tests/nose tests. bdb
    class dummytb():
        def normalise_freq(self, freq):
            return(2*freq*np.average(np.diff(self.timebase)))

        def __init__(self, tb):
            self.timebase = tb

    class dummysig():
        def __init__(self, tb,sig):
            self.timebase = tb
            self.signal = [sig]

    import doctest
    doctest.testmod()
    import pylab as pl
    pl.figure()
    tb = dummytb(np.linspace(0,20,2048))
    w = 2*np.pi* 10  # 10 Hertz
    dat = dummysig(tb,np.sin(w*tb.timebase)*(tb.timebase<np.max(tb.timebase)/3))
    fop = filter_fourier_bandpass(dat,[9,11],[8,12],debug=2).signal[0]
