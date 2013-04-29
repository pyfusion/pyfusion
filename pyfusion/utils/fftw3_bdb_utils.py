import pyfftw
import os

default_path = os.getenv('HOME')+'/.pyfftw'

if not(os.path.isdir(default_path)):
    os.mkdir(default_path)

default_filenames=[default_path+'/wisdom_'+ x for x in ['d','f','l']]

def save_wisdom(filenames=default_filenames):
    wisdom = pyfftw.export_wisdom()
    for (fn,w) in zip(filenames,wisdom):
        f = open(fn,'w')
        f.write(w)
        f.close()

def load_wisdom(filenames=default_filenames):
    allwisdom = []
    for fn in filenames:
        f=open(fn,'r')
        allwisdom.append(f.read())
        f.close()
    
    pyfftw.import_wisdom(tuple(allwisdom))
