""" Simple demonstration of modulated test signals
The modulation makes it easier to distinguish noise from signal
"""
import pyfusion

if pyfusion.settings.DEVICE != 'TestDevice': 
    raise ValueError, "Must have pyfusion.settings.DEVICE='TestDevice' PRIOR to import pyfusion"
diag_name = 'testdiag2'

shot_number = 1000
print 'shot_number = ', shot_number, ': 0NNN noisy, 1NNN less so 9NNN quiet'

s = pyfusion.get_shot(shot_number)
s.load_diag(diag_name)

t0 = 0.0
t1 = 0.05

ts = pyfusion.new_timesegment(s, diag_name, t0,t1)
ts_svd = pyfusion.new_svd(ts)

ts_svd.plot()
