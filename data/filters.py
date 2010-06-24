"""
Some un-pythonic code here (checking instance type inside
function). Need to figure out a better way to do this.
"""
from numpy import searchsorted, arange, mean, resize, repeat, fft, conjugate, linalg, array, zeros_like, take, argmin, pi
from numpy import correlate as numpy_correlate
import pyfusion

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

@register("TimeseriesData", "DataSet")
def reduce_time(input_data, new_time_range):
    from pyfusion.data.base import DataSet
    if isinstance(input_data, DataSet):
        output_dataset = input_data.copy()
        output_dataset.clear()
        for data in input_data:
            try:
                output_dataset.add(data.reduce_time(new_time_range))
            except AttributeError:
                pyfusion.logger.warning("Data filter 'reduce_time' not applied to item in dataset")
        return output_dataset

    new_time_args = searchsorted(input_data.timebase, new_time_range)
    input_data.timebase =input_data.timebase[new_time_args[0]:new_time_args[1]]
    if input_data.signal.ndim == 1:
        input_data.signal = input_data.signal[new_time_args[0]:new_time_args[1]]
    else:
        input_data.signal = input_data.signal[:,new_time_args[0]:new_time_args[1]]
    return input_data


@register("TimeseriesData", "DataSet")
def segment(input_data, n_samples):
    from pyfusion.data.base import DataSet
    from pyfusion.data.timeseries import TimeseriesData
    if isinstance(input_data, DataSet):
        output_dataset = input_data.copy()
        output_dataset.clear()
        for data in input_data:
            try:
                output_dataset.update(data.segment(n_samples))
            except AttributeError:
                pyfusion.logger.warning("Data filter 'segment' not applied to item in dataset")
        return output_dataset
    output_data = DataSet()
    for el in arange(0,len(input_data.timebase), n_samples):
        if input_data.signal.ndim == 1:
            tmp_data = TimeseriesData(timebase=input_data.timebase[el:el+n_samples],
                                      signal=input_data.signal[el:el+n_samples],
                                      channels=input_data.channels)
        else:
            tmp_data = TimeseriesData(timebase=input_data.timebase[el:el+n_samples],
                                      signal=input_data.signal[:,el:el+n_samples],
                                      channels=input_data.channels)
            
        tmp_data.meta = input_data.meta.copy()
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
def normalise(input_data, method='peak', separate=False):
    from numpy import mean, sqrt, max, abs, var, atleast_2d
    from pyfusion.data.base import DataSet
    if isinstance(input_data, DataSet):
        output_dataset = DataSet()
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
    return input_data
    
@register("TimeseriesData")
def svd(input_data):
    from timeseries import SVDData
    return SVDData(input_data.timebase, input_data.channels, linalg.svd(input_data.signal, 0))

@register("TimeseriesData")
def flucstruc(input_data, min_dphase = -pi):
    from pyfusion.data.base import DataSet
    from pyfusion.data.timeseries import FlucStruc

    fs_dataset = DataSet()

    svd_data = input_data.subtract_mean().normalise(method="var").svd()

    for fs_gr in svd_data.fs_group():
        fs_dataset.data.append(FlucStruc(svd_data, fs_gr, input_data.timebase, min_dphase=min_dphase))
    
    return fs_dataset

@register("TimeseriesData", "SVDData")
def fs_group(input_data):
    """
    no filtering implemented yet
    """
    from timeseries import SVDData

    if not isinstance(input_data, SVDData):
        input_data = input_data.subtract_mean().normalise(method="var").svd()
    
    #energy_threshold = 0.9999
    
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
        tmp_cp_argsort = array(tmp_cp).argsort()[::-1]
        sort_cp = take(tmp_cp,tmp_cp_argsort)
        delta_cp = sort_cp[1:]-sort_cp[:-1]
        output_fs_list.append([remaining_ids[i] for i in tmp_cp_argsort[:argmin(delta_cp)+1]])
            

        for i in output_fs_list[-1]: remaining_ids.remove(i)
    if len(remaining_ids) == 1:
        output_fs_list.append(remaining_ids)

    return output_fs_list


@register("TimeseriesData", "DataSet")
def subtract_mean(input_data):
    from pyfusion.data.base import DataSet
    if isinstance(input_data, DataSet):
        output_dataset = DataSet()
        for d in input_data:
            output_dataset.add(subtract_mean(d))
        return output_dataset
    if input_data.signal.ndim == 1:
        mean_value = mean(input_data.signal)
    else:
        mean_vector = mean(input_data.signal, axis=1)
        mean_value = resize(repeat(mean_vector, input_data.signal.shape[1]), input_data.signal.shape)
    input_data.signal -= mean_value
    return input_data


#########################################
## wrappers to numpy signal processing ##
#########################################
@register("TimeseriesData")
def correlate(input_data, index_1, index_2, **kwargs):
    return numpy_correlate(input_data.signal[index_1],
                           input_data.signal[index_2], **kwargs)
