import pyfusion

diag_name = 'MP_ALL'
readback=False
shot_number=33343

execfile('process_cmd_line_args.py')

s = pyfusion.get_shot(shot_number)
s.load_diag(diag_name, savelocal=True, ignorelocal=True)

# I don't believe this test - always true!

if readback:
    srb = pyfusion.get_shot(shot_number)
    srb.load_diag(diag_name, savelocal=False, ignorelocal=False)
    srb==s

