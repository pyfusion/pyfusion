""" A VERY small MP+HMP set, just shot 65139
"""
from DA_datamining import DA
from pyfusion.utils.utils import fix2pi_skips, modtwopi
from pyfusion.visual.sp import sp
from pyfusion.data.convenience import between, btw, bw, decimate, his, broaden

DAfilename='DA65MP2010HMPno612b5_M_N_fmax.npz'
DA65=DA(DAfilename,load=1)
dd=DA65.copyda() 
DA65.extract(locals())
DA65.info()
print('DA65', DAfilename)

