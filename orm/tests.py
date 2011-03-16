from pyfusion.test.tests import PfTestBase

class TestORM(PfTestBase):
    def test_orm(self):
        from pyfusion import orm

TestORM.sql = True

