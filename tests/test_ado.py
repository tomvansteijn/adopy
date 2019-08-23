#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import adopy

import numpy as np
import pytest

import shutil
import os

@pytest.fixture
def sourcefile(tmpdir):
    datadir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    sourcefilename = r'RL1.ado'
    sourcefile = os.path.join(datadir, sourcefilename)
    testfile = tmpdir.join(sourcefilename)
    shutil.copyfile(sourcefile, testfile)
    return testfile


@pytest.fixture
def destfile(tmpdir):
    copyfilename =  r'RL1_copy.ado'
    testfile = tmpdir.join(copyfilename)
    return testfile


class TestAdoFile(object):
    def test_read(self, sourcefile):
        with adopy.open(sourcefile) as src:
            blocks = [bl for bl in src.read()]
        block = blocks[0]
        assert len(blocks) == 1
        assert block.name == 'RL1'
        assert block.blocktype.value == 2
        assert block.values.shape == (46274,)
        assert block.values.dtype == np.float
        assert np.isclose(block.values.max(), 33.31)

    def test_write_array(self):
        datadir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        destfilename = r'random.ado'
        destfile = os.path.join(datadir, destfilename)
        records = [
            {
            'name': 'random',
            'blocktype': 2,
            'values': np.random.rand(46274),
                },
            ]
        with adopy.open(destfile, 'w') as dst:
            dst.write(records=records)

    def test_read_write(self, sourcefile, destfile):
        with adopy.open(sourcefile) as src:
            blocks = [bl for bl in src.read()]

        with adopy.open(destfile, mode='w') as dst:
            dst.write(blocks)

        with adopy.open(destfile, mode='r') as src2:
            blocks2 = [bl for bl in src2.read()]

        assert len(blocks) == 1
        assert len(blocks2) == 1
        for block, block2 in zip(blocks, blocks2):
            assert block.name == block2.name
            assert block.blocktype.value == block2.blocktype.value
            assert block.values.shape == block2.values.shape
            assert block.values.dtype == block2.values.dtype
            assert np.isclose(block.values.max(), block2.values.max())