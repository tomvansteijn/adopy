#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import adopy

import numpy as np
import pytest

import shutil
import os

@pytest.fixture
def adofile(tmpdir):
    datadir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    adofilename = r'RL1.ado'
    adofile = os.path.join(datadir, adofilename)
    testfile = tmpdir.join(adofilename)
    shutil.copyfile(adofile, testfile)
    return testfile


class TestAdofile(object):
    def test_read(self, adofile):
        with adopy.open(adofile) as src:
            blocks = src.read()
        block = blocks[0]
        assert block.name == 'RL1'
        assert block.blocktype.value == 2
        assert block.values.shape == (46274,)
        assert block.values.dtype == np.float
        assert np.isclose(block.values.max(), 33.31)