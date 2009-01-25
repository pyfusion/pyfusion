# the original code is now in pyfusion - here is an example
import pyfusion
from pyfusion.visual import plot_sel_flucstrucs
import pylab as pl
    
 plot_sel_flucstrucs(text='dm_fs.energy>0.9')

# plot_sel_flucstrucs(shots=[58123,58124,58125],decimate=0.1)
# plot_sel_flucstrucs(shotrange=[58123,58129],decimate=0.1) 

#    The RAND() function in mysql seems to return more values towards
#    the high end of the interval [0..1], so decimate=0.1 gets ~ 1% of
#    data, rather than 10%.  RANDOM() in sqlite in more puzzling
#    still... am I doing something wrong?
