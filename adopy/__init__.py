# pkg

from adopy.ado import AdoFile
from adopy.flo import SteadyFloFile, TransientFloFile
from adopy.teo import TeoFile


def open(adofile, mode='r'):
    return AdoFile(adofile, mode=mode)

def open_grid(teofile, mode='r'):
    return TeoFile(teofile, mode=mode)

def open_flo(flofile, mode='r', transient=False):
    if transient:
        return TransientFloFile(flofile, mode=mode)
    else:
        return SteadyFloFile(flofile, mode=mode)