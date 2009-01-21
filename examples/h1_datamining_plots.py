import pyfusion
from pyfusion.datamining.clustering.core import FluctuationStructure
import pylab as pl

fs = pyfusion.session.query(FluctuationStructure).filter('energy>0.5').all()

fs_list = [i for i in fs]

# could be expensive on a large database unless we select carefully
pl.plot([i.svs[0].svd.timebase[0] for i in fs_list], [i.frequency for i in fs_list], 'o')
pl.show()

""" also 
fs_list[0].svs[0].topo (quick)
fs_list[0].svs[0].chrono fired up everything (few minutes - maybe the chrono was not stored!

for shot in 33373 33582; do time python examples/Boyds/create_flucstrucs.py  shots=[58$i]; done
