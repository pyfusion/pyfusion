import pyfusion
import pylab as pl

diag_name = 'mirnov_small'

shot_number = 58122
t0 = 0.020
dt = 0.001

execfile('process_cmd_line_args.py')

s = pyfusion.get_shot(shot_number)
s.load_diag(diag_name)

x=s.data.values()
interact=pl.isinteractive
if interact: pl.ioff()
xx=x[0].plot(xlim=[t0,t0+dt],title=str(shot_number))
if interact: pl.ion()
