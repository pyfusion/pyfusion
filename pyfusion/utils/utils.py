from numpy import cumsum, pi, diff

# this changes the behaviour of warnings
import warnings
import pyfusion

# suppress this change altogether with colors=None in globals
# can't be changed at runtime.
if pyfusion.COLORS != None:
    orig_show = warnings.showwarning
    try: 
        from IPython.utils import coloransi
        tc=coloransi.TermColors()
        red = tc.LightRed
        nocolor = tc.NoColor
    except None:
        (red, nocolor) = ('','')

    def my_show(message, category, filename, lineno, file=None, line=None):
        orig_show(red + '**' + message.message + nocolor, 
                  category, filename, lineno, file, line)

    warnings.showwarning = my_show    
# end of color warnings block

def warn(warning, category=UserWarning ,stacklevel=2, exception=None):
    """ Similar to warnings.warn, but includes info about the exception.
    e.g.  warn('extracting data from shot %d' % (shot), exception=ex)
    will print Exception type .., <args>: extraction data from shot 1

     Downside compared to print() is that it generates 2-3 lines
    (including line number of caller) instead of one.  Perhaps use for 
    infrequent or more dangerous situations
    - for "nagging" purposes, print is probably better.
    Perhaps this should always be used for exception catching.
    
    A minor downside to explicit detail in the message is that 
    multiple messages will be printed if the warning string changes 
    from one error to the next (unless warnings are disabled.)
    """
    if exception==None: exmsg=''
    else: exmsg = 'Exception "%s, %s": ' %  (type(exception),exception)
# need the +1 so that the caller's line is printed, not this line.
    warnings.warn(exmsg+warning, category, stacklevel=stacklevel+1)

def fix2pi_skips(phase, sign='+'):
    """ ensure that phase monotonically increases (+) or decreases by
    adding units of 2Pi - 
    New method is highly vectorised and much much faster, doesn't need 
    to know the sign.
    old method is still here (for now) but not very efficient!
    """
#    print(phase)
    fixed_phase = cumsum((diff(phase) < -pi)*2*pi)+phase[1:]
    fixed_phase = cumsum((diff(fixed_phase) > pi)*(-2*pi))+fixed_phase[1:]
    return(fixed_phase)

# this code is never accessed now - maybe keep for tests later
# this was original - only good for a few skips - otherwise slow
    phase = copy(phase)   # to avoid overwriting original
    for i in 1+arange(len(phase[1:])):
        if sign=='+':
            if pyfusion.settings.VERBOSE>3: print("fix2pi phase %d before = %4.4f" % (i, phase[i]))
            if phase[i]<phase[i-1]: 
                for j in range(i,len(phase)): phase[j]+=2*pi
        else: 
            if phase[i]>phase[i-1]:
                for j in range(i,len(phase)): phase[j]-=2*pi
#    print(phase)
    return(phase)

from numpy import array, arange, min, max
def decimate(data, fraction=None, limit=None):
    """ reduce the number of items to a limit or by a fraction
    """
    if (fraction == None and limit==None):
        limit=2000
    if fraction != None:
        step = max([int(1/fraction),1])
    else:
        step = max([int(len(data)/limit),1])
    return(array(data)[arange(0,len(data), step)])        
