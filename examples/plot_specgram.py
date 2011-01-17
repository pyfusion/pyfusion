""" plot a group of signals

"""
import subprocess, sys, warnings
from numpy import sqrt
import pyfusion as pf
import pylab as pl

dev_name='H1Local'   # 'LHD''LHD
device = pf.getDevice(dev_name)

shot_number = 27233
shot_number = 69270
#shot_range = range(90090, 90110)

diag_name= 'MP'
diag_name = "H1DTacqAxial"
exception=Exception
time_range = None
channel_number=0

execfile('process_cmd_line_args.py')

d = device.acq.getdata(shot_number, diag_name)
if time_range != None:
    d.reduce_time(time_range)

d.subtract_mean().plot_spectrogram(channel_number=channel_number)
