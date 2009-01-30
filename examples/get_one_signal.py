""" Useful for simple debugging.  Make sure you use copy.deepcopy(..)
if you want a second signal!
"""
import pylab as pl
import pyfusion

shot_number=58123
diag_name='mirnov_all'
chan_index=0
# kwargs={'skip_timebase_check':True}
kwargs={}

# tweak above parameters according to command line args
execfile('process_cmd_line_args.py')

s = pyfusion.get_shot(shot_number)
s.load_diag(diag_name, **kwargs)
ch=pyfusion.Session.query(pyfusion.Channel)
print("Choosing from", [chn.name for chn in ch])
name=ch[chan_index].name
data = pyfusion.load_channel(shot_number,name)

