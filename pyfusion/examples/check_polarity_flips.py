from numpy import sort, mod, pi
import pylab as pl
import pyfusion
""" use cross correlation and analytic phase to check sign of magnetic probes.  
    Results are not clear for LHD.  Need to find some good example shots.
    May need to restrict frequncy range, to isolate one mode.
    Analytic phase is clearer than correlation, both similar speeds (plot is slow)
    http://en.wikipedia.org/wiki/Analytic_signal

    run pyfusion/examples/check_polarity_flips.py aphase=1

    HMPs flipped are HMP06, HMP13 (flips=[5,12]) (i.e. HMP06,HMP13)
    pyfusion/examples/check_polarity_flips.py corr=0 aphase=1 markersize=.03 diag_name=HMP shot_number=65139 flips=[5,12]
    54198  - 5 confirmed, 12 noisy, can't tell
    73051 - too big - memory error in plot?
    27233 - flips=[7,12]
    39755 - flips=[12] only


"""


# Optional,but these two save data recall time, and plotting time/space
# E4300 U10.04 0.35sec wall for access, 2 secs/channel for 8 seconds at 500ks
# Old pyfusion - 
#pyfusion.settings.SHOT_T_MIN=1.
#pyfusion.settings.SHOT_T_MAX=3.

dev_name= 'LHD' # 'H1Local'
shot_number=None
diag_name = ""

hold=0
corr=False
aphase=True
flips=[]
markersize=0.05
ref_index=None

#execfile('process_cmd_line_args.py')
import pyfusion.utils
exec(pyfusion.utils.process_cmd_line_args())

device = pyfusion.getDevice(dev_name)
if dev_name=='TestDevice':
    chan_name='testch1'
    shot_number=1000
elif (dev_name=='H1') or(dev_name=='H1Local'):
    chan_name='mirnov_1_8'
    shot_number=58123
elif dev_name=='HeliotronJ': 
    chan_name='MP1'
    shot_number=33911
elif dev_name=='LHD': 
    shot_list = [27233,36150,90091]
    diag_name='MP_SMALL'
    chan_name='HMP01'
    shot_number=27233
elif dev_name=='JT60U': 
    chan_name='PMP01'
    shot_number=46066
elif dev_name=='TJII': 
    chan_name='mirnov_5p_105'
    shot_number=18991
else:  # need something so process_cmd can work
    chan_name=''
    shot_number=0

exec(pyfusion.utils.process_cmd_line_args())

from pyfusion.data.signal_processing import smooth, smooth_n, cross_correl, analytic_phase

if pyfusion.VERBOSE>2: 
    print("Using device '%s', diag_name '%s', shot_number %d" %    
          (dev_name, diag_name, shot_number))

dsigs = device.acq.getdata(shot_number, diag_name)    

# now, do we do it in alpha order or in the order in the Device/*.py file?
# let's do alpha

#chans = sort(dsigs.signals.keys())
#lets do it in channel order in the new system
chans = [chn.name for chn in dsigs.channels]
print(chans)

nc = len(chans)   # was nc = len(chans)-1 until set first to be signal ch1


pl.rc('font', size=10) # this is a cheap trick - is there a better way?
#for i, ch in enumerate(chans):  # first is signal
for i in range(len(chans)):
    print(i),
#    ch1 = dsigs.signals[chans[i]]
#    ch2 = dsigs.signals[chans[i-1]]
    if i==0: 
        tb = dsigs.timebase
    else: 
        if ref_index == None: 
            ch1_index = i-1 
        else:
            ch1_index = ref_index

        ch1 = dsigs.signal.get_channel(ch1_index)
        if ch1_index in flips: ch1 = -ch1

    ch2 = dsigs.signal.get_channel(i)
    if i in flips: ch2 = -ch2

    if i == 0:
        axsig = pl.subplot(nc,1,i+1)  # top plot is signal for comparison
    elif i == 1:
        axcross = pl.subplot(nc,1,i+1, sharex=axsig)
    else:
        pl.subplot(nc,1,i+1, sharex=axsig, sharey=axcross)

        
    if i==0 or (corr==0 and aphase==0): 
        pl.plot(tb,ch2,'.',markersize=markersize, hold=hold)    
        pl.ylabel(chans[i])

    elif (corr):
        xc = cross_correl(ch1,ch2)
        xcslow = cross_correl(ch1,ch2,nsmooth=1000)
        pl.plot(tb,xc, '.', markersize=markersize,hold=hold)
        pl.plot(pl.xlim(),[0,0],'--r')  # zero line is the same for both, but will auto scale if we do it after the ylim
        pl.plot(tb,xcslow)
        
    elif (aphase):
        #pl.plot(smooth(analytic_phase(ch2)-analytic_phase(ch1),1500))
        # usually the line is hopeless as phase lock is lost - fine
        # dots below are much better
        # analytic phase has a two pi skip remover, but this si the diff of 2
        # trick: amalyptic phase seems to be  shorter by 2 (sometimes?)
        aph = mod(pi+analytic_phase(ch2)-analytic_phase(ch1),2*pi)-pi
        pl.plot(tb[0:len(aph)],aph,
                '.',markersize=markersize,hold=hold)

        pl.plot(pl.xlim(),[0,0],'--r')
        pl.ylim(-3.5,3.5)


    if (i>0) and (corr or aphase): pl.ylabel(chans[i] + '\n-' 
                                             + chans[ch1_index])
    pl.gcf().subplots_adjust(bottom=0.05, hspace=0.0001, top=1-.05)  # bug - hspace=0 leaves out some plots!
    pl.title("{dev_name}:{shot_number} {diag_name}"
          .format(dev_name=dev_name, diag_name=diag_name, 
                   shot_number=shot_number))

    if pl.isinteractive: pl.show()
## quick test:
##  time run examples/Boyds/check_polarity_flips.py diag_name='MP_3' pyfusion.settings.SHOT_T_MAX=1.1 pyfusion.settings.SHOT_T_MIN=1.0 aphase=True corr=0
#slow test
## time run examples/Boyds/check_polarity_flips.py diag_name='HMP' pyfusion.settings.SHOT_T_MAX=3 aphase=True corr=0 flip=1 markersize=0.01
