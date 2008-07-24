"""
This is code to be "inlined" to allow python statments to be passed
 from the command line.  Simple version unconditionally executes.
 Better version would check for the existence of the LHS of an assignmment
 statement.
 Usage: execfile("process_cmd_line_args.py")
"""
import sys as _sys
# override the defaults that have been set before execfile'ing' this code
if pyfusion.settings.VERBOSE>2: print ('%d args found') % (len(_sys.argv))
for _i in range(1,len(_sys.argv)):
    _expr = _sys.argv[_i]
    print('executing %s') % _expr
    _words=_expr.split('=')
    _firstw=_words[0]
    _lhs=_firstw.strip()
    try:
        exec(_lhs)
        exec(_expr)
    except Exception, inst:
        print("##########Target %s non-existent!#########") % _lhs 
        _user_locals=[]
        _loc_dict=locals().copy() # need to save, as the size changes
        for v in _loc_dict:
            if v.find('_')!=0: _user_locals.append(v)
        print '#########use one of ', _user_locals
        if pyfusion.settings.VERBOSE>0:
            print inst
            raise inst
