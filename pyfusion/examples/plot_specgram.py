""" simple example to plot a spectrogram, uses command line arguments

    run pyfusion/examples/plot_specgram shot_number=69270

    See process_cmd_line_args.py
"""

import pyfusion as pf
import pylab as pl

dev_name='H1Local'   # 'LHD'
dev_name='LHD'
# ideally should be a direct call, passing the local dictionary
import pyfusion.utils

NFFT=256
noverlap=None
time_range = None
channel_number=0
hold=0


exec(pf.utils.process_cmd_line_args())
#execfile('process_cmd_line_args.py')

device = pf.getDevice(dev_name)

if dev_name == 'LHD':
    shot_number = 27233
    diag_name= 'MP'
elif dev_name[0:1] == "H1":
    shot_number = 69270
    diag_name = "H1DTacqAxial"

exec(pf.utils.process_cmd_line_args())

if noverlap==None: noverlap = NFFT/2

d = device.acq.getdata(shot_number, diag_name)
if time_range != None:
    dr = d.reduce_time(time_range)

dr.subtract_mean().plot_spectrogram(noverlap=noverlap, NFFT=NFFT, channel_number=channel_number, hold=hold)
