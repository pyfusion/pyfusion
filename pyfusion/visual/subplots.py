# add an apportion keyword to subplots - also adds subplot feature to
# versions without it (matplotlib < 1?), and make behaviour more like real one.
# in particular arg order, and squeeze behaviour
# Feb 2013 - make apportion apply to all columns (equally so far
#   also correct squeeze behaviour
import pylab as pl
import numpy as np
from warnings import warn

try:
    from pylab import subplots as pylab_subplots
except ImportError:
    warn(' - pylab not new enough - Using a fudged pylab.subplots - should be OK')
    def pylab_subplots(nrows=1, ncols=1, squeeze=True, sharex = False, sharey=False, *args, **kwargs):
        fig=pl.figure()
        axs = []
        shx=None;  shy=None
        for r in range(nrows):
            axrow = [] 
            for c in range(ncols):
                axrow.append(pl.subplot(nrows, ncols, 1+c+r*ncols,sharex=shx, sharey=shy))
                if r*c == 0: 
                    if sharex: shx = axs[0]
                    if sharey: shy = axs[0]
            axs.append(axrow)        
        axs = np.array(axs)
        if squeeze: axs = axs.flatten()
        return(fig,axs)

def subplots(nrows=1, ncols=1, sharex=False, sharey=False, squeeze=True, apportion = None, debug = 0, *args, **kwargs):
    """ enhanced subplot routine, allowing for changing relative sizes
    apportion initially applies only to the vertical direction, first element refers to the topmost element
    """
    #Note: we use squeeze = False internally, then return axes according to the keyword
    fig, axes = pylab_subplots(nrows=nrows, ncols=ncols, sharex=sharex, sharey=sharey, squeeze=False, *args, **kwargs)
    nrows = len(axes[:,0].flatten())
    # start with even allocation of unity
    fracts = np.ones(nrows)
    # if just one arg, that is the first allocation
    if apportion != None:
        if len(np.shape(apportion)) == 0:
            fracts[0]=apportion
        # fill up the rest
        for (i,a) in enumerate(apportion):
            if i<nrows: fracts[i] = a
    # now make into a fractions
    fracts = fracts/np.sum(fracts)

    #loop over axes, bottom to top, extract the space below and the height for each (ignore space above
    above = [] ; height = []
    lasty = 1
    for (i,ax) in enumerate(axes[:,0]):
        bb = ax.get_position().get_points()
        pos = bb.flatten() 
        height.append(pos[3]-pos[1])
        above.append(lasty - pos[3] )
        lasty = pos[1]

# loop again, building down from top according to new share, keep margins
    yabove_0 = 1 # the norm. y coord of the bottom of the above graph
    print(above, height)
    for col in range(np.shape(axes)[1]):
        for (i,ax) in enumerate(axes[:,col]):
            if (i==0): yabove = yabove_0
            bb = ax.get_position().get_points()
            pos = bb.flatten() 
            # convert to x0,y0, dx, dy form by subtracting origin
            newh = height[i]*fracts[i]*nrows

            pos[1] = yabove - newh - above[i]
            pos[3] = newh
            pos[2] = pos[2] - pos[0]
            yabove = pos[1]
            if debug>0: print(pos)
            ax.set_position(pos)

    if squeeze: 
        if len(np.shape(axes[0]))==0: axes = axes.flatten()    
        if len(axes) == 1: axes = axes[0]
    return(fig, axes)

if __name__ == "__main__":
    from subplots import subplots
    fig,ax = subplots(nrows=3, apportion = [5,1,1])
    #fig,ax = pl.subplots(nrows=3)
    t = np.linspace(0,20)
    ax[0].plot(np.sin(t))
    ax[0].set_title('Ax0')
    ax[1].plot(np.cos(t))
    pl.show()
    print('try test1()')
    def test1():
        fig,ax = subplots(nrows=3, ncols=2, apportion = [2,1,1])
        return
