import pyfusion
from numpy import arange
from pyfusion.datamining.clustering.core import generate_flucstrucs

shots = [58123,58124]
shots = arange(58123,58130)

diag_name = 'mirnovbean1'
flucstruc_set_name = 'test_flucstrucs'
figure_filename = 'test_shot_flucstrucs.png'
plot_only=False

execfile('process_cmd_line_args.py')

if not(plot_only):
    for sn in shots:
        try:
            s = pyfusion.get_shot(sn)
            s.load_diag(diag_name)
            generate_flucstrucs(s, diag_name, flucstruc_set_name, store_chronos=True)
        except:
            print ('failed on shot %s') % sn

from pyfusion.datamining.clustering.plots import plot_flucstrucs_for_shot

plot_flucstrucs_for_shot(shots, diag_name, savefile=figure_filename)
