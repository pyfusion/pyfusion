""" Performance - with 18M x 14 phases CWGM dataset float32, with int indices, used 16GB to density cluster, and other ops took and additional 5GB swap.
At face value, this is 1k/entry, much higher than the typical 200-300 bytes.
Loading (copying dd, and extracting) the float32 version alone takes 5.6GB.
loading the float16 version alone (bare: no b_0)takes 3.3GB.
As these include 3 copies, space can be reduced to 40% by dd=0, DA300=0

30 secs for 20 million 
25ns
time for i in range(20*1000*1000): d.update({tuple(random.random(14).tolist()):i
New "unsafe" method takes 680 sec and 1.4GB for 16M of 18M phases
2.5GB after 0.85 Before - so  1.65GB for 16M entries
})
"""
import numpy as np
import pylab as pl

from pyfusion.data.histogramHD import histogramHD

colorset=('b,g,r,c,m,y,k,orange,purple,lightgreen,gray'.split(',')) # to be rotated
from pyfusion.utils.utils import fix2pi_skips, modtwopi

def dist2(a,b, method='euler'):
    return(np.sum((modtwopi((np.array(a)- np.array(b)),offset=0)**2)))

def dists(a, instances, mask = None, method='euler'):
    """ calculate the distance of the phase set to all phase sets
    based on std in new_mode_identify
    """
    if len(a) != np.shape(instances)[1]: 
        raise ValueError('shape of phases does not match shape of sample')
    if mask is None: mask=np.arange(len(a))

    if not(hasattr(instances, 'std')):
        print('make phase_array into an np array to speed up 100x')
        instances = np.array(instances.tolist())

    cc = np.tile(a[mask], (shape(instances)[0],1))
    sq = (modtwopi(instances[:,mask]-a))**2
    return(np.sqrt(np.average(sq,1)))



def group_clusters(instances, radius=None):
    """ Assume the instances are in a priority order,
    return a list of lists which point to clustering, working from the 
    first (which is the most frequent down.
    """
    clusterinds = []
    dim = shape(instances)[1]
    if radius is None:
        radius = 0.1 * sqrt(dim)


    # start with all of them
    # remaining are the indices to the original list    
    remaining = range(len(instances))

    while len(remaining)>0:

        # leave the lead in the group tested - simplifies the logic.
        # find distance to all others.  The lead is always index [0]
        distances = [dist2(instances[remaining[0]], 
                           instances[ind])
                     for ind in remaining]
        # keep are indices to the current (shortened) list
        keep = np.where(np.array(distances) < radius**2)[0]
        # always one result (the lead), don't need to test
        print(len(remaining), distances)
        # work from the back so the elements are not moved til after
        # then reverse the result so the leader is first
        clusterinds.append(
            ([remaining.pop(i) for i in np.sort(keep)[::-1]])[::-1])
        # print(len(keep), keep)
    return(clusterinds)

def group_clustersold(instances, radius=None):
    """ Assume the instances are in a priority order 
    """
    clusters = []
    dim = shape(instances)[1]
    if radius is None:
        radius = 0.1 * sqrt(dim)

    lead = 0
    # start with all of them
    remaining = instances.tolist()
    while len(remaining)>0:

        # leave the lead in the group tested - simplifies the logic.
        # find distance to all others
        distances = [dist2(remaining[lead], instance) for instance in remaining]
        keep = np.where(np.array(distances) < radius**2)[0]
        # always one result (the lead), don't need to test
        clusters.append([remaining.pop(i) for i in np.sort(keep)[::-1]])
        # print(len(keep), keep)
    #if debug: 1/0    
    return(clusters)

_var_default="""

method='unsafe'
mincount=3
hold=0
horiz=True  # horizontal legend
n_bins = 48
sel = range(0,10)
sel.extend(range(12,16))
n_plot = 50
scale=0.01  # scale factor for width of lines
min_count = None  # this count is the smallest visible - None sets to the smallest of the n_plot selected
try:
    result
except:
    result=None  # will not be None after a clustering - so can re run without reclustering

"""
exec(_var_default)

from pyfusion.utils import process_cmd_line_args
exec(process_cmd_line_args())

if hold == 0: pl.clf()

if result is None:
    hHD = histogramHD(phases[:,sel],bins = n_bins,method=method)
    phslist = hHD.d.keys()
    counts = array([hHD.d[k] for k in phslist])
    w3 = np.where(counts>=mincount)[0]
    if len(w3)>1000:
        print('only processing where counts >= {mc}'.format(mc=mincount))
        phslist=[phslist[w] for w in w3]
        counts=counts[w3]

    inds = np.argsort(counts)
    result = n_bins
    if method == 'safe':
        # this is a slow step (1 sec for 150k) - should include eps here too!
        phs = -np.pi+2*np.pi/n_bins*np.array(phslist,dtype=float32)
    else:
        phs = []
        # there is probably a faster way than "ord" using numpy.char
        for phi in phslist:
            indices = [ord(c) for c in phi]
            phs.append(-np.pi+2*np.pi/n_bins*np.array(indices,dtype=float32))
        phs = np.array(phs,dtype=float32)

else:
    print('Using previous data')
    if result != n_bins: raise LookupError("can't change n_bins without re-running")

if min_count is None: min_count = np.min(counts[inds[-n_plot:]])

for (i,ind) in enumerate(inds[-n_plot:][::-1]):   # reverse order
    label="{c}".format(c=counts[ind])
    if (i>200):
        if (i % 10)==0: label=label+'..'
        else: label = '_'+label

    pl.plot(phs[ind], label=label,
                 linewidth=scale*n_bins*np.sqrt(np.max(counts[ind]+1-min_count,0)))

pl.rcParams['legend.fontsize']='small'
if horiz:
    ncol = max(int(sqrt(1.5*n_plot)),12)
    pl.legend(ncol=ncol, mode="expand")
    pl.ylim(pl.ylim()[0],pl.ylim()[1]+n_plot*.03)
else:
    pl.legend(ncol=3)
    pl.xlim(pl.xlim()[0],pl.xlim()[1]+5)

pl.show()

pl.figure()

print('grouping')
subset = phs[inds[-n_plot:][::-1]]  # order so that highest is first
subset_counts = counts[inds[-n_plot:][::-1]]
clinds = group_clusters(subset)

# number in the smallest clinds bin
baseline = np.min([np.sum(subset_counts[clinds[i]]) 
                   for i in range(len(clinds))]) 
for (i,clind) in enumerate(clinds):
    linestyle=['-','--','-.',':',"-","--"][np.mod(int((i/len(colorset))),6)]
    for (p,ind) in enumerate(clind):
        if p==0: label = str("{c}:{nc},{pop}"
                             .format(c=i,nc=len(clind),
                                     pop=np.sum(subset_counts[clind])))
        else: label = ''
        pl.plot(subset[ind],color=colorset[i % len(colorset)], linestyle=linestyle,label=label,linewidth=scale*n_bins*(subset_counts[ind]-baseline*0.95)**0.5)

pl.legend()
pl.show()

