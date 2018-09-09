# dmvtocdf

This repository contains pure Python code for decoding DMV binary files that were devised and created by Ralph G. Dedecker at the 
Space Science and Engineering Center (SSEC) of the University of Wisconsin-Madison. The concept was to look at the structure of the 
binary DMV files and determine how to extract all the housekeeping data and spectral data. The extracted data are put into an Xarray
dataset, which is basically a Python representation of a netCDF file. Once an Xarray dataset is created, it is trivial to save the
dataset as a netCDF file for future use.

## Issues
1) This first attempt at extracting the data from DMV files is incomplete. It currently only works well for RNC and RLC files, and is 
probably quite "fragile".

2) The number of housekeeping variables and data variables changes with different forms of DMV files (such as RNC, RLC, SUM files...). 
Currently the Python code does not handle the different types well. For instance, RLC files appear to have 101 variables, while RNC
files appear to have only 79. But is this true for all RLC and RNC files? Probably not. So future versions will need to decode how many
variables are associated with each file, and then properly extract those variables. I believe that this was the purpose of the SSEC's
OHWHIO library, which I think is a repository for all of the possible variables that could be saved into a DMV file. But I suspect that
the files themselves must have information regarding their specific variables.

Contact: Von P. Walden, v.walden@wsu.edu