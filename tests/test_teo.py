#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import adopy

import numpy as np
import pytest

import shutil
import os

@pytest.fixture
def teofile(tmpdir):
    datadir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    teofilename = r'grid.teo'
    teofile = os.path.join(datadir, teofilename)
    testfile = tmpdir.join(teofilename)
    shutil.copyfile(teofile, testfile)
    return testfile


class TestTeoFile(object):
    def test_read(self, teofile):
        with adopy.open_grid(teofile) as src:
            grid = src.read()
        header = {k: v for k, v in grid.header}
        assert header['NUMBER NODES'] == 46274
        assert grid.x_nodes.shape == (46274,)
        assert grid.y_nodes.shape == (46274,)
        assert grid.x_nodes.dtype == np.float
        assert header['NUMBER RIVER NODES'] == 13773
        assert grid.river_nodes.shape == (13773,)
        assert grid.river_nodes.dtype == np.int     