import MDSplus as M
M.TreeOpen('h1data',58103)

# tricky way -works!
sig = M.TdiExecute('.OPERATIONS:A14_1:INPUT_5')

# straightforward way - doesn't work with this version
nod=M.TreeFindNode('.OPERATIONS:A14_1:INPUT_5')
M.mdsplus_debug.debug_level=99
xx=nod.data()
print xx[10]
