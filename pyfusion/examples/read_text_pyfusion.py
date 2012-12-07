import numpy as np
import pylab as pl
from time import time as seconds

def read_text_pyfusion(files, skip=0):
    st = seconds()
    f='f8'
    ph_dtype = [('p12',f),('p23',f),('p34',f),('p45',f),('p56',f)]
    #ph_dtype = [('p12',f)]
    ds_list =[]
    for filename in files:
        print('{t:.1f} sec, loading data from line {s} of {f}'
              .format(t = seconds()-st, s=skip, f=filename))
        ds_list.append(
            np.loadtxt(fname=filename, skiprows = skip, 
                       dtype= [ ('shot','i8'), ('t_mid','f8'), 
                                ('_binary_svs','i8'), 
                                ('freq','f8'), ('amp', 'f8'), ('a12','f8'),
                                ('p', 'f8'), ('H','f8'), ('phases',ph_dtype)])
        )
    return(ds_list)

def merge_ds(ds_list):
    if type(ds_list[0]) == type({}): keys = np.sort(ds_list[0].keys())
    elif type(ds_list[0]) == np.ndarray: keys = np.sort(ds_list[0].dtype.names)

    dd = {}
    for k in keys:
        arr = np.array(ds_list[0][k].tolist())  # this gets rid of the record stuff
        for (ind, ds) in enumerate(ds_list[1:]):
            oldlen = len(arr)
            if len(np.shape(arr))==1:
                arr.resize(oldlen+len(ds[k]))
                arr[oldlen:] = ds[k][:]
            else:
                arr.resize(oldlen+len(ds[k]),len(arr[0]))
                """ 13 secs to  merge two lots of 500k lines (5 phases)
                for j in range(len(arr[0])):
                    arr[oldlen:,j] = np.array(ds[k].tolist())[:,j]
                """   
                # this version is 3.1 secs/500k lines
                float_phases = np.array(ds[k].tolist())
                for j in range(len(arr[0])):
                    arr[oldlen:,j] = float_phases[:,j]

        dd.update({k: arr})
    return(dd)
    
