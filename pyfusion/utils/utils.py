import numpy as np

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
        normal = tc.Normal
    except None:
        (red, normal) = ('','')

    def my_show(message, category, filename, lineno, file=None, line=None):
        orig_show(red + '**' + message.message + normal, 
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


def modtwopi(x, offset=np.pi):
    """ return an angle in the range of offset +-2pi
    >>> print("{0:.3f}".format(modtwopi( 7),offset=3.14))
    0.717

    This simple strategy works when the number is near zero +- 2Npi,
    which is true for calculating the deviation from the cluster centre.
    does not attempt to make jumps small (use fix2pi_skips for that)
    """
    return ((-offset+np.pi+np.array(x)) % (2*np.pi) +offset -np.pi)



def fix2pi_skips(phase, sign='+', around=None, debug=0):
    """ ensure that phase monotonically increases (+) or decreases by
    adding units of 2Pi - Use modtwopi if you want to keep in that range.
    !!!! 2013 - fixed problem  - loss of two first points!
    >>> ph = fix2pi_skips([1,8,3,-2]); \
    print(', '.join(["{0:.3f}".format(p) for p in ph]))
    1.000, 1.717, 3.000, 4.283
    >>> ph = fix2pi_skips([4,11,7,1],around=None); \
    print(', '.join(["{0:.3f}".format(p) for p in ph]))
    4.000, 4.717, 7.000, 7.283
    >>> ph = fix2pi_skips([4,11,7,1],around=0); \
    print(', '.join(["{0:.3f}".format(p) for p in ph]))
    -2.283, -1.566, 0.717, 1.000

    New method is highly vectorised and much much faster, doesn't need 
    to know the sign.
    old method is still here (for now) but not very efficient!
    """
#    print(phase)
# had to do two steps if the jump is big - maybe should do more (or write somethingnbetter)
    fixed_phase = np.insert(np.cumsum((np.diff(phase) < -np.pi)*2*np.pi)
                            +phase[1:],0,phase[0])
    fixed_phase = np.insert(np.cumsum((np.diff(phase) < -np.pi)*2*np.pi)
                            +phase[1:],0,phase[0])
    if debug>0: print(fixed_phase)
    fixed_phase = np.insert(np.cumsum((np.diff(fixed_phase) > np.pi)*-2*np.pi)
                            +fixed_phase[1:],0,fixed_phase[0])
    fixed_phase = np.insert(np.cumsum((np.diff(fixed_phase) > np.pi)*-2*np.pi)
                            +fixed_phase[1:],0,fixed_phase[0])
    if around != None:
        if np.std(fixed_phase)< 3: # use the average
            ref = np.average(fixed_phase)
        else:                      # use the first
            ref = fixed_phase[0]

        fixed_phase = fixed_phase - 2*np.pi*int(0.5+(ref-around)/(2*np.pi))
    return(fixed_phase)

# this code is never accessed now - maybe keep for tests later
# this was original - only good for a few skips - otherwise slow
    phase = copy(phase)   # to avoid overwriting original
    for i in 1+arange(len(phase[1:])):
        if sign=='+':
            if pyfusion.settings.VERBOSE>3: print("fix2pi phase %d before = %4.4f" % (i, phase[i]))
            if phase[i]<phase[i-1]: 
                for j in range(i,len(phase)): phase[j]+=2*np.pi
        else: 
            if phase[i]>phase[i-1]:
                for j in range(i,len(phase)): phase[j]-=2*np.pi
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

if __name__ == "__main__":
    import doctest
    doctest.testmod()

