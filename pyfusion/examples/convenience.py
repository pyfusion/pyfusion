from numpy import array, arange, min, max
def decimate(data, fraction=None, limit=None):
    """ reduce the number of items to a limit or by a fraction
    returns the same data every call
    """
    if (fraction == None and limit==None):
        limit=2000
    if fraction != None:
        step = max([int(1/fraction),1])
    else:
        step = max([int(len(data)/limit),1])
    return(array(data)[arange(0,len(data), step)])        
