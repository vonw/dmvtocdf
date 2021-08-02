def readDMV(filename):
    """
    Reader for SSEC DMV binary files using "pure Python". This function
    is currently capable of reading RNC, RFC, RLC, and CXS files, but not SUM files.
    The function returns an xarray Dataset that contains various data
    variables and metadata for those variables.

    To use this function, try the steps below:
        For RNC file
            from readDMV import readDMV
            readDMV('160602C1.RNC')

        For RFC file
            from readDMV import readDMV
            readDMV('160602C1.RFC')

        For RLC file
            from readDMV import readDMV
            readDMV('160602C1.RLC')

        For CXS file
            from readDMV import readDMV
            readDMV('160602F1.CXS')

        For CXV file
            from readDMV import readDMV
            readDMV('160602F1.CXV')

        For SUM file
            from readDMV import readDMV
            readDMV('160602.SUM')

    Written by:
        Von P. Walden
        Washington State University
        7 August 2018

        Updates:
        15 August 2019 - Updated documentation within this function.
         8 January 2020- Major update (v2.0): 
            1) create new functions, 
            2) added support for CXV and SUM files.
         1 August 2021 - Added support for RFC files.
    """
    import numpy as np
    import pandas as pd
    import xarray as xr
    from collections import OrderedDict
    from ohwhio import getDMVformat

    def readTOC(sizeTOC):
        dependentVariables = OrderedDict({})
        dependentVariableRecords = OrderedDict({})
        if (sizeTOC == 40):  # RNC, RFC, RLC, ...
            # dependent data information for single-variable file.
            sizeDependentRecord = np.fromfile(f, np.int32, 1)[0]
            formatDependentRecord = np.fromfile(f, np.int32, 1)[0]
            scalingFactorLog = np.fromfile(f, np.int32, 1)[0]
            dependentPrecisionLog = np.fromfile(f, np.int32, 1)[0]
            # independent data information
            independentMinimum = np.fromfile(f, np.float64, 1)[0]
            independentMaximum = np.fromfile(f, np.float64, 1)[0]
            independentPrecisionLog = np.fromfile(f, np.int32, 1)[0]
            # number of attributes for next section.
            numberOfDependentAttributes = np.fromfile(f, np.int32, 1)[0]
            numberOfDependentVariables = 1
            # Now read the attributes for the single variable.
            # Variable name
            nbytes = np.fromfile(f, np.int32, 1)[0]
            variableName = f.read(nbytes).decode('utf-8')
            # Short name
            nbytes = np.fromfile(f, np.int32, 1)[0]
            shortname = f.read(nbytes).decode('utf-8')
            # Short name
            nbytes = np.fromfile(f, np.int32, 1)[0]
            longname = f.read(nbytes).decode('utf-8')
            # Units
            nbytes = np.fromfile(f, np.int32, 1)[0]
            units = f.read(nbytes).decode('utf-8')
            # Precision
            precision = "{:.0E}".format(10 ** dependentPrecisionLog)
            # Now add this to the data variable dictionary.
            dependentVariables.update({variableName: OrderedDict([('longname', longname),
                                                         ('units', units),
                                                         ('precision', precision)])})
            dependentVariableRecords.update({variableName: OrderedDict([('sizeDependentRecord', sizeDependentRecord),
                                                       ('formatDependentRecord', formatDependentRecord),
                                                       ('scalingFactorLog', scalingFactorLog),
                                                       ('dependentPrecisionLog', dependentPrecisionLog),
                                                       ('identifier', identifier),
                                                       ('independentMinimum', independentMinimum),
                                                       ('independentMaximum', independentMaximum),
                                                       ('numberOfDependentAttributes', numberOfDependentAttributes),
                                                       ('numberOfDependentVariables', numberOfDependentVariables)])})
        elif (sizeTOC == 48):  # CXS, CSV, CVS, UVS, SUM, ...
            Continuation = -1  # Non-zero to start loop.
            while (Continuation):
                # dependent data information
                sizeDependentRecord = np.fromfile(f, np.int32, 1)[0]
                formatDependentRecord = np.fromfile(f, np.int32, 1)[0]
                scalingFactorLog = np.fromfile(f, np.int32, 1)[0]
                dependentPrecisionLog = np.fromfile(f, np.int32, 1)[0]
                # independent data information
                independentMinimum = np.fromfile(f, np.float64, 1)[0]
                independentMaximum = np.fromfile(f, np.float64, 1)[0]
                independentPrecisionLog = np.fromfile(f, np.int32, 1)[0]
                # additional data to support multiple variables
                identifier = np.fromfile(f, np.int32, 1)[0]
                Continuation = np.fromfile(f, np.int32, 1)[0]
                # number of attributes for next section.
                numberOfDependentAttributes = np.fromfile(f, np.int32, 1)[0]
                numberOfDependentVariables = identifier + Continuation
                # Now read the attributes for the single variable.
                # Variable name
                nbytes = np.fromfile(f, np.int32, 1)[0]
                variableName = f.read(nbytes).decode('utf-8')
                # Short name
                nbytes = np.fromfile(f, np.int32, 1)[0]
                shortname = f.read(nbytes).decode('utf-8')
                # Short name
                nbytes = np.fromfile(f, np.int32, 1)[0]
                longname = f.read(nbytes).decode('utf-8')
                # Units
                nbytes = np.fromfile(f, np.int32, 1)[0]
                units = f.read(nbytes).decode('utf-8')
                # Precision
                precision = "{:.0E}".format(10 ** dependentPrecisionLog)
                # Now add this to the data variable dictionary.
                dependentVariables.update({variableName: OrderedDict([('longname', longname),
                                                             ('units', units),
                                                             ('precision', precision)])})
                dependentVariableRecords.update({variableName: OrderedDict([('sizeDependentRecord', sizeDependentRecord),
                                                           ('formatDependentRecord', formatDependentRecord),
                                                           ('scalingFactorLog', scalingFactorLog),
                                                           ('dependentPrecisionLog', dependentPrecisionLog),
                                                           ('identifier', identifier),
                                                           ('independentMinimum', independentMinimum),
                                                           ('independentMaximum', independentMaximum),
                                                           ('numberOfDependentAttributes', numberOfDependentAttributes),
                                                           (
                                                           'numberOfDependentVariables', numberOfDependentVariables)])})
        else:
            print('Erroneous size of Table of Contents!! Something is strange with your DMV file!!')
            return (sizeTOC)

        return dependentVariables, dependentVariableRecords

    def DMVfileStructure(filename):
        '''Determines the structure for DMV files.

        Input:
            filename - DMV file name

        Output:
            recordSize - size of data records in bytes for each measurement in time
            variableOffset - offset (in floats) to where the variables start
            dataOffset - offset (in float values) to where data starts

        Notes:
            Determine number of data records for each time step.
                factor of 5 is the number of measurements: BB1-BB2-scene-BB2-BB1
                numberOfDependentVariableBytes is the cumulative number of bytes for all dependent variables
                factor of 4 is the number of bytes in each number.
        '''
        ext    = filename.split('.')[-1]

        # Determine the cumulative number of bytes in the dependent variables.
        numberOfDependentVariableBytes = np.array([dependentVariableRecords[v]['sizeDependentRecord'] for v in dependentVariableRecords]).sum()

        # Determine the record size, variable offset and data offset based on file type.
        # ....RNC ######################################################################################################
        if ((ext == 'RNC') | (ext == 'rnc')):
            channel = filename.split('.')[0][-1]
            if channel == '1':
                nvars = 79
            else:
                nvars = 71
            nvarsExtra1 = 14
            nvarsExtra2 = 22

            recordSize = ((nvars * 5) + nvarsExtra1 + (nvars * 5) + nvarsExtra2) * 4 + numberOfDependentVariableBytes
            variableOffset = (nvars * 4) + (nvars + nvarsExtra1) + (nvars * 4)
            dataOffset = [(nvars * 4) + (nvars + nvarsExtra1) + (nvars * 4) + (nvars + nvarsExtra2)]
        # ....RFC and RLC ######################################################################################################
        elif ((ext == 'RLC') | (ext == 'rlc') | (ext == 'RFC') | (ext == 'rfc')):
            channel = filename.split('.')[0][-1]
            typ = filename.split('.')[0][-2:-1]
            if (typ == 'B'):
                scanDirection = 'Backward'
            elif(typ == 'F'):
                scanDirection = 'Forward'
            else:
                scanDirection = 'Both'    # C1 or C2

            if ((scanDirection=='Backward') | (scanDirection=='Forward')):    # Backward and Forward
                if channel == '1':
                    nvars = 79
                else:
                    nvars = 71
                nvarsExtra = 14

                recordSize = (nvars * 4)*4 + (nvars + nvarsExtra)*4 + numberOfDependentVariableBytes
                variableOffset = nvars * 4
                dataOffset = [(nvars * 5) + nvarsExtra]
            else:                                                             # Both (C1 or C2)
                if channel == '1':
                    nvars = 79
                else:
                    nvars = 71
                nvarsExtra1 = 14
                nvarsExtra2 = 15

                recordSize = ((nvars * 4) + (nvars + nvarsExtra1) + (nvars * 4) + (nvars + nvarsExtra2)) * 4 + numberOfDependentVariableBytes
                variableOffset = (nvars * 4) + (nvars + nvarsExtra1) + (nvars * 4)
                dataOffset = [(nvars * 4) + (nvars + nvarsExtra1) + (nvars * 4) + (nvars + nvarsExtra2)]
        # ....CXS ######################################################################################################
        elif ((ext == 'CXS') | (ext == 'cxs')):
            nvars = 71
            nvarsExtra1 = 0
            nvarsExtra2 = 0
            channel = filename.split('.')[0][-1]
            typ = filename.split('.')[0][-2:-1]
            if (typ == 'B'):
                scanDirection = 'Backward'
            else:
                scanDirection = 'Forward'

            # Special case for Channel 1, Forward direction, which contains 104 extra variables of 28 bytes each.
            if ((channel == '1') & (scanDirection == 'Forward')):
                extraBytes = np.array([dependentVariableRecords[v]['sizeDependentRecord'] for v in dependentVariableRecords])[2:].sum()
                # Now drop all of the extra dependent variables except the real and imag spectra.
                vs = [variable for variable in dependentVariables]
                for v in vs[2:]:
                    dependentVariables.pop(v);
                    dependentVariableRecords.pop(v);
                numberOfDependentVariableBytes = numberOfDependentVariableBytes - extraBytes
            else:
                extraBytes = 0
            # print(numberOfDependentVariableBytes, extraBytes)
            recordSize = (nvars * 4) + numberOfDependentVariableBytes + extraBytes
            variableOffset = 0
            dataOffset = [nvars]
            for v in dependentVariableRecords:
                dataOffset.append(dataOffset[-1] + int(dependentVariableRecords[v]['sizeDependentRecord']/4))
            dataOffset.pop();
        # ....CXV ######################################################################################################
        elif ((ext == 'CXV') | (ext == 'cxv')):
            nvars = 79
            nvarsExtra1 = 0
            nvarsExtra2 = 0
            channel = filename.split('.')[0][-1]
            typ = filename.split('.')[0][-2:-1]
            if (typ == 'B'):
                scanDirection = 'Backward'
            else:
                scanDirection = 'Forward'

            # Special case for Channel 1, Forward direction, which contains 104 extra variables of 28 bytes each.
            if ((channel == '1') & (scanDirection == 'Forward')):
                extraBytes = np.array([dependentVariableRecords[v]['sizeDependentRecord'] for v in dependentVariableRecords])[2:].sum()
                # Now drop all of the extra dependent variables except the real and imag spectra.
                vs = [variable for variable in dependentVariables]
                for v in vs[2:]:
                    dependentVariables.pop(v);
                    dependentVariableRecords.pop(v);
                numberOfDependentVariableBytes = numberOfDependentVariableBytes - extraBytes
            else:
                extraBytes = 0
            # print(numberOfDependentVariableBytes, extraBytes)
            recordSize = (nvars * 4) + numberOfDependentVariableBytes + extraBytes
            variableOffset = 0
            dataOffset = [nvars]
            for v in dependentVariableRecords:
                dataOffset.append(dataOffset[-1] + int(dependentVariableRecords[v]['sizeDependentRecord']/4))
            dataOffset.pop();
        # ....SUM ######################################################################################################
        elif ((ext == 'SUM') | (ext == 'sum')):
            # Handles a special case where the format of the SUM files changed
            #   probably because AERI.xml was changed during ICECAPS.
            yy = filename.split('.')[-2][-6:-4]
            if int(yy)>96:
                yymmdd = '19' + filename.split('.')[-2][-6:]
            else:
                yymmdd = '20' + filename.split('.')[-2][-6:]
            if pd.to_datetime(yymmdd) < pd.to_datetime('20110707'):
                recordSize = 9776
            else:
                recordSize = 9744
            nvars = 144
            variableOffset = 1479
            dataOffset = [variableOffset + nvars]
            for v in dependentVariableRecords:
                dataOffset.append(dataOffset[-1] + int(dependentVariableRecords[v]['sizeDependentRecord']/4))
            dataOffset.pop();
        else:
            print('ERROR: Incorrect file type. Try again...')
            return {}

        numberOfRecords = int((eof - headerSize + 1) / recordSize)
        numberOfValues = int(recordSize / 4)

        return {'recordSize': recordSize,
                'variableOffset': variableOffset,
                'dataOffset': dataOffset,
                'numberOfRecords': numberOfRecords,
                'numberOfValues': numberOfValues,
                'numberOfVariables': nvars
                }

    def determineWavenumberScales(filename):
        ext = filename.split('.')[-1]
        vs = [variable for variable in dependentVariableRecords]

        if ((ext == 'RNC') | (ext == 'rnc') | (ext == 'RFC') | (ext == 'rfc') | (ext == 'RLC') | (ext == 'rlc') | (ext == 'CXS') | (ext == 'cxs') | (ext == 'CXV') | (ext == 'cxv')):
            v = vs[0]
            bwn = dependentVariableRecords[v]['independentMinimum']
            ewn = dependentVariableRecords[v]['independentMaximum']
            nwn = int(dependentVariableRecords[v]['sizeDependentRecord'] / 4)
            wnum1 = np.linspace(bwn, ewn, nwn, dtype=np.float64)

            # Add the wavenumber scale as a variable to the xarray dataset.
            ds[wavenumberScales[v]] = wnum1.astype(np.float64)
            ds[wavenumberScales[v]].attrs['longname'] = 'Wavenumber in reciprocal centimeters'
            ds[wavenumberScales[v]].attrs['units'] = 'centimeter^-1'
            ds[wavenumberScales[v]].attrs['precision'] = '1E-4'
            ds[wavenumberScales[v]].attrs['range_of_values'] = '[ ' + str(bwn) + ', ' + str(ewn) + ' ]'
        elif((ext == 'SUM') | (ext == 'sum')):
            for v in ['ResponsivitySpectralAveragesCh1', 'ResponsivitySpectralAveragesCh2', 'SkyVariabilityAveragesCh1', 'SkyVariabilityAveragesCh2', 'SkyRadianceSpectralAveragesCh1', 'SkyRadianceSpectralAveragesCh2']:
                bwn = dependentVariableRecords[v]['independentMinimum']
                ewn = dependentVariableRecords[v]['independentMaximum']
                nwn = int(dependentVariableRecords[v]['sizeDependentRecord'] / 4)
                wnum1 = np.linspace(bwn, ewn, nwn, dtype=np.float64)
                # Add the wavenumber scale as a variable to the xarray dataset.
                ds[wavenumberScales[v]] = wnum1.astype(np.float64)
                ds[wavenumberScales[v]].attrs['longname'] = 'Wavenumber in reciprocal centimeters'
                ds[wavenumberScales[v]].attrs['units'] = 'centimeter^-1'
                ds[wavenumberScales[v]].attrs['precision'] = '1E-4'
                ds[wavenumberScales[v]].attrs['range_of_values'] = '[ ' + str(bwn) + ', ' + str(ewn) + ' ]'
        else:
            print('ERROR: Incorrect file type. Try again...')
            return {}

        return

    # Opens the DMV file.
    f = open(filename, 'rb')

    # Determine the file size by searching for the end-of-file; eof.
    eof = f.seek(-1, 2)  # go to the file end and record byte value

    # Determine header size, then skip to beginning of data records.
    f.seek(0)

    # Read the header.
    headerSize = int(f.readline().decode('utf-8'))
    f.seek(0)
    FileHistory = f.read(headerSize).decode('utf-8')

    # Decode dependent variables that are associated with the data in the particular file.
    ID = f.read(12).decode('utf-8')
    # f.seek(12,1)    # Skip the 12-byte identifier, "SSECRGD     ".
    sizeTOC = np.fromfile(f, np.int32, 1)[0]
    dependentVariables, dependentVariableRecords = readTOC(sizeTOC)

    # Determine independent variables.
    variables, wavenumberScales = getDMVformat(filename)
    variables.update(dependentVariables)    # Append dependent variables to list of variables

    # Read the next 4 bytes; not sure what these bytes are, but they aren't part of the data records.
    nbytes = np.fromfile(f, np.int32, 1)[0]
    np.fromfile(f, np.int32, nbytes)            # Skip these bytes until I figure out what they represent...

    # Read data in as a float32 array; all RNC variables are float32.
    arr = np.fromfile(f, np.float32)
    f.close()

    # Determine file structure.
    fileStructure = DMVfileStructure(filename)

    # Decode the base_time from the filename.
    base_time = pd.to_datetime('20' + filename.split('/')[-1][0:2] + '-' + filename.split('/')[-1][2:4] + '-' + filename.split('/')[-1][4:6])
    Time = arr[fileStructure['variableOffset']::fileStructure['numberOfValues']]

    # Create a Pandas dataframe for all independent variables.
    df = pd.DataFrame({}, index=base_time + pd.to_timedelta(Time, unit='h'))
    df.index.name = 'time'
    for offset, variable in enumerate(variables):
        if (offset >= fileStructure['numberOfVariables']): break
        df[variable] = arr[fileStructure['variableOffset'] + offset::fileStructure['numberOfValues']]

    # Creates an xarray dataset from the Pandas dataframe.
    ds = xr.Dataset().from_dataframe(df)
    # Determines the wavenumbers scales and adds them to the xarray dataset.
    determineWavenumberScales(filename)

    # Add data for dependent variables.
    for variable, offset in zip(dependentVariables, fileStructure['dataOffset']):
        ds[variable] = xr.DataArray(np.array(
            [arr[int((record * fileStructure['recordSize'] / 4) + offset):int((record * fileStructure['recordSize'] / 4) + offset + len(ds[wavenumberScales[variable]]))] for record in range(fileStructure['numberOfRecords'])]),
                                    coords=[df.index, ds[wavenumberScales[variable]].data],
                                    dims=['time', wavenumberScales[variable]])
    # Global attributes
    ds['FileHistory'] = FileHistory
    # base_time
    ds['base_time'] = np.int32(
        (base_time - pd.to_datetime('1970-01-01') + pd.Timedelta(Time[0], unit='h')).total_seconds())
    ds['base_time'].attrs['longname'] = 'Base time in Epoch'
    ds['base_time'].attrs['date'] = df.index[0].strftime('%Y-%m-%d,%H:%M:%S GMT')
    # date
    ds['date'] = np.int32(filename.split('/')[-1][0:6])
    # time_offset
    ds['time_offset'] = np.array(
        [(pd.Timedelta(time, unit='h') - pd.Timedelta(Time[0], unit='h')).total_seconds() for time in Time])
    ds['time_offset'].attrs['longname'] = 'Time offset from base_time'

    # Adds attributes for each independent variable.
    for offset, variable in enumerate(variables):
        if (offset >= fileStructure['numberOfVariables']): break
        for attribute in variables[variable]:
            ds[variable].attrs[attribute] = variables[variable][attribute]

    # Adds attributes for each dependent variable.
    for variable in dependentVariables:
        for attribute in variables[variable]:
            ds[variable].attrs[attribute] = variables[variable][attribute]

    return ds
