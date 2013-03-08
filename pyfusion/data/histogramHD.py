import numpy as np
import pylab as pl

# there is really no need for a class, unless we want to check bounds.
class CoordHD():
    def __init__(self, dims, debug=0):
        self.dims = dims
        self.d = {}
        self.debug = debug

    def get(self, *indices):
        """ get(1,2,3)  args not a tuple """
        if self.debug>0: print('get indices', indices)
        for (i, index) in enumerate(indices):
            if index>= self.dims[i]:
                raise LookupError()
        if not self.d.has_key(indices): return(0)
        return(self.d[indices])
    
    def set(self, indices, val):
        """ set((1,2,3),49.)  """
        for (i, index) in enumerate(indices):
            if index>= self.dims[i]:
                raise LookupError()
        self.d[indices] = val



def histogramHD(d, bins=None):
    """ make a histogram of data too high in dimension to use histogramdd,
    by successive calls to histogramdd().
    The simplest implementation is to assume all bins are equal and in the 
    range -pi..pi subdivided into nbins bins.
    
    First version will use the coo_utils for simplicity  - not sure how 
    efficient lookup is though - and there is no obvious way to make an 
    array larger than memory
    
    Second - use a dictionary to store the results - 120ns lookup in a 100k dict
    Assume we can do a rank R array with histogramdd
    """
    (n_instances, n_signals) = np.shape(d)
    maxdim_dd = 3
    if bins is None: bins = 12
    if np.isscalar(bins): 
        n_bins = bins
        bins = np.pi * np.linspace(-1, 1, bins)  

    # For each cell, we need the number that lie in that range for each signal
    # for each dimension
    #    for each bin 
    """   
    In 2D it is easy:
    for ix in xbins
       for iy in ybins
          how many in this bin - record
    By induction  - to add an extra phase, for each HDD, how many are in each new bin
    SO you add a layer for each bin, and the totals in the original are subdivided
    So the function should add hyperlayers.  Problem - to extend

    # this code allows for arbitray bin edges - not really necessary here.
    # for each signal, we need to record a count of the number that are in each bin
    mask = np.empty((n_instances, n_bins), dtype=bool)
    for s in range(n_signals):
        for (i, bin) in enumerate(bins[1:]):
            mask[:,i] = ((phases[:,s]>=bins[i-1]) & (phases[:,s]<bins[i]))
        w = np.where(mask.any(1))[0]
        print(s,len(w))
    """
    """

    The only way feasible with 20^10 cells is to place them in cells one by one
    can't afford to operate bin by bin as there are bins**n_phases - say 20**10 = 10^13

    """    
    
    dims = n_signals*(n_bins,)
    hdd = CoordHD(dims)
    print('histograms into {s:.2g} bins'.format(s=np.product(np.array(dims).astype(float))))
    for phase in d[:]:
        inds = tuple(np.array((phase+np.pi)*n_bins/(2*np.pi),dtype=int))
        hdd.set((inds), hdd.get(*inds) + 1)

    return(hdd)

if __name__ == '__main__':

    print('CoordHD test')
    arrHD = CoordHD((4,5,6))
    arrHD.set((1,2,3),3)
    print(arrHD.get(1,2,3))

    """  n_signals n_bins n_instances  time
              6      12     100k        3.5 sec
              16     12     100k        5.2 sec  
    """

    print('generate artificial data')
    from numpy.random import random as randu
    n_signals = 6
    n_instances = 100000
    n_bins = 12
    seed = 0

    np.random.seed(seed)
    phases = 2*np.pi * (np.random.random((n_instances, n_signals)) - 0.5)
    # the normal way
    try:
        hdd = np.histogramdd(phases, n_signals*[np.pi * np.linspace(-1,1,n_bins+1)])
        flat_counts = hdd[0].flatten()
        print('histogramdd gives {b:.2g} bins, {s} set, total of {t}'
              .format(b=len(flat_counts), s=len(np.where(flat_counts!=0)[0]),t=np.sum(flat_counts)))
    except ValueError,MemoryError:
        print('Too big for histogramdd')
        
    # the high dimensional way
    sel = range(0,10)
    sel.extend(range(12,16))
    hHD = histogramHD(phases,bins = n_bins)
    phs = hHD.d.keys()
    counts = [hHD.d[k] for k in hHD.d.keys()]
    print('{n} elements set, total of {t}, max count of {m}'
          .format(n=len(counts), t=np.sum(counts), m=np.max(counts)))

    """ 
    n_bins = 48
    sel = range(0,10)
    sel.extend(range(12,16))
    hHD = histogramHD(phases[:,sel],bins = n_bins)
    phs = hHD.d.keys()
    counts = [hHD.d[k] for k in hHD.d.keys()]
    inds = argsort(counts)
    for i in inds[-100:]: plot(-np.pi+2*np.pi/n_bins*np.array(phs[i]), linewidth=0.001*n_bins*counts[i])
    show()

    """
