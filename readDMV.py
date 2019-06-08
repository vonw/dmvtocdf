def readDMV(filename):
    """
    First attempt to create a reader for SSEC DMV binary files that is 
    "pure Python". This function isn't complete yet, because I was unable 
    to determine how to extract the information for the wavenumber grid for
    the various file types (RLC, RNC, CXS. SUM). So there is work yet to do...
    
    To use this function, try the steps below:
        For RNC file
            from readDMV import readDMV
            readDMV('160602C1.RNC')
        
        For RLC file
            from readDMV import readDMV
            readDMV('160602C1.RLC')
            
        For CXS file
            from readDMV import readDMV
            readDMV('160602F1.CXS')
            
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
    
    # Determine the set of housekeeping variables from ohwhio.py based on the type of DMV file (extension).
    if((ext=='RNC') | (ext=='rnc')):
        variables          = getDMVformat(ext)
        dependentVariables = ['mean_rad']
        nvars              = 79
        skipValues1        = 14
        skipValues2        = 22
    elif((ext=='RLC') | (ext=='rlc')):
        variables          = getDMVformat(ext)
        dependentVariables = ['averageRadiance']
        nvars              = 79
        skipValues1        = 14
        skipValues2        = 15
    elif((ext=='CXS') | (ext=='cxs')):
        variables   = getDMVformat(ext)
        nvars       = 71
        skipValues1 = 0
        skipValues2 = 0
        channel = filename.split('.')[0][-1]
        typ = filename.split('.')[0][-2:-1]
        if (typ=='B'):
            scanDirection = 'Backward'
        else:
            scanDirection = 'Forward'
        dependentVariables = ['Ch' + channel + scanDirection + 'ScanRealPartCounts', 
                              'Ch' + channel + scanDirection + 'ScanImagPartCounts']
    else:
        print('ERROR: Incorrect file type. Try again...')
        return {}
    
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
    records = {}
    if(sizeTOC == 40):   # RNC, RLC, ...
        # dependent data information for single-variable file.
        sizeDependentRecord         = np.fromfile(f,np.int32,1)[0]
        formatDependentRecord       = np.fromfile(f,np.int32,1)[0]
        scalingFactorLog            = np.fromfile(f,np.int32,1)[0]
        dependentPrecisionLog       = np.fromfile(f,np.int32,1)[0]
        # independent data information
        independentMinimum          = np.fromfile(f,np.float64,1)[0]
        independentMaximum          = np.fromfile(f,np.float64,1)[0]
        independentPrecisionLog     = np.fromfile(f,np.int32,1)[0]
        # number of attributes for next section.
        numberOfDependentAttributes = np.fromfile(f,np.int32,1)[0]
        numberOfDependentVariables  = 1
        # Now read the attributes for the single variable.
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
        # Precision
        precision    = "{:.0E}".format(10**dependentPrecisionLog)  
        # Now add this to the data variable dictionary.
        variables.update({variableName: OrderedDict([('longname',  longname),
                                                     ('units',     units),
                                                     ('precision', precision)])})
        records.update(  {variableName: OrderedDict([('sizeDependentRecord',         sizeDependentRecord),
                                                     ('formatDependentRecord',       formatDependentRecord),
                                                     ('scalingFactorLog'     ,       scalingFactorLog),
                                                     ('dependentPrecisionLog',       dependentPrecisionLog),
                                                     ('identifier',                  identifier),
                                                     ('independentMinimum',          independentMinimum),
                                                     ('independentMaximum',          independentMaximum),
                                                     ('numberOfDependentAttributes', numberOfDependentAttributes),
                                                     ('numberOfDependentVariables',  numberOfDependentVariables)])})
    elif(sizeTOC == 48):  # CXS, CSV, CVS, UVS, SUM, ...
        Continuation  = -1    # Non-zero to start loop.
        while(Continuation):
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
            # number of attributes for next section.
            numberOfDependentAttributes = np.fromfile(f,np.int32,1)[0]
            numberOfDependentVariables  = identifier + Continuation
            # Now read the attributes for the single variable.
            # Variable name
            nbytes        = np.fromfile(f,np.int32,1)[0]
            variableName  = f.read(nbytes).decode('utf-8')
            # Short name
            nbytes        = np.fromfile(f,np.int32,1)[0]
            shortname     = f.read(nbytes).decode('utf-8')
            # Short name
            nbytes        = np.fromfile(f,np.int32,1)[0]
            longname      = f.read(nbytes).decode('utf-8')
            # Units
            nbytes        = np.fromfile(f,np.int32,1)[0]
            units         = f.read(nbytes).decode('utf-8')
            # Precision
            precision     = "{:.0E}".format(10**dependentPrecisionLog)  
            # Now add this to the data variable dictionary.
            variables.update({variableName: OrderedDict([('longname',  longname),
                                                         ('units',     units),
                                                         ('precision', precision)])})
            records.update(  {variableName: OrderedDict([('sizeDependentRecord',         sizeDependentRecord),
                                                         ('formatDependentRecord',       formatDependentRecord),
                                                         ('scalingFactorLog'     ,       scalingFactorLog),
                                                         ('dependentPrecisionLog',       dependentPrecisionLog),
                                                         ('identifier',                  identifier),
                                                         ('independentMinimum',          independentMinimum),
                                                         ('independentMaximum',          independentMaximum),
                                                         ('numberOfDependentAttributes', numberOfDependentAttributes),
                                                         ('numberOfDependentVariables',  numberOfDependentVariables)])})
    else:
        print('Erroneous size of Table of Contents!! Something is strange with your DMV file!!')
        return(sizeTOC)
    
    # Create a list of the new dependent variables to add; used later to add data.
    variableNames = [list(variables.items())[i][0] for i in np.arange(-1*(identifier+Continuation),0)]
    
    # Read the next 4 bytes; not sure what these bytes are, but they aren't part of the data records.
    nbytes = np.fromfile(f,np.int32,1)[0]
    tail   = np.fromfile(f,np.int32,nbytes)
    
    # Determine current position in file, which is now at the beginning of the data records.
    beginningOfData = f.tell()

    # Determine number of data records for each time step.
    #       factor of 5 is the number of measurements: BB1-BB2-scene-BB2-BB1
    #       nwn is the number of elements in the spectrum.
    #       factor of 4 is the number of bytes in each number.
    bwn = records[dependentVariables[0]]['independentMinimum']
    ewn = records[dependentVariables[0]]['independentMaximum']
    nwn = int(records[dependentVariables[0]]['sizeDependentRecord']/4)
    if  ((ext=='RNC') | (ext=='rnc')):
        recordSize     = ( (nvars*5) + skipValues1 + (nvars*5) + skipValues2 + nwn ) * 4
        variableOffset = (nvars*4) + (nvars+skipValues1) + (nvars*4)
        dataOffset     = [(nvars*4) + (nvars+skipValues1) + (nvars*4) + (nvars+skipValues2)]
    elif((ext=='RLC') | (ext=='rlc')):
        recordSize     = ( (nvars*5) + skipValues1 + (nvars*5) + skipValues2 + nwn ) * 4
        variableOffset = (nvars*4) + (nvars+skipValues1) + (nvars*4)
        dataOffset     = [(nvars*4) + (nvars+skipValues1) + (nvars*4) + (nvars+skipValues2)]
    elif((ext=='CXS') | (ext=='cxs')):
        # Special case for Channel 1, Forward direction, which contains 104 extra variables of 28 bytes each.
        if ((channel=='1') & (scanDirection=='Forward')):
            extraBytes = np.array([records[r]['sizeDependentRecord'] for r in records])[2:].sum()
        else:
            extraBytes = 0
        recordSize     = (nvars + nwn * 2) * 4 + extraBytes
        variableOffset = 0
        dataOffset     = [nvars, nvars + nwn]
    numberOfRecords = int((eof-headerSize+1)/recordSize)
    numberOfValues  = int(recordSize/4)
    
    # Read data in as a float32 array; all RNC variables are float32.
    arr  = np.fromfile(f,np.float32)
    f.close()
    
    # Decode the base_time from the filename.
    base_time = pd.to_datetime('20' + filename[-12:-10] + '-' + filename[-10:-8] + '-' + filename[-8:-6])
    Time = arr[variableOffset::numberOfValues]
    
    # Create a Pandas dataframe.
    df   = pd.DataFrame({}, index=base_time + pd.to_timedelta(Time,unit='h'))
    df.index.name = 'time'
    for offset, variable in enumerate(variables):
        if(offset>=nvars): break
        df[variable] = arr[variableOffset+offset::numberOfValues]
    
    # Create wnum grid.
    wnum1 = np.linspace(bwn,ewn,nwn)
    
    # Creates an xarray dataset from the Pandas dataframe.
    ds = xr.Dataset().from_dataframe(df)
    # Adds attributes to each variable.
    for offset, variable in enumerate(variables):
        if(offset>=nvars): break
        for attribute in variables[variable]:
            ds[variable].attrs[attribute] = variables[variable][attribute]
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
    
    # Add data for dependent variables.
    for variable, offset in zip(dependentVariables, dataOffset):
        ds[variable] = xr.DataArray(np.array([arr[int((record*recordSize/4)+offset):int((record*recordSize/4)+offset+nwn)] for record in range(numberOfRecords)]), 
                            coords=[df.index,wnum1],
                            dims=['time','wnum1'])
    
    # Adds attributes for dependent variables.
    if((ext=='RNC') | (ext=='rnc')):
        # mean_rad
        ds['mean_rad'].attrs['longname']  = 'Downwelling radiance interpolated to standard wavenumber scale'
        ds['mean_rad'].attrs['units']     = 'mw/(m2 sr cm-1)'
        ds['mean_rad'].attrs['precision'] = '1E4'         
    elif((ext=='RLC') | (ext=='rlc')):
        # averageRadiance
        ds['averageRadiance'].attrs['longname']  = 'Interferometer scan directional average of radiance'
        ds['averageRadiance'].attrs['units']     = 'mw/(m2 sr cm-1)'
        ds['averageRadiance'].attrs['precision'] = '1E4'
    elif((ext=='CXS') | (ext=='cxs')):
        if(channel=='1'):
            if(scanDirection=='Forward'):
                ds['Ch1ForwardScanRealPartCounts'].attrs['longname']   = 'AERI LW (Ch1) Forward Scan Real Part Counts'
                ds['Ch1ForwardScanRealPartCounts'].attrs['units']      = 'Counts'
                ds['Ch1ForwardScanRealPartCounts'].attrs['precision']  = '1E4'
                ds['Ch1ForwardScanImagPartCounts'].attrs['longname']   = 'AERI LW (Ch1) Forward Scan Imaginary Part Counts'
                ds['Ch1ForwardScanImagPartCounts'].attrs['units']      = 'Counts'
                ds['Ch1ForwardScanImagPartCounts'].attrs['precision']  = '1E4'
            else:
                ds['Ch1BackwardScanRealPartCounts'].attrs['longname']  = 'AERI LW (Ch1) Backward Scan Real Part Counts'
                ds['Ch1BackwardScanRealPartCounts'].attrs['units']     = 'Counts'
                ds['Ch1BackwardScanRealPartCounts'].attrs['precision'] = '1E4'
                ds['Ch1BackwardScanImagPartCounts'].attrs['longname']  = 'AERI LW (Ch1) Backward Scan Imaginary Part Counts'
                ds['Ch1BackwardScanImagPartCounts'].attrs['units']     = 'Counts'
                ds['Ch1BackwardScanImagPartCounts'].attrs['precision'] = '1E4'
        else:
            if(scanDirection=='Forward'):
                ds['Ch2ForwardScanRealPartCounts'].attrs['longname']   = 'AERI LW (Ch2) Forward Scan Real Part Counts'
                ds['Ch2ForwardScanRealPartCounts'].attrs['units']      = 'Counts'
                ds['Ch2ForwardScanRealPartCounts'].attrs['precision']  = '1E4'
                ds['Ch2ForwardScanImagPartCounts'].attrs['longname']   = 'AERI LW (Ch2) Forward Scan Imaginary Part Counts'
                ds['Ch2ForwardScanImagPartCounts'].attrs['units']      = 'Counts'
                ds['Ch2ForwardScanImagPartCounts'].attrs['precision']  = '1E4'
            else:
                ds['Ch2BackwardScanRealPartCounts'].attrs['longname']  = 'AERI LW (Ch2) Backward Scan Real Part Counts'
                ds['Ch2BackwardScanRealPartCounts'].attrs['units']     = 'Counts'
                ds['Ch2BackwardScanRealPartCounts'].attrs['precision'] = '1E4'
                ds['Ch2BackwardScanImagPartCounts'].attrs['longname']  = 'AERI LW (Ch2) Backward Scan Imaginary Part Counts'
                ds['Ch2BackwardScanImagPartCounts'].attrs['units']     = 'Counts'
                ds['Ch2BackwardScanImagPartCounts'].attrs['precision'] = '1E4'
    else:
        print('ERROR: Incorrect file type. Try again...')
        return {}
    
    return(ds)
