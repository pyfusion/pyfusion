import pyfusion

# default parameters
shot_number = 58123
diag_name = 'mirnov_small'
flucstruc_set_name = 'test_flucstrucs'
figure_filename = 'test_shot_flucstrucs.png'

# tweak parameters according to command line args
execfile('process_cmd_line_args.py')

# below is a reminder of the full name for settings
# pyfusion.settings.SHOT_T_MIN=pyfusion.settings.SHOT_T_MAX-0.01

s = pyfusion.get_shot(shot_number)
s.load_diag(diag_name)

from pyfusion.datamining.clustering.core import generate_flucstrucs

generate_flucstrucs(s, diag_name, flucstruc_set_name, store_chronos=True)


from pyfusion.datamining.clustering.plots import plot_flucstrucs_for_shot

plot_flucstrucs_for_shot(shot_number, diag_name, savefile=figure_filename)
