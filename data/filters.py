"""
"""
from numpy import searchsorted, arange
from pyfusion.data.base import DataSet
from pyfusion.data.timeseries import TimeseriesData
import pyfusion

def reduce_time(input_data, new_time_range):
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

reduce_time.allowed_class=[TimeseriesData, DataSet]

def segment(input_data, n_samples):
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

segment.allowed_class=[TimeseriesData, DataSet]



def normalise(input_data, method='peak', separate=False):
    from numpy import mean, sqrt, max, abs, var, atleast_2d
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
    
normalise.allowed_class=[TimeseriesData]#, DataSet]
