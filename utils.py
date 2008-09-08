"""
helper functions for pyfusion
"""
from numpy import fft, conjugate, array, choose, min, max, pi,random,take,argsort
from datetime import datetime
import pyfusion

def add_timesegmentdatasummary_for_ts_list(input_ts_list, diag_name, exist_check='any',savelocal=False, ignorelocal=False, is_channel=False):
    """
    add TimeSegmentDataSummary for each TimeSegment instance in ts_list for given diag
    we find distinct shots to minimise number of times we need to fetch data, and close the session 
    between shots to conserve memory... 
    TODO - this is probably not the best implementation of SQLalchemy, check...

    exist_check: 'none' or None : don't check existing TimeSegmentDataSummary instances
                 'any' : if any channel from diag exists, don't regenerate the TSDS
                 'all' : if all channels from diag exists, don't regenerate the TSDS

    """
    if exist_check == None or is_channel==True:
        exist_check = 'none'

    if is_channel:
        print 'implementation shortfall: overriding checking (ie: not checking) of existing data summaries.'

    if exist_check.lower() == 'none':
        ts_list = input_ts_list
    elif exist_check.lower() == 'any':
        diag = pyfusion.q(pyfusion.Diagnostic).filter_by(name=diag_name).one()
        chan_ids = [c.id for c in diag.channels]
        ts_list = []
        for tsi,ts in enumerate(input_ts_list):
            print 'Checking TS %d of %d' %(tsi+1, len(input_ts_list))
            add_ts = True
            for chid in chan_ids:
                if pyfusion.q(pyfusion.TimeSegmentDataSummary).filter_by(timesegment_id=ts.id, channel_id=chid).count()>0:
                    add_ts = False
            if add_ts:
                ts_list.append(ts)
    elif exist_check.lower() == 'all':
        diag = pyfusion.q(pyfusion.Diagnostic).filter_by(name=diag_name).one()
        chan_ids = [c.id for c in diag.channels]
        ts_list = []
        for ts in input_ts_list:
            add_ts = False
            for chid in chan_ids:
                if pyfusion.q(pyfusion.TimeSegmentDataSummary).filter_by(timesegment_id=ts.id, channel_id=chid).count()==0:
                    add_ts = True
            if add_ts:
                ts_list.append(ts)
    
    print 'Number of input Time Segments: %d' %(len(input_ts_list))
    print 'Number of new TSDS to create: %d' %(len(ts_list))
    shot_dict = {}
    for ts in ts_list:
        if str(ts.shot.shot) in shot_dict.keys():
            shot_dict[str(ts.shot.shot)].append(ts)
        else:
            shot_dict[str(ts.shot.shot)] = [ts]
    n_shots = len(shot_dict.keys())
    print 'Number of shots: %d' %(n_shots)
    for shi,sh_str in enumerate(shot_dict.keys()):
        for tsi,ts in enumerate(shot_dict[sh_str]):
            print 'Shot %s, %d of %d. Timesegment %d of %d. Diag: %s' %(sh_str, shi+1,n_shots,tsi+1,len(shot_dict[sh_str]), diag_name)
            ts.generate_data_summary(diag_name,channel=is_channel, savelocal=savelocal,ignorelocal=ignorelocal)
        #pyfusion.session.close()


def update_device_info(pyf_class):
    existing = pyfusion.session.query(pyf_class).all()
    for devmod_object_str in pyfusion._device_module.__dict__.keys():
        if hasattr(pyfusion._device_module.__dict__[devmod_object_str], '__class__'):        
            devmod_inst_class = pyfusion._device_module.__dict__[devmod_object_str].__class__
            if pyf_class == devmod_inst_class or pyf_class in devmod_inst_class.__bases__:
                if pyfusion._device_module.__dict__[devmod_object_str].name not in [i.name for i in existing]:
                    pyfusion.session.save_or_update(pyfusion._device_module.__dict__[devmod_object_str]) 



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


def remap_angle_negpi_pi(angle, offset=0.0):
    """
    surely there's a better way?
    """
    while angle >= offset+pi:
        angle -= 2*pi
    while angle < offset-pi:
        angle += 2*pi
    return angle

def random_sample(input_arr, out_length):
    if out_length >= len(input_arr):
        return input_arr
    rand_list = random.rand(len(input_arr))
    rand_args = argsort(rand_list)[:out_length]
    return take(input_arr, rand_args)
    
