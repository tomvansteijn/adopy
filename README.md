# adopy

Simple IO library for ado, teo and flo files.

Supported functionality:
* Reading ado data files with one or more data blocks
* Reading steady-state and transient flo files
* Reading teo grid files
* Writing ado files
* Writing steady-state and transient flo files

To Do:
* Test reading and writing trace tro files
* Write more tests
* Cython speedup for reading and writing array data?

The following projects are similar:
* [triwaco_flo](https://gitlab.com/rhdhv/water/groundwater/io/tree/master/triwaco_flo)
* [triwaco_tro](https://gitlab.com/rhdhv/water/groundwater/io/tree/master/triwaco_tro)

## Example usage
Reading an ado file:
```python
with adopy.open(r'data\RL1.ado') as src:
    blocks = [bl for bl in src.read()]

block = blocks[0]    
print(f'block name: {block.name:>6}')
print(f'block mean: {block.values.mean():6.3f}')
```
Output:
```
block name:    RL1
block mean: 26.152
```
Reading an ado file as dictionary:
```python
with adopy.open(r'data\RL1.ado') as src:
    blocks = src.as_dict()
print(blocks)
```
Output:
```
{'RL1': AdoBlock(name=RL1, type=ARRAY)}
```
Reading a steady-state flo file:
```python
with adopy.open_flo(r'data\flairs.FLO') as src:
    for block in src.read():
        print(f'block name: {block.name:>6}')
        print(f'block mean: {block.values.mean():6.3f}')
```
Output:
```
block name:   PHIT
block mean:  2.771
block name:   PHI1
block mean:  2.771
...
block name:  QBO18
block mean:  3.165
block name:  QBO19
block mean:  6.539
```
Reading a transient flo file:
```python
with adopy.open_flo(r'data\flairs1_2007.flo', transient=True) as src:
    series = []
    for block in src.read():
        series.append((block.time, block.values.mean()))
print(series[:2])
```
Output:
```
[(1005.0, 24.590661709309583), (1010.0, 24.687882623248424)]
```
Reading a teo grid file:
```python
with adopy.open_grid(r'data\grid.teo') as src:
    grid = src.read()
    print(f'number of nodes: {len(grid.x_nodes):d}')
    print(f'number of river nodes: {len(grid.river_nodes):d}')
```
Output:
```
number of nodes: 46274
number of river nodes: 13773
```
Writing an ado file:
```python
import numpy as np
record = {
    'name': 'random',
    'blocktype': 2,  # array
    'values': np.random.rand(50_000,),
    }
with adopy.open(r'data\random.ado', 'w') as dst:
    dst.write(records=[record,])
```