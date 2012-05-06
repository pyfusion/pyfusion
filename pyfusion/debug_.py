def debug_(debug,level=1,key=None,msg=''):
    """ Nice debug function, breaks to debugger if debug>level, or if
    key is asubstring of the string value in debug.  This way, one
    debug input can control several breakpoints, without too much
    recoding.  Works interactively with python and/or with iptyhon.

    Once a possible debug point is reasonably OK, its level can be
    raised, (level=3 etc) so that it is still accessible, but only at
    high debug levels, or if specifically targeted by pyfusion.DEBUG
    (as a string) Simple calls can be like debug_(debug,3) - where the
    3 reduces the priority of this relative to other calls that share
    the same debug parameter.  Once debugged, leave the call in, but
    make it specific with key='something' - then export
    PYFUSION_DEBUG='something,local_access' and it (or another call
    tagged with 'key='local_access') will be triggered.  msg = allows
    a message to be given - if the key is long enough, then there is
    no need for a msg, and key will be used instead.


    Developer's notes: Calls from unexpected situations (which have
    fixups such as try catch, can be set at low levels (such as 1),
    with a key that is long, and unlikely to match another.  THis way, if DEBUG=0,
    the fixup will be used, and if DEBUG=1, the pdb will be called.

    Note that as PYFUSION_DEBUG can be a string or an int, there is a try/except
    after reading in from the enviroment.


    Further explanation:
    What does this mean?  Say there are three possible calls to debug
    in a piece of code where the debug argument is passed in at one
    point only.  Then _debug(debug,3) will break out if debug is very
    high, whereas debug_(debug) will more easily break out.

    key is a string which allows string values of debug to selectively 
    trigger breakout:

    e.g key='lookup' and debug='lookup,open' then execution breaks
    """
    import warnings
    if type(debug) == type('abc'):
        if key.find(debug) < 0: return            
    
    elif debug<level: return

    try:
        """
        # pydbgr is nice, but only works once - then debug is ignored
        print('try to import pydbgr')
        from pydbgr.api import debug
        'debugging, '+ msg + ' in correct frame,  c to continue '        
        print('execute debug()')
        debug()

    except ImportError:
        # pydb is nice, but overwrites the history file.
        # could import readline, and save history in a backup UNLESS it 
        # is < 50 or so
        # 
        import pydb
        pydb.set_trace(['up'])
        'debugging, '+ msg + ' in correct frame,  c to continue '        
    except ImportError:
    """
        from sys import _getframe
        frame = _getframe()
        print(frame.f_lineno,frame.f_code)
        frame = _getframe().f_back
        print(frame.f_lineno,frame.f_code)
        from ipdb import set_trace

        if msg =='' and key !=None: msg = key # use key if no msg
        print('debugging, '+ msg)
        set_trace(_getframe().f_back)
        ' use up to get to frame, or c to continue '
    except ImportError:
        warnings.warn('error importing ipdb: try pdb instead')
        from pdb import set_trace
        set_trace()
        'debugging '+ msg + ' use up to get to frame, or c to continue '
    except ImportError:
        print('failed importing debugger pdb')

