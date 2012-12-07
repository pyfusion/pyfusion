import os, sys
import pyfusion

def purge_old(path, wild, number=20):
    import subprocess
    print('*** Warning!! purging from temp dir %s' % (path+wild))
    old_dir = os.getcwd()
    # -f prevents questions
    cmd = str("rm -f `ls -t "+wild+" |tail -%d`" % (number))
    try:
        os.chdir(path) # chdir just to be safe! avoids needing full names
        del_pipe = subprocess.Popen(cmd,  shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        (resp,err) = del_pipe.communicate()
        if pyfusion.VERBOSE > 0: print del_pipe.returncode, resp, err
        if (err != '') or (del_pipe.returncode != 0):
            print("Error %d freeing space: cmd=%s\nstdout=%s, stderr=%s" % 
                  (del_pipe.poll(), cmd, resp, err))
    except Exception, delerr: raise Exception('unexpected error in purge_old: {err=0}'.format(err=delerr))
    finally: os.chdir(old_dir)

def get_free_bytes(path):
    vfsst = os.statvfs(path)
    return vfsst.f_bavail*vfsst.f_bsize
