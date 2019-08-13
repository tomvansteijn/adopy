#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from adopy.ado import AdoBlock, AdoFileReader

import logging
import os

log = logging.getLogger(os.path.basename(__file__))


class SteadyFloFileReader(AdoFileReader):
    def read(self, clean_names=True):
        self._skip_header()
        blocks = super().read()
        if clean_names:
            for block in blocks:
                block.name = (block.name
                    .replace(', STEADY-STATE==', '')
                    .strip()
                    )
        return blocks

    def as_dict(self, clean_names=True):
        return {bl.name: bl for bl in self.read(clean_names=clean_names)}

    def _skip_header(self, header=5):
        for i in range(header):
            line = next(self.lines)


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


class TransientFloFileReader(AdoFileReader):
    def read_block(self):
        block = super().read_block()

        # extract time from block name
        block.name, timestr = block.name.split(',')
        time = float(timestr.replace('TIME: ', ''))

        # return transient ado block
        return TransientAdoBlock.from_block(block, time)
