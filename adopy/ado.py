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

ARRAYFORMAT = (
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

    def __repr__(self):
        return ('{s.__class__.__name__:}('
            'name={s.name:}, '
            'type={s.blocktype.name:}'
            ')').format(s=self)

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


class AdoFile(object):
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

    def reset_file(self):
        self.f.seek(0)

    def read(self, use_loop=False):
        self.reset_file()
        yield from self.read_blocks(use_loop=use_loop)

    def read_blocks(self, use_loop=False):
        if self.mode == 'w':
            raise ValueError('File not readable in write mode')
        while True:
            try:
                block = self.read_block(use_loop=use_loop)
                yield block
            except StopIteration:
                break

    def as_dict(self):
        return {bl.name: bl for bl in self.read()}

    def read_block(self, use_loop=False):
        # parse block name
        name = self._read_name()

        # parse block type
        blocktype = self._read_blocktype()

        # read values
        if blocktype is BlockType.SCALAR:
            values = self._read_scalar()            
        elif blocktype is BlockType.ARRAY:
            values = self._read_array(use_loop=use_loop)
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

        # try to cast as int, then float, otherwise as string array
        try:
            value = np.array(line, dtype=np.int)
        except ValueError:
            try:
                value = np.array(line, dtype=np.float)
            except:
                value = np.array(line)
                
        return value

    def _read_array(self, use_loop=False):
        # read array header
        line = next(self.lines)
        nvalues, arrayformat = line.split()
        nvalues = int(nvalues)

        # parse number format        
        m = re.search(ARRAYFORMAT, arrayformat)
        if m is None:
            raise ValueError('error reading array format')
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
        nrows = nvalues // ncols
        nremainder = nvalues % ncols
        if use_loop:
            rows = []
            for irow in range(nrows + 1):
                line = next(self.lines)
                if (irow < nrows) or (nremainder == 0):
                    count = ncols
                else:
                    count = nremainder
                if count > 0:
                    row = np.array(
                        [line[ic * width: (ic + 1) * width]
                        for ic in range(count)],
                        dtype=dtype,
                        )
                    rows.append(row)
            values = np.concatenate(rows, axis=0)
        else:
            values = []
            if nrows > 0:
                delimiter = [width,] * ncols
                rect_array = np.genfromtxt(self.f,
                    dtype=dtype,
                    delimiter=delimiter,
                    max_rows=nrows,
                    )
                values.append(rect_array.flatten())
            if nremainder > 0:
                delimiter = [width,] * nremainder
                remainder = np.genfromtxt(self.f,
                    dtype=dtype,
                    delimiter=delimiter,
                    max_rows=1,
                    )
                values.append(remainder.flatten())
            values = np.concatenate(values, axis=0)
        return values

    def _read_endset(self):
        line = next(self.lines)
        assert (line == 'ENDSET') or (line == 'ENDTEXT'), \
            'error reading file {f.name:}'.format(
            f=self.filepath,
            )

    def write(self, blocks=None, records=None, use_loop=False, **blockformat):        
        records = records or []
        blocks = blocks or []
        for record in records:
            block = AdoBlock.from_record(record)
            blocks.append(block)

        for block in blocks:
            self.write_block(block, use_loop=use_loop, **blockformat)

    def write_block(self, block, ncols=6, width=14, precision=6, use_loop=False):
        # get dtype
        try:
            dtype = block.values.dtype
        except AttributeError:
            dtype = np.array(block.values).dtype

        # write separator
        self._write_separator()

        # write name
        self._write_name(block.name, dtype)

        # write block type
        self._write_blocktype(block.blocktype)

        # write values
        if block.blocktype is BlockType.SCALAR:
            self._write_scalar(block.values, dtype)
        elif block.blocktype is BlockType.ARRAY:
            self._write_array(block.values,
                dtype, ncols, width, precision, use_loop,
                )
        else:
            raise ValueError('block type {blocktype:d} not implemented'.format(
                blocktype=blocktype.value,
                ))

        # write endset
        self._write_endset(dtype)

    def _write_separator(self):
        self.f.write(72*'-' + '\n')

    def _write_name(self, name, dtype):
        if dtype.type is np.str_:
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
            valuetext = '{value:9.6f}'.format(value=value)
        elif dtype == np.int:
            valuetext = '{value:d}'.format(value=value)
        else:
            valuetext = '{value:}'.format(value=value)
        self.f.write('{valuetext:}'.format(
            valuetext=valuetext,
                ) + '\n'
            )

    def _write_array(self, values, dtype,
        ncols, width, precision=6,
        use_loop=False,
        ):        
        # write array header
        nvalues = values.size
        if dtype == np.float:
            formattext = '({ncols:d}E{width:d}.{precision:d})'.format(
                ncols=ncols,
                width=width,
                precision=precision,
                )
        elif dtype == np.int:
            formattext = '({ncols:d}I{width:d})'.format(
                ncols=ncols,
                width=width,
                )
        else:
            formattext = '({ncols:d}A{width:d})'.format(
                ncols=ncols,
                width=width,
                )
        self.f.write('{nvalues:<10d}{formattext:}'.format(
            nvalues=nvalues,
            formattext=formattext,
                ) + '\n'
            )

        # write array values
        values = np.ravel(values)
        nrows = nvalues // ncols
        nremainder = nvalues % ncols
        if use_loop:
            if dtype == np.float:
                fmt = '{{:+{width:d}.{precision:d}E}}'.format(
                    width=width,
                    precision=precision,
                    )
            elif dtype == np.int:
                fmt = '{{:{width:d}d}}'.format(
                    width=width,
                    )
            else:
                fmt = '{{:<{width:d}}}'.format(
                    width=width,
                    )
            for irow in range(nrows + 1):
                if (irow < nrows) or (nremainder == 0):
                    count = ncols
                else:
                    count = nremainder
                if count > 0:
                    row = values[irow*ncols:irow*ncols + count]
                    line = (fmt*count).format(*row)
                    self.f.write(line + '\n')
        else:
            if dtype == np.float:
                fmt = '%+{width:d}.{precision:d}E'.format(
                    width=width,
                    precision=precision,
                    )
            elif dtype == np.int:
                fmt = '%{width:d}d'.format(
                    width=width,
                    )
            else:
                fmt = '%{width:d}s'.format(
                    width=width,
                    )
            if nrows > 0:
                rect_array = values[:nrows*ncols].reshape((nrows, ncols))
                np.savetxt(self.f, rect_array,
                    delimiter='',
                    fmt=fmt,
                    )
            remainder = values[nrows*ncols:].reshape((1, nremainder))
            np.savetxt(self.f, remainder,
                delimiter='',
                fmt=fmt,
                )         



    def _write_endset(self, dtype):
        if dtype.type is np.str_:
            suffix = 'TEXT'
        else:
            suffix = 'SET'
        self.f.write('END{suffix:}'.format(
            suffix=suffix,
                ) + '\n'
            )
