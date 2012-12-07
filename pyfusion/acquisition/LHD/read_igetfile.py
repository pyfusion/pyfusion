from numpy import sin, cos, shape, average, array, max, abs, mod

""" ts=igetfile('cache/TS{0:06d}.dat.bz2',shot=36248)
    ts.plot() 
""" 

class igetfile():
    data = None
    vardict = {}
    shot = None
    filename = ""
    
    def __init__(self, filename=None, fileformat=None, shot=None, verbose=0, plot=False, hold=True):
        """ read in data, optionally plot (True gets default channel, N gets ch=N
        if filename contains a {, assume it is a format
        let get_basic_params deal with .bz2 files etc for now.
        """
        if filename == None or "{" in filename:
            self.shot = int(shot)
            if "{" in filename: self.filename = filename.format(self.shot)
            else: self.filename = fileformat.format(self.shot)
        else:
            self.filename = filename

        (self.data,self.vardict) = read_igetfile(filename=self.filename, 
                                                 verbose=0, plot=plot, hold=hold)
        if plot !=0: 
            if type(plot) == type(True):  self.plot()
            else: self.plot(ch=plot)

    def plot(self, hold=0, ch=None, tstart=None, tend=None, tstep=None, scl=None, navg=1, debug=1, axes=None, *args, **kwargs):
        """ Plot all the data items - can take a ling time.
        """
        import pylab as pl
        name=self.vardict['Name']
        dim=self.vardict['DimSize']
        nv=self.vardict['ValNo']
        nd=self.vardict['DimNo']
        if ch == None: 
            if name =='lhd_mse1':
                ch = 19
            elif name.lower() =='thomson':
                ch=3
            else:
                ch = 1

        if axes != None: ax = axes
        else: ax = pl.gca()

        ax.plot(hold=hold)
        
        linest = ['-',':','--','-.']
        print(shape(dim))
        if len(shape(dim))==0:
            for (p,name) in enumerate(self.vardict['ValName']):
                if ch==None or ch==(p+1):
                    ax.plot(self.data[:,0], self.data[:,p+1],
                            label="{0}:{1}".format(name, self.shot),
                            linestyle=linest[(p/8) % (len(linest))], 
                            *args, **kwargs)
                
        else:  # 2 dim plots
            # reshape into radial profiles
            data3D=self.data.reshape(dim[0],dim[1],nd+nv)
            if tstart == None: tstart=0
            if tend == None: tend=dim[0]/2
            if tstep == None: tstep=max([tend/50,1])  # reduce to 50 steps
            # check maximum to determine scaling
            if scl == None: scl = max(abs((data3D[:,:,ch+nd-1])/50))  # was /10
            if debug>0: 
                print("tstart=%.4g, tstep=%.4g, tend=%.4g, scl=%.4g))" % 
                      (tstart, tstep, tend, scl))
            # if more than 10 profiles, plot all in grey, then
            if (((tend-tstart)/tstep) > 10) and tstep>0: 
                for t in range(tstart,tend,tstep): 
                    xval = average(data3D[t:t+navg,:,nd-1],0)
                    ax.plot(xval, scl*t+average(data3D[t:t+navg,:,ch+nd-1],0),
                            color=0.8-(0.4/5)*mod(t-tstart,5)*array([1,1,1]))

            if navg>1: avg="avg%d" % (navg)
            else: avg = ''
            # plot every 5th one in colour

            for t in range(tstart,tend,tstep*5): 
                lab=avg+"%s:%.4g %s" % (self.vardict['ValName'][ch-1],data3D[t,0,0],self.vardict['DimUnit'][0])
                ax.plot(xval,scl*t+average(data3D[t:t+navg,:,ch+nd-1],0),
                        label=lab,*args, **kwargs)

        square_inches = (array(ax.get_figure().get_size_inches()).prod() /
                         array(ax.get_geometry()[0:2]).prod())
        if square_inches< 15: pl.rcParams['legend.fontsize']='small'
        if square_inches > 5: ax.legend()
        pl.title("%d:%s" % (self.vardict['ShotNo'],self.vardict['Name']))

def read_igetfile(filename=None, verbose=0, plot=True, hold=True, quiet=0):
    """ Read LHD data from igetfile
    Note that the plot option on this call is crude, compared to in igetfile
        pseudocode: 
           read file into a buffer
           find "[Parameters]"
           find "[data]"
           put brackets around lines with = sign and unquoted comma
           read stuff between
           read data into a rank 2 array

        ( This example creates it's own file-like object - not normally
        required - also note that we use \\n (double backslash.
        Finally, this test runs into a problem at the first line of data
        maybe new since 2.7?)

        >>> from StringIO import StringIO
        >>> data = ' \\n'.join(["%f, %f, %f" % (n/1e3, sin(n/1e3), cos(n/1e3)) for n in range(4)])
        >>> st=StringIO("#[Parameters]\\n# Name = 'mmw'\\nShotNo=50623\\n# Dimno=1 \\n " \
        + "# DimName = 'Time'\\n# DimSize = 2600\\n# DimUnit = 's'\\n# \\n" \
        + "# ValNo = 2\\n# ValName = 'nL()', 'nL()'\\n# ValUnit = 'e19m-2', 'e19m-2'\\n" \
        + "# [Comments]\\n#  \\n# [data]\\n" \
        + data+" \\n ")
        >>> read_igetfile(st)[0][2]
        array([ 0.002   ,  0.002   ,  0.999998])


    """
    from numpy import where, diff, loadtxt, array
    import time
    from StringIO import StringIO

    if filename == None: filename = '/home/bdb112/python/mmw@50623.dat'
    strt = time.time()
#    print(filename.readlines())
#    print('asd************8')
#    filename.seek(0)
#    return([1,2,3])
    try:  # this one is to catch missing files
        try:
            # loadtxt does auto decompression~ 3x slower than uncompressed on lenny
            # avoid breaking into token by using impossible delimiter
            # or just "\n" will do
            #   comments has to be a character - '\000' seems OK
            fbuff = loadtxt(filename, delimiter='\n', dtype='S',comments='~')
            # careful - loadtxt removes the \n, readlines doesn't
            reader='loadtxt'
        except:     
            if type(filename) == type('str'): fp=open(filename)
            else: fp=filename
            fp.seek(0)
            #print(fp.readlines())
            #return([1,2,3,4])
            fbuff=fp.readlines()
            reader='readlines'
    except Exception, info:
        if quiet>0: 
            pass
        else:
            raise(IOError,'finish me: {0}'.format(info))

    if verbose>0: print ("Used %s" % reader), 
    pinds = [st.upper().find("[PARAMETERS]") for st in fbuff ]
    pstarts = where(array(pinds)>-1)[0]   # where function only operates on arrays!
    cinds = [st.upper().find("[COMMENTS]") for st in fbuff ]
    cstarts = where(array(cinds)>-1)[0]   # where function only operates on arrays!
    dinds = [st.upper().find("[DATA]") for st in fbuff ]
    dstarts = where(array(dinds)>-1)[0]
    if verbose: print(", %d data lines found" % (len(dstarts))),

    trystart=0
    found=False
    from time import sleep
    while not(found) and trystart<len(pstarts):
        ValName = None
        vardict = {}
        parmlines = fbuff[pstarts[trystart]+1:cstarts[trystart]]
        parms = [line[2:].strip() for line in parmlines]
        for (p,parm) in enumerate(parms):
            if verbose>1: print(parm)
            if parm.find(',')>=0: parms[p] = '= ['.join(parm.split('=')) + ']'
            try:
                exec(parms[p],vardict)
            except SyntaxError:
                if parm.find(',')>0:
                    print('bad syntax {%s} try to reparse' % (parms[p])),
                    (lhs,rhs) = parm.split('=')
                    parsesyms = rhs.replace("'","").split(",")
                    reparse = (lhs+"=["
                               + ','.join(["'%s'" % (sym.strip()) for sym in parsesyms])
                               + ']')
                    try:
                        exec(reparse,vardict)                               
                        print(': recovered {%s}' % reparse)
                    except:
                        print('Error executing reparsed [%s]' % (reparse))

            except:
                print('Error executing [%s]' % (parms[p]))
               
#        if ValName != None:
        if vardict.has_key('ValName'):
            if verbose: print('Found %s ' % (ValName))
            found = True
            
    if not(found): 
        raise LookupError, str(' data not in %s ' % (filename))


# StringIO allows a string to be treated like a file.
# could alternatively pass a skiprows to loadtxt - but this avoids re-reading file

# the '\n' is needed when the buffer comes from loadtxt.  I hope the next loadtxt doesn't mind.
    sio = StringIO('\n'.join(fbuff[dstarts[trystart]+1:]))
    ## this is an attempt to debug the test code - 
    """ x=sio.readlines()
    print([ord(c) for c in x[0]])
    print(x[0])
    print(x[1])
    sio.seek(0)
    return(sio.readlines())
    """
    arr=loadtxt(sio,delimiter=',')
    if plot: 
        import pylab as pl
        ax.plot(arr[:,0],arr[:,1],'.',markersize=1, hold=hold)
    return(arr,vardict)
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
"""
#self=igetfile(filename='/home/bdb112/LHD/TS099000.dat')
import os
import pylab as pl
#print(os.path.split(???__str__.split("'")[3])[0]+'/TS099000.dat')
filename='/home/bdb112/pyfusion/pyfusion/acquisition/LHD/TS090000.dat.bz2'
self=igetfile(filename)
dim=self.vardict['DimSize']
nv=self.vardict['ValNo']
nd=self.vardict['DimNo']
data3D=self.data.reshape(dim[0],dim[1],nd+nv)
for t in range(0,dim[0],5): plot(average(data3D[t:t+10,:,4],0))
#for (t,dat) in enumerate(data3D[:,:]): print(dat[0])
tend=dim[0]/2
for t in range(0,tend,5): pl.plot(10*t+average(data3D[t:t+10,:,4],0),color=0.8*array([1,1,1]))

for t in range(0,tend,25): pl.plot(10*t+average(data3D[t:t+10,:,4],0),label=("%d ms" % (data3D[t,0,0])))

pl.legend()

"""

