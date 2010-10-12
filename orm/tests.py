from pyfusion.test.tests import BasePyfusionTestCase

class TestORM(BasePyfusionTestCase):
    def test_orm(self):
        from pyfusion import orm

TestORM.sql = True

