# pkg

from adopy.ado import AdoFileReader
from adopy.flo import SteadyFloFileReader, TransientFloFileReader
from adopy.teo import TeoFileReader


def open(adofile, mode='r'):
    return AdoFileReader(adofile, mode=mode)

def open_grid(teofile, mode='r'):
    return TeoFileReader(teofile, mode=mode)

def open_flo(flofile, mode='r', transient=False):
    if transient:
        return TransientFloFileReader(flofile, mode=mode)
    else:
        return SteadyFloFileReader(flofile, mode=mode)