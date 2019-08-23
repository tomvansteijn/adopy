#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

import adopy

# read ado
with adopy.open(r'data\RL1.ado') as src:
    blocks = [bl for bl in src.read()]
    rl1 = blocks[0]
    
print('block name:  ', rl1.name)
print('max value: ', rl1.values.max())

# read steady-state flo file
