import pylab as pl


def get_set_plot_axis(xlim= None, ylim=None, axdict=None, fignum=None, 
                      offset=None, verbose=0, show=None):
    """ code to get and set limits in specgram (assuming it is the second last axis)
    Accepts xlim, ylim, or dictionary containing such items, individual keywords
    override the dictionary.   bdb Jan 2009
      run examples/Boyds/get_set_plot_axis.py
      ll=get_set_plot_axis()
      get_set_plot_axis(axisdict=ll,xlim=([192,196]))
    Can take other dictionary entries and execute them 
    xx=get_set_plot_axis(axisdict={'title':'"foo"'})
    Main use is in getting to subplots other than the most recent.
    Use show=-2 to see the second last child etc
    Can also use to dynamically resize the radio button boxes etc for publication
      get_set_plot(show=-4) shows you what is at child -4 (f from end) of the current 
      figure.  Button boxes will look like xlim = [ 0.  1.], ylim = [ 0.  1.],
      Axes(0.205,0.02;0.035x0.045), and their size can be set by 
      Demo to draw two subplots, and go back to modify the first: offset=-2 (default)
      DOn't know how to suppress "output not expected" messages
      >>> from time import sleep
      >>> pl.ioff()
      >>> pl.subplot(121); pl.plot([1,2]); pl.title('old title'); pl.subplot(122)
      >>> oldax=get_set_plot_axis(); pl.show(); sleep(2)
      >>> get_set_plot_axis(xlim=[-1,2], ylim=[-1,3], axdict={'title':'"new title"'})
      >>> sleep(2); get_set_plot_axis(axdict=oldax)

    """ 
    from matplotlib.cbook import is_numlike
    import copy
    if fignum==None: 
        cf=pl.gcf()
        fignum=cf.number
    f1=pl.figure(fignum)
    chdn=f1.get_children()
    if offset==None:
        if show != None: offset=show
        else: offset=-2
    ax=chdn[offset] # second last, usually
    
    if show != None: 
        print('Child %d is %s' %  (offset, ax))
        try:
            print('Child is offset %d from %d and has xlim = %s, ylim = %s'
                  % (offset, len(chdn), ax.get_xlim(), ax.get_ylim()))
        except: 
            print('looks like child with offset %d is not a subplot' % offset)
            print('Here is a list:', chdn)
            return(None)

    xlt=ax.get_xlim()
    # ordinary copy will be updated as limits change!
    oldaxdict=copy.deepcopy({'xlim':xlt, 'ylim':ax.get_ylim()})
    
    if xlim==None and ylim==None and axdict==None: return(oldaxdict)

#  here on only if we want to change something
    if xlim != None:   # xlim can still be None! if another arg is set
        # the next line catches mistake of putting the dict as the first arg
        # better to detect this and proceed, but no "is_dict"
        if (not is_numlike(xlim[0])) or (len(xlim)<2): 
            raise ValueError, "first arg or xlim must be a tuple"

    if axdict != None: _axdict=copy.deepcopy(axdict)
    else: _axdict=None

## xlim gets priority over dictionary
    xlimtemp=xlim
    if (axdict != None) and (xlimtemp==None):
        if axdict.has_key('xlim'): 
            print('getting xlimtemp from dict')
            xlimtemp=_axdict.pop('xlim')

    print('xlimtemp %s' % xlimtemp)
    if xlimtemp != None:  ax.set_xlim(xlimtemp)

    ylimtemp=ylim
    if (axdict != None) and (ylimtemp==None):
        if axdict.has_key('ylim'): ylimtemp=_axdict.pop('ylim')

    if ylimtemp != None:  ax.set_ylim(ylimtemp)

    if _axdict != None:
        if len(_axdict)>0:
            for key in _axdict.keys():
                print("processing key %s" % key)
                exestr='ax.set_'+key+"("+str(_axdict.pop(key))+")"
                print("executing %s" %exestr)
                exec(exestr)
    pl.show()
    return(oldaxdict)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
