""" example file to be run as a script
"""
import pyfusion
from numpy import arange
from pyfusion.datamining.clustering.core import generate_flucstrucs

shots = [58123,58124]
shots = arange(58123,58130)

diag_name = 'mirnovbean1'
flucstruc_set_name = 'test_flucstrucs'
# a filename here may suppress plot unless interactive...
figure_filename = 'test_shot_flucstrucs.png'
plot_only=False
plot_spec=True

# this should be more automatic
device=pyfusion.settings.DEVICE
if device=='H1':           chan_name='mirnov_1_8'
elif device=='HeliotronJ': chan_name='MP1'
elif device=='TJII':       chan_name='mirnov_50_105'

execfile('process_cmd_line_args.py')

if not(plot_only):
    for sn in shots:
        try:
            s = pyfusion.get_shot(sn)
            s.load_diag(diag_name)
        except:
            print(' failed to retrieve shot %s') % sn
        try:
            generate_flucstrucs(s, diag_name, flucstruc_set_name, store_chronos=True,normalise=True)
        except:
            print ('generate flucstrucs failed on shot %s') % sn
            if pyfusion.pyfusion_settings.VERBOSE>2:
                generate_flucstrucs(s, diag_name, flucstruc_set_name, store_chronos=True,normalise=False)

# if desired, overplot the spectrogram
if plot_spec:
    data = pyfusion.load_channel(shots[0],chan_name)
    NFFT=pyfusion.settings.N_SAMPLES_TIME_SEGMENT
    clim=(-60,20)   # eventually make this adjustable
    data.spectrogram(hold=1, NFFT=NFFT,clim=clim,
                     noverlap=NFFT*pyfusion.settings.SEGMENT_OVERLAP/2)

from pyfusion.datamining.clustering.plots import plot_flucstrucs_for_shot, plot_flucstrucs_for_set

# choose which is more appropriate
#plot_flucstrucs_for_shot(shots, diag_name=diag_name, savefile=figure_filename)
plot_flucstrucs_for_set(flucstruc_set_name,  savefile=figure_filename)

