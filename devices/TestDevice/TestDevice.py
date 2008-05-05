
import pyfusion
from pyfusion.data_acq.TestSignals.TestSignals import SingleFreqChannel
from numpy import pi

sample_freq = 1000000.
n_samples = 10000

ch1 = SingleFreqChannel(name='testch1',amplitude = 0.80, frequency=30000, phase = 0, SNR=0.2, sample_frequency = sample_freq, n_samples = n_samples)
ch2 = SingleFreqChannel(name='testch2',amplitude = 0.72, frequency=30000, phase = 0.32*pi, SNR=0.43, sample_frequency = sample_freq, n_samples = n_samples)
ch3 = SingleFreqChannel(name='testch3',amplitude = 0.49, frequency=30000, phase = 0.47*pi, SNR=0.13, sample_frequency = sample_freq, n_samples = n_samples)
ch4 = SingleFreqChannel(name='testch4',amplitude = 0.93, frequency=30000, phase = 0.92*pi, SNR=0.62, sample_frequency = sample_freq, n_samples = n_samples)
ch5 = SingleFreqChannel(name='testch5',amplitude = 0.64, frequency=30000, phase = 1.42*pi, SNR=0.18, sample_frequency = sample_freq, n_samples = n_samples)

diag1 = pyfusion.Diagnostic(name='testdiag1')
for ch in [ch1, ch2, ch3, ch4, ch5]:
    diag1.add_channel(ch)

class TestDevice(pyfusion.Device):
    def __init__(self):
        self.name = 'TestDevice'

TestDeviceInst = TestDevice()
