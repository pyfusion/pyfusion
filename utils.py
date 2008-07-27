"""
helper functions for pyfusion
"""
from numpy import fft, conjugate, array, choose, min, max, pi,random,take,argsort
#import settings
from datetime import datetime
import pyfusion

def r_lib(r_inst, libname):
    """
    If R fails to import library, give user option to install and try again.
    r_inst is an RPy instance (from rpy import r)
    """
    try:
        r_inst.library(libname)
    except:
        raw_input("\nR library %s not found: press Enter to install...\n" %libname)
        r_inst("install.packages('%s')" %libname)
        r_inst.library(libname)

def local_import(name):
    """
    Taken from http://docs.python.org/lib/built-in-funcs.html
    """
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def get_conditional_select(input_list, key_list, exclude_keys=True):
    """
    returns a list of values, filtered by key_list and an arg determining whether to exlude the list or those not on the list
    """
    if exclude_keys == True:
        use_keys = [i for i in input_list if i not in key_list]
    else:
        use_keys = key_list

    return use_keys


def check_inputtype(calling_object, input_data,requested_datatype):
    # TODO: should learn how to define types, and check object type in less ambiguous way
    if not requested_datatype in str(input_data.__class__):
        raise ValueError, "Class %s requires input to be an instance of %s" %(str(calling_object.__class__),datatype)

def cps(a,b):
    """
    cross power spectrum
    """
    return fft.fft(array(a))*conjugate(fft.fft(array(b)))

def timestamp(fstr = '%y%m%d%H%M'):
    """
    return a string timestamp. 
    """
    return datetime.now().strftime(fstr)
    
def check_same_timebase(a,b):
    if len(a.timebase) != len(b.timebase):
        return False
    return max(abs(array(a.timebase) - array(b.timebase))) < pyfusion.settings.TIMEBASE_DIFFERENCE_TOLERANCE

from time import time
timelast=time()
timestart=time()

def delta_t(categ, total=False):
    """ returns a convenient string delta_t (wall) in ms since last
    Has the potential to accumulate delta_t in different categories
    Can also return the total wall time since initialization
    """
    global timelast, timestart
    timenow=time()
    if total: dt=timenow-timestart
    else: dt=timenow-timelast
    retval=str('%.3g s') % (1*dt)
    if total: retval = retval + ' total'
    timelast=time()
    return retval

def bigger(x,y):
    """
    more like the IDL > - note - different to numpy.greater
    """
    return choose(x < y, (x,y))


def smaller(x,y):
    """
    more like the IDL < - note - different to numpy.lesser
    """
    return choose(x > y, (x,y))

def show_db(partial_name='', page_width=80):
    """ first native SQLAlchemy version
    Works on all databases, f.metadata.tables is probably a very indirect way to
    access data
    Early version and pyfusion-independent version (but for mysql only) in dev_utils.py
    Usage: utils.show_db()   shows all tables in the current pyfusion db
        formatted according to page_width
    """
    tmp = pyfusion.session.query(pyfusion.Device)
    f=tmp.first()
    table_list = f.metadata.tables.values()
    counts=[] ; table_names=[]
    for (i,table) in enumerate(table_list):    
        table_name=str(table)
        countqry=table.count()
        count=countqry.execute().fetchone()[0]
        counts.append(count) ; table_names.append(table_name)

    len_wid = max([len(str(st)) for st in counts])
    tabl_wid = max([len(st) for st in table_names])
    for (i,table) in enumerate(table_list):    
        # print str(table), count, str(table._columns)
        col_list_long =  str(table._columns)
        col_list= [ss.strip("' ") for ss in col_list_long.strip("[]").split(",")]
        col_list_short= [ss.replace(table_names[i]+'.','') for ss in col_list]
        print ('%*s:[%*s] ') % ( tabl_wid,table_names[i],len_wid,counts[i]),
        start_col=len_wid+tabl_wid+6
        next_col=start_col
        for (i,strg) in enumerate(col_list_short): 
            if (next_col+len(strg)+2 > page_width): 
                print 
                print('%*s') % (start_col,""),
                next_col=start_col
            print ('%s,') % (strg),
            next_col += len(strg)+2
        print 

    print "\nSummary:"
    stmp = pyfusion.session.query(pyfusion.Shot)
    print '%d shot%s ' % (int(stmp.count()), ['','s'][stmp.count()!=1]),
    if stmp.count():
        shots = [shot.shot for shot in stmp]
        if len(shots) < 6: 
            print (str(shots)),
        else:
            print('from %d to %d') % (min(shots),max(shots)),

    dtmp = pyfusion.session.query(pyfusion.Device)
    print ', %d device%s ' % (int(dtmp.count()), ['','s'][dtmp.count()!=1]),
    if dtmp.count():
        devices = [d.name for d in dtmp]
        if len(devices) < 6: 
            print (devices)
        else:
            print('%s ... etc') % str(devices[0:6])

    dgtmp = pyfusion.session.query(pyfusion.Diagnostic)
    print '%d diagnostic%s' % (int(dgtmp.count()), ['','s'][dgtmp.count()!=1]),
    if dgtmp.count():
        diags = [d.name for d in dgtmp]
        if len(diags) < 6: 
            print (diags)
        else:
            print('%s ... etc') % str(diags[0:6])

def shotrange(shot_numbers, max_width=30):
    """ Return a concise string representation of a numer of shots
    limiting the character width to max_width
    """
    shots=array(shot_numbers) # to be brief!
    sstr =str('shot%s ') % (['','s'][len(shots)!=1])
    if len(shots):
        if len(str(shots)+sstr) < max_width: 
            sstr += str("%s") % ','.join([str(s) for s in shots])
        elif (max(shots)-min(shots)) == (len(shots)-1):
            sstr +=('%d-%d') % (min(shots),max(shots))
        else:
            sstr = str("%d ") % int(len(shots)) + sstr.rstrip() + ', ' + (
                       '[%d,...,%d]') % (min(shots),max(shots))
    return sstr

def remap_angle_0_2pi(angle,avoid_zero=False):
    """
    surely there's a better way?
    avoid_zero is useful if you want to guarantee against div by 0....
    """
    if avoid_zero:
        while angle > 2*pi:
            angle -= 2*pi
        while angle <= 0:
            angle += 2*pi        
    else:
        while angle >= 2*pi:
            angle -= 2*pi
        while angle < 0:
            angle += 2*pi
    return angle


def remap_angle_negpi_pi(angle):
    """
    surely there's a better way?
    """
    while angle >= pi:
        angle -= 2*pi
    while angle < -pi:
        angle += 2*pi
    return angle

def random_sample(input_arr, out_length):
    if out_length >= len(input_arr):
        return input_arr
    rand_list = random.rand(len(input_arr))
    rand_args = argsort(rand_list)[:out_length]
    return take(input_arr, rand_args)
    
