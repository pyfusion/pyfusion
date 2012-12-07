#!/usr/bin/env python
""" job controller for preprocessing pyfusion data.  Replaces do_range script, so
that a nice argument form can be used, and eventually multi-processing.
"""
from warnings import warn


if __name__ == '__main__':

    try:
        from argparse import ArgumentParser, FileType
    except ImportError:   # may work better in early versions
        warn("can't find argparse - trying Ipython version instead")
        import IPython
        from IPython.external.argparse import ArgumentParser, FileType


    PARSER = ArgumentParser( description='job controller for preprocessing pyfusion data.: '+__doc__ )
    # note - default= for positional arg requires nargs = '?' or '*'
    PARSER.add_argument( 'output_path', metavar='output_path', help=' path to store output text files', default='.', nargs='1', type=str) # just 1 for now
    PARSER.add_argument( '--debug', type=int, default=1, 
                         help='debug level, > 1 will prevent exceptions being hidden')
    PARSER.add_argument( '--quiet', type=int, default=0, 
                         help='extra information' )
    PARSER.add_argument( '--height', type=int, default=None, 
                         help='height of display in inches' )
