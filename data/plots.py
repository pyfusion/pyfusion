"""
Note, plots (this file) doesn't have unittests
"""

from pyfusion.data.timeseries import TimeseriesData

def plot_signals(input_data, filename=None):
    import pylab as pl
    n_rows = input_data.signal.n_channels()

    for row in range(n_rows):
        pl.subplot(n_rows, 1, row+1)
        pl.plot(input_data.timebase, input_data.signal.get_channel(row))
    
    if filename != None:
        pl.savefig(filename)
    else:
        pl.show()

plot_signals.allowed_class=[TimeseriesData]

def plot_multichannel_coord(input_data, coord=None, savefig=None):
    pass
