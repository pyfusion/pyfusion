import pyfusion
from pyfusion.datamining.clustering.ah import phase_pdist
from pyfusion.devices.H1.utils import h1_khavg_fs_phases
from pyfusion.datamining.clustering.core import FluctuationStructure
import hcluster
from pylab import *

fs_list = pyfusion.session.query(FluctuationStructure).filter(FluctuationStructure.energy > 0.9).all()

phase_array = h1_khavg_fs_phases(fs_list)


pdist_data = phase_pdist(phase_array)


Y = hcluster.linkage(pdist_data)
print Y
X = hcluster.dendrogram(Y)

show()
