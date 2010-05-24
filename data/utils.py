from numpy import fft, conjugate, array, mean, arange, searchsorted, argsort, pi

def cps(a,b):
    return fft.fft(a)*conjugate(fft.fft(b))

def peak_freq(signal,timebase,minfreq=0,maxfreq=1.e18):
    """
    TODO: old code: needs review
    this function only has a basic unittest to make sure it returns
    the correct freq in a simple case.
    """
    timebase = array(timebase)
    sig_fft = fft.fft(signal)
    sample_time = float(mean(timebase[1:]-timebase[:-1]))
    fft_freqs = (1./sample_time)*arange(len(sig_fft)).astype(float)/(len(sig_fft)-1)
    # only show up to nyquist freq
    new_len = len(sig_fft)/2
    sig_fft = sig_fft[:new_len]
    fft_freqs = fft_freqs[:new_len]
    [minfreq_elmt,maxfreq_elmt] = searchsorted(fft_freqs,[minfreq,maxfreq])
    sig_fft = sig_fft[minfreq_elmt:maxfreq_elmt]
    fft_freqs = fft_freqs[minfreq_elmt:maxfreq_elmt]
    
    peak_elmt = (argsort(abs(sig_fft)))[-1]
    return fft_freqs[peak_elmt]

def remap_periodic(input_array, min_val, period = 2*pi):
    while len(input_array[input_array<min_val]) > 0:
        input_array[input_array<min_val] += period
    while len(input_array[input_array>=min_val+period]) > 0:
        input_array[input_array>=min_val+period] -= period
    return input_array

def list2bin(input_list):
    # we explicitly cast to int(), as numpy's integer type clashes with sqlalchemy
    return int(sum(2**array(input_list)))

def bin2list(input_value):
    output_list = []
    bin_index_str = bin(input_value)[2:][::-1]
    for ind,i in enumerate(bin_index_str):
        if i == '1':
            output_list.append(ind)
    return output_list
