from numpy import fft, conjugate, array, mean, arange, searchsorted, argsort, pi

def cps(a,b):
    return fft.fft(a)*conjugate(fft.fft(b))

def peak_freq(signal,timebase,minfreq=0,maxfreq=1.e18):
    """
    TODO: old code: needs review
    DOESN'T HAVE UNIT TEST
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

