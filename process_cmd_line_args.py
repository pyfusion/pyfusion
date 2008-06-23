"""
This is code to be "inlined" to allow python statments to be passed
 from the command line.  Simple version unconditionally executes.
 Better version would check for the existence of the LHS of an assignmment
 statement.
 Usage: execfile("process_cmd_line_args.py")
"""
import sys
# override the defaults set before execfile'ing' this code
if pyfusion.settings.VERBOSE>2: print ('%d args found') % (len(sys.argv))
for i in range(1,len(sys.argv)):
    print('executing %s') % sys.argv[i]
    exec(sys.argv[i])
