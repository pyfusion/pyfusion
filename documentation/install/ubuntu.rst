.. _install-ubuntu:

###################################
Installing pyfusion on Ubuntu Linux
###################################

:Release: |version|
:Date: |today|


This procedure has been tested for Ubuntu 10.04 LTS 64bit and assumes you have sudo privileges. 

Installing pyfusion
-------------------

At present, the recommended method of installing pyfusion is from the code repository. You'll need a directory in your PYTHONPATH to install to, eg::
   
   mkdir -p $HOME/code/python
   echo "export PYTHONPATH=\$PYTHONPATH:\$HOME/code/python" >> $HOME/.bashrc
   source $HOME/.bashrc

Install the `git <http://git-scm.com/>`_ distributed version control system::

	sudo apt-get install git-core

Make a clone of the pyfusion repository in your python path::

     cd $HOME/code/python
     git clone http://github.com/dpretty/pyfusion.git

Until version 1.0 of the code, we'll be using the dev branch, so you need to check it out::

     cd pyfusion
     git checkout -b dev origin/dev
 
