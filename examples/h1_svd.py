import pyfusion

diag_name = 'mirnovbeans'

shot_number = 58080

s = pyfusion.get_shot(shot_number)
s.load_diag(diag_name)

t0 = 0.030
t1 = 0.035

# tweak parameters according to command line args
execfile('process_cmd_line_args.py')

ts = pyfusion.new_timesegment(s, diag_name, t0,t1)
ts_svd = pyfusion.new_svd(ts)

ts_svd.plot()
