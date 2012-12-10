import pyfusion
from pyfusion.acquisition.process_chirps import process_chirps

Ms = None
Ns = [2]
shots = [54185]

# the frequency deviation in kHz allowed before more is considered different
maxd=5

# minimum run length
minlen = 3

plt=True

debug=0

process_chirps(dd, shots=shots, Ns=Ns, Ms=Ms, maxd=maxd, minlen=minlen, plot=plt, debug=debug) 
