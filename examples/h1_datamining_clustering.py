"""
"""
import pyfusion
from pyfusion.datamining.clustering.core import FluctuationStructure, get_clusters

fs_query = pyfusion.pyfsession.query(FluctuationStructure).filter('energy>0.5').all()

ch_query = pyfusion.pyfsession.query(pyfusion.Diagnostic).filter_by(name='mirnovbean1').one()

chs = [pyfusion.pyfsession.query(pyfusion.Channel).filter_by(name=i).one() for i in ch_query.ordered_channel_list]

ch_pairs = [[chs[i],chs[i+1]] for i in range(len(chs)-1)]
#print len(chs)
#print len(ch_pairs[0])
get_clusters(fs_query, ch_pairs)

