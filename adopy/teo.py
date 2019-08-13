#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from adopy.ado import AdoFileReader
import numpy as np

from pathlib import Path
import logging
import os

log = logging.getLogger(os.path.basename(__file__))


TEO_NAMES = {
    'X-COORDINATES NODES=': 'x_nodes',
    'Y-COORDINATES NODES=': 'y_nodes',
    'ELEMENT NODES 1=====': 'elem1',
    'ELEMENT NODES 2=====': 'elem2',
    'ELEMENT NODES 3=====': 'elem3',
    'ELEMENT AREA========': 'elem_area',
    'NODE INFLUENCE AREA=': 'nia',
    'SOURCE NODES========': 'source_nodes',
    'NUMBER NODES/RIVER==': 'num_nodes_river',
    'LIST RIVER NODES====': 'river_nodes',
    'LIST BOUNDARY NODES=': 'boundary_nodes',
    'BOUNDARY SEGMENTS===': 'boundary_segments',
    'SOURCENUMBER':'sourcenumber',
    'RIVERNUMBER': 'rivernumber',
    'RIVERID': 'riverid',
    }

class TeoGrid(object):
    def __init__(self,
        header,
        x_nodes,
        y_nodes,
        elem1,
        elem2,
        elem3,
        elem_area,
        nia,
        source_nodes,
        num_nodes_river,
        river_nodes,
        boundary_nodes,
        boundary_segments,
        sourcenumber,
        rivernumber,
        riverid,
        ):
        self.header = header
        self.x_nodes = x_nodes
        self.y_nodes = y_nodes
        self.elem1 = elem1
        self.elem2 = elem2
        self.elem3 = elem3
        self.elem_area = elem_area
        self.nia = nia
        self.source_nodes = source_nodes
        self.num_nodes_river = num_nodes_river
        self.river_nodes = river_nodes
        self.boundary_nodes = boundary_nodes
        self.boundary_segments = boundary_segments
        self.sourcenumber = sourcenumber
        self.rivernumber = rivernumber
        self.riverid = riverid


class TeoFileReader(AdoFileReader):
    def __init__(self, filepath, mode='r'):
        super().__init__(filepath, mode)

    def read(self):
        header = self._read_header()
        blocks = super().read()

        grid_kwargs = {}
        for block in blocks:
            key = TEO_NAMES[block.name]
            grid_kwargs[key] = block.values    
        return TeoGrid(header, **grid_kwargs)


    def _read_header(self):
        # skip first line
        line = next(self.lines)

        # read header items
        header = []
        line = next(self.lines)
        while not line.startswith('---'):
            key, value = line.split('=')
            key = key.strip()
            value = int(value)
            header.append((key, value))
            line = next(self.lines)

        return header
