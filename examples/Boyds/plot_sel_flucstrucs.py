import pyfusion
from numpy import average, min, max, array
from pyfusion.datamining.clustering.core import FluctuationStructure
    
def plot_sel_flucstrucs(shots=[58123], shotrange=None, decimate=None, text=""):
    """
    Selective plotting routine for flucstrucs, this time with a more flexible 
    selection mecahism built incrementally.
       plot_sel_flucstrucs(shots=[58123,58124,58125],text='dm_fs.energy>0.9')
       plot_sel_flucstrucs(shots=[58123,58124,58125],decimate=0.1)
       plot_sel_flucstrucs(shotrange=[58123,58129],decimate=0.1)
    """
    qry = pyfusion.session.query(FluctuationStructure)
    if shotrange: 
        qry=qry.filter(pyfusion.Shot.shot.between(shotrange[0], shotrange[1]))
    else: 
        qry=qry.filter(pyfusion.Shot.shot.in_(shots))
        
    if decimate: qry=qry.filter("rand() < " + str(decimate))
    if len(text) > 0 : qry = qry.filter(text)
    fs_list=qry.all()
    if len(fs_list) == 0: raise Exception," no results from query "+str(qry)

    import pylab as pl
    entropy=array([fs.svd.entropy for fs in fs_list])
    energy=array([fs.energy for fs in fs_list])
    freq=array([fs.frequency for fs in fs_list])/1e3
    time=array([average(fs.svd.timebase) for fs in fs_list])
# lots of SQL calls - one per sv - consider another form of query - e.g. join
    ax1=pl.subplot(221)
    pl.scatter(time,freq,30*energy/max(energy),200*freq/max(freq))
    pl.xlabel('time (size->fs.energy, colour->fs.freq)')
    pl.ylabel('fs.freq (kHz)')
    ax2=pl.subplot(222)
    pl.scatter(time,freq,30*entropy/max(entropy),200*freq/max(freq))
    pl.xlabel('time (size->svd.entropy, colour->fs.freq)')
    pl.ylabel('fs.freq (kHz)')

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
