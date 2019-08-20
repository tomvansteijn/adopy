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

    @classmethod
    def from_record(cls, record):
        return cls(
            name=record['name'],
            blocktype=BlockType(record['blocktype']),
            values=record['values'],
            )

    def to_record(self):
        return {
            'name': self.name,
            'blocktype': self.blocktype.value,
            'values': self.values,
            }


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

        while True:
            try:
                block = self.read_block()
                yield block
            except StopIteration:
                break

    def as_dict(self):
        return {bl.name: bl for bl in self.read()}

    def read_block(self):
        # parse block name
        name = self._read_name()

        # parse block type
        blocktype = self._read_blocktype()

        # read values
        if blocktype is BlockType.SCALAR:
            values = self._read_scalar()            
        elif blocktype is BlockType.ARRAY:
            values = self._read_array()
        else:
            raise ValueError('block type {blocktype:d} not implemented'.format(
                blocktype=blocktype.value,
                ))

        # read endset
        self._read_endset()

        # return Block object
        return AdoBlock(name=name, blocktype=blocktype, values=values)

    def _read_name(self):        
        line = next(self.lines)
        while line.startswith('---'):
            line = next(self.lines)
        if line == 'END FILE GRIDFL':
            raise StopIteration
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
        for iline in range(nlines):
            line = next(self.lines)
            if (iline + 1) < nlines:
                count = ncols
            else:
                count = nvalues % ncols
            row = np.array(
                [line[ic * width: (ic + 1) * width] for ic in range(count)],
                dtype=dtype,
                )
            rows.append(row)
        values = np.concatenate(rows, axis=0)
        return values

    def _read_endset(self):
        line = next(self.lines)
        assert (line == 'ENDSET') or (line == 'ENDTEXT'), \
            'error reading file {f.name:}'.format(
            f=self.filepath,
            )

    def write(self, blocks=None, records=None, **blockspec):
        blocks = blocks or []
        for record in records:
            block = AdoBlock.from_record(record)
            blocks.append(block)

        for block in blocks:
            self.write_block(**blockspec)

    def write_block(self, block, ncols=6, width=14, precision=6):
        # get dtype
        if block.blocktype is BlockType.SCALAR:
            if isinstance(block.values, str):
                dtype = np.str

        # write name
        self._write_name(block.name)

        # write block type
        self._write_blocktype(self, block.blocktype)

        # write values
        if block.blocktype is BlockType.SCALAR:
            self._write_scalar(block.values)
        elif block.blocktype is BlockType.ARRAY:
            self._write_array(block.values)
        else:
            raise ValueError('block type {blocktype:d} not implemented'.format(
                blocktype=blocktype.value,
                ))

        # write endset
        self._write_endset(dtype)

    def _write_name(self, name, dtype):
        if dtype == np.str:
            prefix = 'TEXT'
        else:
            prefix = 'SET'
        self.f.write('*{prefix:}*{name:}'.format(
            prefix=prefix,
            name=name.upper(),
                ) + '\n'
            )

    def _write_blocktype(self, blocktype):
        self.f.write('{blocktype:d}'.format(
            blocktype=blocktype.value,
                ) + '\n'
            )

    def _write_scalar(self, value, dtype):
        if dtype == np.float:
            floatfmt = '{{width.'
            valuestr = '{:}'.format(value)
        self.f.write('{value:}'.format(
            value=value,
                ) + '\n'
            )

    def _write_array(self, values):
        pass

    def _write_endset(self, dtype):
        if dtype == np.str:
            suffix = 'TEXT'
        else:
            suffix = 'SET'
        self.f.write('END{suffix:}'.format(
            suffix=suffix,
                ) + '\n'
            )
