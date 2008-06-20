import pyfusion

shot_number = 58060
diag_name = 'mirnov_all'
flucstruc_set_name = 'test_flucstrucsp7'
figure_filename = 'test_shot_flucstrucs.png'

#execfile('process_cmd_line_args.py')

pyfusion.settings.SHOT_T_MIN=pyfusion.settings.SHOT_T_MAX-0.01
print('tmin, max' , pyfusion.settings.SHOT_T_MIN,pyfusion.settings.SHOT_T_MAX)

s = pyfusion.get_shot(shot_number)
s.load_diag(diag_name)

from pyfusion.datamining.clustering.core import generate_flucstrucs

generate_flucstrucs(s, diag_name, flucstruc_set_name, store_chronos=True)

from pyfusion.datamining.clustering.plots import plot_flucstrucs_for_shot

plot_flucstrucs_for_shot(shot_number, diag_name, savefile=figure_filename)
