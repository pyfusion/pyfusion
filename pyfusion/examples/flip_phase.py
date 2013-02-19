""" flip the phase of flucstructs according to the magnetic field direction
checks against phorig to make sure that phase is not flipped twice.
  works on dictionary of arrays "dd"
"""


_var_defaults="""

inds = None  #  if None, do it for all instances
method = 'asB'  # asB, invertB, orig, flip, check

"""
exec(_var_defaults)

from  bdb_utils import process_cmd_line_args
exec(process_cmd_line_args())

o_copy = 1*dd['phorig']
if (o_copy*dd['phases'][:,0] >= 0).all():
    print('appears to be untouched')
else: 
    print('appears to be altered according to phorig')

if inds == None:  inds = np.arange(len(dd['b_0']))
whneg = np.where(dd['b_0'] < 0)[0]

if method == 'asB':
    dd['phases'][whneg] = -dd['phases'][whneg]
    o_copy[whneg] = -o_copy[whneg]
elif method == 'invertB':
    dd['phases'][whneg,:] = -dd['phases'][whneg,:]
    dd['phases'][:,:] = -dd['phases'][:,:]
    o_copy[whneg] = -o_copy[whneg]
    o_copy[:] = -o_copy[:]
elif method == 'flip':
    print('not checking - just flipping')
    dd['phases'][:][:] = -dd['phases'][:][:]
elif method == 'check':
    print('checking - doing nothing')
else:
    raise ValueError('{m} is not a known method'.format(m=method))

if (o_copy*dd['phases'][:,0] >= 0).all():
    print('{m} OK!'.format(m=method))
else:
    print('Error - phase sign not consistent with B')

