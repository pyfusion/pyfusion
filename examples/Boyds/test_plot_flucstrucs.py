import pyfusion
diag_name='mirnovbean1'
shot_number=66587

# tweak parameters according to command line args
execfile('process_cmd_line_args.py')

s = pyfusion.get_shot(shot_number)
s.load_diag(diag_name)
from pyfusion.datamining.clustering.plots import plot_flucstrucs_for_shot
plot_flucstrucs_for_shot(s.shot, diag_name=diag_name, savefile='',number=10)
