"""
w=where(array(sd)<10)[0]
for ii in decimate(w,limit=2000): pl.plot(dd["phases"][ii],'k',linewidth=0.02)
mode.plot()

dd['N']=-1+0*dd["shot"].copy()

"""
import pylab as pl
import sys

from numpy import intersect1d, pi
from numpy import loadtxt
import numpy as np

# This simple strategy works when the number is near zero +- 2Npi,
# which is true for calculating the deviation from the cluster centre.
def twopi(x):
    return ((pi+np.array(x)) % (2*pi) -pi)

global modelist
modelist=[]
shot_list = []

def askif(message, quiet=0):
    """ give messge, ask if continue (if quiet=0) or go on 
         anyway (quiet-1)
    """
    if quiet == 0: suffix =  " Continue?(y/N) "
    else: suffix = "continuing, set quiet=0 to stop..."
    if quiet==0: 
        ans = raw_input("Warning: {0}: {1}".format(message, suffix))
        if len(ans) ==0 or ans[0].lower() != 'y':
            raise LookupError(message)

class Mode():
    global modelist
    def __init__(self,name, N, NN, cc, csd, threshold=None, shot_list=[]):
        self.name = name
        self.N = N
        self.NN = NN
        self.cc = np.array(cc)#-np.pi
        self.csd = csd
        if threshold == None: threshold = 1
        self.threshold = threshold
        self.shot_list = shot_list
        leng = len(self.cc)
        if np.sum(self.cc)>0: Nest = np.sum(twopi(np.array(self.cc)-2)+2)
        else: Nest = np.sum(twopi(np.array(self.cc)+2)-2)

        Nest = float(leng+1)/leng/(2*np.pi) * Nest
        self.comment = self.name+",<N>~{0:.1f}".format(Nest)
        modelist.append(self)

    def store(self, dd, threshold=None,Nval=None,NNval=None,shot_list=None,quiet=0):
        """ stoe coars and fine mode (N, NN) numbers according to a threshold std and an optional shot_list.  If not specified, the internal shot_list is used.
        """
        if shot_list == None: shot_list = self.shot_list
        if threshold == None: threshold=self.threshold
        else: self.threshold=threshold  # save the last manually set.

        if Nval==None: Nval = self.N
        if NNval==None: NNval = self.NN
        if NNval in np.unique(dd['NN']): 
            askif('NNval {0} already used'.format(NNval),quiet=quiet)

        if not(hasattr(dd['phases'],'std')):
            askif('convert phases to nd.array?',quiet=quiet)
            dd['phases'] = np.array(dd['phases'].tolist())

        sd = self.std(dd['phases'])
        w = np.where(sd<threshold)[0]

        # normally apply to all shots, but can restrict to a particular
        # range of shots - e.g. dead MP1 for shot 54186 etc.
        if shot_list !=None:
            where_in_shot = []
            for sht in shot_list:
                ws = where(dd['shot'][w] == sht)[0]
                where_in_shot.extend(w[ws])
            # this unique should not be required, but if the above logic
            # is changed, it might
            w = np.unique(where_in_shot)    

        if len(w) == 0: 
            print('threshold {th:.2g} is too low for phases: '
                  'minimum std for {m} is {sd:.1f}'
                  .format(th=threshold, m=self.name, sd=np.min(sd)))
            return()

        w_already = np.where(dd['NN'][w]>=0)[0]
        if len(w_already)>0:
            (cnts,bins) = np.histogram(dd['NN'][w], arange(-0.5,1.5+max(dd['NN'][w]),1))
            amx = np.argsort(cnts)
            print("NN already set in {0}/{1} locations {2:.1f}% of all data"
                  .format(len(w_already), len(w),
                          100*len(w_already)/float(len(dd['shot']))))
            print("NN={0} is most frequent ({1} inst.)"
                  .format(amx[-1],cnts[amx[-1]]))
            fract = len(w_already)/float(len(w))
            if fract>0.2: askif("{0:.1f}% already set?".
                                format(fract*100),quiet=quiet)

        dd['NN'][w]=NNval
        dd['N'][w]=Nval
        print("set {s:.1f}%, total set is now {t:.1f}%".
              format(s=100*float(len(w))/len(dd['shot']),
                     t=100*float(len(where(dd['N']>=0)[0]))/len(dd['shot'])
                     ))
           
    def plot(self, axes=None, label=None, suptitle=None, **kwargs):
        if suptitle==None:
            pl.suptitle("{0}, cc={1} sd={2} ".
                        format(self.name,self.cc,self.csd))               

        xd = arange(5)
        #pl.plot(xd, self.cc, label=self.name, **kwargs)
        if axes != None: ax = axes
        else: ax=pl.gca()
        if label == None: label =self.name
        ax.plot(xd, self.cc,label=label, **kwargs)
        current_color = ax.get_lines()[-1].get_color()
        ax.errorbar(xd, self.cc, self.csd, ecolor=current_color, color=current_color)
        ax.set_xlim(xd[0]-0.1,xd[-1]+.1)
    def one_rms(self, phases):
        """ Return the standard deviation normalised to the cluster sds
            a point right on the edge of each sd would return 1
        """
        return(np.sqrt(np.average((twopi(self.cc-phases)/self.csd)**2)))
    def std(self, phase_array):
        """ Return the standard deviation normalised to the cluster sds
            a point right on the edge of each sd would return 1
        """
        if not(hasattr(phase_array, 'std')):
            print('make phase_array into an np arry to speed up 100x')
            phase_array = np.array(phase_array.tolist())

        cc = np.tile(self.cc, (shape(phase_array)[0],1))
        csd = np.tile(self.csd, (shape(phase_array)[0],1))
        sq = (twopi(phase_array-cc)/csd)**2
        return(sqrt(average(sq,1)))


# manually enter the mean and sd for the modes, called by color
# n=1
blue=Mode('N=1', N=1, NN=100, cc = [1.020, 1.488, 1.348, -0.080, 0.989], csd= [0.4, 0.2, 0.3, 0.20, 0.2 ])
#blue.csd= [0.077, 0.016, 0.048, 0.020, 0.008 ]


blue1=Mode('N=1,46747', N=1, NN=101, cc = [0.6, 1.7, 0.8, 0.2, 0.989], csd= [0.4, 0.2, 0.3, 0.20, 0.2 ])
# obscured by other noise....


blue2=Mode('N=1,or 0?', N=1, NN=102, cc = [1.0, -0.65, 1.84, 1.8, 1.95], csd= [0.2, 0.2, 0.3, 0.20, 0.2 ])
# very clear on 38100


blue3=Mode('N=1 - broad', N=1, NN=103, cc =[0.3, 0.25, 1.3, 2.0, 1.8], csd=[ 0.48, 0.5, 0.5, 0.5, 0.42])

blue4=Mode('N=1 - residual', N=1, NN=104, cc =[1.2, 0.86, 1.8, -0.1, 1.0], csd=[ 0.2, 0.2, 0.3, 0.3, 0.3])


# n=0
lblue=Mode('N=0', N=0, NN=50, cc =[-1.146, -1.094, 0.608, 0.880, 0.164], csd=[ 0.48, 0.33, 0.34, 0.33, 0.42])
# mainly low 27s
#lblue.csd=[ 0.048, 0.033, 0.034, 0.033, 0.042]


lbluef=Mode('N=0 - fract', N=0, NN=51, cc =[0.3, -.75, 0.608, 0.880, 0.45], csd=[ 0.48, 0.33, 0.34, 0.33, 0.42])

lbluef1=Mode('N=0 - fract1', N=0, NN=52, cc =[-2.1, -1.1, 0.5, 1.06, 0.17], csd=[ 0.3, 0.33, 0.34, 0.33, 0.25])



# n=2
red=Mode('N=2', N=2, NN=200, cc =[2.902, 2.217, 2.823, 1.021, 2.157], csd= [0.2, 0.2, 0.2, 0.3, 0.2 ])
#red.csd= [0.023, 0.006, 0.028, 0.025, 0.007 ]
# saved as 200  with sumsd2 <10


redlow=Mode('N=2, LF', N=2, NN=201, cc =[2., 2.4, 2.0, 1.5, 2.2], csd= [0.2, 0.2, 0.2, 0.3, 0.2 ])
#red.csd= [0.023, 0.006, 0.028, 0.025, 0.007 ]
# saved 201 with sumsd2 <10 


red60=Mode('N=2, 60k', N=2, NN=202, cc =[2.3, 2.4, 1.7, 2.1, 1.7], csd= [0.3, 0.2, 0.2, 0.2, 0.2 ])
#red.csd= [0.023, 0.006, 0.028, 0.025, 0.007 ]
# saved NN=202 sumsd2<10  - -model is 47634 (3928 overlap with  redlow)

red60MP1 = Mode('N=2, 60k MP1', N=2, NN=204, cc =[0, 2.4, 1.7, 2.1, 1.7], csd= [5, 0.2, 0.2, 0.2, 0.2 ],shot_list=[54184,54185,54194,54195,54196,54197,54198])
# ref60, but allow for MP1 to be dead (large csd)

weird=Mode('W1', N=2, NN=203, cc =[2.5, 0.3, -1.4, 0.7, 2.2], csd =[0.5, 0.5, 0.3, 0.3, .25])
# too rare to worry


ind = None
mode=redlow
threshold=None

import pyfusion.utils
exec(pyfusion.utils.process_cmd_line_args())

if ind == None: ind = arange(len(dd['shot']))
phases = dd["phases"][ind]
#phases = np.array(phases.tolist())

sd = mode.std(phases)

for mname in 'N,NN,M,MM'.split(','):
    if not(dd.has_key(mname)):
        dd[mname]=-np.ones(len(dd['shot']),dtype=int16)

for mode in modelist:
    mode.store(dd, threshold)


"""
29th Nov method- obsolete

sd = []
sdlb = []
sdred = []

sh = []
amp = []
ind = []
#arr=loadtxt('MP_27233_cf_syama.txt',skiprows=4)
# arr=loadtxt('MP512all.txt',skiprows=4)
# read in the delta phases from the aggregated pyfusion database
# and build up a list of flucstrucs and the sum of squares relative to the
# three modes.
#fsfile='MP512all.txt'
#fsfile='PF2_120229_MP_27233_27233_1_256.dat'

## let plot_text_pyfusion choose the file and skip
#fsfile='PF2_120229_MP_50633_50633_1_256.dat'
#skip=4
hold=1
dt=140e-6
ind = None
mode=redlow

import pyfusion.utils
exec(pyfusion.utils.process_cmd_line_args())
#run -i ./examples/plot_text_pyfusion.py filename='MP_27233_cf_syama.txt' skip=4
#run -i ./examples/plot_text_pyfusion.py filename=fsfile skip=skip
#sys.argv = ['filename='+fsfile, 'skip='+str(skip)]

#execfile("./examples/plot_text_pyfusion.py") 

if ind == None: ind = arange(len(dd['shot']))
phases = dd["phases"][ind]

for i in ind:
    if (i % 100000) == 0: print(i),
    sd.append(sum((twopi(dd["phases"][i]-mode.cc)/mode.csd)**2))
    sh.append(dd["shot"][i])
"""
"""
exec(pyfusion.utils.process_cmd_line_args())

# find the indices of modes within a  short distance from the classification
neq0 = (array(sdlb) < 1).nonzero()[0]
neq1 = (array(sd) < 1).nonzero()[0]
neq2 = (array(sdred) < 1).nonzero()[0]

# do a crude plout by color=mode only
msize=40
print(hold)
pl.scatter(dt+ds['t_mid'][neq0],fsc*ds['freq'][neq0],hold=hold,label='N=0',c='cyan',s=msize)
pl.scatter(dt+ds['t_mid'][neq1],fsc*ds['freq'][neq1],label='N=1',s=msize)
pl.scatter(dt+ds['t_mid'][neq2],fsc*ds['freq'][neq2],label='N=2',c='red',s=msize)

pl.legend()
pl.suptitle(filename)
#for x in array([ds['t_mid'][neq0],1e3*ds['freq'][neq0],neq0]).T.tolist(): text(x[0],x[1],int(x[2])) 
# inds=[5106,5302,5489,1228,1233,1236,478,657,1260] ; average(arr[inds,8:],0); arr[inds,8:]

"""
