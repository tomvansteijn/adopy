#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import numpy as np

from pathlib import Path
from enum import Enum
import logging
import os
import re

log = logging.getLogger(os.path.basename(__file__))

NUMBERFORMATPATTERN = (
    r'\((?P<ncols>\d+)(?P<atype>[AEI])(?P<width>\d+).?(?P<precision>\d+)?\)'
    )


class BlockType(Enum):
    SCALAR = 1
    ARRAY = 2


class AdoBlock(object):
    def __init__(self, name, blocktype, values):
        self.name = name
        self.blocktype = blocktype
        self.values = values


class AdoFileReader(object):
    def __init__(self, filepath, mode='r'):
        self.filepath = Path(filepath)
        self.f = self.open(mode=mode)

    @property
    def closed(self):
        return self.f.closed

    @property
    def mode(self):
        return self.f.mode

    @property
    def lines(self):
        return (l.rstrip('\n') for l in self.f)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def open(self, mode='r'):
        return open(self.filepath, mode=mode)

    def close(self):
        self.f.close()

    def read(self):
        if self.mode == 'w':
            raise ValueError('File not readable in write mode')

        blocks = []
        while True:
            try:
                block = self.read_block()
            except StopIteration:
                break
            blocks.append(block)
        return blocks

    def read_block(self):
        # parse ado block name
        name = self._read_name()

        # parse block type
        blocktype = self._read_blocktype()

        # read values
        if blocktype is BlockType.SCALAR:
            values = self._read_scalar()            
        elif blocktype is BlockType.ARRAY:
            values = self._read_array()

        # read endset
        self._read_endset()

        # return Block object
        return AdoBlock(name=name, blocktype=blocktype, values=values)

    def _read_name(self):        
        line = next(self.lines)
        while line.startswith('---'):
            line = next(self.lines)
        name = (line
            .replace('*SET*', '')
            .replace('*TEXT*', '')
            )
        return name

    def _read_blocktype(self):        
        line = next(self.lines)
        blocktype = BlockType(int(line))
        return blocktype

    def _read_scalar(self):
        line = next(self.lines)
        value = np.float(line)  # scalar is always float
        return value

    def _read_array(self):
        # read array header
        line = next(self.lines)
        nvalues, numberformat = line.split()
        nvalues = int(nvalues)

        # parse number format        
        m = re.search(NUMBERFORMATPATTERN, numberformat)
        ncols = int(m.group('ncols'))
        width = int(m.group('width'))
        atype = m.group('atype')
        if atype == 'E':
            dtype = np.float
        elif atype == 'I':
            dtype = np.int
        elif atype == 'A':
            dtype = np.str
        else:
            raise ValueError('data type \'{atype:}\' not implemented'.format(
                atype=atype,
                ))

        # read array values
        nlines = (nvalues + ncols - 1) // ncols
        rows = []
        for i in range(nlines):
            line = next(self.lines)
            if dtype == np.str:
                items = line.split()
                row = np.array(items, dtype=dtype)
            else:
                row = np.fromstring(line, sep=' ', dtype=dtype)
            rows.append(row)
        values = np.concatenate(rows, axis=0)
        return values

    def _read_endset(self):
        line = next(self.lines)
        assert (line == 'ENDSET') or (line == 'ENDTEXT'), \
            'error reading file {f.name:}'.format(
            f=self.filepath,
            )
