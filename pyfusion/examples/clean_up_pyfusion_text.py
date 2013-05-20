"""
(sort(lines[next_good:])==sort(lines[2*next_good-num-1:next_good-1])).all()

 strip bad lines out of pyfusion text files.
"""
import bz2
import StringIO
import os
import numpy as np
import sys
import glob

debug=1
all_errors=[]

#filename='/home/bdb112/datamining/preproc/PF2_121208/PF2_121209_MP2010_99931_99931_1_384_rms_1.dat.bz2'  # I killed it
#filename = '/home/bdb112/datamining/preproc/PF2_121208/foo.bz2'
for filename in np.sort(glob.glob('/home/bdb112/datamining/preproc/PF2_121208/*2')):
#for filename in np.sort(glob.glob('/home/bdb112/datamining/preproc/PF2_121208/PF2_121209_MP2010_113431_113431_1_384_rms_1.dat.bz2')):  # I killed it
    with bz2.BZ2File(filename) as fd:
        lines=fd.readlines()

      # gets the first occurrence of 'Shot'
    shotline_candidates = np.where(np.char.find(lines,'Shot')==0)[0]
    if len(shotline_candidates)==0: 
        print('no Shot line in '+filename)
        all_errors.append((filename, len(lines), [-1])) # -1 means no shotline
        continue
    if len(shotline_candidates)!=1: 
        print('need just one Shot line in '+filename)

    shotline = shotline_candidates[-1]
    shotlinetext = lines[shotline]
    header_toks = shotlinetext.split()

    ph_dtype = None
    f='f8'
    if ph_dtype == None:
        ph_dtype = [('p12',f),('p23',f),('p34',f),('p45',f),('p56',f)]
        #ph_dtype = [('p12',f)]


    # is the first character of the 2nd last a digit?
    if header_toks[-2][0] in '0123456789': 
        if pyfusion.VERBOSE > 0: 
            print('found new header including number of phases')
        n_phases = int(header_toks[-2])
        ph_dtype = [('p{n}{np1}'.format(n=n, np1=n+1), f) for n in range(n_phases)]

    if 'frlow' in header_toks:  # add the two extra fields
        fs_dtype= [ ('shot','i8'), ('t_mid','f8'), 
                    ('_binary_svs','i8'), 
                    ('freq','f8'), ('amp', 'f8'), ('a12','f8'),
                    ('p', 'f8'), ('H','f8'), 
                    ('frlow','f8'), ('frhigh', 'f8'),('phases',ph_dtype)]
    else:
        fs_dtype= [ ('shot','i8'), ('t_mid','f8'), 
                    ('_binary_svs','i8'), 
                    ('freq','f8'), ('amp', 'f8'), ('a12','f8'),
                    ('p', 'f8'), ('H','f8'), ('phases',ph_dtype)]
    try:
        np.loadtxt(StringIO.StringIO(''.join(lines[shotline+1:])), 
                   dtype=fs_dtype)
        if debug: print('OK'),
    except (IndexError, ValueError):
        print('processing errors in' + filename)

        errors = []
        num = len(lines)
        for l in range(shotline+1, num)[::-1]:
            try:
                np.loadtxt(StringIO.StringIO(lines[l]), dtype=fs_dtype)
            except:
                errors.append(l)
                if len(errors)<3: print(lines[l])
                if debug>0: ans = raw_input('delete this line? (Y, A(ll),^C to stop)').lower()
                if ans=='a': 
                    debug=0
                if ans in ['y','','a']:
                    lines.pop(l)
                    num = len(lines)
                    next_good = l
                    if (((2*next_good-num)>0) and 
                        (np.sort(lines[next_good:])==
                         np.sort(lines[2*next_good-num:next_good])).all()):
                        if debug>0: 
                            print('=== remove {dups} duplicates ==='
                                  .format(dups=num-next_good))
                        errors.append(-(num-next_good))  # negative num( not -1) means dups
                        for ll in range(next_good, num)[::-1]:
                            lines.pop()

                else: sys.exit()

        if len(errors) == 0:
            if debug>0: print('no errors found')
        else:
            (folder, fn) = os.path.split(filename)
            baddir = os.path.join(folder, 'bad')
            print('errors found in {e}, move to \n{bad} and rewrite only good lines\n to '
                  .format(e=errors)),

            if not os.path.isdir(baddir):  os.mkdir(baddir)
            os.rename(filename, os.path.join(baddir, fn))
            newname = filename.rsplit('.')[0]+'.txt'
            print(newname)
            with file(newname,'w') as fw:
                fw.writelines(lines)

        all_errors.append((filename, len(lines), errors))
"""

fd=bz2.BZ2File('/home/bdb112/datamining/preproc/PF2_121208/PF2_121209_MP2010_99931_99931_1_384_rms_1.dat.bz2')
problem
'/home/bdb112/datamining/preproc/PF2_121208/PF2_121208_MP2010_56431_56431_1_384_rms_1.dat.bz2'

"""
