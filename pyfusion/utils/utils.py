
def warn(warning, category=UserWarning ,stacklevel=2, exception=None):
    """ Similar to warnings.warn, but inlcudes info about the exception.
    e.g.  warn('extracting data from shot %d' % (shot), exception=ex)
    will print Exception type .., <args>: extraction data from shot 1

     Downside compared to print() is that it generates 2-3 lines
    (including line number of caller) instead of one.  Perhaps use for 
    infrequent or more dangerous situations
    - for "nagging" purposes, print is probably better.
    Perhaps this should always be used for exception catching.
    
    A monor downside to explicit detail in the message is that 
    multiple messages will be printed if the warning string changes 
    from one error to the next (unless warnings are disabled.)
    """
    import warnings
    if exception==None: exmsg=''
    else: exmsg = 'Exception "%s, %s": ' %  (type(exception),exception)
# need the +1 so that the caller's line is printed, not this line.
    warnings.warn(exmsg+warning, category, stacklevel=stacklevel+1)
