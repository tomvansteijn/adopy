#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from adopy.ado import AdoBlock, AdoFile

import logging
import os

log = logging.getLogger(os.path.basename(__file__))


class SteadyFloFile(AdoFile):
    def read(self, clean_names=True):
        self.reset_file()
        self._skip_header()
        blocks = super().read_blocks()        
        for block in blocks:
            if clean_names:
                block.name = (block.name
                    .replace(', STEADY-STATE==', '')
                    .strip()
                    )
            yield block

    def as_dict(self, clean_names=True):
        return {bl.name: bl for bl in self.read(clean_names=clean_names)}

    def _skip_header(self, header=5):
        for i in range(header):
            line = next(self.lines)

    def write(self, blocks=None, records=None, **blockformat):
        self._write_header()
        super().write(blocks, records, **blockformat)

    def _write_header(self, header=5):
        for i in range(header):
            self._write_separator()


class TransientAdoBlock(AdoBlock):
    def __init__(self, name, time, blocktype, values):
        super().__init__(name, blocktype, values)
        self.time = time

    @classmethod
    def from_block(cls, block, time):
        return cls(
            name=block.name,
            time=time,
            blocktype=block.blocktype,
            values=block.values,
            )

    @classmethod
    def from_record(cls, record):
        return cls(
            name=record['name'],
            time=record['time'],
            blocktype=BlockType(record['blocktype']),
            values=record['values'],
            )

    def to_record(self):
        return {
            'name': self.name,
            'time': self.time,
            'blocktype': self.blocktype.value,
            'values': self.values,
            }

    def to_base(self):
        block_name = '{name:},TIME:{time:10.4f}'.format(
            name=self.name,
            time=self.time,
            )
        return AdoBlock(
            name=name,
            blocktype=self.blocktype,
            values=self.values,
            )


class TransientFloFile(AdoFile):
    def read_block(self):
        block = super().read_block()

        # extract time from block name
        block.name, timestr = block.name.split(',')
        time = float(timestr.replace('TIME: ', ''))

        # return transient ado block
        return TransientAdoBlock.from_block(block, time)

    def write(self, blocks=None, records=None, **blockformat):
        records = records or []
        blocks = blocks or []
        for record in records:
            block = TransientAdoBlock.from_record(record)
            blocks.append(block)

        for block in blocks:
            self.write_block(block.to_base(), **blockformat)
