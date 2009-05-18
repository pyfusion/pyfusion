"""Fake data acquisition used for testing pyfusion code."""

from pyfusion.acquisition.base import BaseAcquisition, BaseDataFetcher

class FakeDataAcquisition(BaseAcquisition):
    """Generate fake data for testing code."""
    pass


class SingleChannelSineDF(BaseDataFetcher):
    """Data fetcher for single channel sine wave."""
    def __init__(self, sample_rate=None, amplitude=None,
                 frequency=None, n_samples=None, **kwargs):
        super(SingleChannelSineDF, self).__init__(**kwargs)

    def fetch(self):
        from pyfusion.data.timeseries import SCTData
        return SCTData()
