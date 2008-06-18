import pyfusion, settings

shot_number = 58123
diag_name = 'mirnovbeans'
flucstruc_set_name = 'test_flucstrucsp7'
figure_filename = 'test_shot_flucstrucs.png'

execfile('process_cmd_line_args.py')

#settings.SHOT_T_MIN=settings.SHOT_T_MAX-0.01
#print('tmin, max' , settings.SHOT_T_MIN,settings.SHOT_T_MAX)

s = pyfusion.get_shot(shot_number)
s.load_diag(diag_name)

from pyfusion.datamining.clustering.core import generate_flucstrucs

generate_flucstrucs(s, diag_name, flucstruc_set_name, store_chronos=True)

from pyfusion.datamining.clustering.plots import plot_flucstrucs_for_shot

plot_flucstrucs_for_shot(shot_number, diag_name, savefile=figure_filename)
