from DA_datamining import DA
from pyfusion.utils.utils import fix2pi_skips, modtwopi
from pyfusion.visual.sp import sp
from pyfusion.data.convenience import between, bw, decimate, his, broaden

DA300=DA('PF2_121206MPRMSv2_Par_fixModes_chirp_ff.npz',load=1)
dd=DA300.copyda() 
DA300.extract(locals())
DA300.info()
