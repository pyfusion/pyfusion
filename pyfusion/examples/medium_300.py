from DA_datamining import DA

DA300=DA('PF2_121206MPRMSv2_Par_fixModes_chirp_ff.npz',load=1)
dd=DA300.copy() 
DA300.extract(locals())
DA300.info()
