#run pyfusion/examples/small_65.py
import numpy as np
import pylab as pl

size_scale=30

cind = 0
colorset=('b,g,r,c,m,y,k,orange,purple,lightgreen,gray'.split(',')) # to be rotated

DA65MPH=DA('DA65MP2010HMPno612b5_M_N_fmax.npz',load=1)
DA65MPH.extract(locals())
pyfusion.config.set('Plots',"FT_Axis","[0.5,4,0,80000]")
"""
run -i pyfusion/examples/plot_specgram.py shot_number=65139 channel_number=1 NFFT=1024
pl.set_cmap(cm.gray_r)
pl.clim(-60,-0)
"""
sc_kw=dict(edgecolor='k',linewidth = 0.3)

for n in (-1,0,1):
    for m in (-2, -1,1,2):
        w =np.where((N==n) & (M==m) & (_binary_svs < 99) & bw(freq,frlow,frhigh))[0]
        if len(w) != 0:
            col = colorset[cind]
            pl.scatter(t_mid[w], freq[w], size_scale*amp[w], color=col, label='m,n=~{m},{n}'.format(m=m, n=n),**sc_kw)
            cind += 1
w=where((_binary_svs < 99) & bw(freq,frlow,frhigh)  & bw(MM, 0,130) & (NN== -4))[0]
col = colorset[cind] ; cind+=1
m = 1; n=0
pl.scatter(t_mid[w], freq[w], size_scale*amp[w], color=col, label='m,n=~{m},{n}'.format(m=m, n=n),**sc_kw)

DA65H=DA('DA65HMPno612b_M.npz',load=1)
DA65H.extract(locals())

w=where((_binary_svs < 99999) & bw(freq,frlow*0.8,frhigh*1.2)  & bw(MM, -60,-5))[0]
#col = colorset[cind] ; cind+=1
m = 1; n=0
pl.scatter(t_mid[w], freq[w], size_scale*amp[w], color=col, label='m,n=~{m},{n}'.format(m=m, n=n),**sc_kw)


pl.ylabel('frequency (kHz)')
pl.xlabel('time (s)')

pl.legend(loc=3)
pl.show()


