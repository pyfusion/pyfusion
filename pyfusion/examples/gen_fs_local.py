""" test generation of flucstrucs.
#exception=None catches no exceptions, so you get a stop and a traceback
#exception=Exception catches all, so it continues, but no traceback
python dm/gen_fs.py shot_range=[27233] exception=None

71 secs to sqlite.txt (9MB) (21.2k in basedata, 3.5k fs, 17.7k float_delta
34 secs with db, but no fs_set.save()
17 secs to text 86kB - but only 1k fs
"""
import subprocess, sys, warnings
from numpy import sqrt, mean
import pyfusion as pf
from pyfusion.debug_ import debug_

lhd = pf.getDevice('LHD')

#min_shot = 84000
#max_shot = 94000
#every_nth = 10

#shot_range = range(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))

debug=0
shot_range = [27233]
#shot_range = range(90090, 90110)
n_samples = 512
overlap=1.0
diag_name= 'MP'
exception=Exception
time_range = None
min_svs=1
max_H=0.97

# ids are usually handled by sqlalchemy, without SQL we need to look after them ourselves
fs_id = 0

# ideally should be a direct call, passing the local dictionary
import pyfusion.utils
exec(pf.utils.process_cmd_line_args())
#execfile('process_cmd_line_args.py')

for shot in shot_range:
    try:
        d = lhd.acq.getdata(shot, diag_name)
        if time_range != None:
            d.reduce_time(time_range, copy=False)
        sections = d.segment(n_samples, overlap)
        print(d.history, len(sections))

        for ii,t_seg in enumerate(sections):
            fs_set = t_seg.flucstruc()
            for fs in fs_set:
                if fs.H < max_H and fs.p>0.01 and len(fs.svs())>min_svs:
                    phases = ' '.join(["%5.2f" % j.delta for j in fs.dphase])
                    RMS_scale = sqrt(mean(t_seg.scales**2))
                    adjE = fs.p*fs.E*RMS_scale**2
                    debug_(debug)
                    if pyfusion.orm_manager.IS_ACTIVE: 
                    # 2-2.05, MP: 11 secs, 87  , commit=False 10.6 secs 87
                    # commits don't seem to reduce time.    
                        fs.save(commit=True)           
                    else: 
                        print ("%d %7.4g %s %6.3g %6.3f %.2f %.3f %.3f    %s" % (
                                shot, fs.t0, "{0:8b}".format(fs._binary_svs), 
                                fs.freq/1000., sqrt(fs.E*fs.p)*RMS_scale, 
                                fs.a12, fs.p, fs.H, phases))

        # the -f stops the rm cmd going to the terminal
#        subprocess.call(['/bin/rm -f /data/tmpboyd/pyfusion/FMD*%d*' %shot], shell=True)
#        subprocess.call(['/bin/rm -f /data/tmpboyd/pyfusion/SX8*%d*' %shot], shell=True)
    except exception:
#set Exception=None to allow traceback to show - it can never happen
# otherwise, the warnigns.warn will prevent multiple identical messages
        warning_msg = str('shot %d not processed: %s' % 
                          (shot,sys.exc_info()[1].__repr__()))
        warnings.warn(warning_msg,stacklevel=2)

if pyfusion.orm_manager.IS_ACTIVE: 

    pyfusion.orm_manager.Session().commit()
    pyfusion.orm_manager.Session().close_all()
