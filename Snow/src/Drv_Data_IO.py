"""
Class Features:

Name:          Drv_Data_IO
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20150330'
Version:       '1.0.3'
"""

#################################################################################
# Logging
import logging
oLogStream = logging.getLogger('sLogger')

# Global libraries
import os
import time
import datetime
import numpy as np

from os.path import join
from os.path import isfile
from os.path import split

import Lib_Data_Apps as Lib_Data_Apps

from GetException import GetException

# Debug
import matplotlib.pylab as plt
#################################################################################

#################################################################################
# Class to manage IO files
class Drv_Data_IO:
    
    #--------------------------------------------------------------------------------
    # Class init
    def __init__(self, sFileName, sFileMode=None, sFileType=None):
        
        # Define filename
        sFilePath = split(sFileName)[0]
        sFileName = split(sFileName)[1]
        
        # Define FileType and FileWorkspace
        if sFileName.endswith('txt') or sFileName.endswith('asc'):
            
            sFileType = 'ascii'
            self.oFileWorkspace = FileAscii(sFilePath, sFileName, sFileType, sFileMode)

        elif sFileName.endswith('nc'):
            
            sFileType = 'netCDF'
            self.oFileWorkspace = FileNetCDF(sFilePath, sFileName, sFileType, sFileMode)
            
        elif sFileName.endswith('tiff') or sFileName.endswith('tif'):
            
            sFileType = 'tiff'
            self.oFileWorkspace = FileTiff(sFilePath, sFileName, sFileType, sFileMode)
            
        elif sFileName.endswith('bin'):
            
            sFileType = 'binary'
            self.oFileWorkspace = FileBinary(sFilePath, sFileName, sFileType, sFileMode)
            
        elif sFileName.endswith('mat'):
            
            sFileType = 'matlab'
            self.oFileWorkspace = FileMat(sFilePath, sFileName, sFileType, sFileMode)
        
        elif sFileName.endswith('grb') or sFileType == 'grib':
            
            sFileType = 'grib'
            self.oFileWorkspace = FileGrib(sFilePath, sFileName, sFileType, sFileMode)
        
        elif sFileName.endswith('db'):
            
            sFileType = 'pickle_db'
            self.oFileWorkspace = FilePickleDB(sFilePath, sFileName, sFileType, sFileMode)
        
        elif sFileName.endswith('csv'):
            
            sFileType = 'csv'
            self.oFileWorkspace = FileCSV(sFilePath, sFileName, sFileType, sFileMode)
            
        elif sFileName.endswith('hdf') or sFileName.endswith('hdf4'):
            
            sFileType = 'hdf4'
            self.oFileWorkspace = FileHDF4(sFilePath, sFileName, sFileType, sFileMode)
        
        else:
            sFileType = 'unknown'
            self.oFileWorkspace = {}
            GetException(' -----> ERROR: file format unknown! Please check your settings file!',1,1)
    #--------------------------------------------------------------------------------
    
#################################################################################

#################################################################################

#--------------------------------------------------------------------------------
# Class to manage HDF4 files
class FileHDF4:
    
    #--------------------------------------------------------------------------------
    # Class init
    def __init__(self, sFilePath, sFileName, sFileType, sFileMode):
        
        self.sFilePath = sFilePath
        self.sFileName = sFileName
        self.sFileType = sFileType
        self.sFileMode = sFileMode
        
        # Open file (read or write mode)
        self.openFile(); 
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Open hdf4 file
    def openFile(self):
        
        from osgeo import gdal
        
        #`Check method
        try:
            # Open file
            oFile = gdal.Open(join(self.sFilePath, self.sFileName))
            self.oFile = oFile
            
        except IOError as oError:
            GetException(' -----> ERROR: in open file (HDF4 I/O)' + ' [' + str(oError) + ']',1,1)
        
    #--------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------
    # Get data from hdf4 file
    def readFileData(self):
        
        #-------------------------------------------------------------------------------------
        # Import library
        from osgeo import gdal
        from GetGeoData import defineGeoData
        #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------
        # File handling
        oFile = self.oFile
        # Getting dataset(s)
        oDSet = oFile.GetSubDatasets()
        oAttrs = oFile.GetMetadata_Dict()
        
        # Defining filename, time and product
        sFilePath, sFileName = os.path.split(self.sFileName)
        a1sFileName = sFileName.split('.')
        sFileTime = a1sFileName[3]
        sFileProduct = a1sFileName[0] + '.' + a1sFileName[1] 
        #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------
        # Cycle(s) on dataset(s)
        oDict = {}; a2dGeoX = None; a2dGeoY = None;
        for oDs in oDSet:
            
            #-------------------------------------------------------------------------------------
            # Dataset handler
            oData = gdal.Open(oDs[0])
            # Data values
            a2dData = oData.ReadAsArray()
            # Data description
            oDataDescription = oData.GetDescription()
            # Data name
            sDataName = oData.GetDescription().split(':')[4]
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Geographical data
            if (a2dGeoX is None) or (a2dGeoY is None):
                
                [iRows, iCols] = a2dData.shape
                a2dDataGeoCoord = oData.GetGeoTransform()
                
                dGeoXMin = a2dDataGeoCoord[0]; dGeoXStep = a2dDataGeoCoord[1]
                dGeoYMax = a2dDataGeoCoord[3]; dGeoYStep = a2dDataGeoCoord[5]
                
                dGeoXMin = dGeoXMin + dGeoXStep/2.
                dGeoYMax = dGeoYMax + dGeoYStep/2.
                dGeoXMax = dGeoXMin + (iCols - 1) * dGeoXStep
                dGeoYMin = dGeoYMax + (iRows - 1) * dGeoYStep
                
                [a2dGeoX, a2dGeoY, a1dGeoBox] = defineGeoData(dGeoYMin, dGeoXMin, 
                                                              dGeoYMax, dGeoXMax, 
                                                              dGeoYStep, dGeoXStep, 
                                                              iRows, iCols)
            else:
                pass
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Saving data in a dictionary
            sDataName = sDataName.lower()
            oDict[sDataName] = a2dData
            
            # Debugging fields
            #plt.figure(1)
            #plt.imshow (a2dData, interpolation='nearest', vmin=0)
            #plt.show()
            #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------    
        # File object
        oFileObject = {}
        oFileObject['Data'] = oDict
        oFileObject['GeoX'] = a2dGeoX
        oFileObject['GeoY'] = a2dGeoY
        oFileObject['GeoZ'] = None
        oFileObject['Attributes'] = oAttrs
        oFileObject['Proj'] = None
        oFileObject['Time'] = sFileTime
        
        # Return file object
        return oFileObject
        #-------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Class to manage csv files
class FileCSV:
    
    #--------------------------------------------------------------------------------
    # Class init
    def __init__(self, sFilePath, sFileName, sFileType, sFileMode):
        
        self.sFilePath = sFilePath
        self.sFileName = sFileName
        self.sFileType = sFileType
        self.sFileMode = sFileMode
        
        # Open file (read or write mode)
        self.openFile(); 
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Open csv file (in read mode)
    def openFile(self):
    
        import csv 
        
        try:
            oFileHandle = open( join(self.sFilePath, self.sFileName) , self.sFileMode )
            
            if 'r' in self.sFileMode:
                oFile = csv.reader(oFileHandle)
            elif 'w' in self.sFileMode:
                oFile = csv.writer(oFileHandle, quoting=csv.QUOTE_NONNUMERIC)
                
            self.oFileData = oFile
        except IOError as oError:
            GetException(' -----> ERROR: in open file (CSV I/O)' + ' [' + str(oError) + ']',1,1)
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to write csv data
    def writeFileData(self, a2oDBData):
        
        # Get file handle
        oFile = self.oFileData
        # Write data 
        oFile.writerows(a2oDBData)
  
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to read csv data
    def readFileData(self, oOpVarMethod=None):
        
        # Get info about math operation
        iCountTr = oOpVarMethod['Op_Math']['Aggregation']['DataThr']
        sAggFunc = oOpVarMethod['Op_Math']['Aggregation']['Func']
         
        # Get data raw from csv handle file
        oDataRaw = []
        for oData in self.oFileData:
            oDataRaw.append(oData)
        
        # Initialize value(s) and counter(s)
        a1oValue = []; a1oGeoX = []; a1oGeoY = []; a1oGeoZ = []; a1oTime = []; a1oCode = [];
        iCodeTest = -9999; iCodeStep = -9999; dValueFinal = 0; iCount = 0; iD = 0; iStep = 0; sTime =''
        # Iteration on field(s)
        while iStep < len(oDataRaw):
            
            # Get all data
            oData = oDataRaw[iStep]
            
            # Get sensor code
            iCodeStep = int(oData[0])
            if iCodeTest == -9999:
                iCodeTest = iCodeStep
            
            # Check code(s)
            if iCodeTest == iCodeStep:
                
                # Get value and geo data
                dValue = np.float16(oData[3])
                dGeoX = np.float16(oData[4]); dGeoY = np.float16(oData[5]); dGeoZ = np.float16(oData[6])
                
                # Get time information
                sTime = oData[12].encode('utf-8') 
                oTime = datetime.datetime.strptime(sTime,'%Y-%m-%dT%H:%M:%S')
                sTime = oTime.strftime('%Y%m%d%H%M');
                
                # Get code information
                iCode = np.int(oData[0])
                
                # Check for no data value(s)
                if dValue > -9990:
                
                    if sAggFunc == 'aggregCumulated':
                        
                        # Cumulated value
                        dValueFinal = dValueFinal + dValue
                        
                    elif sAggFunc == 'aggregInstantaneous':
                        
                        # Istantaneous value
                        dValueFinal = dValue
                        
                    else:
                        # Exit error
                        dValueFinal = np.nan
                        GetException(' -----> ERROR: aggregation method undefined! Check your settings file!', 1, 1)
                    
                else:
                    GetException(' -----> WARNING: no data value find. Skipping it!', 2, 1)
                    
                # Update counter(s)
                iCount += 1; iStep += 1
                iCodeTest = iCodeStep
                
                # Condition to save last array value
                if iStep == len(oDataRaw):
                    iCodeTest = -9999
                    
            if iCodeTest != iCodeStep:
                
                # Save geo information
                a1oGeoX.append(np.float16(dGeoX)); a1oGeoY.append(np.float16(dGeoY)); 
                a1oGeoZ.append(np.float16(dGeoZ))
                
                # Save time information
                a1oTime.append(sTime)
                
                # Save code information
                a1oCode.append(np.int(iCode))
                
                # Save value(s)
                if sAggFunc == 'aggregCumulated':
                    
                    if iCount >= iCountTr:
                        a1oValue.append(np.float16(dValueFinal))
                    else:
                        a1oValue.append(np.float16(-9999.0))

                elif sAggFunc == 'aggregInstantaneous':
                    
                    if iCount == iCountTr:
                        a1oValue.append(np.float16(dValueFinal))
                    elif iCount > iCountTr:
                        GetException(' -----> ERROR: in computing instantaneous data!', 1, 1)
                    else:
                        a1oValue.append(np.float16(-9999.0))
                    
                else:
                    # Exit error
                    a1oValue.append(np.float16(-9999.0))
                    GetException(' -----> ERROR: aggregation method undefined! Check your settings file!', 1, 1)
                
                # Re-initialize counter(s)
                iCodeTest = -9999; iCodeStep = -9999 
                iCount = 0; dValueFinal = 0;
                
        # Create array(s)
        a1dValue = np.asarray(a1oValue, dtype=np.float32)
        a1dGeoX = np.asarray(a1oGeoX, dtype=np.float32); a1dGeoY = np.asarray(a1oGeoY, dtype=np.float32); 
        a1dGeoZ = np.asarray(a1oGeoZ, dtype=np.float32)
        a1iCode = np.asarray(a1oCode, dtype=np.int)
        
        iValueN = len(a1dValue)
        a1dValue = np.reshape(a1dValue, [1, iValueN])
        a1dGeoX = np.reshape(a1dGeoX, [1, iValueN])
        a1dGeoY = np.reshape(a1dGeoY, [1, iValueN])
        a1dGeoZ = np.reshape(a1dGeoZ, [1, iValueN])
        a1iCode = np.reshape(a1iCode, [1, iValueN])
        
        # File object
        oFileObject = {}
        oFileObject['Data'] = a1dValue
        oFileObject['GeoX'] = a1dGeoX
        oFileObject['GeoY'] = a1dGeoY
        oFileObject['GeoZ'] = a1dGeoZ
        oFileObject['Attributes'] = {}
        oFileObject['Attributes']['Code'] = a1iCode
        oFileObject['Proj'] = None
        oFileObject['Time'] = sTime
        
        # Return file object
        return oFileObject
        
    #-------------------------------------------------------------------------------- 
        
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Class to manage pickle db files
class FilePickleDB:
    
    #--------------------------------------------------------------------------------
    # Class init
    def __init__(self, sFilePath, sFileName, sFileType, sFileMode):
        
        self.sFilePath = sFilePath
        self.sFileName = sFileName
        self.sFileType = sFileType
        self.sFileMode = sFileMode
        
        # Open file (read or write mode)
        self.openFile(); 
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Open pickle db file (in read mode)
    def openFile(self):
    
        import pickle
        
        try:
            if 'r' in self.sFileMode:
                oFile = pickle.load( open( join(self.sFilePath, self.sFileName) , self.sFileMode + 'b' ) )  
            elif 'w' in self.sFileMode:
                oFile = open( join(self.sFilePath, self.sFileName), self.sFileMode + 'b' )
            
            self.oFileData = oFile
        except IOError as oError:
            GetException(' -----> ERROR: in open file (PICKLE DB I/O)' + ' [' + str(oError) + ']',1,1)
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to write pickle db data
    def writeFileData(self, a1oDBData):
        
        # Import library
        import pickle
        # Dump data on disk ### DA RIVEDERE
        pickle.dump( a1oDBData, self.oFileData )
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to read pickle db data
    def readFileData(self, oOpVarMethod=None):
        
        # Get info about math operation
        iCountTr = oOpVarMethod['Op_Math']['Aggregation']['DataThr']
        sAggFunc = oOpVarMethod['Op_Math']['Aggregation']['Func']

        # Initialize value(s) and counter(s)
        a1oValue = []; a1oGeoX = []; a1oGeoY = []; a1oGeoZ = []; a1oTime = []; a1oCode = [];
        iCodeTest = -9999; iCodeStep = -9999; dValueFinal = 0; iCount = 0; iStep = 0;
        # Iteration on field(s)
        while iStep < len(self.oFileData):
            
            # Get all data
            oData = self.oFileData[iStep]
            
            # Get sensor code
            iCodeStep = oData[0]
            if iCodeTest == -9999:
                iCodeTest = iCodeStep
            
            # Check code(s)
            if iCodeTest == iCodeStep:
                
                # Get value and geo data
                dValue = np.float16(oData[3])
                dGeoX = np.float16(oData[4]); dGeoY = np.float16(oData[5]); dGeoZ = np.float16(oData[6])
                
                # Get time information
                sTime = oData[12].encode('utf-8') 
                oTime = datetime.datetime.strptime(sTime,'%Y-%m-%dT%H:%M:%S')
                sTime = oTime.strftime('%Y%m%d%H%M');
                
                # Get code information
                iCode = np.int(oData[0])
                
                # Check for no data value(s)
                if dValue > -9990:
                
                    if sAggFunc == 'aggregCumulated':
                        
                        # Cumulated value
                        dValueFinal = dValueFinal + dValue
                        
                    elif sAggFunc == 'aggregInstantaneous':
                        
                        # Istantaneous value
                        dValueFinal = dValue
                        
                    else:
                        # Exit error
                        dValueFinal = np.nan
                        GetException(' -----> ERROR: aggregation method undefined! Check your settings file!', 1, 1)
                    
                else:
                    GetException(' -----> WARNING: no data value find. Skipping it!', 2, 1)
                    
                # Update counter(s)
                iCount += 1; iStep += 1
                iCodeTest = iCodeStep
                
            else:
                
                # Save geo information
                a1oGeoX.append(np.float16(dGeoX)); a1oGeoY.append(np.float16(dGeoY)); 
                a1oGeoZ.append(np.float16(dGeoZ))
                
                # Save time information
                a1oTime.append(sTime)
                
                # Save code information
                a1oCode.append(np.int(iCode))
                
                # Save value(s)
                if sAggFunc == 'aggregCumulated':
                    
                    if iCount >= iCountTr:
                        a1oValue.append(np.float16(dValueFinal))
                    else:
                        a1oValue.append(np.float16(-9999.0))
                        
                    iCodeTest = iCodeStep
                        
                elif sAggFunc == 'aggregInstantaneous':
                    
                    if iCount == iCountTr:
                        a1oValue.append(np.float16(dValueFinal))
                    elif iCount > iCountTr:
                        GetException(' -----> ERROR: in computing instantaneous data!', 1, 1)
                    else:
                        a1oValue.append(np.float16(-9999.0))
                    
                    iCodeTest = -9999; iCodeStep = -9999
                    
                else:
                    # Exit error
                    iCodeTest = -9999; iCodeStep = -9999
                    a1oValue.append(np.float16(-9999.0))
                    GetException(' -----> ERROR: aggregation method undefined! Check your settings file!', 1, 1)
                
                # Re-initialize counter(s)
                iCount = 0; dValueFinal = 0;
                
        # Create array(s)
        a1dValue = np.asarray(a1oValue, dtype=np.float32)
        a1dGeoX = np.asarray(a1oGeoX, dtype=np.float32); a1dGeoY = np.asarray(a1oGeoY, dtype=np.float32); 
        a1dGeoZ = np.asarray(a1oGeoZ, dtype=np.float32)
        a1iCode = np.asarray(a1oCode, dtype=np.int)
        
        iValueN = len(a1dValue)
        a1dValue = np.reshape(a1dValue, [1, iValueN])
        a1dGeoX = np.reshape(a1dGeoX, [1, iValueN])
        a1dGeoY = np.reshape(a1dGeoY, [1, iValueN])
        a1dGeoZ = np.reshape(a1dGeoZ, [1, iValueN])
        a1iCode = np.reshape(a1iCode, [1, iValueN])
        
        
        # File object
        oFileObject = {}
        oFileObject['Data'] = a1dValue
        oFileObject['GeoX'] = a1dGeoX
        oFileObject['GeoY'] = a1dGeoY
        oFileObject['GeoZ'] = a1dGeoZ
        oFileObject['Attributes'] = {}
        oFileObject['Attributes']['Code'] = a1iCode
        oFileObject['Proj'] = None
        oFileObject['Time'] = sTime
        
        # Return file object
        return oFileObject
        
    #-------------------------------------------------------------------------------- 
        
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Class to manage Grib files
class FileGrib:
    
    #--------------------------------------------------------------------------------
    # Class init
    def __init__(self, sFilePath, sFileName, sFileType, sFileMode):
        
        self.sFilePath = sFilePath
        self.sFileName = sFileName
        self.sFileType = sFileType
        self.sFileMode = sFileMode
        
        # Open file (read or write mode)
        self.openFile(); 
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Open grib file (in read mode)
    def openFile(self):
        
        import pygrib
        
        try:
            oFile = pygrib.open(join(self.sFilePath, self.sFileName))    
            self.oFileData = oFile
        except IOError as oError:
            GetException(' -----> ERROR: in open file (GRIB I/O)' + ' [' + str(oError) + ']',1,1)
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to read grib data
    def readFileData(self, sFileNameGeo=None, oOpVarLoad=None, oOpVarMath=None):
        
        #--------------------------------------------------------------------------------
        # Library
        import datetime
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Retrieve messages GRIB file
        oFileObject = {}; 
        try:
            iFileMessages = self.oFileData.messages
            
            if iFileMessages == 0:
                
                GetException(' -----> WARNING: no message in GRIB file! Check your input file!', 2, 1)
                oFileObject = None
                return oFileObject
            else:
                pass
            
        except:
            GetException(' -----> WARNING: no message in GRIB file! Check your input file!', 2, 1)
            oFileObject = None
            return oFileObject
        
        # Define file message array 
        a1iFileMessages = np.linspace(1, iFileMessages, iFileMessages, endpoint=True)
        iFMLen = len(a1iFileMessages);
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Get Geographical information 
        if not sFileNameGeo:
            [a2dGeoY, a2dGeoX] = self.oFileData[1].latlons()
            a2dGeoX = np.flipud(a2dGeoX)
        else:
            
            try:
                oFileDrv_Geo = Drv_Data_IO(sFileNameGeo, 'r')
                a2dGeoX = np.flipud(np.rot90(oFileDrv_Geo.oFileWorkspace.get2DVar('GeoX')))
                a2dGeoY = np.rot90(oFileDrv_Geo.oFileWorkspace.get2DVar('GeoY'))
            except:
                GetException(' -----> ERROR: geographical information defined by user! File not found or format unknown! Check your geo file!', 1, 1)
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Get parameters projection
        oProjParams = self.oFileData[1].projparams
        
        # Attributes
        oFileAttrs={}; iKeyID = 0; 
        for sKey in self.oFileData[1].keys():
            
            sKey = sKey.encode('UTF-8')
            iKeyID = iKeyID + 1
            
            if not (sKey == 'values' or sKey == 'parameterName' or
                    sKey == 'latLonValues' or sKey == 'latitudes' or sKey == 'longitudes' or
                    sKey == 'distinctLatitudes' or sKey == 'distinctLongitudes' or
                    sKey == 'month' or sKey == 'day' or sKey == 'hour' or sKey == 'minute' or sKey == 'second'):
                
                try:
                    
                    oValue = self.oFileData[1][sKey]
                    oFileAttrs.update({sKey: oValue})
                    
                except:
                    GetException(' -----> WARNING: file key ' + sKey + ' not found in analyzed file! Check input file!',2,1)
                
                # Debug
                #oLogStream.debug('ID: ' +str(iKeyID) + ' KEY: ' + str(sKey) + ' VALUE:' + str(oValue))
                
            else:
                pass
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Compute variable(s) type number
        oVarDict = {}; iVarID = 0; iVarN = 0;
        for sFM in a1iFileMessages:
            iFM = int(sFM)
            if self.oFileData[iFM]['name']:
                
                oVarName = self.oFileData[iFM]['name']
                sVarName = oVarName.replace(' ', '_')
                
                if not sVarName in oVarDict.values():                
                    iVarID = iVarID + 1
                    oVarDict[iVarID] = sVarName
                else:
                    break
            else:
                pass
        # Number of variable(s)
        iVarN = len(oVarDict); iFMRatio = 0;
        oLogStream.info(' ----> Number of variable(s) into dataset: ' + str(iVarN)) 
        if iVarN < 1:
            GetException(' -----> ERROR: variable(s) are not available into dataset! Check your input file!',1,1)
        else:
            iFMRatio = iFMLen/iVarN
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Check op variable workspace(s)
        if oOpVarLoad and oOpVarMath:
            
            # Get name components and math function(s)
            sOpVarName = oOpVarLoad['Name']; a1oOpVarComp = oOpVarLoad['Comp']['IN'].values()
            
            # Get function name to update raw data
            sOpVarFunc = oOpVarMath['Conversion']['Func']
            
            # Get method to update raw variable
            try:
                oOps_FuncMethod = getattr(Lib_Data_Apps, sOpVarFunc)
            except:
                oOps_FuncMethod = None
            
        else:
            # None function
            oOps_FuncMethod = None
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # DEBUG
        #print('NUMERO MESSAGGI MINIMO PER DEBUG --> DISATTIVARE QUANDO TESTATO (FOR VALUE MIN 3 --> START VALUE 2 --> INIT VALUE 1')
        #iFileMessages = 6 # per due variabili 6 altrimenti 3 (minimo dataset)
        #iFileMessages = 24 # per testare Net radiation
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Cycle on steps (GRIB message starts from 1)
        a1oTimeSteps = []; a2oData = {}; oTimeStepVarPrevious = None; iFMZero = 0; iFM_Ratio = 0; iCountN = 0; iTimeSteps = 0; iTimeSteps_PS = 0;
        a2dVarSum = np.zeros([a2dGeoX.shape[0], a2dGeoX.shape[1]])
        for sFM in a1iFileMessages:
            
            #--------------------------------------------------------------------------------
            # Get integer value
            iFM = int(sFM)
            
            if iFM_Ratio == 0 or iCountN == 0:
                iFM_Ratio = iFM; iTimeSteps_PS = iTimeSteps 
            else: pass
            if iCountN < iVarN: iCountN = iCountN + 1
            if iCountN == iVarN: iCountN = 0; 
            
            # Get time step information
            sFM_Year = str(self.oFileData[iFM]['year']).zfill(4); 
            sFM_Month = str(self.oFileData[iFM]['month']).zfill(2); sFM_Day = str(self.oFileData[iFM]['day']).zfill(2) 
            sFM_HH = str(self.oFileData[iFM]['hour']).zfill(2); sFM_MM = str(self.oFileData[iFM]['minute']).zfill(2);
            
            iFM_UTR = int(self.oFileData[iFM]['unitOfTimeRange']);
            iFM_P1 = int(self.oFileData[iFM]['P1']); 
            iFM_P2 = int(self.oFileData[iFM]['P2'])
            iFM_TRI = int(self.oFileData[iFM]['timeRangeIndicator'])
            
            # Variable name definition
            sVarMessage = str(self.oFileData[iFM])
            a1oVarMessage = sVarMessage.split(':')
            sVarName = a1oVarMessage[1]
            sVarName = sVarName.replace(' ', '_')
            sVarName = sVarName.lower()
            
            oTimeAnalysis = self.oFileData[iFM].analDate
            sTimeAnalysis = oTimeAnalysis.strftime('%Y%m%d%H%M')
            oTimeAnalysis = datetime.datetime.strptime(sTimeAnalysis,'%Y%m%d%H%M')
            
            # Info
            oLogStream.info(' ----> Get variable: ' + sVarName + ' ... ')
            #--------------------------------------------------------------------------------
            
            #--------------------------------------------------------------------------------
            # Check time forecast units
            if iFM_UTR == 0:
                sTimeForecastUnit = 'minute'
                iTimeForecastUnit = 60 
            elif iFM_UTR == 1:
                sTimeForecastUnit = 'hour'
                iTimeForecastUnit = 3600 
            elif iFM_UTR == 2:
                sTimeForecastUnit = 'day'
                iTimeForecastUnit = 86400 
            elif iFM_UTR == 3:
                sTimeForecastUnit = 'month'
                iTimeForecastUnit = None
            elif iFM_UTR == 4:
                sTimeForecastUnit = 'year'
                iTimeForecastUnit = None
            elif iFM_UTR == 5:
                sTimeForecastUnit = 'decade'
                iTimeForecastUnit = None
            elif iFM_UTR == 6:
                sTimeForecastUnit = 'normal' # 30 years
                iTimeForecastUnit = None
            elif iFM_UTR == 7:
                sTimeForecastUnit = 'century'
                iTimeForecastUnit = None
            elif iFM_UTR == 254:
                sTimeForecastUnit = 'second'
                iTimeForecastUnit = 1
            else:
                sTimeForecastUnit = 'undefined'
                iTimeForecastUnit = None
                GetException(' -----> ERROR: GRIB time forecast units is not available!',1,1)
            #--------------------------------------------------------------------------------
            
            #--------------------------------------------------------------------------------
            # EXAMPLE_TIME PARAMETER(S)
            # RAIN            P1 = 0,1,2 ...,71 P2 = 1,2,3, ... 72                 UTR = 1, TRI = 4
            # TEMPERATURE     P1 = 0,1,2 ,,,,73 P2 = 0,0,0,0                 UTR = 1, TRI = 0
            # SWH             P1 = 0,0,0 P2 = 3,6,9                 UTR = 1, TRI = 3
            # WIND            P1 = 0,1,2 P2 = 0,0,0                 UTR = 1, TRI = 0 (DOPPIA VARIABILE)
            # RELHUMIDITY     P1 = 0,1,2 P2 = 0,0,0                 UTR = 1, TRI = 0 
            #--------------------------------------------------------------------------------
            
            #--------------------------------------------------------------------------------
            # Save time information
            sTimeStart = sFM_Year + sFM_Month + sFM_Day + sFM_HH + sFM_MM
            oTimeStart = datetime.datetime.strptime(sTimeStart,'%Y%m%d%H%M')
            
            oTimeStep_P1 = oTimeStart + datetime.timedelta(seconds = iTimeForecastUnit*iFM_P1)
            oTimeStep_P2 = oTimeStart + datetime.timedelta(seconds = iTimeForecastUnit*iFM_P2)
            
            # Time ratio definition
            iTimeRatio = 1; iTimeSteps = 1
            if np.abs((oTimeStep_P2 - oTimeStep_P1).total_seconds()) > iTimeForecastUnit:
                iTimeRatio = np.abs(int((((oTimeStep_P2 - oTimeStep_P1).total_seconds())/iTimeForecastUnit)/iFM_Ratio))
                iTimeSteps = np.abs(int((((oTimeStep_P2 - oTimeStep_P1).total_seconds())/iTimeForecastUnit)))
            elif (oTimeStep_P2 - oTimeStep_P1).total_seconds() == iTimeForecastUnit:
                iTimeRatio = 1
                iTimeSteps = 1
            
            # Check to update time P2 if P2 is zero
            if (oTimeStep_P2 == oTimeAnalysis):
                oTimeStep_P2 = oTimeStep_P1
                iFM_P2 = iFM_P1
            else:
                pass
            
            # Get timestep
            sTimeStep_P1 = oTimeStep_P1.strftime('%Y%m%d%H%M'); sTimeStep_P2 = oTimeStep_P2.strftime('%Y%m%d%H%M')
        
            # Info time and variable
            oLogStream.info(' -----> Get temporal info :: ' +
                            ' TimeStart: ' + sTimeStart + ' TimeStepFrom: ' + sTimeStep_P1 + ' TimeStepTo: ' + sTimeStep_P2 + 
                            ' P1:  ' + str(iFM_P1) + ' P2: ' + str(iFM_P2)) 
            #--------------------------------------------------------------------------------
  
            #--------------------------------------------------------------------------------
            # Info
            oLogStream.info(' ----> Get raw data :: VarName: ' + sVarName + 
                            ' TimeStepFrom: ' + sTimeStep_P1 + ' TimeStepTo: ' + sTimeStep_P2 + ' ... ')
            #--------------------------------------------------------------------------------
  
            #--------------------------------------------------------------------------------
            # Check timestep
            if oTimeStep_P1 != oTimeAnalysis or oTimeStep_P2 != oTimeAnalysis:
                
                #--------------------------------------------------------------------------------
                # Update index
                #iFM_P1_Upd = iFM_P1 + iFMZero; iFM_P2_Upd = iFM_P2 + iFMZero
                #oLogStream.info(' -----> Get index info ::  IndexFrom: '+str(iFM_P1_Upd)+' IndexTo: '+str(iFM_P2_Upd) )
                #--------------------------------------------------------------------------------
                
                #--------------------------------------------------------------------------------
                # EXAMPLE_TIME PARAMETER(S)
                # RAIN            P1 = 0,1,2 P2 = 1,2,3                 UTR = 1, TRI = 4
                # TEMPERATURE     P1 = 0,1,2 P2 = 0,0,0                 UTR = 1, TRI = 0
                # SWH             P1 = 0,0,0 P2 = 3,6,9                 UTR = 1, TRI = 3
                # WIND            P1 = 0,1,2 P2 = 0,0,0                 UTR = 1, TRI = 0 (DOPPIA VARIABILE)
                # RELHUMIDITY     P1 = 0,1,2 P2 = 0,0,0                 UTR = 1, TRI = 0 
                #--------------------------------------------------------------------------------
                
                #--------------------------------------------------------------------------------
                # Check time range indicator
                a2dVarDef = np.zeros([a2dGeoX.shape[0], a2dGeoX.shape[1]])
                if iFM_TRI == 0:
                    
                    #--------------------------------------------------------------------------------
                    # Istantaneous variable  
                    sTimeRangeIndicator = 'istantaneous';      
                    iFM_Index = iFM
                     
                    # Get data
                    a2dVarDef = np.flipud(self.oFileData[iFM_Index].values)
                    
                    # Compute time delta between two steps
                    iTimeStepsDelta = iTimeSteps - iTimeSteps_PS
                    
                    # Define timestep(s)
                    oTimeSave_P1 = oTimeStep_P2 - datetime.timedelta(seconds=(iTimeStepsDelta-1)*iTimeForecastUnit)
                    
                    #oTimeSave_P1 = oTimeStep_P1
                    oTimeSave_P2 = oTimeStep_P1
                    #--------------------------------------------------------------------------------
                    
                elif iFM_TRI == 3:
                    
                    #--------------------------------------------------------------------------------
                    # Istantaneous variable  
                    sTimeRangeIndicator = 'average';
                    
                    # Define data resolutions
                    
                    #iFM_Index = int(iFM_P2_Upd/iTimeRatio)
                    iFM_Index = iFM
                    
                    # Get data
                    a2dVarRaw = np.flipud(self.oFileData[iFM_Index].values)

                    # Rule to compute average:
                    # VarMean_xhour_n = n(VarMean_nxhour_n) - VarMean_xhour_n-1
                    a2dVarDef = (iFM_Index)*a2dVarRaw - a2dVarSum
                    a2dVarSum = a2dVarSum + a2dVarDef
                    
                    # Define timestep(s)
                    oTimeSave_P1 = oTimeStep_P2 - datetime.timedelta(seconds=(iTimeRatio-1)*iTimeForecastUnit)
                    oTimeSave_P2 = oTimeStep_P2
                    
                    # Debug
                    #dVarDefMean = np.mean(a2dVarDef); dVarRawMean = np.mean(a2dVarRaw); dVarSumMean = np.mean(a2dVarSum); 
                    #oLogStream.info('Mean value ('+str(iTS_1)+')-- Raw: '+ str(dVarRawMean) + ' Def: ' + str(dVarDefMean) + 
                    #                ' Sum: ' + str(dVarSumMean) )
                    #--------------------------------------------------------------------------------
                    
                elif iFM_TRI == 4:
                    
                    #--------------------------------------------------------------------------------
                    # Accumulated variable
                    sTimeRangeIndicator = 'accumulation'; # accumulation in time period 
                    iFM_Index = iFM
  
                    # Get data
                    a2dVarDef = np.flipud(self.oFileData[iFM_Index].values)
                    
                    # Divide data in time ratio element(s)
                    a2dVarDef = a2dVarDef/float(iTimeSteps)
                 
                    # Define timestep(s)
                    oTimeSave_P1 = oTimeStep_P1 + datetime.timedelta(seconds=iTimeForecastUnit)
                    oTimeSave_P2 = oTimeStep_P2;
                    
                    # Debug
                    dVarDefMean = np.mean(a2dVarDef); dVarRawMean = np.mean(a2dVarDef); dVarSumMean = np.mean(a2dVarDef); 
                    oLogStream.info('Mean value ('+str(iFM_Index)+')-- Raw: '+ str(dVarRawMean) + ' Def: ' + str(dVarDefMean) + 
                                    ' Sum: ' + str(dVarSumMean) )
                    #--------------------------------------------------------------------------------
                    
                else:
                    
                    #--------------------------------------------------------------------------------
                    # Exit status
                    sTimeRangeIndicator = 'undefined'
                    GetException(' -----> ERROR: GRIB time range indicator is not available!', 1, 1)
                    #--------------------------------------------------------------------------------
                
                #--------------------------------------------------------------------------------
                # Info 
                oLogStream.info(' ----> Get raw data :: VarName: ' + sVarName + 
                            ' TimeStepFrom: ' + sTimeStep_P1 + ' TimeStepTo: ' + sTimeStep_P2 + ' ... OK')
                #--------------------------------------------------------------------------------
                
                #--------------------------------------------------------------------------------
                # Cycle on time step(s) for saving value(s)
                while oTimeSave_P1 <= oTimeSave_P2:
                    
                    # Get time
                    oTimeSave = oTimeSave_P1
                    
                    # Get timestep
                    sTimeSave = oTimeSave.strftime('%Y%m%d%H%M')
                    
                    # Info
                    oLogStream.info(' ----> Save raw data :: VarName: ' + sVarName + ' TimeStep: ' + sTimeSave + ' ... ') 
                    
                    # Init time workspace
                    if not sTimeSave in a2oData:
                        a2oData[sTimeSave] = {}; 
                    else:
                        pass
                    
                    # Save variable
                    a2oData[sTimeSave][sVarName] = a2dVarDef
                    
                    # Save time steps
                    a1oTimeSteps.append(sTimeSave)
                    
                    # Increase time step
                    oTimeSave_P1 += datetime.timedelta(seconds = iTimeForecastUnit)
                    
                    # info
                    oLogStream.info(' ----> Save raw data :: VarName: ' + sVarName + ' TimeStep: ' + sTimeSave + ' ... OK')
                #--------------------------------------------------------------------------------

            else:
                
                #--------------------------------------------------------------------------------
                # Exit code to date run
                oLogStream.info(' ----> Get raw data :: VarName: ' + sVarName + 
                            ' TimeStepFrom: ' + sTimeStep_P1 + ' TimeStepTo: ' + sTimeStep_P2 + ' ... SKIPPED --- STARTING TIME ')
                iFMZero = iFMZero + 1;
                iTimeSteps = 0;
                #--------------------------------------------------------------------------------
            
            #--------------------------------------------------------------------------------
            
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------                            
        # Cycle on timestep(s) to re-process variable
        a1oTimeSteps = set(a1oTimeSteps)
        a1oTimeSave = sorted(list(a1oTimeSteps))

        a2oDataFinal = {};
        for sTimeSave in a1oTimeSave:
            
            # Init time workspace
            if not sTimeSave in a2oDataFinal:
                a2oDataFinal[sTimeSave] = {}; 
            else:
                pass
            
            # info
            oLogStream.info(' ----> Save data :: TimeStep: ' + sTimeSave + ' ... ')
            
            # Select method to process raw data
            oLogStream.info(' -----> Apply updating function ... ')
            if oOpVarMath:
                if oOps_FuncMethod:
                    if set(a1oOpVarComp).issubset(a2oData[sTimeSave].keys()):
                        
                        oLogStream.info(' ----> Save data :: Variables: ' + str(a2oData[sTimeSave].keys()) + ' ... ')
                        
                        a2dVarOp = oOps_FuncMethod(a1oOpVarComp, a2oData[sTimeSave])
                        
                        # Debug
                        #a2dVar1=a2oData[sTimeSave]['10_metre_u_wind_component']
                        #a2dVar2=a2oData[sTimeSave]['10_metre_v_wind_component']
                        #plt.figure(1)
                        #plt.imshow(a2dVar1); plt.colorbar()
                        #plt.figure(2)
                        #plt.imshow(a2dVar2); plt.colorbar()
                        #plt.figure(3)
                        #plt.imshow(a2dVarOp); plt.colorbar()
                        #plt.show()

                        a2oDataFinal[sTimeSave][sOpVarName] = a2dVarOp
                        
                        oLogStream.info(' -----> Apply updating function ... OK --- SAVE DERIVED VAR')
                    else:
                        pass
                else:
                    a2oDataFinal[sTimeSave][sOpVarName] = a2oData[sTimeSave][sVarName]
                    oLogStream.info(' -----> Apply updating function ... NOT DEFINED --- SAVE RAW VAR')
            else:
                a2oDataFinal[sTimeSave][sOpVarName] = a2oData[sTimeSave][sVarName]
                oLogStream.info(' -----> Apply updating function ... NOT DEFINED --- SAVE RAW VAR')
            
            # Info
            oLogStream.info(' ----> Save data :: Variables: ' + str(a2oData[sTimeSave].keys()) + ' ... OK')
            oLogStream.info(' ----> Save data :: TimeStep: ' + sTimeSave + ' ... OK')
        #--------------------------------------------------------------------------------    
        
        #--------------------------------------------------------------------------------
        # File object
        oFileObject['Data'] = a2oDataFinal
        oFileObject['GeoX'] = a2dGeoX
        oFileObject['GeoY'] = np.flipud(a2dGeoY)
        oFileObject['GeoZ'] = None
        oFileObject['Attributes'] = oFileAttrs
        oFileObject['GeoInfo'] = {}
        oFileObject['GeoInfo']['Proj'] = oProjParams
        oFileObject['Time'] = a1oTimeSave
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Return file object
        return oFileObject
        #--------------------------------------------------------------------------------
        
    #--------------------------------------------------------------------------------
    
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Class to manage TIFF files
class FileMat:
    
    #--------------------------------------------------------------------------------
    # Class init
    def __init__(self, sFilePath, sFileName, sFileType, sFileMode):
        
        self.sFilePath = sFilePath
        self.sFileName = sFileName
        self.sFileType = sFileType
        self.sFileMode = sFileMode
        
        # Open file (read or write mode)
        self.openFile(); 
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Open mat file (in read mode)
    def openFile(self):
        
        import scipy.io
        
        try:
            oFile = scipy.io.loadmat(join(self.sFilePath, self.sFileName))
            self.oFileData = oFile
        except IOError as oError:
            GetException(' -----> ERROR: in open file (MAT I/O)' + ' [' + str(oError) + ']',1,1)

    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Read mat file
    def readFileData(self, oOpVarMethod=None):
        
        # List of variable(s) in matlab dictionary
        # a1sFileVar = ['a1iCodeSensor', 'a1dAlt', 'a1dLon', 'a1dData', 'a2dMeteoVar', 'a1sDate', 'a1dLat'];
        
        oFileObject = {}
        oFileObject['Data'] = self.oFileData['a2dMeteoVar']
        oFileObject['GeoX'] = self.oFileData['a1dLon']
        oFileObject['GeoY'] = self.oFileData['a1dLat']
        oFileObject['GeoZ'] = self.oFileData['a1dAlt']
        oFileObject['Attributes'] = {}
        oFileObject['Attributes']['Code'] = self.oFileData['a1iCodeSensor']
        oFileObject['Proj'] = None
        
        a1oTimes = self.oFileData['a1sDate']
        iTimeLen = len(a1oTimes[0][:])
        
        a1oTime = []
        for iI in range(0,iTimeLen):
            
            sTime = a1oTimes[0][iI][0].encode('utf-8')
            a1oTime.append(sTime)
        
        oFileObject['Time'] = a1oTime
        
        return oFileObject

    #--------------------------------------------------------------------------------
    
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Class to manage TIFF files
class FileBinary:
    
    #--------------------------------------------------------------------------------
    # Class init
    def __init__(self, sFilePath, sFileName, sFileType, sFileMode):
        
        self.sFilePath = sFilePath
        self.sFileName = sFileName
        self.sFileType = sFileType
        self.sFileMode = sFileMode
        
        # Open file (read or write mode)
        self.openFile(); 
    
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Open binary file 
    def openFile(self):
        
        try: # Read = 'rb: Write = 'wb'
            oFile = open(join(self.sFilePath, self.sFileName), self.sFileMode + 'b') 
            self.oFileData = oFile   
        except IOError as oError:
            GetException(' -----> ERROR: in open file (BINARY I/O)' + ' [' + str(oError) + ']',1,1)

    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to write 1d binary variable
    def write1DVar(self, a2dVarData, oVarFeat):
        
        # Import struct library
        import struct
        
        # Get variable features
        sVarFormat = str(oVarFeat['Format'])
        iVarScaleFactor = int(oVarFeat['ScaleFactor'])
        
        # Define nodata value
        dNoData = -9999.0
        dNoData = dNoData/iVarScaleFactor

        # Values shape (1d)
        iNVals = a2dVarData.shape[0]*a2dVarData.shape[1]
        # Values format sVarFormat = 'i'
        sDataFormat=sVarFormat* iNVals
        
        # Define nodata value (instead of NaN values)
        a2dVarData[np.where(np.isnan(a2dVarData))] = dNoData
        
        # NOTA BENE:
        # NON OCCORRE FARE IL FLIPUD SE LE VAR SONO ORIENTATE IN MODO CORRETTO partendo da angolo
        # IN BASSO A SX [sud-->nord ovest --> est]
        #a1iVarData = np.int32((numpy.flipud(a2dVarData)).reshape(iNVals, order='F') * iScaleFactor)
        
        a1iVarData = np.int32(((a2dVarData)).reshape(iNVals, order='F') * iVarScaleFactor)
        oBinData = struct.pack(sDataFormat,*(a1iVarData))
        
        self.oFileData.write(oBinData)
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to close binary file
    def closeFile(self):
        self.oFileData.close()
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to read 1dV variable in binary format
    def read1DVar(self, iRows, iCols, iVarScaleFactor):
        
        import struct
        
        # Values shape (1d)
        iNVals = iRows*iCols
        # Values format
        sDataFormat='i'* iNVals
        
        oFileCheck = self.oFileData.read(-1)
        a1dVarDataCheck = struct.unpack(sDataFormat, oFileCheck)
        
        a2dVarDataCheck = np.reshape(a1dVarDataCheck,(iRows, iCols), order='F')
        #a2dVarDataCheck = np.flipud(a2dVarDataCheck);
        a2dVarDataCheck = a2dVarDataCheck/iVarScaleFactor
        
        oFileObject = {}
        oFileObject['Data'] = a2dVarDataCheck
        oFileObject['GeoX'] = None
        oFileObject['GeoY'] = None
        oFileObject['GeoZ'] = None
        oFileObject['Attributes'] = None
        oFileObject['GeoInfo'] = None
        oFileObject['Time'] = None
        
        return oFileObject
    
    #--------------------------------------------------------------------------------
            
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Class to manage TIFF files
class FileTiff:

    #--------------------------------------------------------------------------------
    # Class init
    def __init__(self, sFilePath, sFileName, sFileType, sFileMode):
        
        self.sFilePath = sFilePath
        self.sFileName = sFileName
        self.sFileType = sFileType
        self.sFileMode = sFileMode
        
        # Open file (read or write mode)
        self.openFile(); 
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Open tiff file (in read or write mode)
    def openFile(self):
        
        from PIL import Image
        
        try:
            oFile = Image.open(join(self.sFilePath, self.sFileName), self.sFileMode)
            self.oFileData = oFile
        except IOError as oError:
            GetException(' -----> ERROR: in open file (TIFF I/O)' + ' [' + str(oError) + ']',1,1)

    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Read 2d variable
    def read2DVar(self, iRowsRef, iColsRef):
        
        a1oDataVar = list(self.oFileData.getdata()) 
        a1dDataVar = np.asarray(a1oDataVar, dtype=np.float32) 
        a2dDataVar = np.reshape(a1dDataVar,(iRowsRef,iColsRef))
        
        oFileObject = {}
        oFileObject['Data'] = np.flipud(a2dDataVar)
        oFileObject['GeoX'] = None
        oFileObject['GeoY'] = None
        oFileObject['GeoZ'] = None
        oFileObject['Attributes'] = None
        oFileObject['GeoInfo'] = None
        oFileObject['Time'] = None
        
        return oFileObject
        
        # GDAL ...
        #oFileTiff = osgeo.gdal.Open(sFileNameTiff)
        #a2dDataVarInterp = np.zeros((iRowsRef, iColsRef))
        #a2dDataVarInterp = oFileTiff.ReadAsArray()
        #a2dDataVarInterp = np.flipud(a2dDataVarInterp)
    
    #--------------------------------------------------------------------------------
        
    #--------------------------------------------------------------------------------
    # Close tiff file
    def closeFile(self):
        self.oFileData.close()
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Convert tiff 2 ascii
    def tiff2ascii(self, sFileName_Ascii):
        
        import subprocess
        
        sLineCommand = ('gdal_translate -of AAIGrid ' + join(self.sFilePath, self.sFileName) + 
                        ' ' + sFileName_Ascii)
                
        print(sLineCommand)
        oPr = subprocess.Popen(sLineCommand, shell=True)
        oOut, oErr = oPr.communicate()
        print oOut, oErr
        
        pass
    
    #--------------------------------------------------------------------------------
    
#################################################################################

#################################################################################
# Class to manage ASCII grid files
class FileAscii:
    
    #--------------------------------------------------------------------------------
    # Variable tags
    getNCOLS = "ncols"
    getNROWS = "nrows"
    getXLLCORNER = "xllcorner"
    getYLLCORNER = "yllcorner"
    getCELLSIZE = "cellsize"
    getNODATAVALUE = "NODATA_value"
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Class init
    def __init__(self, sFilePath, sFileName, sFileType, sFileMode):
        
        self.sFilePath = sFilePath
        self.sFileName = sFileName
        self.sFileType = sFileType
        self.sFileMode = sFileMode
        
        # Open file (read or write mode)
        self.openFile(); 
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Open ascii file (in read or write mode)
    def openFile(self):
        
        try:
            oFile = open(join(self.sFilePath, self.sFileName), self.sFileMode)
            self.oFileData = oFile
        except IOError as oError:
            GetException(' -----> ERROR: in open file (ASCII I/O)' + ' [' + str(oError) + ']',1,1)
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Close ascii file
    def closeFile(self):
        self.oFileData.close()
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Convert ascii 2 tiff
    def ascii2tiff(self, sFileName_Tiff):
        
        # Check method 
        try:
        
            import subprocess
            
            sLineCommand = ('gdal_translate -of "GTiff" ' + join(self.sFilePath, self.sFileName) + 
                            ' ' + sFileName_Tiff)
            
            #print(sLineCommand)
            oPr = subprocess.Popen(sLineCommand, shell=True)
            oOut, oErr = oPr.communicate()
            
            print oOut, oErr
        
        except:
            # Exit status with error
            GetException(' -----> ERROR: in ascii2tiff function (ASCII I/O)',1,1)
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Write 1D data in ascii file (column array)
    def read1DVar(self):
        
        # Check method 
        try:
            
            # Read all data
            oVarData = np.loadtxt(self.oFileData, skiprows=0)
            
            # Save file data in a dictionary
            oFileObject = {}
            oFileObject['Data'] = oVarData
            oFileObject['GeoX'] = None
            oFileObject['GeoY'] = None
            oFileObject['GeoZ'] = None
            oFileObject['Attributes'] = None
            oFileObject['GeoInfo'] = None
            oFileObject['Time'] = None
        
            return oFileObject
    
        except:
            # Exit status with error
            GetException(' -----> ERROR: in readFileData function (ASCII I/O)',1,1)
    
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Write 1D data in ascii file (column array)
    def write1DVar(self, a1dDataValues, sDataFormat=None):
        
        # Check method 
        try:
        
            # Defining max number of digits before comma
            dVarDataMin = np.nanmin(np.unique(a1dDataValues))
            dVarDataMax = np.nanmax(np.unique(a1dDataValues))
            iVarDataMax = int(dVarDataMax)
            
            # Get data format and digits
            if sDataFormat == 'f':
                iDigitNum = len(str(iVarDataMax)) + 3
                sFmt = '%'+str(iDigitNum)+'.2' + sDataFormat;
            elif sDataFormat == 'i':
                iDigitNum = len(str(iVarDataMax)) 
                sFmt = '%'+str(iDigitNum)+'.0' + sDataFormat;
            else:
                GetException(' -----> WARNING: data format unknown! Set float type!', 2, 1)
                iDigitNum = len(str(iVarDataMax)) + 3
                sFmt = '%'+str(iDigitNum)+'.2' + sDataFormat;
                
            # Write array values
            np.savetxt(self.oFileData, a1dDataValues, fmt=sFmt,  newline='\n')
        
        except:
            # Exit status with error
            GetException(' -----> ERROR: in write1DVar function (ASCII I/O)',1,1)

    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Read data from 
    def readInfoFile(self):
        
        # Get data from all lines
        oInfoFile = self.oFileData.readlines()
        
        oInfoData = {}; iL = 0;
        for sLineFile in oInfoFile:
            oInfoData[iL] = sLineFile
            iL = iL + 1
        
        # Save file data in a dictionary
        oFileObject = {}
        oFileObject['Data'] = oInfoData
        oFileObject['GeoX'] = None
        oFileObject['GeoY'] = None
        oFileObject['GeoZ'] = None
        oFileObject['Attributes'] = None
        oFileObject['GeoInfo'] = None
        oFileObject['Time'] = None
                
        return oFileObject
        
    #--------------------------------------------------------------------------------
       
    #--------------------------------------------------------------------------------
    # Read data from ascii file (columns arrays)
    def readFileData(self, oDataComp=None):
        
        # Check method 
        try:
            
            if oDataComp:
                # Set skiprows
                if oDataComp['skiprows']:
                    iSkipRows = oDataComp['skiprows'];
                else:
                    iSkipRows = 0
            else:
                iSkipRows = 0
            
            # Read all data
            a2dVarData = np.loadtxt(self.oFileData, skiprows=iSkipRows)
            
            # Select data using keys
            oVarData = {}
            for sCompKey in oDataComp:
                if not sCompKey == 'skiprows':
                    iCompValue = int(oDataComp[sCompKey]) - 1
                    a1dVarData = a2dVarData[:,iCompValue]
                    oVarData[sCompKey] = a1dVarData;
           
            # Save file data in a dictionary
            oFileObject = {}
            oFileObject['Data'] = oVarData
            oFileObject['GeoX'] = None
            oFileObject['GeoY'] = None
            oFileObject['GeoZ'] = None
            oFileObject['Attributes'] = None
            oFileObject['GeoInfo'] = None
            oFileObject['Time'] = None
                    
            return oFileObject
    
        except:
            # Exit status with error
            GetException(' -----> ERROR: in readFileData function (ASCII I/O)',1,1)
    
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Read ArcGrid data
    def readArcGrid(self):
        
        # Check method 
        try:
            from string import atof, atoi, split
    
            # Read Header
            a1oVarHeader = {
                "ncols"        : atoi(split(self.oFileData.readline())[1]),
                "nrows"        : atoi(split(self.oFileData.readline())[1]),
                "xllcorner"    : atof(split(self.oFileData.readline())[1]),
                "yllcorner"    : atof(split(self.oFileData.readline())[1]),
                "cellsize"     : atof(split(self.oFileData.readline())[1]),
                "NODATA_value" : atof(split(self.oFileData.readline())[1]),
            }
            
            iNCols = a1oVarHeader["ncols"]; iNRows = a1oVarHeader["nrows"]
            
            # Read grid values
            a2dVarData = np.zeros((iNRows, iNCols)) 
            a2dVarData = np.loadtxt(self.oFileData, skiprows=0)
            
            # Debugging
            #plt.figure(1)
            #plt.imshow(a2dVarData); plt.colorbar();
            #plt.show()
            
            oFileObject = {}
            oFileObject['Data'] = a2dVarData
            oFileObject['GeoX'] = None
            oFileObject['GeoY'] = None
            oFileObject['GeoZ'] = None
            oFileObject['Attributes'] = None
            oFileObject['GeoInfo'] = {}
            oFileObject['GeoInfo']['Coords'] = a1oVarHeader
            oFileObject['Time'] = None
    
            return oFileObject
    
        except:
            # Exit status with error
            GetException(' -----> ERROR: in readFileData function (ASCII I/O)',1,1)
    
    #----------------------------------------------------------------------------
    
    #----------------------------------------------------------------------------
    # Write 2dVar
    def writeArcGrid(self, a2dVarData, a1oVarHeader, sDataFormat=None):
        
        # sDataFormat: f, i, None
        
        # Check method 
        try:
            
            # Defining max number of digits before comma
            dVarDataMin = np.nanmin(np.unique(a2dVarData))
            dVarDataMax = np.nanmax(np.unique(a2dVarData))
            iVarDataMax = int(dVarDataMax)
            
            # Get data format and digits
            if sDataFormat == 'f':
                iDigitNum = len(str(iVarDataMax)) + 3
                sFmt = '%'+str(iDigitNum)+'.2' + sDataFormat;
            elif sDataFormat == 'i':
                iDigitNum = len(str(iVarDataMax)) 
                sFmt = '%'+str(iDigitNum) + sDataFormat;
            else:
                GetException(' -----> WARNING: data format unknown! Set float type!', 2, 1)
                iDigitNum = len(str(iVarDataMax)) + 3
                sFmt = '%'+str(iDigitNum)+'.2' + sDataFormat;
            
            # Write header
            self.oFileData.write("ncols\t%i\n" % a1oVarHeader["ncols"])
            self.oFileData.write("nrows\t%i\n" % a1oVarHeader["nrows"])
            self.oFileData.write("xllcorner\t%f\n" % a1oVarHeader["xllcorner"])
            self.oFileData.write("yllcorner\t%f\n" % a1oVarHeader["yllcorner"])
            self.oFileData.write("cellsize\t%f\n" % a1oVarHeader["cellsize"])
            if sDataFormat == 'f':
                self.oFileData.write("NODATA_value\t%f\n" % a1oVarHeader["NODATA_value"])
            elif sDataFormat == 'i':
                self.oFileData.write("NODATA_value\t%i\n" % a1oVarHeader["NODATA_value"])
            else:
                GetException(' -----> WARNING: no data format set in float type!', 2, 1)
                self.oFileData.write("NODATA_value\t%f\n" % a1oVarHeader["NODATA_value"])
            
            # Write grid values
            #sDataFormat = '%'+str(iDigitNum)+'.2f';
            np.savetxt(self.oFileData, a2dVarData, delimiter=' ', fmt=sFmt,  newline='\n')

        except:
            # Exit status with error
            GetException(' -----> ERROR: in writeArcGrid function (ASCII I/O)',1,1)
        
    #----------------------------------------------------------------------------
    
#################################################################################

#################################################################################
# Class to manage NETCDF grid files
class FileNetCDF:
    
    #----------------------------------------------------------------------------
    # Class init
    def __init__(self, sFilePath, sFileName, sFileType, sFileMode):
        
        # Common variable(s)
        self.sFilePath = sFilePath
        self.sFileName = sFileName
        self.sFileType = sFileType
        self.sFileMode = sFileMode
        
        # Open file (read or write mode)
        self.openFile(); 
        
    #----------------------------------------------------------------------------
    
    #----------------------------------------------------------------------------   
    # Closing file 
    def closeFile(self):
        self.oFileData.close()
    #----------------------------------------------------------------------------
    
    #----------------------------------------------------------------------------
    # Opening file    
    def openFile(self):
        
        try:
            from netCDF4 import Dataset
        except:
            from scipy.io.netcdf import netcdf_file as Dataset
            GetException(' -----> WARNING: NetCDF module import from scipy (usually imported from netcdf-python)!', 2, 1)

        try:
            # NetCDF type: NETCDF3_CLASSIC , NETCDF3_64BIT , NETCDF4_CLASSIC , NETCDF4
            oFile = Dataset(join(self.sFilePath, self.sFileName), self.sFileMode, format='NETCDF4')
            #oFile = Dataset(join(self.sFilePath, self.sFileName), self.sFileMode, format='NETCDF3_64BIT')
            self.oFileData = oFile
        except IOError as oError:
            GetException(' -----> ERROR: in open file (NETCDF I/O)' + ' [' + str(oError) + ']',1,1)
        
    #----------------------------------------------------------------------------
    
    #----------------------------------------------------------------------------
    # Method to check variable name
    def checkVarName(self, sVarName):
        
        bVarExist = False
        if sVarName in self.oFileData.variables:
            bVarExist = True
        else:
            bVarExist = False
        
        return bVarExist
    
    #----------------------------------------------------------------------------
    
    #----------------------------------------------------------------------------
    # Get file attributes common
    def getFileAttrsCommon(self):
        
        oAttrs = self.oFileData.ncattrs()
        oAttrsFile = {}
        for sAttrName in oAttrs:
            
            oAttrValue = self.oFileData.getncattr(sAttrName.encode('utf-8'))
            
            if isinstance(oAttrValue, basestring):
                oAttrValue = oAttrValue.encode('utf-8')
            elif isinstance(oAttrValue, (np.float)):
                oAttrValue = np.float32(oAttrValue)   
            elif isinstance(oAttrValue, (np.int32)):
                oAttrValue = np.int32(oAttrValue)
            elif isinstance(oAttrValue, (np.int64)):
                oAttrValue = np.int32(oAttrValue)
            else:
                GetException(' -----> ERROR: in reading file attribute(s). Attribute type not defined!',1,1)
                
            oAttrsFile[sAttrName.encode('utf-8')] = oAttrValue

        return oAttrsFile
    
    #----------------------------------------------------------------------------
    
    #----------------------------------------------------------------------------
    # Get 2d variable (using variable name)
    def get2DVar(self, sVarName):
        
        a2dVarName_IN = self.oFileData.variables[sVarName][:];
        a2dVarName_OUT = np.transpose(np.rot90(a2dVarName_IN,-1));
        
        return a2dVarName_OUT
    #----------------------------------------------------------------------------
    
    #----------------------------------------------------------------------------
    # Get 3d variable (using variable name)
    def get3DVar(self, sVarName):
        
        a3dVarName_IN = self.oFileData.variables[sVarName][:];
        
        a3dVarName_OUT = np.zeros([a3dVarName_IN.shape[1], a3dVarName_IN.shape[2], a3dVarName_IN.shape[0]])
        for iT in range(0,a3dVarName_IN.shape[0]):
            a2dVarName_IN = np.transpose(np.rot90(a3dVarName_IN[iT,:,:],-1));
            a3dVarName_OUT[:,:,iT] = a2dVarName_IN
            
            a2dVarName_IN[a2dVarName_IN < -900] = np.nan
            
            # Debug
            #plt.figure(1); plt.imshow(a2dVarName_IN); plt.colorbar(); plt.clim(-10,40);
            #plt.show()
        
        return a3dVarName_OUT
    #----------------------------------------------------------------------------
    
    
    #----------------------------------------------------------------------------
    # Write field dimension
    def writeDims(self, sDimVar, iDimValue):
                
        # Dim declaration
        self.oFileData.createDimension(sDimVar, iDimValue)
        
    #----------------------------------------------------------------------------
    
    #----------------------------------------------------------------------------
    # Write 3d variables 
    def write3DVar(self, sVarName, a3dVarDataXYT, oVarAttr, sVarFormat, sVarDimT=None, sVarDimY=None, sVarDimX=None):
        
        # Creating variable
        oVar = self.oFileData.createVariable(sVarName, sVarFormat, (sVarDimT, sVarDimY, sVarDimX,), zlib = True)
        
        # Saving all variable attribute(s)
        for sVarAttr in oVarAttr:
            # Retrivieng attribute value
            sVarOptValue = oVarAttr[sVarAttr]
            # Saving attribute
            oVar.setncattr(sVarAttr.lower(),str(sVarOptValue))
        
        # Debug to check map orientation
        #if sVarName == 'Terrain':
        #    plt.figure(1)
        #    plt.imshow(np.transpose(np.rot90(a2dVarDataXY,-1))); plt.colorbar()
        #    plt.show()
        
        # Define 3d field(s)
        a3dVarDataTYX = np.zeros([a3dVarDataXYT.shape[2], a3dVarDataXYT.shape[0], a3dVarDataXYT.shape[1]])
        for iStep in range(0, a3dVarDataXYT.shape[2]):
            
            # Get data
            a2dVarDataXY = np.zeros([a3dVarDataXYT.shape[0], a3dVarDataXYT.shape[1]])
            a2dVarDataXY = a3dVarDataXYT[:,:, iStep]
            
            # Organize data
            a2dVarDataYX = np.zeros([a3dVarDataXYT.shape[0], a3dVarDataXYT.shape[1]])
            a2dVarDataYX = np.transpose(np.rot90(a2dVarDataXY,-1));
            
            # Store data
            a3dVarDataTYX[iStep, : , : ] = a2dVarDataYX
        
        # Save data
        oVar[:,:] = np.transpose(np.rot90(a3dVarDataXYT,-1));
    
    #---------------------------------------------------------------------------- 
    
    
    #----------------------------------------------------------------------------
    # Write 2d variables 
    def write2DVar(self, sVarName, a2dVarDataXY, oVarAttr, sVarFormat, sVarDimY=None, sVarDimX=None):
        
        # Creating variable
        oVar = self.oFileData.createVariable(sVarName, sVarFormat, (sVarDimY, sVarDimX,), zlib = True)
        
        # Saving all variable attribute(s)
        for sVarAttr in oVarAttr:
            # Retrivieng attribute value
            sVarOptValue = oVarAttr[sVarAttr]
            # Saving attribute
            oVar.setncattr(sVarAttr.lower(),str(sVarOptValue))
        
        # Debug to check map orientation
        #if sVarName == 'Terrain':
        #    plt.figure(1)
        #    plt.imshow(np.transpose(np.rot90(a2dVarDataXY,-1))); plt.colorbar()
        #    plt.show()
        
        # Saving variable data
        oVar[:,:] = np.transpose(np.rot90(a2dVarDataXY,-1));
    
    #----------------------------------------------------------------------------    
    
    #----------------------------------------------------------------------------
    # Write 1d variables 
    def write1DVar(self, sVarName, a1dVarData, oVarAttr, sVarFormat, sVarDimY=None, sVarDimX=None):
        
        # Use Y var to create column array
        sVarDim = sVarDimY
        
        # Creating variable
        oVar = self.oFileData.createVariable(sVarName, sVarFormat, (sVarDim), zlib = True)
        # Saving all variable attribute(s)
        for sVarAttr in oVarAttr:
            # Retrivieng attribute value
            sVarOptValue = oVarAttr[sVarAttr]
            # Saving attribute
            oVar.setncattr(sVarAttr.lower(),str(sVarOptValue))
        
        # Saving variable data
        oVar[:] = a1dVarData;
        
    #----------------------------------------------------------------------------    
    
    #----------------------------------------------------------------------------
    # Method to get time information
    def getTime(self):
        
        a1sTime = None;
        try:
            from datetime import datetime
            from netCDF4 import num2date, date2num
            
            oTime = self.oFileData.variables['time'];
            a1oTime = num2date(oTime[:],units=oTime.units,calendar=oTime.calendar)
            
            a1sTime = []
            for oTime in a1oTime:
                sTime = oTime.strftime('%Y%m%d%H%M')
                a1sTime.append(sTime)
        except:
            a1sTime = None;
        
        return sorted(a1sTime)
    #----------------------------------------------------------------------------
    
    #----------------------------------------------------------------------------
    # Method to write time information
    def writeTime(self, oTime, sVarFormat='f8', sVarDimT=None, dTimeStep=None):
        
        from datetime import datetime
        from netCDF4 import num2date, date2num
        
        iTimeSteps = len(oTime)
        
        oDateFrom = datetime.strptime(oTime[0],'%Y%m%d%H%M')
        oDateTo = datetime.strptime(oTime[-1],'%Y%m%d%H%M')
        oDateRef = datetime.strptime('197001010000','%Y%m%d%H%M')
        
        dTimeStepCum = -dTimeStep
        a2iBnds = np.zeros([iTimeSteps,2])
        oDates = []; a1oBnds = []; a1dElapsed = []
        for iTime, sTime in enumerate(oTime):
            oDates.append(datetime(int(sTime[0:4]), int(sTime[4:6]), int(sTime[6:8]), int(sTime[8:10]), int(sTime[10:12])))
            
            a2iBnds[iTime][0] = dTimeStepCum
            a2iBnds[iTime][1] = dTimeStepCum + dTimeStep
            
            a1oBnds.append(dTimeStepCum)
            a1oBnds.append(dTimeStepCum + dTimeStep)
            
            a1dElapsed.append(dTimeStepCum)
            
            dTimeStepCum = dTimeStepCum + dTimeStep
            
        # Convert bnd from list to float
        a1dBnds = [float(iI) for iI in a1oBnds]
        
        # Times
        oTimes = self.oFileData.createVariable(sVarDimT, sVarFormat,(sVarDimT,))
        oTimes.calendar = 'gregorian'
        oTimes.units = 'hours since ' + oDateFrom.strftime('%Y-%m-%d %H:%M:%S')
        oTimes.bounds = 'time_bnds'
        
        oTimes[:] = date2num(oDates,units=oTimes.units, calendar=oTimes.calendar)
        
        # Time Bounds
        oTimeBounds = self.oFileData.createVariable('time_bnds','d',(sVarDimT, 'ntime',), zlib = True)
        oTimeBounds.time = str(np.array(a1dElapsed))
        oTimeBounds.time_bounds = a1dBnds
        oTimeBounds.time_date = str(np.array(oTime))
        oTimeBounds.datestart = oDateFrom.strftime('%Y-%m-%d %H:%M:%S')
        oTimeBounds.dateend = oDateTo.strftime('%Y-%m-%d %H:%M:%S')
        oTimeBounds.dateref = oDateRef.strftime('%Y-%m-%d %H:%M:%S')
        oTimeBounds.axis = 'T'
        
        oTimeBounds[:,:] = a2iBnds
        
        # Debug
        #oDates_Check = num2date(oTimes[:],units=oTimes.units,calendar=oTimes.calendar)
        #print(oDates_Check)
        
    #----------------------------------------------------------------------------
    
    #----------------------------------------------------------------------------  
    # Write common file attribute(s)
    def writeFileAttrsCommon(self, oFileAttributes):
        
        # GENERAL ATTRIBUTE(S) ---> FROM FILE
        # Cycle on file attribute(s)
        for sFileAttr in oFileAttributes:
            # Retrieve attribute value
            sFileValue = oFileAttributes[sFileAttr]
            # Save attribute
            self.oFileData.setncattr(sFileAttr, sFileValue)
            
        # EXTRA ATTRIBUTE(S) ---> FROM SCRIPT
        self.oFileData.filename = self.sFileName
        self.oFileData.filedate = 'Created ' + time.ctime(time.time())

    #----------------------------------------------------------------------------
    
    #----------------------------------------------------------------------------  
    # Write extra file attribute(s)
    def writeFileAttrsExtra(self, oParamsInfo, oGeoInfo):
        
        # Insert parameter(s) information
        for oParamKeys, oParamsValue in oParamsInfo.items():
            
            # Avoid save DB information in file(s)
            if oParamKeys != 'DB':
            
                if isinstance(oParamsValue,dict):
                    sStrValues=''
                    for sKey, dValue in oParamsValue.items():
                        sStrValues = sStrValues + sKey + ':' + str(dValue) + ';'
                    oParamsValue = sStrValues
                else:
                    pass
            
                self.oFileData.setncattr(oParamKeys.lower(), str(oParamsValue))
                
            else:
                pass
        
        # Insert geo information
        for oGeoKeys, oGeoValue in oGeoInfo.items():
            self.oFileData.setncattr(oGeoKeys.lower(), oGeoValue)    

    #----------------------------------------------------------------------------
    
    #----------------------------------------------------------------------------
    # Write geographical system
    def writeGeoSystem(self, oGeoSystemInfo, a1dGeoBox=None):
        
        # Open geosystem variable(s)
        oGeoSystem = self.oFileData.createVariable('crs','i')
        
        # Insert geobox
        oGeoSystem.bounding_box = a1dGeoBox
        
        # Insert geosystem information
        for oGeoSystemKeys, oGeoSystemValue in oGeoSystemInfo.items():
            oGeoSystem.setncattr(oGeoSystemKeys.lower(), oGeoSystemValue)
        
    #----------------------------------------------------------------------------
    
#################################################################################   








