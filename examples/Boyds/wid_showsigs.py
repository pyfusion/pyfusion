"""
All time axes are glued together with sharex

From wid_specgram - intention is a point-and-click shot overview

David suggests Qt is better for interactive use
Advantage of this simple version is it is toolkit independent.

Notes:
Should really try to modularise this
Display updates are sometimes behind
"""
## thought about implementing spanselector, but, sharex is easier....
from matplotlib.widgets import RadioButtons, CheckButtons, Button, SpanSelector
from pylab import *
import pyfusion
from pyfusion.visual import ShotOverview


# defaults
global shot_number, diag_name, t0, dt, hold, x_auto
shot_number=58123
diag_name='mirnovbean1'
# note that axes are ganged with sharex, so zoom applies to all.
t0=0.0
dt=0.1
hold=0
x_auto=1
cmap=None
xextent=None
NFFT=512
Fsamp=2
Fcentre=0
detrend=mlab.detrend_none
local_none=1 # fudge
ch_list=['mirnov_1_9','mirnov_1_10','ne_centre']
fft_list=['mirnov_1_9']
_window = local_none
foverlap=0
_type='F'
fmod=0
# t_max=0.08
execfile('process_cmd_line_args.py')

ax = subplot(111)
subplots_adjust(left=0.3)

axcolor = 'lightgoldenrodyellow'

#define the box where the buttons live
rax = axes([0.02, 0.75, 0.13, 0.13], axisbg=axcolor)
radio = RadioButtons(rax, ('xlabels', 'no xlabs'), active=0)
def xlabfunc(label):
    print 'xlabfunc', label
    if label=='no xlabs': setp(gca(), 'xticklabels', [])
    if label=='xlabels': 
        
     draw()

radio.on_clicked(xlabfunc)

rax = axes([0.02, 0.6, 0.13, 0.13], axisbg=axcolor)
radio = RadioButtons(rax, ('vert gap', 'small','no gap'), active=0)
def xgapfunc(label):
    gapdict={'vert gap':0.7, 'small':0.03, 'no gap':0}
    print 'xgapfunc', label
    gcf().subplotpars.hspace=gapdict[label]
    gcf().subplotpars.top=1-gapdict[label]
    gcf().subplotpars.bottom=gapdict[label]
    draw()

radio.on_clicked(xgapfunc)

rax = axes([0.02, 0.45, 0.13, 0.13], axisbg=axcolor)
radio = RadioButtons(rax, ('hold', 'off'),active=1)
def holdfunc(label):
    global hold
    print 'holdfunc', label
    if label=='hold': hold=1
    else: hold=0

radio.on_clicked(holdfunc)

rax = axes([0.02, 0.3, 0.13, 0.13], axisbg=axcolor)
radio = RadioButtons(rax, ('x auto', 'x freeze'),active=0)
def xfreezefunc(label):
    global x_auto
    print 'xfreeze', label
    if label=='x auto': x_auto=1
    else: x_auto=0

radio.on_clicked(xfreezefunc)

##############################################################
# This line is where I joined the radio button code to the shot number code
# Would be nice to pull this apart into two modules and a short script.
###############################################################
#
#ax = subplot(111)
#
#subplots_adjust(left=0.3)

x0=0
y0=0

class IntegerCtl():
# these really should be in an init
    shot=shot_number

    def set_shot(s):
        shot=s

    def get_shot(self):
        return(self.shot)
    
# probably need to redraw the whole graph
    def redraw(self):
        global hold, x_auto
        bshot.label.set_text(str(self.shot))
        inter=isinteractive
        if inter: ioff()
        s = pyfusion.get_shot(self.shot)
        s.load_diag(diag_name)
        x=s.data.values()
        inter=isinteractive
        if inter: ioff()
        if x_auto: xlims=[None, None] 
        else: 
#            xlims=gca().xaxis.get_data_interval()
            xlims=gca().get_axes().viewLim._get_intervalx()

        print xlims
        xx=x[0].plot(xlim=array(xlims),title=str(shot_number), hold=hold)
        subplots_adjust(left=0.3)
        draw()
        if inter: ion()

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
        os.spawnlp(os.P_NOWAIT, 'ipython', '-pylab',  'examples/Boyds/wid_specgram.py')
        self.redraw()

    def wid_showsigs(self, event):
        import os 
        os.spawnlp(os.P_NOWAIT, 'ipython', '-pylab',  'examples/Boyds/wid_showsigs.py')
        self.redraw()


callback = IntegerCtl()
axcolor = 'lightgoldenrodyellow'
but_h = 0.05

axshowsigs =     axes([x0+0.01,  y0+0.03+but_h, 0.1, but_h], axisbg=axcolor)
axwid_specgram = axes([x0+0.01,  y0+0.04+2*but_h, 0.1, but_h], axisbg=axcolor)

#axwid_specgram = axes([x0+0.12,  y0+0.03+but_h, 0.2, but_h], axisbg=axcolor)
axfrew = axes([x0+0.01,  y0+0.02, 0.03, but_h], axisbg=axcolor)
axrew  = axes([x0+0.045, y0+0.02, 0.02, but_h], axisbg=axcolor)
axshot = axes([x0+0.070, y0+0.02, 0.1,  but_h], axisbg=axcolor)
axfwd  = axes([x0+0.175, y0+0.02, 0.02, but_h], axisbg=axcolor)
axffwd = axes([x0+0.2,   y0+0.02, 0.03, but_h], axisbg=axcolor)

#radio = RadioButtons(rax, ('2 Hz', '4 Hz', '8 Hz'))
bfrew=Button(axfrew,'<<')
bfrew.on_clicked(callback.frew)

brew=Button(axrew,'<')
brew.on_clicked(callback.rew)

bshot=Button(axshot,'12345')

bfwd=Button(axfwd,'>')
bfwd.on_clicked(callback.fwd)

bffwd=Button(axffwd,'>>')
bffwd.on_clicked(callback.ffwd)

bwid_specgram=Button(axwid_specgram,'widspec')
bwid_specgram.on_clicked(callback.wid_specgram)

bshowsigs=Button(axshowsigs,'showsigs')
bshowsigs.on_clicked(callback.wid_showsigs)

callback.redraw()
show()

