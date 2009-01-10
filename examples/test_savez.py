""" This is a script file with procedures inline to develop and test a
compressed save routine mainly for pyfusion.  The idea is to extend
the dictionary in Dave's original code so that it contains a version
number, and most importantly, expressions for obtaining the data from
the compressed form.  For simplicity, the compression used is
discretization into integer arrays, which will compress well with
pkzip etc.  Unfortunately, as of python 2.5 and the assoicated numpy,
savez does not use the built in compress feature, so a slighly
modified copy of io.py (hacked_numpy_io_savez.py) is needed.  A
try/except clause on import of hacked_numpy_io.py should quietly
default to no compression.

Plan:
Original:  dictionary contained timebase, signal and internal info 
        in parent_element
Added: version (i32), starting at 100
       rawsignal, rawtime - i32 arrays (rawtime maybe missing 
                            if exprtime doesn't need it )
       exprdata, exprtime - string expressions referring to rawdata and rawtime
These will be intercepted by loadz which will generate replacement values for 
signal and timebase
      units, timebaseunits - strings containing units.

"""
#try:
#    debug_save_compress
#except:
#    debug_save_compress=False;

global verbose
from numpy import savez, array, arange, remainder, mod, sin, pi, min, max, \
        size, diff, random, mean, unique, sort, sqrt, float32
from time import time
from pylab import plot, show
import os

from numpy import load as loadz
try:
    actual_file = '../local_data/test_haarray.npz'
    struc=loadz(actual_file)   # need the extension
    print('file contains %s' % struc.files)
except: print("actual data file %s not found, continuing" % actual_file)

# quick test for exec overhead
expr="x=5.12/2048*raw - 5.12"
raw=mod(arange(100000),4096)
exec(expr)

# now test the timing in more detail

simple_expr='x=1'
loops=10000
st=time()
for i in arange(loops): exec(simple_expr)
ns=1e9*(time()-st)/loops
print('%g %s for %s'  % (1e-3*ns, 'usec/exec', simple_expr))
st=time() ; exec(expr) 
ns=1e9*(time()-st)
print('%.3g %s for %s'  % (ns/len(x), 'nsec/exec element', expr))
maxp=min([1e5,len(x)])
plot(x[0:maxp],hold=0)
show()

# now to test discretisation
# First put in the range 0,2^n-1
bits=14
t=arange(2000)*1e-6
rdata=2000*sin(5e3*2*pi*t)
plot(t[0:maxp],rdata[0:maxp],'c',hold=0)
plot(t[0:maxp],rdata[0:maxp],'.b',hold=1,markersize=1.5)
show()
rlims=(min(rdata), max(rdata))
yspan=2.0**bits-1
ints=((rdata-rlims[0])*yspan/(rlims[1]-rlims[0])).astype('i')

from pyfusion.hacked_numpy_io import savez
savez('test',ints)   # is the simplest, but array takes a default name
savez('test', raw=ints, expr=expr)

# now test load.  Unmodified, it should handle compressed zips of the basic type
from numpy import load as loadz
struc=loadz('test.npz')   # need the extension
print('file contains %s' % struc.files)
struc['expr']
exec(expr)
# now see how fast it is for a little one
small=arange(10)
st=time()
from tempfile import gettempdir, gettempprefix, mkstemp

#tmp=gettempdir()+gettempprefix()
tmpfd=mkstemp(suffix='.npz')
tmp=tmpfd[1]
print(' using temporary file %s' % tmp)
savez(tmp,small=small)
sv=time()
loadz(tmp)
ld=time()
print('trivial file saved in %.3g msecs, loaded in %.3g msec' % ((sv-st)*1e3, (ld-sv)*1e3)) 
print(' Now a big one')
st=time()
savez(file=tmp,raw=raw)
sv=time()
readfd=open(tmp,'r') #  wants integer  - too low level?
# ideally, refer by file object, but CRC-32 error rdstr=loadz(file=readfd)
rdstr=loadz(file=tmp)
ld=time()
if (rdstr['raw'] != raw).any(): print("Error retrieving data from " + tmp)
print('%d ints saved in %.3g msecs, loaded in %.3g msec' % (len(raw),(sv-st)*1e3, (ld-sv)*1e3)) 
## print(os.fstat[tmpfd[0])  too low level?
os.close(tmpfd[0])
try: os.remove(tmp)
except: print('unable to delete '+tmp)

# now design an algorithm to find the natural discetisation of data
# make it easy - no  noise
cdata=(ints-mean(ints))*5.12/max(ints)/2
cdata_sort=unique(cdata)
diff_sort=unique(diff(cdata_sort))
# with real representation, there will be many diffs ~ eps - 1e-8 or 1e-15*max
# this step is to ignore trivial differences
min_real_diff_ind=(diff_sort > max(diff_sort)/1e5).nonzero()
deltar=diff_sort[min_real_diff_ind[0][0]]
print('estimate minimum difference is %g' % deltar)
remain=mod((cdata-min(cdata))/deltar, 1)
maxerr=(max(abs(remain)))
print('maximum error = %g' % maxerr)

print('Now noisy data - 1e-8 precision')
# will use eps in relative sense
eps=1e-7
clean_data=cdata
cdata=(ints+random.uniform(low=-1, high=1,size=len(ints))*eps-mean(ints))*5.12/max(ints)/2
cdata_sort=unique(cdata)
diff_sort=unique(diff(cdata_sort))
# with real representation, there will be many diffs ~ eps - 1e-8 or 1e-15*max
min_real_diff_ind=(diff_sort > max(diff_sort)*3e-4).nonzero()
deltar=diff_sort[min_real_diff_ind[0][0]]
print('seems like minimum difference is %g' % deltar)
remain=mod((cdata-min(cdata))/deltar, 1)
# remain is relative to unit step, need to scale back down
maxerr=max(abs(remain))*deltar
# not clear what the max expected error is - small for 12 bits, gets larger quicly
if maxerr<eps*sqrt(yspan): print("appears to be successful")
print('maximum error with %g noise = %g, =%.3g x eps' % (eps,maxerr,maxerr/eps))

# 
from numpy import std
#""
def discretise_array(arr, eps=0, bits=0, maxcount=0, verbose=0):
    """
    Return an integer array and scales etc in a dictionary 
    - the dictionary form allows for added functionaility.
    If bits=0, find the natural accuracy.  eps defaults to 3e-6, and 
    is the error relative to the larest element, as is maxerror.
    """
    from numpy import max, std, array, min, sort, diff, unique
    if eps==0: eps=3e-6
    if maxcount==0: maxcount=10
    count=1
    ans=try_discretise_array(arr, eps=eps,bits=bits, verbose=verbose)
    initial_deltar=ans['deltar']
    while (ans['maxerror']>eps) and (count<maxcount):
        count+=1
        # have faith in our guess, assume problem is that step is
        # not the minimum.  e.g. arr=[1,3,5,8] 
        #          - min step is 2, natural step is 1
        ans=try_discretise_array(arr, eps=eps,bits=bits,deltar=initial_deltar/count, verbose=verbose)
        
    if verbose>0: print("integers from %d to %d, delta=%.5g" % (\
            min(ans['iarr']), max(ans['iarr']), ans['deltar']) )    
    return(ans)
#    return(ans.update({'count':count})) # need to add in count

def try_discretise_array(arr, eps=0, bits=0, deltar=None, verbose=0):
    """
    Return an integer array and scales etc in a dictionary 
    - the dictionary form allows for added functionaility.
    If bits=0, find the natural accuracy.  eps defaults to 1e-6
    """
    if verbose>2: import pylab as pl
    if eps==0: eps=1e-6
    if deltar==None: 
        data_sort=unique(arr)
        diff_sort=sort(diff(data_sort))  # don't want uniques because of noise

    # with real representation, there will be many diffs ~ eps - 1e-8 
    # or 1e-15*max - try to skip over these
    #  will have at least three cases 
    #    - timebase with basically one diff and all diffdiffs in the noise    
    #    - data with lots of diffs and lots of diffdiffs at a much lower level
        min_real_diff_ind=(diff_sort > max(diff_sort)/1e4).nonzero()
#      min_real_diff_ind[0] is the array of inidices satisfying that condition 
        if verbose>1: print("min. real difference indices = ", min_real_diff_ind)
        #discard all preceding this
        diff_sort=diff_sort[min_real_diff_ind[0][0]:]
        deltar=diff_sort[0]
        diff_diff_sort=diff(diff_sort)
        # now look for the point where the diff of differences first exceeds half the current estimate of difference
        
        # the diff of differences should just be the discretization noise 
        # by looking further down the sorted diff array and averaging over
        # elements which are close in value to the min real difference, we can
        # reduce the effect of discretization error.
        large_diff_diffs_ind=(abs(diff_diff_sort) > deltar/2).nonzero()
        if size(large_diff_diffs_ind) ==0:
            last_small_diff_diffs_ind = len(diff_sort)-1
        else: 
            first_large_diff_diffs_ind = large_diff_diffs_ind[0][0]
            last_small_diff_diffs_ind = first_large_diff_diffs_ind-1
            
        deltar=mean(diff_sort[0:last_small_diff_diffs_ind])
        peaknoise = max(abs(diff_sort[0:last_small_diff_diffs_ind] -
                                deltar))
        rmsnoise = std(diff_sort[0:last_small_diff_diffs_ind] -
                                deltar)
        if (verbose>0) or (peaknoise>1e-5): 
            print('looks like numerical noise ~ %.2g pk, %.2gRMS' % 
                  (peaknoise, rmsnoise))

        if verbose>2: 
            print("%d diff diffs meeting criterion < %g " % 
                  (last_small_diff_diffs_ind, deltar/2 ))
            pl.plot(diff_sort,hold=0)
        if verbose>10: x=1/0  # a debug point

    if verbose>1: print('seems like minimum difference is %g' % deltar)
    iarr=(0.5+(arr-min(arr))/deltar).astype('i')
    remain=iarr-((arr-min(arr))/deltar)
    remainck=mod((arr-min(arr))/deltar, 1)

# remain is relative to unit step, need to scale back down
    maxerr=max(abs(remain))*deltar/max(arr)
# not clear what the max expected error is - small for 12 bits, gets larger quicly
    if (verbose>0) and maxerr<eps: print("appears to be successful")
    if verbose>0: print('maximum error with eps = %g, is %g, %.3g x eps' % (eps,maxerr,maxerr/eps))
    return({'iarr':iarr, 'maxerror':maxerr, 'deltar':deltar, 'minarr':min(arr),
            'intmax':max(iarr)})

def discretise_signal(timebase=None, signal=None, eps=0, verbose=0, 
                      delta_encode_time=True,
                      filename=None):
    """  a function to return a dictionary from signal and timebase, with 
    relative accuracy eps, optionally saving if filename is defined. 
    Achieves a factor of ~10x on MP1 signal 33373 using delta_encode_time=True
    """
    from numpy import remainder, mod, min, max, \
        diff, mean, unique, append
    from pyfusion.hacked_numpy_io import savez
    dat=discretise_array(signal,eps=eps,verbose=verbose)
#    signalexpr=str("signal=%g+rawsignal*%g" % (dat['minarr'], dat['deltar']))
# this version works here and now - need a different version to work in loadz
    signalexpr=str("signal=%g+%s*%g" % (dat['minarr'], "dat['iarr']",
                                        dat['deltar']))

# this version is designed to be evaluated on dictionary called dic
    signalexpr=str("signal=%g+%s*%g" % (dat['minarr'], "dic['rawsignal']",
                                        dat['deltar']))
# saving bit probably should be separated
    tim=discretise_array(timebase,eps=eps,verbose=verbose)
    rawtimebase=tim['iarr']
    timebaseexpr=str("timebase=%g+%s*%g" % (tim['minarr'], "tim['iarr']",
                                            tim['deltar']))
# this version 
    timebaseexpr=str("timebase=%g+%s*%g" % (tim['minarr'], "dic['rawtimebase']",
                                          tim['deltar']))
    if delta_encode_time: 
#        need to maintain the first element and the length
        rawtimebase=append(rawtimebase[0],diff(rawtimebase))
        timebaseexpr=str("timebase=%g+%s*%g" % (tim['minarr'], 
                                                "cumsum(dic['rawtimebase'])",
                                                tim['deltar']))
    if filename!=None:
        if verbose>0: print('Saving as %s' % filename)
        savez(filename, timebaseexpr=timebaseexpr, signalexpr=signalexpr,
              rawsignal=dat['iarr'], rawtimebase=rawtimebase, version=1)    


def newload(filename):
    from numpy import load as loadz
    from numpy import cumsum
    dic=loadz(filename)
    if dic['version'] != None:
        print ("version %d" % (dic['version']))
    else: 
        print("version 0: simple")
        return(dic)

    print('file contains %s' % dic.files)
    signalexpr=dic['signalexpr']
    timebaseexpr=dic['timebaseexpr']
# savez saves ARRAYS always, so have to turn array back into scalar    
    exec(signalexpr.tolist())
    exec(timebaseexpr.tolist())
    return({"signal":signal, "timebase":timebase})



def test_compress(file=None, verbose=0, eps=0, debug=False, maxcount=0):
    print("Testing %s" % file)
    if file==None: file='18993_densitymediaIR.npz'
    test=loadz(file)
    stat=os.stat(file)

    if verbose > 0: print("=========== testing signal compression ===========")
    sig=discretise_array(test['signal'],eps=eps,verbose=verbose,maxcount=maxcount)
    if verbose > 0: print("=========== testing timebase compression===========")
    tim=discretise_array(test['timebase'],eps=eps,verbose=verbose)
    print('  File length %d bytes, %d samples, %.3g bytes/sample' % (
            stat.st_size ,len(sig['iarr']),
            float(stat.st_size)/len(sig['iarr'])))
    temp='temp.npz'
    savez(temp,sig['iarr'])
    print("    compressed to %d bytes" % os.stat(temp).st_size)
    savez(temp,diff(sig['iarr']))
    print("      differences compressed to %d bytes" % os.stat(temp).st_size)
    savez(temp,diff(diff(sig['iarr'])))
    print("      double differences compressed to %d bytes" % os.stat(temp).st_size)
    print("    time compressed to %d bytes" % os.stat(temp).st_size)
    savez(temp,diff(tim['iarr']))
    print("      difference compressed to %d" % os.stat(temp).st_size)
    savez(temp,diff(diff(tim['iarr'])))
    print("      double difference compressed to %d" % os.stat(temp).st_size)
    if debug: xx=1/0

# First, try the tricky case of a marginal precision timebase
# This happens when a 32bit real timebase has a large offset e.g. 1sec on 1us
try:    verbose
except: verbose=1

print('====== synthetic marginal precision timebase test =========')
noisytime=1+array(arange(1e4),dtype=float32)/1e6
tim=discretise_array(noisytime,eps=eps,verbose=verbose)

pushd=os.getcwd()
os.chdir(os.getenv('PYFUSIONPATH'))
os.chdir('..')
os.chdir('local_data')
try:
    print('verbose = ', verbose)
except: verbose=2

mp1=loadz('33373_MP1.npz')

discretise_signal(filename="foo",signal=mp1['signal'], 
                  timebase=mp1['timebase'], verbose=verbose)
mp1read=newload("foo.npz")

if len(mp1['signal']) != len(mp1read['signal']): print("length mismatch")
if len(mp1['timebase']) != len(mp1read['timebase']): print("length mismatch")
print("max signal error = %g" % max(mp1['signal']-mp1read['signal']))
print("max timebase error = %g" % max(mp1['timebase']-mp1read['timebase']))

if verbose > 10: x=1/0
test_compress('33373_MP1.npz',verbose=verbose,eps=1e-5)
# Haarray31 shot 33373 compresses least well - eps=1.9e-6 (rel), maybe because
# dave's save is limited in precision and signal is small.
test_compress('33373_HAARRAY31.npz',verbose=verbose)

test_compress('18993_densitymediaIR.npz')
os.chdir(pushd)


