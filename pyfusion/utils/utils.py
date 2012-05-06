from numpy import cumsum, pi, diff
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
    import warnings
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

