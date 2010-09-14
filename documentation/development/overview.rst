Pyfusion Development
====================

-----------------
Design principles
-----------------

Documentation
-------------

Documentation is maintained in the code repository. An online version is kept up to date `here http://h1nf.anu.edu.au/collaborate/pyfusion/docs/`_


Test-driven design (TDD)
------------------------


Distributed source code
-----------------------


------------------------
Developing with pyfusion
------------------------

Documentation
-------------

* use sphinx
* built docs not stored in repository

Tests
-----
* use nosetests

* running nosetest pyfusion should be *very* fast. The idea behind regular testing is that the tests should be so fast that you don't hesitate to run the test. Any test which requires significant computation or hard disk / network access should be disabled by default. Using $HOME/.pyfusion/tests.cfg you can enable any of these tests when you need them.
