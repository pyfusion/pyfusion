"""
From wid_specgram - intention is a point-and-click shot overview

David suggests Qt is better for interactive use
Advantage of this simple version is it is toolkit independent.

Notes:
Should really try to modularise this
Display updates are sometimes behind
"""
from matplotlib.widgets import RadioButtons, Button
from pylab import *
import pyfusion
from pyfusion.visual import ShotOverview


# defaults
global shot_number, ch_list, fft_list
shot_number=58123
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

#call_spec()

axcolor = 'lightgoldenrodyellow'

#define the box where the buttons live
rax = axes([0.05, 0.75, 0.15, 0.2], axisbg=axcolor)
radio = RadioButtons(rax, ('win 128', '256', '512', '1024','2048','4096'))
def hzfunc(label):
    global y,NFFT,Fsamp,Fcentre,foverlap,detrend,_window, _type, fmod
    hzdict = {'win 128':128, '256':256, '512':512, '1024':1024,
              '2048':2048, '4096':4096}
    NFFT = hzdict[label]
    call_spec()

radio.on_clicked(hzfunc)

rax = axes([0.05, 0.5, 0.15, 0.2], axisbg=axcolor)
radio = RadioButtons(rax, ('overlap 0', '1/4', '1/2', '3/4','7/8','15/16'))
def ovlfunc(label):
    global y,NFFT,Fsamp,Fcentre,foverlap,detrend,_window, _type, fmod
    ovldict = {'overlap 0':0, '1/4':0.25, '1/2':0.5, '3/4':0.75, '7/8':0.875,
               '15/16':0.9375}
    foverlap = ovldict[label]
    call_spec()

radio.on_clicked(ovlfunc)

rax = axes([0.05, 0.25, 0.15, 0.2], axisbg=axcolor)
radio = RadioButtons(rax, ('no window',  'Bartlett', 'Hanning', 'Hamming',
                           'Blackman', 'Kaiser3','Flat-top-F'))

rax = axes([0.05, 0.1, 0.15, 0.1], axisbg=axcolor)
radio = RadioButtons(rax, ('f-t plot', 'test data', 'log-spect', 'window'))
def typfunc(label):
    global y,NFFT,Fsamp,Fcentre,foverlap,detrend,_window, _type, fmod
    typdict = {'f-t plot':'F', 'test data':'T', 'log-spect':'L', 'window':'W'}
    _type = typdict[label]
    call_spec()

radio.on_clicked(typfunc)
##############################################################
# This line is where I joined the radio button code to the shot number code
# Would be nice to pull this apart into two modules and a short script.
###############################################################
#
ax = subplot(111)
subplots_adjust(left=0.3)

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
        from pyfusion.devices.H1.utils import get_kappa_h
        bshot.label.set_text(str(self.shot))
        inter=isinteractive
        if inter: ioff()
        SO=ShotOverview(self.shot, ch_list, fft_list=fft_list)
        SO.plot()
        xlabel('k_h='+str(get_kappa_h(self.shot)))
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
        os.spawnlp(os.P_NOWAIT, 'ipython', -'pylab', 'examples/Boyds/wid_specgram.py',
                   str("shot_number=%d" % self.shot))
        self.redraw()

    def wid_showsigs(self, event):
        import os 
        os.spawnlp(os.P_NOWAIT, 'ipython', '-pylab', 'examples/Boyds/wid_showsigs.py',
                  str("shot_number=%d" % self.shot))
        self.redraw()

    def wid_showallsigs(self, event):
        import os 
        os.spawnlp(os.P_NOWAIT, 'ipython', '-pylab',  'examples/Boyds/wid_showsigs.py', 
                   "diag_name='mirnovbeans'", str("shot_number=%d" % self.shot))
        self.redraw()


callback = IntegerCtl()
axcolor = 'lightgoldenrodyellow'
but_h = 0.05

axshowsigs =     axes([x0+0.01,  y0+0.03+but_h, 0.1, but_h], axisbg=axcolor)
axshowallsigs =  axes([x0+0.01,  y0+0.04+2*but_h, 0.1, but_h], axisbg=axcolor)
axwid_specgram = axes([x0+0.01,  y0+0.05+3*but_h, 0.1, but_h], axisbg=axcolor)

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

bshowsigs=Button(axshowsigs,'showsigs')
bshowsigs.on_clicked(callback.wid_showsigs)

bshowallsigs=Button(axshowallsigs,'allsigs')
bshowallsigs.on_clicked(callback.wid_showallsigs)

bwid_specgram=Button(axwid_specgram,'widspec')
bwid_specgram.on_clicked(callback.wid_specgram)

callback.redraw()
show()

