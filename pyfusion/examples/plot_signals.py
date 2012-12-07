import pyfusion as pf

dev_name = "LHD"
diag_name = 'MPflip5'
shot_number=27233

import pyfusion.utils
exec(pyfusion.utils.process_cmd_line_args())

device = pf.getDevice(dev_name)

data=device.acq.getdata(shot_number,diag_name)
data.plot_signals()


