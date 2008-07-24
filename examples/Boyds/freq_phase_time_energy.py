import pyfusion
from numpy import average, min, max, array, size
# Note: This is independent of clustering....
# Ideally, would pull all flucsets out for a check button selection

from pyfusion.datamining.clustering.core import FluctuationStructure
#fs_list = pyfusion.session.query(FluctuationStructure).all()
shots=[58123]
execfile('process_cmd_line_args.py')
# this join syntax says that svd points to timesegment which points to shot - shot is several tables away
fs_list = pyfusion.session.query(FluctuationStructure).join(['svd','timesegment','shot']).filter(pyfusion.Shot.shot.in_(shots)).all()

import pylab as pl
## funny thing with phases - simple indexing gives error as the first fs.phases is []
phases=[]
for fs in fs_list:
    for ph in fs.phases:
        phases.append(ph.d_phase)
#    if size(fs.phases): phases.append(fs.phases[0].d_phase)
phases=array(phases)
energy=array([fs.energy for fs in fs_list])
freq=array([fs.frequency for fs in fs_list])/1e3
time=array([average(fs.svd.timebase) for fs in fs_list])
print("%d phases, %d freqs") % (len(phases), len(freq))
# lots of SQL calls - one per sv - consider another form of query - e.g. join
# however this runs pretty fast on a small data set
pl.suptitle(pyfusion.utils.shotrange(shots))
ax1=pl.subplot(221)
pl.scatter(time,freq,30*energy/max(energy),200*freq/max(freq))
pl.xlabel('time (size->fs.energy, colour->fs.freq)')
pl.ylabel('fs.freq (kHz)')

ax2=pl.subplot(222)
pl.scatter(time,freq,30*(phases+4)/max(phases+4),200*freq/max(freq))
pl.xlabel('time (size->fs.phases[].d_phase, colour->fs.freq)')
pl.ylabel('fs.freq (kHz)')

# good to keep the same colour codes in the same row
ax3=pl.subplot(223)
pl.scatter(phases,freq,30*time/max(time))#?? to_rgb: Invalid rgb arg "80",200*freq/max(freq))
pl.xlabel('fs.phases[].d_phase (size->time, colour->freq)')
pl.ylabel('freq')

ax4=pl.subplot(224)
pl.scatter(time,phases,30*(phases+4)/max(phases+4),200*freq/max(freq))
pl.xlabel('time (size->fs.phases[].d_phase, colour->freq)')
pl.ylabel('fs.phases')


pl.show()

