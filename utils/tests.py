"""Test code for test code."""

from pyfusion.test.tests import BasePyfusionTestCase


class TestPing(BasePyfusionTestCase):
    """Test the ping utility"""

    def testPing(self):
        from pyfusion.utils.net import ping



