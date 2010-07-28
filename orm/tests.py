"""this directory was getting ignored by git pull when tehre was only __init__.py, let's see if this helps"""

from pyfusion.test.tests import BasePyfusionTestCase

class TestORM(BasePyfusionTestCase):
    def test_orm(self):
        """ this is just to see if git pull will work properly..."""
        j=0
        for i in range(3):
            j+=1
