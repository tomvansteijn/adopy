#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import adopy

# Reading an ado file:
with adopy.open(r'data\RL1.ado') as src:
    blocks = [bl for bl in src.read()]

block = blocks[0]    
print(f'block name: {block.name:>6}')
print(f'block mean: {block.values.mean():6.3f}')

# Reading an ado file as dictionary:
with adopy.open(r'data\RL1.ado') as src:
    blocks = src.as_dict()
print(blocks)

# Reading a steady-state flo file:
with adopy.open_flo(r'data\flairs.FLO') as src:
    for block in src.read():
        print(f'block name: {block.name:>6}')
        print(f'block mean: {block.values.mean():6.3f}')

# Reading a transient flo file:
with adopy.open_flo(r'data\flairs1_2007.flo', transient=True) as src:
    series = []
    for block in src.read():
        series.append((block.time, block.values.mean()))
print(series[:2])

# Reading a teo grid file:
with adopy.open_grid(r'data\grid.teo') as src:
    grid = src.read()
    print(f'number of nodes: {len(grid.x_nodes):d}')
    print(f'number of river nodes: {len(grid.river_nodes):d}')

# Writing an ado file:
import numpy as np
record = {
    'name': 'random',
    'blocktype': 2,  # array
    'values': np.random.rand(50_000,),
    }
with adopy.open(r'data\random.ado', 'w') as dst:
    dst.write(records=[record,])
