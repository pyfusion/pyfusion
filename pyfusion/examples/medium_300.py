from DA_datamining import DA
from pyfusion.utils.utils import fix2pi_skips, modtwopi
from pyfusion.visual.sp import sp
from pyfusion.data.convenience import between, bw, btw, decimate, his, broaden

DAfilename='PF2_121206MPRMSv2_Par_fixModes_chirp_ff.npz'
from  pyfusion.utils import process_cmd_line_args
exec(process_cmd_line_args())

DA300=DA('DAfilename,load=1)
dd=DA300.copyda() 
DA300.extract(locals())
DA300.info()
print('DA300', DAfilename)
