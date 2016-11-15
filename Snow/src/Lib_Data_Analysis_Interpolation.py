"""
Library Features:

Name:          Lib_Data_Analysis_Interpolation
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20150903'
Version:       '1.5.0'
"""

#################################################################################
# Logging
import logging
oLogStream = logging.getLogger('sLogger')

# Global libraries
import os
import datetime
import numpy as np
import subprocess
from os.path import join
from random import randint

from scipy.interpolate import griddata

import Lib_Data_Apps as Lib_Data_Apps
import Lib_Data_Analysis_Regression as Lib_Data_Analysis_Regression

from Drv_Data_IO import Drv_Data_IO
from GetException import GetException

# Debug
import matplotlib.pylab as plt
#################################################################################

#--------------------------------------------------------------------------------
# Method to use ZReg interpolation
def interpVarPointZReg(oDataGeo, oDataVar, oGeoXVar, oGeoYVar, oGeoZVar, 
                       dRadiusX, dRadiusY, dRadiusInfluence=None, 
                       iEPSGCode=None, sPathTemp=None, oDataAnalyzed=None):
    
    # Check temporary folder
    if not sPathTemp: sPathTemp = os.path.dirname(os.path.abspath(__file__))
    else: pass
    
    # Check EPSG Code
    if not iEPSGCode: iEPSGCode = 4326 
    else: pass
    
    # Retrivieng static information
    a2dGeoData = oDataGeo.a2dGeoData
    a2dGeoXRef = oDataGeo.oGeoData.a2dGeoX
    a2dGeoYRef = oDataGeo.oGeoData.a2dGeoY
    iColsRef = oDataGeo.oGeoData.iCols
    iRowsRef = oDataGeo.oGeoData.iRows
    a2bGeoDataFinite = oDataGeo.a2bGeoDataFinite
    a2bGeoDataNan = oDataGeo.a2bGeoDataNan
    
    # Searching undefined values
    a1bDataVarIndexNaN = []; a1bDataVarIndexFinite = []
    a1bDataVarIndexNaN = np.where(np.isnan(oDataVar) == True)
    a1bDataVarIndexFinite = np.where(np.isnan(oDataVar) == False)
    
    oDataVar = np.delete(oDataVar, a1bDataVarIndexNaN)
    oGeoXVar = np.delete(oGeoXVar, a1bDataVarIndexNaN)
    oGeoYVar = np.delete(oGeoYVar, a1bDataVarIndexNaN)
    oGeoZVar = np.delete(oGeoZVar, a1bDataVarIndexNaN)

    # Checking array dimensions number
    if oGeoXVar != None and oGeoYVar != None:
    
        if (len(oGeoXVar.shape) == 1):
            a1dGeoXVar = oGeoXVar
            a1dGeoYVar = oGeoYVar
        elif (len(oGeoXVar.shape) == 2):
            
            oGeoDims = oGeoXVar.shape
            
            a1dGeoXVar = np.reshape(oGeoXVar, (oGeoDims[0] * oGeoDims[1]))
            a1dGeoYVar = np.reshape(oGeoYVar, (oGeoDims[0] * oGeoDims[1]))
        
        if a1dGeoYVar is not None and a1dGeoXVar is not None: 
            if a1dGeoXVar.shape[0] == a1dGeoYVar.shape[0]:
                
                dGeoXRefMin = np.min(a2dGeoXRef)
                dGeoXRefMax = np.max(a2dGeoXRef)
                dGeoYRefMin = np.min(a2dGeoYRef)
                dGeoYRefMax = np.max(a2dGeoYRef)
                 
                # Checking values on selected domain
                a1iIndexSel = []
                a1iIndexSel = np.nonzero(((a1dGeoXVar>=dGeoXRefMin) & (a1dGeoXVar<=dGeoXRefMax)) &
                              ((a1dGeoYVar>=dGeoYRefMin) & (a1dGeoYVar<=dGeoYRefMax)))
                a1iIndexSel = a1iIndexSel[0]
            
            else:
                #print('geocoord are different shape ... stopped')
                a1iIndexSel = None;

        else:
            #print('geocoords are unknown ... stopped')
            a1iIndexSel = None; 
    
        # Ckecking on data quality
        if a1iIndexSel is not None:
            
            # Checking array dimensions number
            if (len(oDataVar.shape) == 1):
                a1dDataVar = oDataVar
            elif (len(oDataVar.shape) == 2):
                a1iDataDims = oDataVar.shape
                a1dDataVar = np.reshape(oDataVar, (a1iDataDims[0] * a1iDataDims[1]))
                
            # Checking array dimensions number
            if (len(oGeoZVar.shape) == 1):
                a1dGeoZVar = oGeoZVar
            elif (len(oGeoZVar.shape) == 2):
                a1iZDims = oGeoZVar.shape
                a1dGeoZVar = np.reshape(oGeoZVar, (a1iZDims[0] * a1iZDims[1]))

            # Selected data
            a1dDataVarSel = []; a1dGeoXVarSel = []; a1dGeoYVarSel = [];  a1dGeoZVarSel = [];
            a1dDataVarSel = a1dDataVar[a1iIndexSel]
            a1dGeoXVarSel = a1dGeoXVar[a1iIndexSel];
            a1dGeoYVarSel = a1dGeoYVar[a1iIndexSel];
            a1dGeoZVarSel = a1dGeoZVar[a1iIndexSel];
            
            # Sorting altitude value(s)
            a1iIndexSort = []
            a1iIndexSort = np.argsort(a1dGeoZVarSel)
        
            # Extracting sorting value(s) from finite arrays
            a1dGeoXVarSort = a1dGeoXVarSel[a1iIndexSort]; 
            a1dGeoYVarSort = a1dGeoYVarSel[a1iIndexSort];
            a1dGeoZVarSort = a1dGeoZVarSel[a1iIndexSort];
            a1dDataVarSort = a1dDataVarSel[a1iIndexSort];
        
            # Polyfit parameters and value(s) (--> linear regression)
            a1dPolyParams = np.polyfit(a1dGeoZVarSort, a1dDataVarSort, 1)
            a1dPolyValues = np.polyval(a1dPolyParams, a1dGeoZVarSort)
        
            # Defining residual for point value(s)
            a1dDataVarRes = a1dDataVarSort - a1dPolyValues;
            
            oDataVarResInterp = interpVarPointIDW(oDataGeo, a1dDataVarRes, 
                                                  a1dGeoXVarSort, a1dGeoYVarSort, a1dGeoZVarSort,
                                                  dRadiusX, dRadiusY, dRadiusInfluence, 
                                                  iEPSGCode, sPathTemp, oDataAnalyzed)
            
            
            # Interpolating polynomial parameters on z map
            a2dGeoDataZPoly = np.polyval(a1dPolyParams,a2dGeoData);
            
            # Calculating var (using z regression and idw method(s))
            a2dDataVarInterp = a2dGeoDataZPoly + oDataVarResInterp['Var_1'];
            
            # Checking interpolation values 
            a2dDataVarInterp[np.where(a2bGeoDataNan == True)] = np.nan
            
            # Debugging
            #plt.figure(1)
            #plt.imshow(a2dGeoData); plt.colorbar()
            #plt.figure(2)
            #plt.imshow(a2dDataVarInterp); plt.colorbar()
            #plt.show()
            
        else:
            # Data are not available on domain
            #print('data are not available on selected domain ... stopped')
            a2dDataVarInterp = np.zeros((iRowsRef, iColsRef)); 
            a2dDataVarInterp[:] = np.nan

    else:
        # Exit for data problems
        GetException(' -----> WARNING: all data are none! Data are not available!', 2, 1)
        a2dDataVarInterp = np.zeros((iRowsRef, iColsRef)); 
        a2dDataVarInterp[:] = np.nan
    
    # Store data in a final dictionary
    oWorkspace = {}
    oWorkspace['Var_1'] = a2dDataVarInterp
    oWorkspace['Var_2'] = None
    
    # Return results
    return oWorkspace
    
#-------------------------------------------------------------------------------- 

#--------------------------------------------------------------------------------
# Method to use IDW interpolation 
def interpVarPointIDW(oDataGeo, oDataVar, oGeoXVar, oGeoYVar, oGeoZVar, 
                      dRadiusX, dRadiusY, dRadiusInfluence=None, 
                      iEPSGCode=None, sPathTemp=None, oDataAnalyzed=None):
    
    # Check temporary folder
    if not sPathTemp: sPathTemp = os.path.dirname(os.path.abspath(__file__))
    else: pass
    
    # Check EPSG Code
    if not iEPSGCode: iEPSGCode = 4326 
    else: pass
    
    # Temporary file
    sRN = str(randint(0,1000))
    oTimeTemp = datetime.datetime.now(); sTimeTemp = oTimeTemp.strftime('%Y%m%d-%H%M%S_%f')
    sFileName = 'interpIDW_temp_' + sTimeTemp + '_' + sRN
    
    # Retrivieng static information
    a2dGeoData = oDataGeo.a2dGeoData
    a2dGeoXRef = oDataGeo.oGeoData.a2dGeoX
    a2dGeoYRef = oDataGeo.oGeoData.a2dGeoY
    iColsRef = oDataGeo.oGeoData.iCols
    iRowsRef = oDataGeo.oGeoData.iRows
    a2bGeoDataFinite = oDataGeo.a2bGeoDataFinite
    a2bGeoDataNan = oDataGeo.a2bGeoDataNan
    
    # NoData value
    dNoData = np.nan
    
    # Searching undefined values
    a1bDataVarIndexNaN = []; a1bDataVarIndexFinite = []
    a1bDataVarIndexNaN = np.where(np.isnan(oDataVar) == True)
    a1bDataVarIndexFinite = np.where(np.isnan(oDataVar) == False)
    
    oDataVar = np.delete(oDataVar, a1bDataVarIndexNaN)
    oGeoXVar = np.delete(oGeoXVar, a1bDataVarIndexNaN)
    oGeoYVar = np.delete(oGeoYVar, a1bDataVarIndexNaN)
    oGeoZVar = np.delete(oGeoZVar, a1bDataVarIndexNaN)

    # Checking array dimensions number
    if oGeoXVar != None and oGeoYVar != None:
    
        if (len(oGeoXVar.shape) == 1):
            a1dGeoXVar = oGeoXVar
            a1dGeoYVar = oGeoYVar
        elif (len(oGeoXVar.shape) == 2):
            
            oGeoDims = oGeoXVar.shape
            
            a1dGeoXVar = np.reshape(oGeoXVar, (oGeoDims[0] * oGeoDims[1]))
            a1dGeoYVar = np.reshape(oGeoYVar, (oGeoDims[0] * oGeoDims[1]))
        
        if a1dGeoYVar is not None and a1dGeoXVar is not None: 
            if a1dGeoXVar.shape[0] == a1dGeoYVar.shape[0]:
                
                dGeoXRefMin = np.min(a2dGeoXRef)
                dGeoXRefMax = np.max(a2dGeoXRef)
                dGeoYRefMin = np.min(a2dGeoYRef)
                dGeoYRefMax = np.max(a2dGeoYRef)
                 
                # Checking values on selected domain
                a1iIndexSel = []
                a1iIndexSel = np.nonzero(((a1dGeoXVar>=dGeoXRefMin) & (a1dGeoXVar<=dGeoXRefMax)) &
                              ((a1dGeoYVar>=dGeoYRefMin) & (a1dGeoYVar<=dGeoYRefMax)))
                a1iIndexSel = a1iIndexSel[0]
            
            else:
                #print('geocoord are different shape ... stopped')
                a1iIndexSel = None;

        else:
            #print('geocoords are unknown ... stopped')
            a1iIndexSel = None;
    
        # Ckecking on data quality
        if a1iIndexSel is not None:

            # Checking array dimensions number
            if (len(oDataVar.shape) == 1):
                a1dDataVar = oDataVar
            elif (len(oDataVar.shape) == 2):
                a1iDataDims = oDataVar.shape
                a1dDataVar = np.reshape(oDataVar, (a1iDataDims[0] * a1iDataDims[1]))

            a1dDataVarSel = []; a1dGeoXVarSel = []; a1dGeoYVarSel = [];
            a1dDataVarSel = a1dDataVar[a1iIndexSel]
            a1dGeoXVarSel = a1dGeoXVar[a1iIndexSel];
            a1dGeoYVarSel = a1dGeoYVar[a1iIndexSel];
            
            a1dDataVarSel.shape[0]
            
            # Storing all data in one dataset
            a2dDataSel = [];
            a2dDataSel = np.zeros(shape = [a1dDataVarSel.shape[0], 3])            
            a2dDataSel[:,0] = a1dGeoXVarSel
            a2dDataSel[:,1] = a1dGeoYVarSel
            a2dDataSel[:,2] = a1dDataVarSel
            
            sOption = []; 
            sOption = ('-a invdist:power=4.0:smoothing=0.0:radius1=' + str(dRadiusX) + 
                       ':radius2=' + str(dRadiusY) + ':angle=0.0:nodata=' + str(dNoData) + 
                       ':max_points=0:min_points=0');
    
            # Writing asci file with data selected values
            sVarGeoX = 'GeoX'; sVarGeoY = 'GeoY'; sVarData = 'GeoData'; 
            
            os.chdir(sPathTemp)
            sFileNameCSV = sFileName + '.csv';
            oFid = open(sFileNameCSV , 'w' )
            oFid.write( sVarGeoX + ',' +  sVarGeoY + ',' + sVarData +'\n' )
            np.savetxt(oFid, a2dDataSel, fmt='%10.4f', delimiter=',', newline='\n')
            oFid.close()
            
            os.chdir(sPathTemp)
            sFileNameVRT = sFileName + '.vrt';
            oFileVRT = open(sFileNameVRT,'w')
            oFileVRT.write('<OGRVRTDataSource>\n')
            oFileVRT.write('    <OGRVRTLayer name="' + sFileNameCSV[: -4] + '">\n')
            oFileVRT.write('        <SrcDataSource>' + sFileNameCSV + '</SrcDataSource>\n')
            oFileVRT.write('    <GeometryType>wkbPoint</GeometryType>\n')
            oFileVRT.write('    <LayerSRS>WGS84</LayerSRS>\n')
            oFileVRT.write('    <GeometryField encoding="PointFromColumns" x="'+sVarGeoX+'" y="'+sVarGeoY+'" z="' + sVarData+ '"/>\n')
            oFileVRT.write('    </OGRVRTLayer>\n')
            oFileVRT.write('</OGRVRTDataSource>\n')
            oFileVRT.close()
            
            os.chdir(sPathTemp)
            sFileNameTiff = sFileName + '.tif'; # /home/dpc-marche/library/gdal-2.0.0/bin/
            sLineCommand = ('gdal_grid -zfield "' + sVarData + '"  -txe ' + 
                            str(dGeoXRefMin) + ' ' + str(dGeoXRefMax) + ' -tye ' + 
                            str(dGeoYRefMin) + ' ' + str(dGeoYRefMax) + ' -a_srs EPSG:'+str(iEPSGCode)+' ' + 
                            sOption + ' -outsize ' + str(iColsRef) + ' ' + str(iRowsRef)  + 
                            ' -of GTiff -ot Float32 -l '+ sFileNameCSV[: -4] + ' ' + 
                            sFileNameVRT + ' ' + sFileNameTiff + ' --config GDAL_NUM_THREADS ALL_CPUS' )
            
            # Execute algorithm
            oLogStream.info( ' ------> INTERP VAR: ' + sLineCommand)
            #oPr = subprocess.Popen(sLineCommand, shell=True)
            #oOut, oErr = oPr.communicate()
            
            # Execute command line
            oPr = subprocess.Popen(sLineCommand, shell=True,  stdout=subprocess.PIPE)
            while True:
                sOut = oPr.stdout.readline()
                if sOut == '' and oPr.poll() is not None:
                    break
                if sOut:
                    oLogStream.info(str(sOut.strip()))
            
            # Collect stdout and stderr and exitcode
            oOut, oErr = oPr.communicate()
            
            oLogStream.info(str(oOut))
            oLogStream.info(str(oErr))
            
            # Read tiff file
            oFileDriver_TIFF = Drv_Data_IO(join(sPathTemp,sFileNameTiff),'r')
            oDataVarInterp = oFileDriver_TIFF.oFileWorkspace.read2DVar(iRowsRef, iColsRef)
            a2dDataVarInterp = oDataVarInterp['Data']
            
            # Debugging
            #plt.figure(1)
            #plt.imshow(a2dGeoData); plt.colorbar()
            #plt.figure(2)
            #plt.imshow(a2dDataVarInterp); plt.colorbar()
            #plt.show()
            
            # Checking interpolation values 
            a2dDataVarInterp[np.where(a2bGeoDataNan == True)] = np.nan

            # Deleting all ancillary files (for generating interpolating map)
            os.remove(join(sPathTemp,sFileNameCSV))
            os.remove(join(sPathTemp,sFileNameVRT))
            os.remove(join(sPathTemp,sFileNameTiff))
            
        else:
            # Data are not available on domain
            #print('data are not available on selected domain ... stopped')
            a2dDataVarInterp = np.zeros((iRowsRef, iColsRef)); 
            a2dDataVarInterp[:] = np.nan

    else:
        # Exit for data problems
        GetException(' -----> WARNING: all data are none! Data are not available!', 2, 1)
        a2dDataVarInterp = np.zeros((iRowsRef, iColsRef)); 
        a2dDataVarInterp[:] = np.nan
    
    # Store data in a final dictionary
    oWorkspace = {}
    oWorkspace['Var_1'] = a2dDataVarInterp
    oWorkspace['Var_2'] = None
    
    # Return results
    return oWorkspace

#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to use NN interpolation 
def interpVarPointNN(oDataGeo, oDataVar, oGeoXVar, oGeoYVar, oGeoZVar, 
                     dRadiusX, dRadiusY, dRadiusInfluence=None, 
                     iEPSGCode=None, sPathTemp=None, oDataAnalyzed=None):
    
    # Check temporary folder
    if not sPathTemp: sPathTemp = os.path.dirname(os.path.abspath(__file__))
    else: pass
    
    # Check EPSG Code
    if not iEPSGCode: iEPSGCode = 4326 
    else: pass
    
    # Temporary file
    sRN = str(randint(0,1000))
    oTimeTemp = datetime.datetime.now(); sTimeTemp = oTimeTemp.strftime('%Y%m%d-%H%M%S.%f')
    sFileName = 'interpnearest_temp_' + sTimeTemp + '_' + sRN

    # Retrivieng static information
    a2dGeoData = oDataGeo.a2dGeoData
    a2dGeoXRef = oDataGeo.oGeoData.a2dGeoX
    a2dGeoYRef = oDataGeo.oGeoData.a2dGeoY
    iColsRef = oDataGeo.oGeoData.iCols
    iRowsRef = oDataGeo.oGeoData.iRows
    a2bGeoDataFinite = oDataGeo.a2bGeoDataFinite
    a2bGeoDataNan = oDataGeo.a2bGeoDataNan
    
    # NoData value
    dNoData = np.nan
    
    # Searching undefined values
    a1bDataVarIndexNaN = []; a1bDataVarIndexFinite = []
    a1bDataVarIndexNaN = np.where(np.isnan(oDataVar) == True)
    a1bDataVarIndexFinite = np.where(np.isnan(oDataVar) == False)
    
    oDataVar = np.delete(oDataVar, a1bDataVarIndexNaN)
    oGeoXVar = np.delete(oGeoXVar, a1bDataVarIndexNaN)
    oGeoYVar = np.delete(oGeoYVar, a1bDataVarIndexNaN)
    
    if oGeoZVar != None:
        oGeoZVar = np.delete(oGeoZVar, a1bDataVarIndexNaN)
    
    # Checking array dimensions number
    if oGeoXVar != None and oGeoXVar != None:
    
        if (len(oGeoXVar.shape) == 1):
            a1dGeoXVar = oGeoXVar
            a1dGeoYVar = oGeoYVar
        elif (len(oGeoXVar.shape) == 2):
            
            a1iGeoDims = oGeoXVar.shape
            
            a1dGeoXVar = np.reshape(oGeoXVar, (a1iGeoDims[0] * a1iGeoDims[1]))
            a1dGeoYVar = np.reshape(oGeoYVar, (a1iGeoDims[0] * a1iGeoDims[1]))
        
        if a1dGeoYVar is not None and a1dGeoXVar is not None: 
            if a1dGeoXVar.shape[0] == a1dGeoYVar.shape[0]:
                
                dGeoXRefMin = np.min(a2dGeoXRef)
                dGeoXRefMax = np.max(a2dGeoXRef)
                dGeoYRefMin = np.min(a2dGeoYRef)
                dGeoYRefMax = np.max(a2dGeoYRef)
                 
                # Checking values on selected domain
                a1iIndexSel = []
                a1iIndexSel = np.nonzero(((a1dGeoXVar>=dGeoXRefMin) & (a1dGeoXVar<=dGeoXRefMax)) &
                              ((a1dGeoYVar>=dGeoYRefMin) & (a1dGeoYVar<=dGeoYRefMax)))
                a1iIndexSel = a1iIndexSel[0]
            
            else:
                #print('geocoord are different shape ... stopped')
                a1iIndexSel = None;
    
        else:
            #print('geocoords are unknown ... stopped')
            a1iIndexSel = None;
        
        # Ckecking on data quality
        if a1iIndexSel is not None:
    
            # Checking array dimensions number
            if (len(oDataVar.shape) == 1):
                a1dDataVar = oDataVar
            elif (len(oDataVar.shape) == 2):
                a1iDataDims = oDataVar.shape
                a1dDataVar = np.reshape(oDataVar, (a1iDataDims[0] * a1iDataDims[1]))
    
            a1dDataVarSel = []; a1dGeoXVarSel = []; a1dGeoYVarSel = [];
            a1dDataVarSel = a1dDataVar[a1iIndexSel]
            a1dGeoXVarSel = a1dGeoXVar[a1iIndexSel];
            a1dGeoYVarSel = a1dGeoYVar[a1iIndexSel];
            
            a1dDataVarSel.shape[0]
            
            # Storing all data in one dataset
            a2dDataSel = [];
            a2dDataSel = np.zeros(shape = [a1dDataVarSel.shape[0], 3])            
            a2dDataSel[:,0] = a1dGeoXVarSel
            a2dDataSel[:,1] = a1dGeoYVarSel
            a2dDataSel[:,2] = a1dDataVarSel
            
            sOption = [];
            sOption = ( '-a nearest:radius1=' + str(dRadiusX) + ':radius2=' + 
                        str(dRadiusY) + ':angle=0.0:nodata=' + str(dNoData) );
    
            # Writing asci file with data selected values
            sVarGeoX = 'GeoX'; sVarGeoY = 'GeoY'; sVarData = 'GeoData'; 
            
            os.chdir(sPathTemp)
            sFileNameCSV = sFileName + '.csv';
            oFid = open(sFileNameCSV , 'w' )
            oFid.write( sVarGeoX + ',' +  sVarGeoY + ',' + sVarData +'\n' )
            np.savetxt(oFid, a2dDataSel, fmt='%10.4f', delimiter=',', newline='\n')
            oFid.close()
            
            os.chdir(sPathTemp)
            sFileNameVRT = sFileName + '.vrt';
            oFileVRT = open(sFileNameVRT,'w')
            oFileVRT.write('<OGRVRTDataSource>\n')
            oFileVRT.write('    <OGRVRTLayer name="' + sFileNameCSV[: -4] + '">\n')
            oFileVRT.write('        <SrcDataSource>' + sFileNameCSV + '</SrcDataSource>\n')
            oFileVRT.write('    <GeometryType>wkbPoint</GeometryType>\n')
            oFileVRT.write('    <LayerSRS>WGS84</LayerSRS>\n')
            oFileVRT.write('    <GeometryField encoding="PointFromColumns" x="'+sVarGeoX+'" y="'+sVarGeoY+'" z="' + sVarData+ '"/>\n')
            oFileVRT.write('    </OGRVRTLayer>\n')
            oFileVRT.write('</OGRVRTDataSource>\n')
            oFileVRT.close()
            
            os.chdir(sPathTemp)
            sFileNameTiff = sFileName + '.tif';
            sLineCommand = ('gdal_grid -zfield "' + sVarData + '"  -txe ' + 
                            str(dGeoXRefMin) + ' ' + str(dGeoXRefMax) + ' -tye ' + 
                            str(dGeoYRefMin) + ' ' + str(dGeoYRefMax) + ' -a_srs EPSG:'+str(iEPSGCode)+' ' + 
                            sOption + ' -outsize ' + str(iColsRef) + ' ' + str(iRowsRef)  + 
                            ' -of GTiff -ot Float32 -l '+ sFileNameCSV[: -4] + ' ' + 
                            sFileNameVRT + ' ' + sFileNameTiff + ' --config GDAL_NUM_THREADS ALL_CPUS' )

            # Execute algorithm
            oLogStream.info( ' ------> INTERP VAR: ' + sLineCommand)
            oPr = subprocess.Popen(sLineCommand, shell=True)
            oOut, oErr = oPr.communicate()
            
            # Read tiff file
            oFileDriver_TIFF = Drv_Data_IO(join(sPathTemp,sFileNameTiff),'r')
            oDataVarInterp = oFileDriver_TIFF.oFileWorkspace.read2DVar(iRowsRef, iColsRef)
            a2dDataVarInterp = oDataVarInterp['Var_1']
            
            # Checking interpolation values 
            a2dDataVarInterp[np.where(a2bGeoDataNan == True)] = np.nan

            # Deleting all ancillary files (for generating interpolating map)
            os.remove(join(sPathTemp,sFileNameCSV))
            os.remove(join(sPathTemp,sFileNameVRT))
            os.remove(join(sPathTemp,sFileNameTiff))
            
            # Debugging
            #plt.figure(1)
            #plt.imshow(a2dGeoData); plt.colorbar()
            #plt.figure(2)
            #plt.imshow(a2dDataVarInterp); plt.colorbar()
            #plt.show()
            
        else:
            # Data are not available on domain
            #print('data are not available on selected domain ... stopped')
            a2dDataVarInterp = np.zeros((iRowsRef, iColsRef)); 
            a2dDataVarInterp[:] = np.nan

    else:
        # Exit for data problems
        GetException(' -----> WARNING: all data are none! Data are not available!', 2, 1)
        a2dDataVarInterp = np.zeros((iRowsRef, iColsRef)); 
        a2dDataVarInterp[:] = np.nan
    
    # Store data in a final dictionary
    oWorkspace = {}
    oWorkspace['Var_1'] = a2dDataVarInterp
    oWorkspace['Var_2'] = None
    
    # Return results
    return oWorkspace
    
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to use multi linear regression
def interpVarPointMLR(oDataGeo, oDataVar, oGeoXVar, oGeoYVar, oGeoZVar, 
                      dRadiusX, dRadiusY, dRadiusInfluence, 
                      iEPSGCode=None, sPathTemp=None, oDataAnalyzed=None):
    
    #--------------------------------------------------------------------------------
    # Check temporary folder
    if not sPathTemp: sPathTemp = os.path.dirname(os.path.abspath(__file__))
    else: pass
    
    # Check EPSG Code
    if not iEPSGCode: iEPSGCode = 4326 
    else: pass
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Searching undefined values
    a1bVarIndexNaN = []; a1dVarD = oDataVar
    a1bVarIndexNaN = np.where(np.isnan(a1dVarD) == True)
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------
    # Get predictor data
    try:
        oDataPred = oDataAnalyzed.oDataAnalyzed
    except:
        oDataPred = None
    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------
    # Check workspace data predictor(s)
    if not oDataPred:
        # Define dictionary with terrain field only (default setting)
        oDataPred = {}
        oDataPred['terrain'] = {}
        oDataPred['terrain'] = oDataGeo.a2dGeoData
        iDataPredDim = 1
    else:
        # Adding terrain data at data predictor
        oDataPred['terrain'] = oDataGeo.a2dGeoData
        iDataPredDim = len(oDataPred)
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Get XY indexes
    oGeoIndexVar = Lib_Data_Apps.findVarXYIndex(oDataGeo, oGeoXVar, oGeoYVar)
    # Get XY value(s)
    a1dVarZ = oDataGeo.a2dGeoData[oGeoIndexVar['X'], oGeoIndexVar['Y']]
    a1dVarX = oDataGeo.oGeoData.a2dGeoX[oGeoIndexVar['X'], oGeoIndexVar['Y']]
    a1dVarY = oDataGeo.oGeoData.a2dGeoY[oGeoIndexVar['X'], oGeoIndexVar['Y']]
    # Delete undefined value(s)
    a1dVarD = np.delete(a1dVarD, a1bVarIndexNaN)
    a1dVarX = np.delete(a1dVarX, a1bVarIndexNaN)
    a1dVarY = np.delete(a1dVarY, a1bVarIndexNaN)
    a1dVarZ = np.delete(a1dVarZ, a1bVarIndexNaN)
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Select data predictor
    iP = 0; 
    a2dVarPredXY = np.zeros([a1dVarZ.shape[0],iDataPredDim]); a2dVarPredXY[:] = -9999.0
    a3dVarPred = np.zeros(shape=[oDataGeo.a2dGeoData.shape[0],oDataGeo.a2dGeoData.shape[1],iDataPredDim])
    for sVarName in oDataPred:
        
        # Initialize temporary variable(s)
        a2dDataPred = []; a1dDataPredXY = [];
        
        # Get predictor data
        a2dDataPred = oDataPred[sVarName]
        a2dDataPred[np.where(oDataGeo.a2bGeoDataNan == True)] = np.nan
        
        # Select predictor data XY
        a1dDataPredXY = a2dDataPred[oGeoIndexVar['X'], oGeoIndexVar['Y']]
        a1dDataPredXY = np.delete(a1dDataPredXY, a1bVarIndexNaN)
        
        # Save data
        a3dVarPred[:,:,iP] = a2dDataPred
        a2dVarPredXY[:,iP] = a1dDataPredXY
        
        # Counter
        iP = iP + 1
    #--------------------------------------------------------------------------------
        
    # Debug value
    #print('DEBUG VALUE!!!! DELETE VALUES!!!!!')
    #a1dVarD = [110, 100, 80, 120, 190, 75]

    #--------------------------------------------------------------------------------
    # Fit data using stepwise function
    [a1dB, a1dSe, a1dPVal, bInModel, oStats, iNextStep, oHistory] = Lib_Data_Analysis_Regression.stepwisefit(a2dVarPredXY, a1dVarD, [], 0.1 )
    
    # Check variable X predictor(s) availability
    if np.any(bInModel == True):
        
        a1bModelIndexNaN = np.where(bInModel == False)
        a2dVarPred = np.delete(a2dVarPredXY, a1bModelIndexNaN, axis=1)
        a3dVarPred = np.delete(a3dVarPred, a1bModelIndexNaN, axis=2)
        
    elif np.all(bInModel == False):
        
        a2dVarPred = np.zeros(shape=[a1dVarZ.shape[0],1])
        a3dVarPred = np.zeros(shape=[oDataGeo.a2dGeoData.shape[0], oDataGeo.a2dGeoData.shape[1],1])
        a2dVarPred[:,0] = a1dVarZ
        a3dVarPred[:,:,0] = oDataGeo.a2dGeoData            
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Multivariate linear regression
    a2dVarA = np.concatenate((a2dVarPred, np.ones( [len(a2dVarPred),1] )), axis=1)
    a1dVarCoeff = np.linalg.lstsq(a2dVarA, a1dVarD)[0]
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Define basemap 
    a2dVarMap = np.ones([oDataGeo.a2dGeoData.shape[0],oDataGeo.a2dGeoData.shape[1]])
    a2dVarMap[:,:] = a1dVarCoeff[-1];
    for iP in range(0,len(a1dVarCoeff) - 1):
        a2dVarMap = a2dVarMap + a3dVarPred[:,:,iP]*a1dVarCoeff[iP]
    a2dVarMap[a2dVarMap<0] = 0;
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Compute residual
    a1dVarMap = a2dVarMap[oGeoIndexVar['X'], oGeoIndexVar['Y']]
    a1dVarRes = a1dVarMap - a1dVarD 
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Interpolate residual
    oDataInterp = interpVarPointIDW(oDataGeo, a1dVarRes, 
                                    a1dVarX, a1dVarY, a1dVarZ,
                                    dRadiusX, dRadiusY, dRadiusInfluence, 
                                    iEPSGCode, sPathTemp, oDataAnalyzed)
    
    # Final variable estimation (Snow Hweight in [cm])
    a2dVarFinal = a2dVarMap + oDataInterp['Var_1']
    a2dVarFinal[a2dVarFinal<1.0] = -9999.0
    a2dVarFinal[np.where(oDataGeo.a2bGeoDataNan == True)] = np.nan
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Compute kernel matrix
    a2dVarW = Lib_Data_Apps.computeVarKernel(oDataGeo, 
                                             oGeoIndexVar['X'], oGeoIndexVar['Y'],
                                             dRadiusInfluence)
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Debug ### CONTROLLARE ANCORA RISULTATI
    #plt.figure(1)
    #plt.imshow(a2dVarMap); plt.colorbar();plt.clim(0, 270)
    #plt.figure(2)
    #plt.imshow(a2dVarResInterp); plt.colorbar(); 
    #plt.figure(3)
    #plt.imshow(a2dVarFinal); plt.colorbar(); plt.clim(0, 270)
    #plt.figure(4)
    #plt.imshow(a2dVarW); plt.colorbar(); plt.clim(0, 1)
    #plt.show()
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Store data in a final dictionary
    oWorkspace = {}
    oWorkspace['Var_1'] = a2dVarFinal
    oWorkspace['Var_2'] = a2dVarW
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Return interpolation result
    return oWorkspace
    #--------------------------------------------------------------------------------
    
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to interpolate grid index using NN
def interpIndexGridNN(a2dGeoX_IN, a2dGeoY_IN, a2dGeoX_OUT, a2dGeoY_OUT):
    
    iGeoDim_IN = a2dGeoX_IN.shape[0]*a2dGeoY_IN.shape[1]
    
    a1iGeoVal_IN = np.arange(0,iGeoDim_IN)
    
    a2iIndex_OUT = griddata((a2dGeoX_IN.ravel(), a2dGeoY_IN.ravel()),
                            a1iGeoVal_IN, 
                            (a2dGeoX_OUT, a2dGeoY_OUT), method='nearest')
    
    return a2iIndex_OUT
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to interpolate grid data using NN
def interpVarGridNN(oDataGeo, oDataVar, oGeoXVar, oGeoYVar, oGeoZVar=None, dNoData=np.nan, a2iIndexVar=None, bGeoCut=False):
    
    # Retrieve variable information
    a2dGeoXVar = oGeoXVar
    a2dGeoYVar = oGeoYVar
    a2dDataVar = oDataVar
    
    # Retrieve reference information
    a2dGeoXRef = oDataGeo.oGeoData.a2dGeoX
    a2dGeoYRef = oDataGeo.oGeoData.a2dGeoY
    a2bGeoDataNan = oDataGeo.a2bGeoDataNan
    
    # Cut geo domain for avoiding large griddata interpolation (set bGeoCut==True)
    if bGeoCut == True:
        dGeoXRefMax = np.nanmax(a2dGeoXRef); dGeoXRefMin = np.nanmin(a2dGeoXRef);
        dGeoYRefMax = np.nanmax(a2dGeoYRef); dGeoYRefMin = np.nanmin(a2dGeoYRef);
        
        # UPPER RIGHT CORNER
        oURCorner = abs( a2dGeoYVar - dGeoYRefMax ) + abs( a2dGeoXVar - dGeoXRefMax )
        iURIndexI, iURIndexJ = np.unravel_index(oURCorner.argmin(), oURCorner.shape, order='C')
        # LOWER RIGHT CORNER
        oLRCorner = abs( a2dGeoYVar - dGeoYRefMin ) + abs( a2dGeoXVar - dGeoXRefMax )
        iLRIndexI, iLRIndexJ = np.unravel_index(oLRCorner.argmin(), oLRCorner.shape, order='C')
        # UPPER LEFT CORNER
        oULCorner = abs( a2dGeoYVar - dGeoYRefMax ) + abs( a2dGeoXVar - dGeoXRefMin )
        iULIndexI, iULIndexJ = np.unravel_index(oULCorner.argmin(), oULCorner.shape, order='C')
        # LOWER LEFT CORNER
        oLLCorner = abs( a2dGeoYVar - dGeoYRefMin ) + abs( a2dGeoXVar - dGeoXRefMin )
        iLLIndexI, iLLIndexJ = np.unravel_index(oLLCorner.argmin(), oLLCorner.shape, order='C')
        
        iIndexIMax = np.max([iURIndexI, iLRIndexI, iULIndexI, iLLIndexI])
        iIndexIMin = np.min([iURIndexI, iLRIndexI, iULIndexI, iLLIndexI])
        
        iIndexJMax = np.max([iURIndexJ, iLRIndexJ, iULIndexJ, iLLIndexJ])
        iIndexJMin = np.min([iURIndexJ, iLRIndexJ, iULIndexJ, iLLIndexJ])
        
        a2dGeoXVar_SUB = a2dGeoXVar[iIndexIMin:iIndexIMax,iIndexJMin:iIndexJMax]
        a2dGeoYVar_SUB = a2dGeoYVar[iIndexIMin:iIndexIMax,iIndexJMin:iIndexJMax]
        a2dDataVar_SUB = a2dDataVar[iIndexIMin:iIndexIMax,iIndexJMin:iIndexJMax]
    
    else:
        a2dGeoXVar_SUB = a2dGeoXVar
        a2dGeoYVar_SUB = a2dGeoYVar
        a2dDataVar_SUB = a2dDataVar
    
    # GridNN methods (or griddata or using indexes)
    if a2iIndexVar is None:
    
        # Initialize regridded variable
        a2dDataVarRegrid = griddata((a2dGeoXVar_SUB.ravel(), a2dGeoYVar_SUB.ravel()), a2dDataVar_SUB.ravel(),
                                              (a2dGeoXRef, a2dGeoYRef), method='nearest', fill_value = dNoData)
          
    elif a2iIndexVar is not None:
        
        a1dDataVarRegrid = a2dDataVar_SUB.ravel()[a2iIndexVar.ravel()]
        a2dDataVarRegrid = np.reshape(a1dDataVarRegrid, [a2dGeoXRef.shape[0], a2dGeoYRef.shape[1]])
    
    # Debug
#     plt.figure(1); plt.imshow(a2dGeoXVar); plt.colorbar()
#     plt.figure(2); plt.imshow(a2dGeoYVar); plt.colorbar()
#     plt.figure(3); plt.imshow(a2dDataVar); plt.colorbar()
#     plt.figure(4); plt.imshow(a2dGeoXRef); plt.colorbar()
#     plt.figure(5); plt.imshow(a2dGeoYRef); plt.colorbar()
#     plt.figure(6); plt.imshow(a2dGeoXVar_SUB); plt.colorbar()
#     plt.figure(7); plt.imshow(a2dGeoYVar_SUB); plt.colorbar()
#     plt.figure(8); plt.imshow(a2dDataVar_SUB); plt.colorbar()
#     plt.figure(9); plt.imshow(a2dDataVarRegrid); plt.colorbar()
#     plt.show()
    
    # Round re-gridded variable
    a2dDataVarRegrid = np.around(a2dDataVarRegrid, decimals=3)
    
    # Check interpolation values 
    a2dDataVarRegrid[np.where(a2bGeoDataNan == True)] = np.nan
    
    # Store data in a final dictionary
    oWorkspace = {}
    oWorkspace['Var_1'] = a2dDataVarRegrid
    oWorkspace['Var_2'] = None
    
    # Return results
    return oWorkspace
#--------------------------------------------------------------------------------
    
    
