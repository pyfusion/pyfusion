def debug_(debug,level=1,key=None,msg=''):
    """ Nice debug function, breaks to debugger if debug>level, or if
    key is asubstring of the string value in debug.  This way, one
    debug input can control several breakpoints, without too much
    recoding.  Once a possible dedbug point is reasonably OK, its
    level can be raised, so that it is still accessible, but only at
    high debug levels.  Most calls can be like debug_(debug,3) - where
    the 3 reduces the priority of this relative to other calls that
    share the same debug parameter.

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

