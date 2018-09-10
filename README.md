# dmvtocdf

This repository contains pure Python code for decoding DMV binary files that were devised and created by Ralph G. Dedecker at the 
Space Science and Engineering Center (SSEC) of the University of Wisconsin-Madison. The concept was to look at the structure of the 
binary DMV files and determine how to extract all the housekeeping data and spectral data. The extracted data are put into an Xarray
dataset, which is basically a Python representation of a netCDF file. Once an Xarray dataset is created, it is trivial to save the
dataset as a netCDF file for future use.

## Usage

1) Place the directory, 'dmvtocdf', on your local Python path. For instance, I added the following line to my .profile Bash script on my Mac.

```bash
export PYTHONPATH="/Users/vonw/work/software/paeri/dmvtocdf/:$PYTHONPATH"
```

2) Then 

```python
# Import the readDMV function from the readDMV.py file.
from readDMV import readDMV
# Read a DMV file.
c1 = readDMV('/Users/vonw/data/paeri/raw/AE160602/160602C1.RNC')
```

3) This should create an xarray Dataset called 'c1'.


Contact: Von P. Walden, v.walden@wsu.edu
