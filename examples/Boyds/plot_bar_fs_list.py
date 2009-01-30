def plot_bar_fs_list(fs_list, orientation='horizontal', width=None, hold=1):
    """ accept a flucstruc list and plot as an overlapped bar
    width is the bar width relative to unity.
    """ 
    import pylab as pl
    from numpy import zeros, ones, arange, array
#data=exp(-0.5*arange(10))
#    pl.plot hold=0
    data=[fs.a1 for fs in fs_list]
    if width==None: width=0.7

    com_kw={'align':'center', 'orientation': orientation}
    
    left=arange(len(data))
    bottom=zeros(len(data))

    if orientation=='horizontal': (left,bottom)=(bottom,left)

    fs0=fs_list[0]
    ec0=(len(fs_list))*['red',]  # replicate 'black' len times (note trailing comma)
# want to mark all the fs's from the same svd or time segment
    for (i,fs) in enumerate(fs_list):
        if fs.svd.id!=fs0.svd.id: ec0[i]='gray'

    wid0=width*ones(len(data))
    if orientation=='horizontal': (wid0,data)=(data,wid0)
    pl.bar(left,data,wid0, bottom, color='c', hold=hold, edgecolor=ec0, **com_kw)

# for the horizontal case
    lab=str('  fr=%.3g\n  t=%.3g' % (fs0.frequency/1e3, fs0.tmid*1e3))
    if orientation=='horizontal': pl.text(wid0[0], 0, lab)
    else: pl.text(0, data[0], lab, va='bottom', ha='center')

    data=[fs.a1*fs.a12 for fs in fs_list]
    wid1=width*array([fs.a12 for fs in fs_list])
    if orientation=='horizontal': (wid1,data)=(data,wid1)
    pl.bar(left,data,wid1, bottom, color='b',edgecolor='none', **com_kw)

    data=[fs.a1*fs.a13 for fs in fs_list]
    wid1=width*array([fs.a13 for fs in fs_list])
    if orientation=='horizontal': (wid1,data)=(data,wid1)
    pl.bar(left,data, wid1, bottom, color='y',edgecolor='none', **com_kw)

