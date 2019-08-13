# pkg

from adopy.ado import AdoFileReader
from adopy.teo import TeoFileReader


def open(adofile, mode='r'):
    return AdoFileReader(adofile, mode=mode)

def open_grid(teofile, mode='r'):
    return TeoFileReader(teofile, mode=mode)