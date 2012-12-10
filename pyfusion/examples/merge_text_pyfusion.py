import pyfusion
from pyfusion.acquisition.read_text_pyfusion import read_text_pyfusion, merge_ds

from pyfusion.debug_ import debug_

debug=0
exception=Exception
file_list = [pyfusion.root_dir+'/acquisition/PF2_121206_54185_384_rms_1.dat.bz2']

import pyfusion.utils
exec(pyfusion.utils.process_cmd_line_args())

ds_list = read_text_pyfusion(file_list)
dd = merge_ds(ds_list)
