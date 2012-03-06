import pyfusion as pf
h1=pf.getDevice("LHD")
data=h1.acq.getdata(27233,'MP')
data.plot_signals()
