#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

from adopy.ado import AdoFile

import numpy as np

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

    @classmethod
    def from_file(cls, 
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
        '''
        Create class instance from teo file. Note that indices are converted to zero-based indexing.
        Source and River numbers are unchanged!
        '''
        return cls(
            header,
            x_nodes,
            y_nodes,
            elem1 - 1,
            elem2 - 1,
            elem3 - 1,
            elem_area,
            nia,
            source_nodes - 1,
            num_nodes_river,
            river_nodes - 1,
            boundary_nodes - 1,
            boundary_segments,
            sourcenumber,
            rivernumber,
            riverid,
            )

    def get_midpoints(self):
        x1 = self.x_nodes[self.elem1]
        x2 = self.x_nodes[self.elem2]
        x3 = self.x_nodes[self.elem3]
        y1 = self.y_nodes[self.elem1]
        y2 = self.y_nodes[self.elem2]
        y3 = self.y_nodes[self.elem3]
        return (
            (np.mean([x1, x2], axis=0), np.mean([y1, y2], axis=0)),
            (np.mean([x1, x2], axis=0), np.mean([y1, y2], axis=0)),
            (np.mean([x1, x2], axis=0), np.mean([y1, y2], axis=0)),
            )


    def get_center_coords(self):
        x1 = self.x_nodes[self.elem1]
        x2 = self.x_nodes[self.elem2]
        x3 = self.x_nodes[self.elem3]
        y1 = self.y_nodes[self.elem1]
        y2 = self.y_nodes[self.elem2]
        y3 = self.y_nodes[self.elem3]

        xc = np.mean([x1, x2, x3], axis=0)
        yc = np.mean([y1, y2, y3], axis=0)

        center_coords = np.stack([xc, yc], axis=-1)
        return center_coords

    def get_node_coords(self, nodenumber=None):
        node_coords = np.stack([self.x_nodes, self.y_nodes], axis=-1)
        if nodenumber is None:
            return node_coords
        else:
            return node_coords[nodenumber, :]

    def get_elements_for_node(self, nodenumber):
        is_elem = (
            (nodenumber == self.elem1) |
            (nodenumber == self.elem2) |
            (nodenumber == self.elem3)
            )
        is_elem, = np.where(is_elem)
        return is_elem

    def get_nodes_for_element(self, elementnumber):
        yield self.elem1[elementnumber]
        yield self.elem2[elementnumber]
        yield self.elem3[elementnumber]

    def is_boundary_node(self, nodenumber):
        return nodenumber in self.boundary_nodes


class TeoFile(AdoFile):
    def read(self, use_loop=False):
        self.reset_file()
        header = self._read_header()
        blocks = super().read_blocks(use_loop=use_loop)

        grid_kwargs = {}
        for block in blocks:
            key = TEO_NAMES[block.name]
            grid_kwargs[key] = block.values    
        return TeoGrid.from_file(header, **grid_kwargs)

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

    def write(self):
        raise NotImplementedError('writing teo files not implemented')
