def process_cmd_line_args():
    # sloppy: need to at least put a test for existance here - or use this_dir
    try:
        return(open('/home/blackwell/python/process_cmd_line_args.py', "rb").read())
    except:
        return(open('/home/bdb112/python/process_cmd_line_args.py', "rb").read())
