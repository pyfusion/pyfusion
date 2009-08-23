"""
"""
from numpy import searchsorted
from pyfusion.data.base import DataSet
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
from pyfusion.data.timeseries import TimeseriesData
from pyfusion.data.base import DataSet
reduce_time.allowed_class=[TimeseriesData, DataSet]
