
import pyfusion
from pyfusion.data_acq.TestSignals.TestSignals import SingleFreqChannel
from numpy import pi, array

sample_freq = 1000000.
n_samples = 10000

ch1 = SingleFreqChannel(name='testch1',amplitude = 0.80, frequency=30000, phase = 0, SNR=0.2, sample_frequency = sample_freq, n_samples = n_samples, envelope=None)
ch2 = SingleFreqChannel(name='testch2',amplitude = 0.72, frequency=30000, phase = 0.32*pi, SNR=0.43, sample_frequency = sample_freq, n_samples = n_samples, envelope=None)
ch3 = SingleFreqChannel(name='testch3',amplitude = 0.49, frequency=30000, phase = 0.47*pi, SNR=0.13, sample_frequency = sample_freq, n_samples = n_samples, envelope=None)
ch4 = SingleFreqChannel(name='testch4',amplitude = 0.93, frequency=30000, phase = 0.92*pi, SNR=0.62, sample_frequency = sample_freq, n_samples = n_samples, envelope=None)
ch5 = SingleFreqChannel(name='testch5',amplitude = 0.64, frequency=30000, phase = 1.42*pi, SNR=0.18, sample_frequency = sample_freq, n_samples = n_samples, envelope=None)

diag1 = pyfusion.Diagnostic(name='testdiag1')
for ch in [ch1, ch2, ch3, ch4, ch5]:
    diag1.add_channel(ch)

f2=40000
env=[array([0,1000,3000,3100,6000,6100,6400,6500])/sample_freq,[0,1,1,0,0,1,1,0]] # one long one short
ch1e = SingleFreqChannel(name='testch1e',amplitude = 0.80, frequency=f2, phase = 0, SNR=1, sample_frequency = sample_freq, n_samples = n_samples, envelope=env)
ch2e = SingleFreqChannel(name='testch2e',amplitude = 0.72, frequency=f2, phase = 0.32*pi, SNR=2, sample_frequency = sample_freq, n_samples = n_samples, envelope=env)
ch3e = SingleFreqChannel(name='testch3e',amplitude = 0.49, frequency=f2, phase = 0.47*pi, SNR=4, sample_frequency = sample_freq, n_samples = n_samples, envelope=env)
ch4e = SingleFreqChannel(name='testch4e',amplitude = 0.93, frequency=f2, phase = 0.92*pi, SNR=1, sample_frequency = sample_freq, n_samples = n_samples, envelope=env)
ch5e = SingleFreqChannel(name='testch5e',amplitude = 0.64, frequency=f2, phase = 1.42*pi, SNR=0.1, sample_frequency = sample_freq, n_samples = n_samples, envelope=env)

diag2 = pyfusion.Diagnostic(name='testdiag2')
for ch in [ch1e, ch2e, ch3e, ch4e, ch5e]:
    diag2.add_channel(ch)

class TestDevice(pyfusion.Device):
    def __init__(self):
        self.name = 'TestDevice'

TestDeviceInst = TestDevice()
