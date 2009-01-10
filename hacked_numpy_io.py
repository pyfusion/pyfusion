import numpy as np
from numpy.lib import format
import cStringIO
import os
import itertools

from cPickle import load as _cload, loads
from numpy.lib._datasource import DataSource
from numpy.lib._compiled_base import packbits, unpackbits

def savez(file, *args, **kwds):
    """
    Save several arrays into an .npz file format which is a zipped-archive
    of arrays

    If keyword arguments are given, then filenames are taken from the keywords.
    If arguments are passed in with no keywords, then stored file names are
    arr_0, arr_1, etc.

    Parameters
    ----------
    file : string
        File name of .npz file.
    args : Arguments
        Function arguments.
    kwds : Keyword arguments
        Keywords.

    """

    # Import is postponed to here since zipfile depends on gzip, an optional
    # component of the so-called standard library.
    import zipfile

    if isinstance(file, basestring):
        if not file.endswith('.npz'):
            file = file + '.npz'

    namedict = kwds
    for i, val in enumerate(args):
        key = 'arr_%d' % i
        if key in namedict.keys():
            raise ValueError, "Cannot use un-named variables and keyword %s" % key
        namedict[key] = val

    zip = zipfile.ZipFile(file, mode="w")

    # Place to write temporary .npy files
    #  before storing them in the zip
    import tempfile
    direc = tempfile.gettempdir()
    todel = []

    for key, val in namedict.iteritems():
        fname = key + '.npy'
        filename = os.path.join(direc, fname)
        todel.append(filename)
        fid = open(filename,'wb')
        format.write_array(fid, np.asanyarray(val))
        fid.close()
        zip.write(filename, arcname=fname,compress_type=zipfile.ZIP_DEFLATED)

    zip.close()
    for name in todel:
        os.remove(name)
