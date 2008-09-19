"""
implementation of the hcluster (http://code.google.com/p/scipy-cluster/) Agglomerative Hierarchical (AH) clusterer.
"""

import hcluster
from pyfusion.utils import remap_angle_negpi_pi
from numpy import array, sqrt
"""
replace hcluster pdist function with one that works for phase diffs

take input array where rows are datapoints and columns are dimensions
output an array of distances array([d01,d02,d03,...,d0n,d12,d13,...,dn-1n])
where d01 is distance between row 0 and row 1
"""


def phase_dist_function(ph1, ph2):
    if len(ph1) != len(ph2):
        raise ValueError
    delta_arr = array([remap_angle_negpi_pi(ph2[i] - ph1[i]) for i in range(len(ph1))])
#    return sqrt(abs(sum(delta_arr)))  # looks odd - bdb?
    return sqrt(abs(sum(delta_arr**2)))

def phase_pdist(phase_data):
    """
    phase_data has rows of data points (i.e. fluctuation structures), and columns with dimensions/variables (i.e. channels)
    """
    dist_list = []
    for i,di in enumerate(phase_data):
        for j,dj in enumerate(phase_data[i+1:]):
            dist_list.append(phase_dist_function(di,dj))
    return array(dist_list)

