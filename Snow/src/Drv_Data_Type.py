"""
Class Features

Name:          Drv_Data_Type
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20150724'
Version:       '2.0.4'
"""

######################################################################################
# Logging
import logging
oLogStream = logging.getLogger('sLogger')

# Library
import os
import subprocess

import numpy as np

import Lib_Data_Apps as Lib_Data_Apps

from os.path import join
from scipy.interpolate import griddata

from Drv_Data_IO import Drv_Data_IO

from GetException import GetException

# Debug
import matplotlib.pylab as plt
######################################################################################

#-------------------------------------------------------------------------------------
# Class
class Drv_Data_Type:

    #-------------------------------------------------------------------------------------
    # Method init class
    def __init__(self, oDataGeo=None, oDataAnalyzed=None, oDataInfo=None):
        
        self.oDataGeo = oDataGeo
        self.oDataAnalyzed = oDataAnalyzed
        self.oDataInfo = oDataInfo
        self.a1oFileObject = {}
        
    #-------------------------------------------------------------------------------------  
    
    #-------------------------------------------------------------------------------------
    # Method to select Time
    def getTime(self, sTime, a1oTimes):
        
        try:
            self.a1iIndex = a1oTimes.index(sTime)
            self.bIndex = True
        except:
            GetException(' -----> WARNING: no time step is available! Check input data!', 2, 1)
            self.a1iIndex = None
            self.bIndex = False
        
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to get variable value(s)
    def getVarPoint(self, oFileWorkspace=None, oVarOp=None, dNoData=None, sTime=None, sFileNameGeo=None ):
        
        # Check file workspace availability
        oPointObject = {}
        if oFileWorkspace:
            
            # Extract data from grid file (using a common method readFileData)
            oFileData = oFileWorkspace.readFileData(oVarOp)
            sVarName = oVarOp['Op_Load']['Name']
            
            # Get variable conversion app (if exists)
            sVarConversionApp = oVarOp['Op_Math']['Conversion']['Func']
            
            # Save data object ### CONTOLLO SU oFileData['Data'] da una eccezione!
            if oFileData:
                    
                self.getTime(sTime, oFileData['Time'])
                
                # Check index time boolean
                if self.bIndex:
                
                    # Select time
                    if isinstance(oFileData['Time'], basestring):
                        sTimeSel = oFileData['Time']
                    else:
                        sTimeSel = oFileData['Time'][self.a1iIndex]
                    
                    # Select data
                    a1dPointData = np.float32(oFileData['Data'][self.a1iIndex])
                    a1iPointCode = np.float32(oFileData['Attributes']['Code'][0])
                    a1dPointGeoX = np.float32(oFileData['GeoX'][0])
                    a1dPointGeoY = np.float32(oFileData['GeoY'][0])
                    a1dPointGeoZ = np.float32(oFileData['GeoZ'][0])
                    a1oPointGeoProj = oFileData['Proj']
                    
                    # Convert data variable
                    if sVarConversionApp != '':
                        oVarConversionApp = getattr(Lib_Data_Apps, sVarConversionApp)
                        a1dPointData = oVarConversionApp(a1oVarComp=None, a1oVarValues=a1dPointData)
                    else:
                        pass
                    
                    a1dPointData[a1dPointData==dNoData] = np.nan
                    
                    # Save data object
                    oPointObject = {};
                    oPointObject['Data'] = {}
                    oPointObject['Data'] [sTimeSel] = {}
                    oPointObject['Data'] [sTimeSel] [sVarName]= {}
                    oPointObject['Data'] [sTimeSel] [sVarName] = a1dPointData
                    oPointObject['Attributes'] = {}
                    oPointObject['Attributes']['Code'] = a1iPointCode
                    oPointObject['GeoX'] = a1dPointGeoX
                    oPointObject['GeoY'] = a1dPointGeoY
                    oPointObject['GeoZ'] = a1dPointGeoZ
                    oPointObject['Time'] = sTimeSel
                    oPointObject['GeoInfo'] = a1oPointGeoProj
                    
                else:
                    GetException(' -----> WARNING: no TIME step available ---> No POINT values! Check input data!', 2, 1)
                    oPointObject = None
            else:
                GetException(' -----> WARNING: no POINT values available! Check input data!', 2, 1)
                oPointObject = None

        else:
            GetException(' -----> WARNING: no POINT workspace available! Check input data!', 2, 1)
            oPointObject = None
            
        return oPointObject
        
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to get gridded values (hdf5 or grib)
    def getVarGrid(self, oFileWorkspace=None, oVarOp=None, dNoData=None, sTime=None, sFileNameGeo=None):
        
        # Check file workspace availability
        oGridObject = {}
        if oFileWorkspace:

            # Extract data from grid file (using a common method readFileData)
            if sFileNameGeo:
                oFileData = oFileWorkspace.readFileData(sFileNameGeo=sFileNameGeo, 
                                                        oOpVarLoad=oVarOp['Op_Load'], 
                                                        oOpVarMath=oVarOp['Op_Math'])
            else:
                oFileData = oFileWorkspace.readFileData(oOpVarLoad=oVarOp['Op_Load'], 
                                                        oOpVarMath=oVarOp['Op_Math'])
            
            # Save data object
            if oFileData:
            
                oGridObject['Data'] = oFileData['Data']
                oGridObject['Attributes'] = oFileData['Attributes']
                oGridObject['GeoX'] = oFileData['GeoX']
                oGridObject['GeoY'] = oFileData['GeoY']
                oGridObject['GeoZ'] = None
                oGridObject['Time'] = oFileData['Time']
                oGridObject['GeoInfo'] = oFileData['GeoInfo']
            
            else:
                GetException(' -----> WARNING: no GRID values available! Check input data!', 2, 1)
                oGridObject = None

        else:
            GetException(' -----> WARNING: no GRID workspace available! Check input data!', 2, 1)
            oGridObject = None
            
        return oGridObject
    
    #-------------------------------------------------------------------------------------
    
#-------------------------------------------------------------------------------------
