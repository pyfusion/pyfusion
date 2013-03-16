import os
def process_cmd_line_args():
    try:
        this_file = os.path.abspath( __file__ )
        this_dir = os.path.split(this_file)[0]
        #print('this_dir',this_dir)
        return(open(this_dir+os.sep+'process_cmd_line_args_code.py', "rb").read())
    except:
        print('process_cmd_line is defaulting to some likely spots')
        try: 
            return(open('/home/blackwell/python/process_cmd_line_args.py', "rb").read())
        except:
            return(open('/home/bdb112/python/process_cmd_line_args.py', "rb").read())
