from DA_datamining import DA
from pyfusion.utils.utils import fix2pi_skips, modtwopi

DAfilename='300_small.npz'
DA300=DA(DAfilename,load=1)
dd=DA300.copy() 
DA300.extract(locals())
DA300.info()
