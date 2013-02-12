import numpy as np
import pylab as pl
import pyfusion
from time import time as seconds
import re

def find_data(file, target, skip = 0, recursion_level=0, debug=0):
    """ find the first line number which contains the string (regexp) target 
    work around a "feature" of loadtxt, which ignores empty lines while reading data
    but counts them while skipping.
    This way, everything goes through one reader (instead of gzip.open), simplifying,
    and allowing caching.
    The recursive part could be handled more nicely.
    about 0.14 secs to read 3500 lines, 0.4 if after 11000 lines of text
    """
    lines = np.loadtxt(file,dtype=str,delimiter='FOOBARWOOBAR',skiprows=skip)
    shotlines = np.where(
        np.array([re.match(target, line)!=None for line in lines]))[0]
    if debug>0: print('main, rec, skip=', 
                      recursion_level, skip, shotlines[0],lines[shotlines[0]])
    if len(shotlines) == 0: 
        raise LookupError('target {t} not found in file "{f}". Line 0 follows\n{l}'.
                          format(t=target, f=file, l=lines[0]))
    sk = shotlines[0]
    if recursion_level>0: return(sk)

    for tries in range(10):
        if debug>0: print(sk, shotlines[0], lines[sk])

        sk1 = find_data(file, target=target, skip=sk, 
                        recursion_level=recursion_level+1)
        if debug>0: print(sk, sk1)
        
        if sk1 ==0: return(sk)
        else: sk += sk1

    raise LookupError('too many blank lines?'
                      'target {t} not found in file {f}'.
                      format(t=target, f=file))


def read_text_pyfusion(files, target='^Shot .*', ph_dtype=None, plot=pl.isinteractive(), ms=100, hold=0, debug=0, quiet=1,  exception = Exception):
    """ Accepts a file or a list of files, returns a list of structured arrays
    See merge ds_list to merge and convert types (float -> pyfusion.prec_med
    """
    st = seconds(); last_update=seconds()
    file_list = files
    if len(np.shape(files)) == 0: file_list = [file_list]
    f='f8'
    if ph_dtype == None: ph_dtype = [('p12',f),('p23',f),('p34',f),('p45',f),('p56',f)]
    #ph_dtype = [('p12',f)]
    ds_list =[]
    count = 0
    for filename in file_list:
        if seconds() - last_update > 30:
            last_update = seconds()
            print('processing {f}'.format(f=filename))
        try:
            if pl.is_string_like(target): 
                skip = 1+find_data(filename, target,debug=debug)
            else: 
                skip = target
            if quiet == 0:
                print('{t:.1f} sec, loading data from line {s} of {f}'
                      .format(t = seconds()-st, s=skip, f=filename))
            ds_list.append(
                np.loadtxt(fname=filename, skiprows = skip, 
                           dtype= [ ('shot','i8'), ('t_mid','f8'), 
                                    ('_binary_svs','i8'), 
                                    ('freq','f8'), ('amp', 'f8'), ('a12','f8'),
                                    ('p', 'f8'), ('H','f8'), ('phases',ph_dtype)])
            )
            count += 1
        except ValueError, info:
            print('Conversion error while reading {f} with loadtxt - {info}'.format(f=filename, info=info))

    print("{c} out of {t} files".format(c=count, t=len(file_list)))
    if plot>0: 
        ds = ds_list[0]
        if hold == 0: pl.clf() # for the colorbar()
        pl.scatter(ds['t_mid'],ds['freq'],ms*ds['a12'],ds['amp'])
        pl.title('{s}, colour is amp, size is a12'.format(s=ds['shot'][0]))
        pl.colorbar()
    return(ds_list)

def merge_ds(ds_list):
    """ Take a list of structured arrays, and merge into one
    """
    if len(np.shape(ds_list)) == 0: 
        raise ValueError("{d} should be a list".format(d=ds_list))

    if type(ds_list[0]) == type({}): keys = np.sort(ds_list[0].keys())
    elif type(ds_list[0]) == np.ndarray: keys = np.sort(ds_list[0].dtype.names)

    dd = {}
    for k in keys:
        # get rid of the structure/record stuff, and convert precision
        # warning - beware of data with very high dynamic range!
        if np.issubdtype(type(ds_list[0][k][0]), int): 
            newtype = np.dtype('int32')
        elif np.issubdtype(type(np.array(ds_list[0][k].tolist()).flatten()[0]), float): 
            newtype = pyfusion.prec_med
        else: 
            print("defaulting {0} to its type in ds_list".format(k))
            newtype = type(ds_list[0][k][0])

        # make sure t_mid is at least f32 (so that 100 sec shot records
        # accurately to a few usec
        if k == 't_mid' and np.issubdtype(newtype, np.dtype('float32')):
            newtype = np.dtype('float32')

        arr = np.array(ds_list[0][k].tolist(),dtype=newtype)  # this gets rid 
        # of the record stuff and saves space (pyfusion.med_prec is in .cfg)
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
    
