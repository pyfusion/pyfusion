import pyfusion
from pyfusion.datamining.clustering.core import FluctuationStructure
import pylab as pl

fs = pyfusion.session.query(FluctuationStructure).filter('energy>0.5').all()

fs_list = [i for i in fs]

pl.plot([i.svs[0].svd.timebase[0] for i in fs_list], [i.frequency for i in fs_list], 'o')
pl.show()
