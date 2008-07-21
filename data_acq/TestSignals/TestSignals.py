"""
Test Signals
"""
import pyfusion
from sqlalchemy import Column, Numeric, ForeignKey, Integer, Float, PickleType
from numpy import pi, sqrt, arange, sin, size, interp, mod
from numpy.random import standard_normal

class ProcessData:
    def load_channel(self, channel, shot):        
        if channel.__class__ == SingleFreqChannel:
            ch=channel # abbreviate
            if pyfusion.settings.VERBOSE>0:
                print "Samples=%d, SampFreq=%d" % (ch.n_samples,
                                                   ch.sample_frequency),
                print "Ampl=%.3g, freq=%.3g" % (ch.amplitude, ch.frequency),
                print "Phase = ", ch.phase
                print "Envelope=", ch.envelope
            timebase = arange(ch.n_samples).astype(float)/float(ch.sample_frequency )
            signal = ch.amplitude*sin(2.*pi*ch.frequency*timebase + ch.phase)
            if size(ch.envelope)>1: signal *= interp(timebase, ch.envelope[0], ch.envelope[1])
# SNR is defined in terms of power - tricky mod - reduces noise 
#     according to thousands digit - if 0, no effect, 1 10x smaller, 2 100 smaller
#     This allows a range of 1000 shots to have constant noise amplitude
            reduct = 10**mod(shot/1000,10)
            noise_ampl = ch.amplitude/sqrt(ch.SNR)/reduct
            noise = noise_ampl*standard_normal(size=(ch.n_samples,))
            signal += noise
            if (pyfusion.settings.VERBOSE>6):
                import pylab as pl
                print 'verbose=',pyfusion.settings.VERBOSE
                pl.plot(signal)
                pl.title(ch.name + ':'+str(shot))
                pl.show()
            output_MCT = pyfusion.MultiChannelTimeseries(timebase)
            output_MCT.add_channel(signal, ch.name)
            return output_MCT

        else:
            raise ValueError, 'Unknown Channel Class'

class SingleFreqChannel(pyfusion.Channel):
    __tablename__ = 'test_single_freq'
    __mapper_args__ = {'polymorphic_identity':'TestSignals'}
    id = Column('id', Integer, ForeignKey('channels.id'), primary_key=True)
    frequency = Column('frequency', Float)
    amplitude = Column('amplitude', Float)
    envelope = Column('envelope', PickleType)
    phase = Column('phase', Float)
    SNR = Column('SNR', Float)
    sample_frequency = Column('sample_frequency', Float)
    n_samples = Column('n_samples', Integer)

