import pyfusion
from pyfusion.acquisition.read_text_pyfusion import read_text_pyfusion, merge_ds
from glob import glob
import numpy as np
from pyfusion.debug_ import debug_

debug=0
target='^Shot .*'  # to allow searches for e.g. '^Shot .*'  or skip lines ==4
quiet=1
Append = False
exception=Exception
file_list = [pyfusion.root_dir+'/acquisition/PF2_121206_54185_384_rms_1.dat.bz2']

import pyfusion.utils
exec(pyfusion.utils.process_cmd_line_args())
if len(np.shape(file_list)) == 0: file_list=[file_list]


(ds_list, comment_list) = read_text_pyfusion(file_list, debug=debug, exception=exception, target=target)

if len(ds_list) == 0: raise LookupError('no files found for {f}'.format(f=file_list))

if Append:
    ds_list.append(dd)
    comment_list.extend(dd['comment'])
dd = merge_ds(ds_list, comment_list)
