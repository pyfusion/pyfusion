"""
shot 46365, time 1.967 s

fsfile='54194.txt'
time run -i pyfusion/examples/plot_text_pyfusion.py
tim=ds['t_mid']
run -i pyfusion/examples/get_basic_params.py times=tim shots=[54194]
run -i pyfusion/examples/merge_in_basic_params.py

fsfile='/c/cygwin/home/bdb112/python/daves/pyfusion/MP512all.txt'
time run -i pyfusion/examples/plot_text_pyfusion.py
tim=ds['t_mid']
run -i pyfusion/examples/get_basic_params.py times=tim shots=[54194]
run -i pyfusion/examples/merge_in_basic_params.py
dd=load('fridd.npy').tolist()
run -i pyfusion/examples/test_lasso_fs.py
#save('fridd',dd)
for k in dd.keys(): exec("{0}=array(dd['{0}'])[:]".format(k))
w=where(beta>1)[0]
debug=0
sp(dd,'freq','beta','amp', size_scale=10000,hold=0, ind=w,col='t_mid',marker='s')
Y
sp(dd,'t_mid','freq','amp', size_scale=10000,hold=0, ind=w,col='beta',marker='s')
Y
colorbar()
ind=w
run -i pyfusion/examples/test_lasso_fs.py
=====


"""

import os.path

debug=0
exception = IOError

#dd={}
#for name in ds.dtype.names: dd.update({name: ds[name]})
diags="<n_e19>,b_0,i_p,di_pdt,w_p,dw_pdt,dw_pdt2,beta".split(',')

import pyfusion.utils
exec(pyfusion.utils.process_cmd_line_args())

# now to merge the two.

sz = len(dd[dd.keys()[0]])
missing_shots = []
good_shots =[]
ctr=0
for shot in np.unique(dd['shot']):
    # ws is the set of indices corresponding to the shot
    ws = np.where(shot == dd['shot'])[0]
    if len(ws)==0:   # this is an impossible condition!
       raise LookupError('Impossible! could not find the expected shot {0}'.
                         format(shot))
    else: 
       try:
          times = dd['t_mid'][ws]
          basic_data = get_basic_params(diags,shot=shot,times=times)
          (tstart,tend,inds) = get_flat_top(times=None, shot=shot) # None important
          flat_level = times*0
          w=np.where((times>tstart) & (times<tend))[0]
          flat_level[w] = 1.0
          if debug>0: print("len = {0}".format(len(w)))
          basic_data.update({'flat_level': flat_level})

          good_shots.append(shot)
       except exception:		
          missing_shots.append(shot)
          basic_data={}

       bsign = np.sign(basic_data['b_0'][0])
       for key in basic_data.keys():
           if debug>0: print(key)
           if dd.has_key(key): 
               ctr += 1
               if mod(ctr,10) == 0: 
                   print('\nMerging in key {0} {1}'.format(key, shot)),
               else:
                   print(key),
           else:    
               print('Creating new key {0}'.format(key))               
               dd.update({key: array(np.zeros(sz)+np.nan)})

           #store it at the corresponding indices

           if key in ['w_p','i_p','dw_pdt','dw_pdt2','di_pdt']:
               dd[key][ws] = bsign*basic_data[key]
           else:
               dd[key][ws] = basic_data[key]


save_name = 'saved_'+os.path.splitext(os.path.split(filename)[1])[0]
print('Saving as {0}'.format(save_name))
np.save(save_name,dd)

print("{0} missing shots out of {1}".format(len(missing_shots),(len(missing_shots)+len(good_shots))))

if verbose>0: print('missing shots are {0}'.format(missing_shots))

for key in basic_data.keys():
        print('{0:10s}: {1:.1f}%'.format(key, 100.0*np.sum(dd[key]*0==0)/sz))
