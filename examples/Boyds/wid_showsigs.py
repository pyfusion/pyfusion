"""
All time axes are glued together with sharex
This works without requiring that the shot be in the pyfusion database
From wid_specgram - intention is a point-and-click shot overview

David suggests Qt is better for interactive use
Advantage of this simple version is it is toolkit independent.

Notes:
Should really try to modularise this
Display updates are sometimes behind
"""
## thought about implementing spanselector, but, sharex is easier....
from matplotlib.widgets import RadioButtons, CheckButtons, Button, SpanSelector
import pylab as pl
import pyfusion
from pyfusion.visual import ShotOverview


# defaults
global shot_number, diag_name, t0, dt, _hold, x_auto, marker, markersize, linestyle
# this should be more automatic
device=pyfusion.settings.DEVICE

if device=='H1':
    t0=0.0
    dt=0.1
    chan_name='mirnov_1_8'
    shot_number=58123
    diag_name='mirnov_small'
elif device=='HeliotronJ': 
    t0=165
    dt=130
    chan_name='MP1'
    shot_number=33911
    diag_name='MP'
elif device=='TJII': 
    t0=1020
    dt=280
    chan_name='mirnov_5p_105'
    shot_number=18991
    diag_name='mirnov_small'

# note that axes are ganged with sharex, so zoom applies to all.
_hold=0
marker=''
markersize=0.15
linestyle='-'
x_auto=1
cmap=None
xextent=None
NFFT=512
Fsamp=2
Fcentre=0
detrend=pl.mlab.detrend_none
local_none=1 # fudge
ch_list=['mirnov_1_9','mirnov_1_10','ne_centre']
fft_list=['mirnov_1_9']
_window = local_none
foverlap=0
_type='F'
fmod=0
# t_max=0.08
execfile('process_cmd_line_args.py')
if marker=='.': linestyle='None'
ax = pl.subplot(111)
pl.subplots_adjust(left=0.3)

axcolor = 'lightgoldenrodyellow'

#define the box where the buttons live
rax = pl.axes([0.02, 0.89, 0.13, 0.08], axisbg=axcolor)
radio = RadioButtons(rax, ('xlabels', 'no xlabs'), active=0)
def xlabfunc(label):
    print 'xlabfunc', label
    if label=='no xlabs': setp(gca(), 'xticklabels', [])
    if label=='xlabels': 
        
     draw()

radio.on_clicked(xlabfunc)

rax = pl.axes([0.02, 0.74, 0.13, 0.13], axisbg=axcolor)
radio = RadioButtons(rax, ('vert gap', 'small','no gap'), active=1)
def xgapfunc(label):
    gapdict={'vert gap':0.07, 'small':0.03, 'no gap':0}
    print 'xgapfunc', label
    pl.gcf().subplotpars.hspace=gapdict[label]
   # gcf().subplotpars.top=1-gapdict[label]
    pl.gcf().subplots_adjust(top=1-gapdict[label])
    pl.gcf().subplotpars.bottom=0.04+gapdict[label] # allow for text
    pl.draw()

xgapfunc('small')

radio.on_clicked(xgapfunc)

rax = pl.axes([0.02, 0.64, 0.13, 0.08], axisbg=axcolor)
radio = RadioButtons(rax, ('hold', 'off'),active=1)
def holdfunc(label):
    global _hold
    print 'holdfunc', label
    if label=='hold': _hold=1
    else: _hold=0

radio.on_clicked(holdfunc)

rax = pl.axes([0.02, 0.54, 0.13, 0.08], axisbg=axcolor)
radio = RadioButtons(rax, ('x auto', 'x freeze'),active=0)
def xfreezefunc(label):
    global x_auto
    print 'xfreeze', label
    if label=='x auto': x_auto=1
    else: x_auto=0

radio.on_clicked(xfreezefunc)

# the point size box
rax = pl.axes([0.02, 0.39, 0.13, 0.13], axisbg=axcolor)
radio = RadioButtons(rax, ('line', 'point','small','tiny'), active=0)
def xpointfunc(label):
# note - this needs a redraw - if we were to pl[0].set_markersize, it would
# only apply to the last plotted
    global marker, markersize, linestyle
    typedict={'line':'', 'point':'.', 'small':'.', 'tiny':'.'}
    sizedict={'line':1, 'point':1, 'small':0.3, 'tiny':0.1}
    linedict={'line':'-', 'point':'None', 'small':'None', 'tiny':'None'}
    print 'xpointfunc', label
    marker=typedict[label]
    markersize=sizedict[label]
    linestyle=linedict[label]

radio.on_clicked(xpointfunc)

# box for diagnostic list
#           xlleft yll xwidth yheight
rax = pl.axes([0.02, 0.20, 0.2, 0.17], axisbg=axcolor)
from pyfusion import Diagnostic
dqry=pyfusion.session.query(Diagnostic).all()
act=-1  # be prepared for a diagnostic not the list (why?)
if len(dqry)>0:
    dnames= [d.name for d in dqry]
    for id,dname in enumerate(dnames):
        if dname==diag_name: act=id
    if diag_name=='': #if blank, default to the first
        act=0
        diag_name=dnames[act]
    radio = RadioButtons(rax, dnames, active=act)

def diagfunc(label):
    global diag_name
    print 'diagnostic', label
    diag_name=label

radio.on_clicked(diagfunc)

##############################################################
# This line is where I joined the radio button code to the shot number code
# Would be nice to pull this apart into two modules and a short script.
###############################################################
#
#ax = pl.subplot(111)
#
#subplots_adjust(left=0.3)

x0=0
y0=0

class IntegerCtl:
# these really should be in an init
    shot=shot_number

    def set_shot(s):
        shot=s

    def get_shot(self):
        return(self.shot)
    
# probably need to redraw the whole graph
    def redraw(self):
        global _hold, x_auto, diag_name, marker, markersize, linestyle
        bshot.label.set_text(str(self.shot))
        inter=pl.isinteractive
        if inter: pl.ioff()
        s = pyfusion.get_shot(self.shot)
        s.load_diag(diag_name)
        # x=s.data.values()
        inter=pl.isinteractive
        if inter: pl.ioff()
        if x_auto: xlims=[None, None] 
        else: 
#            xlims=gca().xaxis.get_data_interval()
            xlims=gca().get_axes().viewLim._get_intervalx()

        print xlims 
        #print "bug in load_diag? appends? %d elements in x" % (len(x))
        #ii=len(x)-1       ## a bug in load_diag or data.values appends rather than replaces
        #xx=x[ii].plot(xlim=array(xlims),title=str(shot_number), hold=_hold, marker=marker, markersize=markersize, linestyle=linestyle)
        s.data[diag_name].plot(xlim=array(xlims),title=str(shot_number), hold=_hold, marker=marker, markersize=markersize, linestyle=linestyle)
        print marker, markersize, linestyle
        pl.subplots_adjust(left=0.3)
        pl.draw()
        if inter: pl.ion()

    def frew(self, event):
        self.shot -= 10
        self.redraw()

    def rew(self, event):
        self.shot -= 1
        self.redraw()

    def fwd(self, event):
        self.shot += 1
        self.redraw()

    def ffwd(self, event):
        self.shot += 10
        self.redraw()

    def wid_specgram(self, event):
        import os 
        os.spawnl(os.P_NOWAIT, 'ipython', '-pylab',  'examples/Boyds/wid_specgram.py')
        self.redraw()

    def wid_showsigs(self, event):
        import os 
        os.spawnl(os.P_NOWAIT, 'ipython', '-pylab',  'examples/Boyds/wid_showsigs.py')
        self.redraw()


callback = IntegerCtl()
axcolor = 'lightgoldenrodyellow'
but_h = 0.05

axshowsigs =     pl.axes([x0+0.01,  y0+0.03+but_h, 0.1, but_h], axisbg=axcolor)
axwid_specgram = pl.axes([x0+0.01,  y0+0.04+2*but_h, 0.1, but_h], axisbg=axcolor)

#axwid_specgram = pl.axes([x0+0.12,  y0+0.03+but_h, 0.2, but_h], axisbg=axcolor)
axfrew = pl.axes([x0+0.01,  y0+0.02, 0.035, but_h], axisbg=axcolor)
axrew  = pl.axes([x0+0.05, y0+0.02, 0.02, but_h], axisbg=axcolor)
axshot = pl.axes([x0+0.075, y0+0.02, 0.1,  but_h], axisbg=axcolor)
axfwd  = pl.axes([x0+0.18, y0+0.02, 0.02, but_h], axisbg=axcolor)
axffwd = pl.axes([x0+0.205,   y0+0.02, 0.035, but_h], axisbg=axcolor)

#radio = RadioButtons(rax, ('2 Hz', '4 Hz', '8 Hz'))
bfrew=Button(axfrew,'<<')
bfrew.on_clicked(callback.frew)

brew=Button(axrew,'<')
brew.on_clicked(callback.rew)

bshot=Button(axshot,'12345')
bshot.on_clicked(callback.redraw)
# the above needs two args??
# actually, should not just redraw, but allow changes in shot number

bfwd=Button(axfwd,'>')
bfwd.on_clicked(callback.fwd)

bffwd=Button(axffwd,'>>')
bffwd.on_clicked(callback.ffwd)

bwid_specgram=Button(axwid_specgram,'widspec')
bwid_specgram.on_clicked(callback.wid_specgram)

bshowsigs=Button(axshowsigs,'showsigs')
bshowsigs.on_clicked(callback.wid_showsigs)

callback.redraw()
pl.show()

