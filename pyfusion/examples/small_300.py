from DA_datamining import DA

DAfilename='300_small.npz'
DA300=DA(DAfilename,load=1)
dd=DA300.copy() 
DA300.extract(locals())
DA300.info()
