"""
Some un-pythonic code here (checking instance type inside
function). Need to figure out a better way to do this.
"""
from numpy import searchsorted, arange, mean, resize, repeat
import pyfusion

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

class MetaFilter(type):
    def __new__(cls, name, bases, attrs):
        filter_methods = filter_reg.get(name, [])
        attrs.update((i.__name__,i) for i in filter_methods)
        return super(MetaFilter, cls).__new__(cls, name, bases, attrs)


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
                                      signal=input_data.signal[el:el+n_samples])
        else:
            tmp_data = TimeseriesData(timebase=input_data.timebase[el:el+n_samples],
                                      signal=input_data.signal[:,el:el+n_samples])
            
        tmp_data.meta = input_data.meta.copy()
        output_data.add(tmp_data)
    return output_data


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
    
#@register("TimeseriesData")
#def svd(input_data):
#    pass

@register("TimeseriesData")
def flucstruc(input_data):
    pass



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



