def plot_fs_phase(fs_id, cum=False, hold=True):
    import pyfusion
    from numpy import cumsum
    import pylab as pl
    from pyfusion.datamining.clustering.core import DeltaPhase
    
    fs_dp = pyfusion.session.query(DeltaPhase).\
        filter_by(flucstruc_id=fs_id).order_by(DeltaPhase.channel_1_id).all()
    fs_phases= [ dp.d_phase for dp in fs_dp]
    if cum: ph=cumsum(fs_phases)
    else:   ph=fs_phases
    pl.plot(ph, hold=hold)
