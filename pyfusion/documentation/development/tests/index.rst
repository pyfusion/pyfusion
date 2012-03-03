==============
Pyfusion tests
==============

e.g.
limited tests - naming a test in a file
nosetests pyfusion/acquisition/MDSPlus/tests.py:CheckH1ConfigSection

generated tests
nosetests pyfusion/test/generated_tests.py:TestSQLCheckMDSPlusH1Connection

don't supress stdout on tests that pass
nosetests -s 

nosetests -s pyfusion/test/generated_tests.py:TestSQLCheckDataHistory

.. module:: pyfusion.test.tests

.. module:: pyfusion.devices.tests

