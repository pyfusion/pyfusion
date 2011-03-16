import pyfusion
from pyfusion.test.tests import find_subclasses, PfTestBase, SQLTestCase, NoSQLTestCase

for test_class in find_subclasses(pyfusion, PfTestBase):
    print test_class
    globals()['TestSQL%s' %test_class.__name__] = type('TestSQL%s' %test_class.__name__, (test_class, SQLTestCase), {})
    globals()['TestSQL%s' %test_class.__name__].sql = True
    globals()['TestSQL%s' %test_class.__name__].generated = True
    globals()['TestNoSQL%s' %test_class.__name__] = type('TestNoSQL%s' %test_class.__name__, (test_class, NoSQLTestCase), {})
    globals()['TestNoSQL%s' %test_class.__name__].sql = False
    globals()['TestNoSQL%s' %test_class.__name__].generated = True
