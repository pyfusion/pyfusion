"""
Test code for pyfusion
"""

import unittest, random

import pyfusion

def randstr(string_length):
    return ''.join([random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for x in xrange(string_length)])

class TestRandStr(unittest.TestCase):
    def testRandStr(self):
        str_length = random.randint(1,10)
        rand_str = randstr(str_length)
        assert len(rand_str) == str_length

class TestShot(unittest.TestCase):
    
    def testShotHasCorrectShotNumber(self):
        shot_number = random.randint(1,10)
        shot = pyfusion.Shot(shot_number)
        assert shot.shot == shot_number

class TestDevice(unittest.TestCase):
    
    def testSetDevice(self):
        device_name = randstr(random.randint(1,10))

        pyfusion.set_device(device_name)
        device = pyfusion.Device()
        assert device.name == device_name

if __name__ == "__main__":
    unittest.main()

