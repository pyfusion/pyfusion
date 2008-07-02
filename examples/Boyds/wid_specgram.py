"""
Code to develop shot incrementing widget-like interface
Primarily looks at spectrograms, but has built in test function and crude window inspector.

David suggests Qt is better for interactive use
Advantage of this simple version is it is toolkit independent.

Notes:
Need to include channel selector - hardwired to mirnov 8 at the moment.  
Initially will use radio button channel selector - one at a time.
Ultimate plan is to include an SQL query box to narrow range of shots
Should really try to modularise this
Display updates are 90% right now - still one step behind in adjusting FFT params
"""
from matplotlib.widgets import RadioButtons, Button
from pylab import *
import pyfusion

# local definitions for a few windows. mlab.windows are defined differently,
# and the returned value is multiplied by the input data already.
def local_none(vec):
    return(ones(len(vec)))

def local_hanning(vec):
    return(hanning(len(vec)))

def local_hamming(vec):
    return(hamming(len(vec)))

def local_blackman(vec):
    return(blackman(len(vec)))

def local_bartlett(vec):
    return(bartlett(len(vec)))

# not sure about this, but it is pretty right.
def local_kaiser3(vec):
    return(kaiser(len(vec),3*pi))

def local_flat_top_freq(vec):
    N=len(vec)
    k=arange(N)
    w = (1 - 1.93*cos(2*pi*k/(N-1)) + 1.29*cos(4*pi*k/(N-1)) 
         -0.388*cos(6*pi*k/(N-1)) +0.032*cos(8*pi*k/(N-1)))
    return(w)

# defaults
shot=58123
cmap=None
xextent=None
NFFT=512
Fsamp=2
Fcentre=0
detrend=mlab.detrend_none
_window = local_none
foverlap=0
_type='F'
fmod=0

# arrays for test signal
tm=arange(0,0.02,1e-6)
y=sin((2e5 + 5e3*sin(fmod*2*pi*tm))*2*pi*tm)

def call_spec():
    global y,NFFT,Fsamp,Fcentre,foverlap,detrend,_window, _type, fmod
    print len(y), NFFT,foverlap, _type, fmod
    ax = subplot(111)
    z=_window(y)
    if _type=='F': 
        shot=callback.get_shot()
        print("shot=%d") % shot
        data = pyfusion.load_channel(shot,'mirnov_1_8')
        data.spectrogram(NFFT=NFFT,noverlap=foverlap*NFFT)
#        colorbar() # comes up on a separate page

    elif _type == 'T':
# some matplotlib versions don't know about Fc
        specgram(z*y, NFFT=NFFT, Fs=Fsamp, detrend=detrend,
#                 window = _window
                 noverlap=foverlap*NFFT, cmap=cmap, xextent=xextent)
    elif _type == 'L':
        plot(20*log10(abs(fft(y*z))))
    elif _type == 'W':
        plot(z)
    else: raise ' unknown plot type "' + _type +'"'
ax = subplot(111)
subplots_adjust(left=0.3)
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
def winfunc(label):
    global y,NFFT,Fsamp,Fcentre,foverlap,detrend,_window, _type, fmod
    windict = {'no window':local_none, 'Hanning':local_hanning, 
               'Hamming':local_hamming, 'Blackman':local_blackman, 
               'Bartlett':local_bartlett, 'Kaiser3':local_kaiser3,
               'Flat-top-F':local_flat_top_freq}
    _window = windict[label]
    call_spec()

radio.on_clicked(winfunc)

rax = axes([0.05, 0.1, 0.15, 0.1], axisbg=axcolor)
radio = RadioButtons(rax, ('f-t plot ', 'test data', 'log-spect', 'window'))
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
#ax = subplot(111)
#
#subplots_adjust(left=0.3)

x0=0
y0=0

class IntegerCtl():
# these really should be in an init
    shot=58125

    def set_shot(s):
        shot=s

    def get_shot(self):
        return(self.shot)
    
# probably need to redraw the whole graph
    def redraw(self):
        bshot.label.set_text(str(self.shot))
        call_spec()
        draw()

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


callback = IntegerCtl()
axcolor = 'lightgoldenrodyellow'
but_h = 0.05
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

callback.redraw()
show()

