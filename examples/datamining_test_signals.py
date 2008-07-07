import pyfusion

diag_name = 'testdiag1'

s = pyfusion.get_shot(1)
s.load_diag(diag_name)

from pyfusion.datamining.clustering.core import generate_flucstrucs

flucstruc_set_name = 'test_flucstrucs'
generate_flucstrucs(s, diag_name, flucstruc_set_name, store_chronos=True)

from pyfusion.datamining.clustering.plots import plot_flucstrucs_for_shot

plot_flucstrucs_for_shot(s, diag_name, savefile='')
