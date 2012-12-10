.. _tut-datamining:

**************************************
Example: MHD Data mining with pyfusion
**************************************

Here we show a method for finding classes of coherent fluctuations from many multi-channel timeseries signals (see Pretty and Blackwell paper). 

It is implement on LHD in the following example, using text files for
intermediate preprocessed data.  Currently this is faster than using a
database for this stage by about one order.

*******************************************************
using text files and a dictionary instead of a database
*******************************************************

In addition to the speedd advantage, the example below stores 
data in a form very convenient for improvising analysis.  The
file storage is in a dictionary of arrays, in precision chosen to
optimise accuracy and storage.  The dictionary is simply converted
into individual variables in total, or for a subset of the data
selected by an arbitrary where() statement.

The dictionary can remain resident so that the data can be easily
refreshed or re-selected whith different criteria.

# direct use of the dictionary
pl.plot(dd['t_mid'],dd['freq'])  # standard pylab function

sp(dd,t_mid,freq,amp,a12)   # scatter plot as above, but amplitude is
                            #color, and a12 is size

# selecting high power (>1MW) fast downchirps with N=2, and plotting
w = np.where( (N == 2) & (dw_pdt < -1000) & (Pfract>0.8) & (dfdt < -4) )[0]
sp(dd,t_mid,freq,amp,a12, ind=w)


*************************************
basic scripts to preprocess and merge
*************************************
# change to the directory containing the top pyfusion directory then

export PYTHONPATH=$PYTHONPATH:`pwd`

# preprocess to get flucstructs into a text file
# note - this is run as a linux command - can also run under python
pyfusion/examples/prepfs_range.py --shot_range=[54185] 

#then merge the preprocessed data (set filename=<myfile> to get your data from above)
ipython --pylab
run pyfusion/examples/merge_text_pyfusion.py
run -i pyfusion/examples/merge_basic_diagnostics.py  # the -i keeps dd resident

# save the datafile here if you like
# savez.compressed('dd_file',dd=dd)  # savez('dd_file',dd=dd) # for old numpy - much larger
run -i pyfusion/examples/new_mode_identify_script.py
# once you have a reasonable mode identification (by adjusting threshold, and mode descriptions)
run -i pyfusion/examples/process_chirps

# example query
