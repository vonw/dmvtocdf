def readDMV(filename):
    """
    First attempt to create a reader for SSEC DMV binary files that is 
    "pure Python". This function isn't complete yet, because I was unable 
    to determine how to extract the information for the wavenumber grid for
    the various file types (RLC, RNC, SUM). So there is work yet to do...
    
    To use this function, try the steps below:
        For RNC file
            from readDMV import readDMV
            readDMV('160602C1.RNC')
        
        For RLC file
            from readDMV import readDMV
            readDMV('160602C1.RLC')
            
        For SUM file
            more work to do to decode this type of file...
            
    Written by:
        Von P. Walden
        Washington State University
        7 August 2018
    """
    import numpy       as     np
    import pandas      as     pd
    import xarray      as     xr
    from   collections import OrderedDict
    from   ohwhio      import getDMVformat
    
    # Determines type of file from extension.
    ext = filename.split('.')[-1]
    
    # Opens the DMV file.
    f = open(filename,'rb')
    
    # Determine the file size by searching for the end-of-file; eof.
    eof = f.seek(-1,2)     # go to the file end and record byte value
    
    # Determine header size, then skip to beginning of data records.
    f.seek(0)
    
    # Read the header.
    headerSize  = int(f.readline().decode('utf-8'))
    f.seek(0)
    FileHistory = f.read(headerSize).decode('utf-8')
    
    # Decode new variables that are associated with the data in the particular file.
    ID = f.read(12).decode('utf-8')
    #f.seek(12,1)    # Skip the 12-byte identifier, "SSECRGD     ".
    sizeTOC = np.fromfile(f,np.int32,1)[0]
    if(sizeTOC == 40):
        # dependent data information
        sizeDependentRecord     = np.fromfile(f,np.int32,1)[0]
        formatDependentRecord   = np.fromfile(f,np.int32,1)[0]
        scalingFactorLog        = np.fromfile(f,np.int32,1)[0]
        dependentPrecisionLog   = np.fromfile(f,np.int32,1)[0]
        # independent data information
        independentMinimum      = np.fromfile(f,np.float64,1)[0]
        independentMaximum      = np.fromfile(f,np.float64,1)[0]
        independentPrecisionLog = np.fromfile(f,np.int32,1)[0]
    elif(sizeTOC == 48):
        # dependent data information
        sizeDependentRecord     = np.fromfile(f,np.int32,1)[0]
        formatDependentRecord   = np.fromfile(f,np.int32,1)[0]
        scalingFactorLog        = np.fromfile(f,np.int32,1)[0]
        dependentPrecisionLog   = np.fromfile(f,np.int32,1)[0]
        # independent data information
        independentMinimum      = np.fromfile(f,np.float64,1)[0]
        independentMaximum      = np.fromfile(f,np.float64,1)[0]
        independentPrecisionLog = np.fromfile(f,np.int32,1)[0]
        # additional data to support multiple variables
        identifier              = np.fromfile(f,np.int32,1)[0]
        Continuation            = np.fromfile(f,np.int32,1)[0]
    else:
        print('Erroneous size of Table of Contents!! Something is strange with your DMV file!!')
        return(sizeTOC)
    
    # Determine the set of housekeeping variables from ohwhio.py based on the type of DMV file (extension).
    if((ext=='RNC') | (ext=='rnc')):
        variables = getDMVformat(formatDependentRecord)
        nvars = 79
        skipValues1          = 14
        skipValues2          = 22
    elif((ext=='RLC') | (ext=='rlc')):
        variables = getDMVformat(formatDependentRecord)
        nvars = 79
        skipValues1          = 14
        skipValues2          = 15
    else:
        print('ERROR: Incorrect file type. Try again...')
        return {}
    

    # CHECK THIS OUT; IT MAY NOT BE GENERAL FOR ALL DMV FILE TYPES...
    numberOfDependentAttributes = np.fromfile(f,np.int32,1)[0]
    numberOfDependentVariables  = int(numberOfDependentAttributes / 4)
    for var in range(numberOfDependentVariables):
        # Variable name
        nbytes       = np.fromfile(f,np.int32,1)[0]
        variableName = f.read(nbytes).decode('utf-8')
        # Short name
        nbytes       = np.fromfile(f,np.int32,1)[0]
        shortname    = f.read(nbytes).decode('utf-8')
        # Short name
        nbytes       = np.fromfile(f,np.int32,1)[0]
        longname     = f.read(nbytes).decode('utf-8')
        # Units
        nbytes       = np.fromfile(f,np.int32,1)[0]
        units        = f.read(nbytes).decode('utf-8')
        # Precision - THIS IS hard-wired for now because the precision is NOT contained in the DMV file.
        precision    = str(0.5 * 10**dependentPrecisionLog)  
        # Now add this to the data variable dictionary.
        variables.update({variableName: OrderedDict([('longname',  longname),
                                                     ('units',     units   ),
                                                     ('precision', precision)])})

    # Read the next 4 bytes; not sure what these bytes are, but they aren't part of the data records.
    nbytes       = np.fromfile(f,np.int32,1)[0]
    tail = np.fromfile(f,np.int32,nbytes)
    
    # Set parameters for wavenumber scale.
    bwn = independentMinimum
    ewn = independentMaximum
    nwn = int(sizeDependentRecord/4)
    # Determine number of data records for each time step.
    #       factor of 5 is the number of measurements: BB1-BB2-scene-BB2-BB1
    #       nwn is the number of elements in the spectrum.
    #       factor of 4 is the number of bytes in each number.
    recordSize          = ( (nvars*5) + skipValues1 + (nvars*5) + skipValues2 + nwn ) * 4
    numberOfRecords     = int((eof-headerSize+1)/recordSize)
    numberOfVariables   = int(recordSize/4)
    variableOffset      = (nvars*4) + (nvars+skipValues1) + (nvars*4)
    dataOffset          = (nvars*4) + (nvars+skipValues1) + (nvars*4) + (nvars+skipValues2)
    
    # Read data in as a float32 array; all RNC variables are float32.
    arr  = np.fromfile(f,np.float32)
    f.close()
    
    # Decode the base_time from the filename.
    base_time = pd.to_datetime('20' + filename[-12:-10] + '-' + filename[-10:-8] + '-' + filename[-8:-6])
    Time = arr[variableOffset::numberOfVariables]
    
    # Create a Pandas dataframe.
    df   = pd.DataFrame({}, index=base_time + pd.to_timedelta(Time,unit='h'))
    df.index.name = 'time'
    for offset, variable in enumerate(variables):
        df[variable] = arr[variableOffset+offset::numberOfVariables]
    
    # Create wnum grid.
    wnum1 = np.linspace(bwn,ewn,nwn)
    
    # Creates an xarray dataset from the Pandas dataframe.
    ds = xr.Dataset().from_dataframe(df)
    for variable in variables: 
        for attribute in variables[variable]:
            ds[variable].attrs[attribute] = variables[variable][attribute]
    # DON'T FORGET TO CREATE UNIQUE ATTRIBUTES THAT DEPEND ON DATE AND TIME!!
    #             ('time_offset',
    #              OrderedDict([('longname', 'Time offset from base_time')])),
    #             ('wnum1',
    #              OrderedDict([('longname',
    #                            'Wave number in reciprocal centimeters'),
    #                           ('units', 'centimeter^-1'),
    #                           ('precision', '1E6'),
    #                           ('range_of_values', '[ 520.237, 1799.856]')])),
    # Global attributes
    ds['FileHistory']                   = FileHistory
    # base_time
    ds['base_time']                     = np.int32((base_time - pd.to_datetime('1970-01-01') + pd.Timedelta(Time[0], unit='h')).total_seconds())
    ds['base_time'].attrs['longname']   = 'Base time in Epoch'
    ds['base_time'].attrs['date']       = df.index[0].strftime('%Y-%m-%d,%H:%M:%S GMT')
    # date
    ds['date']                          = np.int32(filename[-12:-6])
    # time_offset
    ds['time_offset']                   = np.array([(pd.Timedelta(time, unit='h') - pd.Timedelta(Time[0], unit='h')).total_seconds() for time in Time])
    ds['time_offset'].attrs['longname'] = 'Time offset from base_time'
    # wnum1
    ds['wnum1']                         = wnum1
    ds['wnum1'].attrs['longname']       = 'Wavenumber in reciprocal centimeters'
    ds['wnum1'].attrs['units']          = 'centimeter^-1'
    ds['wnum1'].attrs['precision']      = '1E-4'
    ds['wnum1'].attrs['range_of_values']       = '[ ' + str(bwn) + ', ' + str(ewn) + ' ]'
    
    if((ext=='RNC') | (ext=='rnc')):
        # mean_rad
        ds['mean_rad'] = xr.DataArray(np.array([arr[int((record*recordSize/4)+dataOffset):int((record*recordSize/4)+dataOffset+nwn)] for record in range(numberOfRecords)]), 
                            coords=[df.index,wnum1],
                            dims=['time','wnum1'])
    elif((ext=='RLC') | (ext=='rlc')):
        # averageRadiance
        ds['averageRadiance'] = xr.DataArray(np.array([arr[int((record*recordSize/4)+dataOffset):int((record*recordSize/4)+dataOffset+nwn)] for record in range(numberOfRecords)]), 
                            coords=[df.index,wnum1],
                            dims=['time','wnum1'])
    else:
        print('ERROR: Incorrect file type. Try again...')
        return {}
    
    return(ds)
