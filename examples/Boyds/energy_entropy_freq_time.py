import pyfusion
from numpy import average, min, max, array
# Ideally, would pull all flucsets out for a check button selection

from pyfusion.datamining.clustering.core import FluctuationStructure
fs_list = pyfusion.session.query(FluctuationStructure).all()

import pylab as pl
entropy=array([fs.svd.entropy for fs in fs_list])
energy=array([fs.energy for fs in fs_list])
freq=array([fs.frequency for fs in fs_list])/1e3
time=array([average(fs.svd.timebase) for fs in fs_list])
# lots of SQL calls - one per sv - consider another form of query - e.g. join
ax1=pl.subplot(221)
pl.scatter(time,freq,30*energy/max(energy),200*freq/max(freq))
pl.xlabel('time (size->fs.energy, colour->fs.freq)')
pl.ylabel('fs.freq (kHz)')

ax2=pl.subplot(222)
pl.scatter(time,freq,30*entropy/max(entropy),200*freq/max(freq))
pl.xlabel('time (size->svd.entropy, colour->fs.freq)')
pl.ylabel('fs.freq (kHz)')

# good to keep the same colour codes in the same row
ax3=pl.subplot(223)
pl.scatter(entropy,energy,30*time/max(time),200*freq/max(freq))
pl.xlabel('svd.entropy (size->time, colour->fs.freq)')
pl.ylabel('fs energy')

ax4=pl.subplot(224)
pl.scatter(time,energy,30*entropy/max(entropy),200*freq/max(freq))
pl.xlabel('time (size->svd.entropy, colour->freq)')
pl.ylabel('fs energy')


pl.show()

