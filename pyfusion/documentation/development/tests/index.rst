==============
Pyfusion tests
==============

e.g.
limited tests - naming a test in a file
nosetests pyfusion/acquisition/MDSPlus/tests.py:CheckH1ConfigSection

generated tests
nosetests pyfusion/test/generated_tests.py:TestSQLCheckMDSPlusH1Connection

don't suppress stdout on tests that pass
nosetests -s pyfusion

nosetests -s pyfusion/test/generated_tests.py:TestSQLCheckDataHistory

mdsplus tests:
nosetests -vs pyfusion/acquisition/MDSPlus/tests.py

avoid net access:
nosetests -a '!net' pyfusion

needs mdsip service to be running on 8000 with copy of test_tree
included here, and h1data shot 58123 in the path
Might be good to define a port separately for test_tree, so that the
unprivileged user can set it up (8000 is likely to be already used by
an MDSPlus server owned by the system)

test method:  (to ensure a clean environment)
# clone a repository if required, and cd to the pyfusion directory
if [ -f ../pyfusion/test/tests.py ]; then echo OK ; else echo not a pyfusion directory; fi
export PYTHONPATH=`pwd`/..
export PYFUSION_CONFIG_FILE=`pwd`/`/bin/ls pyfusion.cfg`
nosetests -a '!net'

The Mar 4 version executes with 8/9 errors out of 256 (on Boyds Ubuntu)
nosetests -v 2>&1|egrep 'ERROR:|FAIL|Ran'
ERROR: test_thick_client_access (pyfusion.acquisition.MDSPlus.tests.TestRefactoredMDSThick)
TreeException: %TREE-E-TreeFAILURE, Operation NOT successful
ERROR: test_thin_client_access (pyfusion.acquisition.MDSPlus.tests.TestRefactoredMDSThin)
MdsException: %TREE-E-TreeFAILURE, Operation NOT successful
ERROR: test_device (pyfusion.devices.LHD.tests.CheckLHDDevice)
ERROR: pyfusion.devices.tests.TestDeviceGetdata.test_device_getdata_single_shot
ERROR: pyfusion.devices.tests.TestDeviceGetdata.test_device_getdatat_multishot
ERROR: test_orm_manager (pyfusion.test.generated_tests.TestNoSQLCheckORMManager)
ERROR: test_device_getdatat_multishot (pyfusion.test.generated_tests.TestNoSQLTestDeviceGetdata)
ERROR: test_manager_reg (pyfusion.test.generated_tests.TestSQLCheckORMManager)
ERROR: test_orm_manager (pyfusion.test.generated_tests.TestSQLCheckORMManager)
Ran 265 tests in 13.117s
FAILED (errors=8 or 9: test_device_getdatat_multishot sometimes passes)

3 of these would pass in the right environment
TestRefactoredMDSThick, TestRefactoredMDSThin, CheckLHDDevice





.. module:: pyfusion.test.tests

.. module:: pyfusion.devices.tests

