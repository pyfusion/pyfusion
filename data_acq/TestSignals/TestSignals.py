"""
Test Signals
"""
import pyfusion
from sqlalchemy import Column, Numeric, ForeignKey, Integer, Float
from numpy import pi, sqrt, arange, sin
from numpy.random import standard_normal

class ProcessData:
    def load_channel(self, channel, shot):        
        if channel.__class__ == SingleFreqChannel:
            print channel.n_samples
            print channel.sample_frequency
            timebase = arange(channel.n_samples).astype(float)/float(channel.sample_frequency )
            print channel.amplitude
            print channel.frequency
            print channel.phase
            signal = channel.amplitude*sin(2.*pi*channel.frequency*timebase + channel.phase)
            noise_ampl = channel.amplitude/sqrt(channel.SNR)
            noise = noise_ampl*standard_normal(size=(channel.n_samples,))
            signal += noise
            output_MCT = pyfusion.MultiChannelTimeseries(timebase)
            output_MCT.add_channel(signal, channel.name)
            return output_MCT

        else:
            raise ValueError, 'Unknown Channel Class'

class SingleFreqChannel(pyfusion.Channel):
    __tablename__ = 'test_single_freq'
    __mapper_args__ = {'polymorphic_identity':'TestSignals'}
    id = Column('id', Integer, ForeignKey('channels.id'), primary_key=True)
    frequency = Column('frequency', Float)
    amplitude = Column('amplitude', Float)
    phase = Column('phase', Float)
    SNR = Column('SNR', Float)
    sample_frequency = Column('sample_frequency', Float)
    n_samples = Column('n_samples', Integer)

