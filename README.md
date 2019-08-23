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
Reading an ado file
```python
with adopy.open(r'data\RL1.ado') as src:
    blocks = [bl for bl in src.read()]
    rl1 = blocks[0]
    
print('block name:  ', rl1.name)
print('max value: ', rl1.values.max())
```
Output
```
block name:   RL1
max value:  33.31
```
