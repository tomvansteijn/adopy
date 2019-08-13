#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import adopy

import numpy as np
import pytest

import shutil
import os

@pytest.fixture
def steadyflofile(tmpdir):
    datadir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    flofilename = r'flairs.FLO'
    flofile = os.path.join(datadir, flofilename)
    testfile = tmpdir.join(flofilename)
    shutil.copyfile(flofile, testfile)
    return testfile


@pytest.fixture
def transientflofile(tmpdir):
    datadir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    flofilename = r'flairs1_2007.flo'
    flofile = os.path.join(datadir, flofilename)
    testfile = tmpdir.join(flofilename)
    shutil.copyfile(flofile, testfile)
    return testfile


class TestSteadyFloFile(object):
    def test_read(self, steadyflofile):
        with adopy.open_flo(steadyflofile, transient=False) as src:
            flo = src.as_dict()
        assert flo['PHI1'].values.shape == (136365,)


class TestTransientFloFile(object):
    def test_read(self, transientflofile):
        with adopy.open_flo(transientflofile, transient=True) as src:
            flo = src.read()