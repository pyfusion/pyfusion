import pyfusion
from numpy import average, min, max, array
import pylab as pl

# Commented out so it can live in visual - handy to paste it at the
#    command level if debugging
# from pyfusion.datamining.clustering.core import FluctuationStructure as  FluctuationStructure
    
def plot_sel_flucstrucs(shots=[58123], shotrange=None, decimate=None, text=""):
    """
    Selective plotting routine for flucstrucs, this time with a more
    flexible selection mechanism than can be built incrementally.

      plot_sel_flucstrucs(shots=[58123,58124,58125],text='dm_fs.energy>0.9')
      plot_sel_flucstrucs(shots=[58123,58124,58125],decimate=0.1)
      plot_sel_flucstrucs(shotrange=[58123,58129],decimate=0.1) 

    The RAND() function in mysql seems to return more values towards
    the high end of the interval [0..1], so decimate=0.1 gets ~ 1% of
    data, rather than 10%.  RANDOM() in sqlite in more puzzling
    still... am I doing something wrong?
    """
    from pyfusion.datamining.clustering.core import FluctuationStructure as  FluctuationStructure

    # this one seems to not get interactive right - do it myself
    inter=pl.isinteractive()
    if inter: pl.ioff()
    qry = pyfusion.session.query(FluctuationStructure)
    if shotrange: 
        qry=qry.filter(pyfusion.Shot.shot.between(shotrange[0], shotrange[1]))
    else: 
        qry=qry.filter(pyfusion.Shot.shot.in_(shots))
        
    if decimate: 
        # there is probably a nicer way to allow for different versions of random....
        if str(pyfusion.session.get_bind(0)).find('mys')>-1: randfn="rand()"
        else: randfn="random()"
        qry=qry.filter(randfn+" < " + str(decimate))

    if len(text) > 0 : qry = qry.filter(text)
    fs_list=qry.all()
    num_results=len(fs_list)
    if num_results == 0: raise Exception," no results from query "+str(qry)
    print("%d results from query %s" % (num_results, qry))

    entropy=array([fs.svd.entropy for fs in fs_list])
    print('entrop')
    energy=array([fs.energy for fs in fs_list])
    print('energ')
    freq=array([fs.frequency for fs in fs_list])/1e3
    print('freq')
    time=array([average(fs.svd.timebase) for fs in fs_list])
    print('time')
# above are lots of SQL calls - one per sv - consider another form of
# query - e.g. join
    ax1=pl.subplot(221)
    pl.scatter(time,freq,30*energy/max(energy),200*freq/max(freq))
    pl.xlabel('time (size->fs.energy, colour->fs.freq)')
    pl.ylabel('fs.freq (kHz)')
    ax2=pl.subplot(222)
    pl.scatter(time,freq,30*entropy/max(entropy),200*freq/max(freq))
    pl.xlabel('time (size->svd.entropy, colour->fs.freq)')
    pl.ylabel('fs.freq (kHz)')
    print('2/4')
# good to keep the same colour codes in the same row
    ax3=pl.subplot(223)
    pl.scatter(entropy,energy,30*time/max(time),200*freq/max(freq))
    pl.xlabel('svd.entropy (size->time, colour->fs.freq)')
    pl.ylabel('fs energy')

    ax4=pl.subplot(224)
    pl.scatter(time,energy,30*entropy/max(entropy),200*freq/max(freq))
    pl.xlabel('time (size->svd.entropy, colour->freq)')
    pl.ylabel('fs energy')

    pl.show()
    if inter: pl.ion()
