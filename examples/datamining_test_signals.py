
import pyfusion

diag_name = 'testdiag1'

s = pyfusion.get_shot(1)
s.load_diag(diag_name)

from pyfusion.datamining.clustering.core import generate_flucstrucs

generate_flucstrucs(s, diag_name, store_chronos=True)

