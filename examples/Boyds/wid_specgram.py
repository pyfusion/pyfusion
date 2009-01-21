"""
usage = wid_specgram shot_number=58123 "chan_name='mirnov_1_8'"
run examples/Boyds/wid_specgram.py shot_number=58043 "chan_name='mirnov_1_8'"

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
import pylab as pl
from numpy import sin, pi, ones, hanning, hamming, bartlett, kaiser, arange

import pyfusion

# local definitions for a few windows. mlab.windows are defined
# differently, and the returned value is multiplied by the input data
# already.  There are only two of the mlab.window_hanning and
# mlab.window_none.  However, to be useful to David's function, they
# need to be exported I think.

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
global shot_number, chan_name
shot_number=58123
cmap=None
#xextent=None  # was here, really belongs in data.spectrogram
NFFT=512
Fsamp=2
chan_name=''
Fcentre=0
detrend=pl.detrend_none
_window = local_none
foverlap=0.75   # 0 is the cheapest, but 3/4 looks better
_type='F'
fmod=0
# t_max=0.08
execfile('process_cmd_line_args.py')

# arrays for test signal
tm=arange(0,0.02,1e-6)
y=sin((2e5 + 5e3*sin(fmod*2*pi*tm))*2*pi*tm)

def call_spec():
    global y,NFFT,Fsamp,Fcentre,foverlap,detrend,_window, _type, fmod, chan_name
    print len(y), NFFT,foverlap, _type, fmod
    ax = pl.subplot(111)
    z=_window(y)
    if _type=='F': 
        shot=callback.get_shot()
        print("shot=%d") % shot
        if chan_name=='':
            try:
                ch=pyfusion.Session.query(pyfusion.Channel)
                print("Choosing from", [chn.name for chn in ch])
                name=ch[0].name
            except:
                print "Failed to open channel database - try mirnov_1_8"
                name='mirnov_1_8'
                name='mirnov_linear_2'
        else:        
            name=chan_name

        data = pyfusion.load_channel(shot,name)
        if _window==local_none: windowfn=pl.window_none 
        else: windowfn=pl.window_hanning

        data.spectrogram(NFFT=NFFT, windowfn=windowfn, noverlap=foverlap*NFFT,
                         colorbar=True)
#        colorbar() # used to come up on a separate page, fixed, but a little clunky - leave for now

    elif _type == 'T':
# some matplotlib versions don't know about Fc
        specgram(z*y, NFFT=NFFT, Fs=Fsamp, detrend=detrend,
#                 window = _window
                 noverlap=foverlap*NFFT, cmap=cmap)
    elif _type == 'L':
        pl.plot(20*log10(abs(fft(y*z))))
    elif _type == 'W':
        pl.plot(z)
    else: raise ' unknown plot type "' + _type +'"'
ax = pl.subplot(111)
pl.subplots_adjust(left=0.3)
#call_spec()

axcolor = 'lightgoldenrodyellow'

#define the box where the buttons live
rax = pl.axes([0.05, 0.75, 0.15, 0.2], axisbg=axcolor)
radio = RadioButtons(rax, ('win 128', '256', '512', '1024','2048','4096'),active=2)
def hzfunc(label):
    global y,NFFT,Fsamp,Fcentre,foverlap,detrend,_window, _type, fmod
    hzdict = {'win 128':128, '256':256, '512':512, '1024':1024,
              '2048':2048, '4096':4096}
    NFFT = hzdict[label]
    call_spec()

radio.on_clicked(hzfunc)

rax = pl.axes([0.05, 0.5, 0.15, 0.2], axisbg=axcolor)
radio = RadioButtons(rax, ('overlap 0', '1/4', '1/2', '3/4','7/8','15/16'),active=3)

def ovlfunc(label):
    global y,NFFT,Fsamp,Fcentre,foverlap,detrend,_window, _type, fmod
    ovldict = {'overlap 0':0, '1/4':0.25, '1/2':0.5, '3/4':0.75, '7/8':0.875,
               '15/16':0.9375}
    foverlap = ovldict[label]
    call_spec()

radio.on_clicked(ovlfunc)

rax = pl.axes([0.05, 0.25, 0.15, 0.2], axisbg=axcolor)
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

rax = pl.axes([0.05, 0.1, 0.15, 0.1], axisbg=axcolor)
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
#ax = subplot(111)
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
        bshot.label.set_text(str(self.shot))
        call_spec()
        pl.draw()

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

# extra fast fwd is 100+
    def Xffwd(self, event):
        self.shot += 100
        self.redraw()


callback = IntegerCtl()
axcolor = 'lightgoldenrodyellow'
but_h = 0.05
axfrew = pl.axes([x0+0.01,  y0+0.02, 0.03, but_h], axisbg=axcolor)
axrew  = pl.axes([x0+0.045, y0+0.02, 0.02, but_h], axisbg=axcolor)
axshot = pl.axes([x0+0.070, y0+0.02, 0.1,  but_h], axisbg=axcolor)
axfwd  = pl.axes([x0+0.175, y0+0.02, 0.02, but_h], axisbg=axcolor)
axffwd = pl.axes([x0+0.2,   y0+0.02, 0.03, but_h], axisbg=axcolor)
axXffwd = pl.axes([x0+0.235,   y0+0.02, 0.035, but_h], axisbg=axcolor)

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

bXffwd=Button(axXffwd,'>>>')
bXffwd.on_clicked(callback.Xffwd)

callback.redraw()
pl.show()

