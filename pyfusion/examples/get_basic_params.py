""" get the basic plasma params for a given shot and range of times
"""

import pyfusion as pf
import pylab as pl
import numpy as np
from read_igetfile import igetfile
from matplotlib.mlab import stineman_interp
from read_csv_data import read_csv_data
from warnings import warn
import re

verbose = 0
times=np.linspace(2,3,20)
local_dir = '/home/bdb112/datamining/cache/'

file_info={}
#file_info.update({'n_e': {'format': 'fircall@{0}.dat','name':'ne_bar(3939)'}})
file_info.update({'n_e': {'format': 'fircall@{0}.dat','name':'ne_bar\(3[0-9]+\)'}})
file_info.update({'i_p': {'format': 'ip@{0}.dat','name':'Ip$'}})
file_info.update({'w_p': {'format': 'wp@{0}.dat','name':'Wp$'}})
file_info.update({'beta': {'format': 'wp@{0}.dat','name':'<beta-dia>'}})
file_info.update({'b_0': {'format': 'lhd_summary_data.csv','name':'MagneticField'}})
file_info.update({'R_ax': {'format': 'lhd_summary_data.csv','name':'MagneticAxis'}})
file_info.update({'Quad': {'format': 'lhd_summary_data.csv','name':'Quadruple'}})

global lhd_summary

def get_basic_params(diags="n_e,b_0,i_p,w_p".split(','), shot=54196, times=times):
    """ return a list of np.arrays of normally  numeric values for the 
    times given, for the given shot.
    """

    global lhd_summary

    times = np.array(times)
    vals = {}
    # make a cross check with an extra time array
    vals.update({'check_tm':times})
    vals.update({'check_shot':np.zeros(len(times),dtype=np.int)+shot})
    for diag in diags:
        if not(file_info.has_key(diag)):
            warn('diagnostic {0} not found in shot {1}'.format(diag, shot),stacklevel=2)
            vals.update({diag: np.nan + times})
        else:
            info = file_info[diag]
            if info['format'].find('.csv') > 0:
                try:
                    test=lhd_summary.keys()
                except:    
                    print('reloading {0}'.format(info['format']))
                    lhd_summary = read_csv_data(local_dir+info['format'], header=3)

                val = lhd_summary[info['name']][shot]    
                valarr = np.double(val)+(times*0)
            else:    
                try:
                    dg = igetfile(local_dir + info['format'], shot=shot)
                except IOError:
                    try:
                        dg = igetfile(local_dir + info['format']+'.bz2', shot=shot)
                    except IOError:
                        try:
                            dg = igetfile(local_dir + info['format']+'.gz', shot=shot)
                        except exception:
                            #debug_(1)
                            dg=None
                            #break  # give up and try next diagnostic
                if dg==None:  # messy - break doesn't do what I want?
                    valarr=None
                else:
                    nd=dg.vardict['DimNo']
                    if nd != 1:
                        raise ValueError(
                            'Expecting a 1 D array in {0}, got {1}!'
                            .format(dg.filename, nd))

                    w = np.where(np.array(dg.vardict['ValName'])==info['name'])[0]
                    matches = [re.match(info['name'],nam) 
                               != None for nam in dg.vardict['ValName']]
                    w = np.where(np.array(matches) != False)[0]
                    if len(w) != 1:
                        raise LookupError(
                            'Need one instance of variable {0} in {1}'.
                            format(info['name'], dg.filename))

                    valarr = dg.data[:,nd+w[0]]
                    tim =  dg.data[:,0]
                    valarr = (stineman_interp(times, tim, valarr))

            if valarr != None: vals.update({diag: valarr})
    return(vals)                

get_basic_params.__doc__ += 'Some diagnostics are \n' + ', '.join(file_info.keys())




#shots=np.loadtxt('lhd_clk4.txt',dtype=type(1))
shots=[54194]
separate=0
diags="n_e,b_0,i_p,w_p,beta".split(',')
exception = IOError

import pyfusion.utils
exec(pf.utils.process_cmd_line_args())

missing_shots = []
good_shots =[]
for shot in shots:
    try:
        basic_data=get_basic_params(diags,shot=shot,times=times)
        good_shots.append(shot)
    except exception:		
        missing_shots.append(shot)

print("{0} missing shots out of {1}".format(len(missing_shots),(len(missing_shots)+len(good_shots))))

if verbose>0: print('missing shots are {0}'.format(missing_shots))


