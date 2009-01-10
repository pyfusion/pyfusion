import pyfusion

diag_name = 'MP_ALL'

shot_number=33343

execfile('process_cmd_line_args.py')

s = pyfusion.get_shot(shot_number)
s.load_diag(diag_name, savelocal=True, ignorelocal=True)
