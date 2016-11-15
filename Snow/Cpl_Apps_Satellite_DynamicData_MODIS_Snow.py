"""
Class Features

Name:          Cpl_Apps_Satellite_DynamicData_MODIS_Snow
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20151015'
Version:       '2.0.0'
"""

######################################################################################
# Logging
import logging
oLogStream = logging.getLogger('sLogger')

# Library
import os
import numpy as np

from os.path import join

import src.Lib_Data_Apps as Lib_Data_Apps
import src.Lib_Data_Analysis_Interpolation as Lib_Data_Analysis_Interpolation
import src.Lib_Data_Analysis_Filtering as Lib_Data_Analysis_Filtering
import src.Lib_Data_IO_Utils as Lib_Data_IO_Utils

from src.GetException import GetException
from src.Drv_Data_FTP import Drv_Data_FTP
from src.Drv_Data_IO import Drv_Data_IO
from src.Drv_Data_Zip import Drv_Data_Zip
from src.Lib_Data_IO_Utils import getFileHistory, writeFileHistory

# Debug
import matplotlib.pylab as plt
######################################################################################

#-------------------------------------------------------------------------------------
# Class
class Cpl_Apps_Satellite_DynamicData_MODIS_Snow:

    #-------------------------------------------------------------------------------------
    # Method init class
    def __init__(self, oDataTime=None, oDataGeo=None, oDataInfo=None):
        
        # Data settings and data reference 
        self.oDataTime = oDataTime
        self.oDataGeo = oDataGeo
        self.oDataInfo = oDataInfo
    
    #-------------------------------------------------------------------------------------  
    
    #------------------------------------------------------------------------------------- 
    # Method to check data availability
    def checkDynamicData(self, sTime):
        
        #-------------------------------------------------------------------------------------
        # Info
        oLogStream.info( ' ====> CHECK DATA AT TIME: ' + sTime + ' ... ')
        #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------
        # Get path information
        sPathData_CHECK = self.oDataInfo.oInfoSettings.oPathInfo['DataCache']
        
        # Get outcome variable information
        oVarsInfo_CHECK = self.oDataInfo.oInfoVarDynamic.oDataOutputDynamic

        # Get time information
        iTimeStep_CHECK = int(self.oDataInfo.oInfoSettings.oParamsInfo['TimeStep'])
        iTimeUpd_CHECK = int(self.oDataInfo.oInfoSettings.oParamsInfo['TimeUpd'])
        a1oTimeSteps_CHECK = self.oDataTime.a1oTimeSteps
        #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------
        # Cache definition
        sTime_CHECK = sTime
        sYear_CHECK = sTime_CHECK[0:4]; sMonth_CHECK = sTime_CHECK[4:6]; sDay_CHECK = sTime_CHECK[6:8];
        sHH_CHECK = sTime_CHECK[8:10]; sMM_CHECK = sTime_CHECK[10:12];
        sPathData_CHECK = Lib_Data_IO_Utils.defineFolderName(sPathData_CHECK,
                                                     {'$yyyy' : sYear_CHECK,'$mm' : sMonth_CHECK,'$dd' : sDay_CHECK, 
                                                      '$HH' : sHH_CHECK,'$MM' : sMM_CHECK})
        #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------
        # Condition to save file for reanalysis period (Reanalysis Time Steps = RTS)
        bSaveTime_CHECK = Lib_Data_IO_Utils.checkSavingTime(sTime_CHECK, a1oTimeSteps_CHECK, iTimeStep_CHECK, iTimeUpd_CHECK)
        #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------
        # Info
        oLogStream.info( ' ====> CHECK DATA AT TIME: ' + sTime_CHECK + ' ... ')
        #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------
        # Cycle(s) on type file(s)
        a1sFileAll_CHECK = []
        for sFileType_CHECK in oVarsInfo_CHECK:
            
            #-------------------------------------------------------------------------------------
            # Cycle(s) to check variable(s)
            a2bSaveVar_CHECK = {};
            #-------------------------------------------------------------------------------------
        
            #-------------------------------------------------------------------------------------
            # Cycle(s) on variable name(s)
            for sVarName_CHECK in oVarsInfo_CHECK[sFileType_CHECK]:
                
                #------------------------------------------------------------------------------------- 
                # Check variable component(s)
                if ( oVarsInfo_CHECK[sFileType_CHECK][sVarName_CHECK]['VarOp']['Op_Load']['Comp'].has_key('OUT') ):
                
                    #-------------------------------------------------------------------------------------
                    # Get variable OUT component(s)
                    oVarCompOUT_CHECK = oVarsInfo_CHECK[sFileType_CHECK][sVarName_CHECK]['VarOp']['Op_Load']['Comp']['OUT']
                    #-------------------------------------------------------------------------------------
                    
                    #-------------------------------------------------------------------------------------
                    # Cycle(s) on outcome variable(s)
                    for sVarCompOUT_CHECK in oVarCompOUT_CHECK.values():
                        
                        #-------------------------------------------------------------------------------------
                        # Initialize dictionary for each new variable(s)
                        if not sVarCompOUT_CHECK in a2bSaveVar_CHECK:
                            a2bSaveVar_CHECK[sVarCompOUT_CHECK] = {}
                        #-------------------------------------------------------------------------------------
                        
                        #-------------------------------------------------------------------------------------
                        # Storage variable checking
                        a1bVarCache_CHECK = []

                        # Check file
                        sFileCache_CHECK = os.path.join(sPathData_CHECK, 'Satellite_MODIS-SNOW_FILENC_' + sTime_CHECK + '_' + sVarCompOUT_CHECK + '.history')
                        bFileCache_CHECK = os.path.isfile(sFileCache_CHECK)
                        
                        # Check file status
                        if bFileCache_CHECK is True:
                            a1sFileName_CHECK = getFileHistory(sFileCache_CHECK)
                            for sFileName_CHECK in a1sFileName_CHECK[0]:
                                
                                bFileName_CHECK = os.path.isfile(sFileName_CHECK)
                                a1sFileAll_CHECK.append(sFileName_CHECK)
                            
                                if bFileName_CHECK is True:
                                    a1bVarCache_CHECK.append(True) 
                                else:
                                    a1bVarCache_CHECK.append(False) 
                        else:
                            a1bVarCache_CHECK.append(False)
                        #-------------------------------------------------------------------------------------
                    
                        #-------------------------------------------------------------------------------------
                        # Final check for each step
                        if np.all(a1bVarCache_CHECK) == True:    
                            a2bSaveVar_CHECK[sVarCompOUT_CHECK] = True
                        else:
                            a2bSaveVar_CHECK[sVarCompOUT_CHECK] = False
                        #-------------------------------------------------------------------------------------
                else:
                    pass
                #-------------------------------------------------------------------------------------
        
            #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------
        # Return check status 
        oLogStream.info( ' ====> CHECK DATA AT TIME: ' + sTime + ' ... OK')
        # Return variable(s)
        self.oVarsInfo_CHECK = a2bSaveVar_CHECK
        self.sPathCache = sPathData_CHECK
        #-------------------------------------------------------------------------------------
        
    #------------------------------------------------------------------------------------- 
    
    #-------------------------------------------------------------------------------------  
    # Method to get data 
    def getDynamicData(self, sTime):
        
        #----------------------------------------------------------------------------
        # Info
        oLogStream.info( ' ====> RETRIEVE DATA AT TIME: ' + sTime + ' ... ')

        # Check processing condition(s) 
        sTime_RET = sTime
        if not ( np.all(self.oVarsInfo_CHECK.values()) == True ):
            
            #----------------------------------------------------------------------------
            # Get data from FTP Server
            oDrvData_RET = Drv_Data_FTP(self.oDataInfo, 'MODIS', sTime_RET)
            
            # Extract info for filename IN
            bFileName_RET = oDrvData_RET.oFileWorkspace.bFileName
            sFileName_RET = oDrvData_RET.oFileWorkspace.sFileName
            sFileProduct_RET = oDrvData_RET.oFileWorkspace.sFileProduct
            sFileVersion_RET = oDrvData_RET.oFileWorkspace.sFileVersion
            sFileComp_RET = oDrvData_RET.oFileWorkspace.sFileComp
            a1sFileTile_RET = oDrvData_RET.oFileWorkspace.a1sFileTile
            #----------------------------------------------------------------------------
            
            #----------------------------------------------------------------------------
            # Info
            oLogStream.info( ' ====> RETRIEVE DATA AT TIME: ' + sTime + ' ... OK')
            #----------------------------------------------------------------------------
        
        else:
            #----------------------------------------------------------------------------
            # Exit 
            oLogStream.info( ' ====> RETRIEVE DATA AT TIME: ' + sTime + ' ... SKIPPED --- ALL DATA PROCESSED PREVIOUSLY!')
            #----------------------------------------------------------------------------
        
        #----------------------------------------------------------------------------
        
        #----------------------------------------------------------------------------
        # Info
        oLogStream.info( ' ====> GET DATA AT TIME: ' + sTime + ' ... ')
        
        # Check processing condition(s) 
        if not ( np.all(self.oVarsInfo_CHECK.values()) == True ):
            
            #----------------------------------------------------------------------------
            # Get information from RET to IN
            bFileName_IN = bFileName_RET
            sFileName_IN = sFileName_RET
            sFileProduct_IN = sFileProduct_RET
            sFileVersion_IN = sFileVersion_RET
            sFileComp_IN = sFileComp_RET
            a1sFileTile_IN = a1sFileTile_RET
            #----------------------------------------------------------------------------
            
            #----------------------------------------------------------------------------
            # Check file IN availability
            if bFileName_IN:
                
                #----------------------------------------------------------------------------
                # Read data in HDF4 format
                oDrvData_IN = Drv_Data_IO(sFileName_IN)
                oFileData_IN = oDrvData_IN.oFileWorkspace.readFileData()
                #----------------------------------------------------------------------------

                #----------------------------------------------------------------------------
                # Info
                self.oData_IN = oFileData_IN
                self.bFileName_IN = bFileName_IN
                self.sFileName_IN = sFileName_IN
                self.sFileProduct_IN = sFileProduct_IN
                self.sFileVersion_IN = sFileVersion_IN
                self.sFileComp_IN = sFileComp_IN
                self.a1sFileTile_IN = a1sFileTile_IN
                
                oLogStream.info( ' ====> GET DATA AT TIME: ' + sTime + ' ... OK')
                #----------------------------------------------------------------------------
            
            else:
                
                #----------------------------------------------------------------------------
                # Info
                self.oData_IN = {}; self.bFileName_IN = False
                oLogStream.info( ' ====> RETRIEVE DATA AT TIME: ' + sTime + ' ... FAILED --- FILES INPUT NOT FOUND')
                #----------------------------------------------------------------------------
            
            #----------------------------------------------------------------------------
            
        else:
            #----------------------------------------------------------------------------
            # Exit 
            self.oData_IN = {}
            oLogStream.info( ' ====> GET DATA AT TIME: ' + sTime + ' ... SKIPPED --- ALL DATA PROCESSED PREVIOUSLY!')
            #----------------------------------------------------------------------------
        
        #----------------------------------------------------------------------------
        
    #-------------------------------------------------------------------------------------  
    
    #-------------------------------------------------------------------------------------
    # Method to compute data 
    def computeDynamicData(self, sTime):
        
        #------------------------------------------------------------------------------------- 
        # Info
        oLogStream.info( ' ====> COMPUTE DATA AT TIME: ' + sTime + ' ... ')
        #------------------------------------------------------------------------------------- 

        #-------------------------------------------------------------------------------------
        # Check file availability and saving conditions
        if not ( np.all(self.oVarsInfo_CHECK.values()) == True ):
                        
            #----------------------------------------------------------------------------
            # Check file IN availability
            if self.bFileName_IN:
                
                #-------------------------------------------------------------------------------------
                # Get data OUT
                oVarsInfo_OUT = self.oDataInfo.oInfoVarDynamic.oDataOutputDynamic['NetCDF']
                # Get geographical data
                oDataGeo = self.oDataGeo
                # Get data IN
                sFileName_IN = self.sFileName_IN; bFileName_IN = self.bFileName_IN
                #-------------------------------------------------------------------------------------
                
                #----------------------------------------------------------------------------
                # Info file
                oLogStream.info( ' -----> Getting data: ' + sFileName_IN + ' ... ')
                #----------------------------------------------------------------------------
                
                #----------------------------------------------------------------------------
                # Get data IN
                oVar_IN = self.oData_IN['Data']
                oGeoX_IN = self.oData_IN['GeoX']
                oGeoY_IN = self.oData_IN['GeoY']
                #----------------------------------------------------------------------------
                
                #----------------------------------------------------------------------------
                # Cycle on variable name OUT
                oDataOUT_OUT = {}; oDataIN_OUT = {}
                for sVarName_OUT in oVarsInfo_OUT:
                    
                    # Debug
                    #sVarName_OUT = 'snow_cover_daily'
                    
                    #------------------------------------------------------------------------------------- 
                    # Variable info
                    oLogStream.info( ' -----> Variable: ' + sVarName_OUT + ' ... ')

                    # Get variable global information
                    oVarInfo_OUT = oVarsInfo_OUT[sVarName_OUT]
                    #------------------------------------------------------------------------------------- 

                    #------------------------------------------------------------------------------------- 
                    # Check variable component(s)
                    if ( oVarInfo_OUT['VarOp']['Op_Load']['Comp'].has_key('IN') and 
                         oVarInfo_OUT['VarOp']['Op_Load']['Comp'].has_key('OUT') ):
                        
                        #------------------------------------------------------------------------------------- 
                        # Get variable component(s)
                        oVarCompIN_OUT = oVarInfo_OUT['VarOp']['Op_Load']['Comp']['IN']
                        oVarCompOUT_OUT = oVarInfo_OUT['VarOp']['Op_Load']['Comp']['OUT']
                        
                        # Get function name(s)
                        sVarMethodConvIN_OUT = oVarInfo_OUT['VarOp']['Op_Math']['Conversion']['Func']
                        sVarMethodInterpIN_OUT = oVarInfo_OUT['VarOp']['Op_Math']['Interpolation']['Func']
                        sVarMethodAggregIN_OUT = oVarInfo_OUT['VarOp']['Op_Math']['Aggregation']['Func']
                        #------------------------------------------------------------------------------------- 
                        
                        #------------------------------------------------------------------------------------- 
                        # Cycle(s) on component(s) variable(s) IN 
                        for sVarCompIN_OUT in oVarCompIN_OUT.values():
                            
                            # Get data IN
                            a2dVar_IN = np.float32(oVar_IN[sVarCompIN_OUT])

                            # Variable conversion
                            oLogStream.info( ' -----> Converting ' + sVarCompIN_OUT + ' at time ' + sTime + ' ... ')
                            if sVarMethodConvIN_OUT:
                                oVarOUT_ConvIN = oVarInfo_OUT['VarOp']['Op_Math']['Conversion']['Keys']
                                oMethodConv = getattr(Lib_Data_Apps, sVarMethodConvIN_OUT)
                                [a2dVar_CONV, sVarName_CONV] = oMethodConv(a2dVar_IN, oVarOUT_ConvIN, 'modis')
                                oLogStream.info( ' -----> Converting ' + sVarCompIN_OUT + ' at time ' + sTime + ' ... OK')
                                
                            else:
                                a2dVar_CONV = a2dVar_IN
                                oLogStream.info( ' -----> Converting ' + sVarCompIN_OUT + ' at time ' + sTime + ' ... SKIPPED --- METHOD NOT DEFINED!')
                            
                            # Variable aggregation/filtering
                            oLogStream.info( ' -----> Aggregating ' + sVarCompIN_OUT + ' at time ' + sTime + ' ... ')
                            if sVarMethodAggregIN_OUT:
                                iVarOUT_PxAggreg = int(oVarInfo_OUT['VarOp']['Op_Math']['Aggregation']['PxSideAggr'])
                                oMethodAggreg = getattr(Lib_Data_Analysis_Filtering, sVarMethodAggregIN_OUT)
                                a2dVar_AGG = oMethodAggreg(a2dVar_CONV, iVarOUT_PxAggreg)
                                oLogStream.info( ' -----> Aggregating ' + sVarCompIN_OUT + ' at time ' + sTime + ' ... OK')
                            else:
                                a2dVar_AGG = a2dVar_CONV
                                oLogStream.info( ' -----> Aggregating ' + sVarCompIN_OUT + ' at time ' + sTime + ' ... SKIPPED --- METHOD NOT DEFINED!')
                            
                            # Variable interpolation
                            oLogStream.info( ' -----> Interpolating ' + sVarCompIN_OUT + ' at time ' + sTime + ' ... ')
                            if sVarMethodInterpIN_OUT:
                                oMethodInterp = getattr(Lib_Data_Analysis_Interpolation, sVarMethodInterpIN_OUT)
                                a2dVar_INTERP = oMethodInterp(oDataGeo, a2dVar_AGG, oGeoX_IN, oGeoY_IN, None, np.nan, None, True)['Var_1']
                                oLogStream.info( ' -----> Interpolating ' + sVarCompIN_OUT + ' at time ' + sTime + ' ... OK')
                            else:
                                a2dVar_INTERP = a2dVar_AGG
                                oLogStream.info( ' -----> Interpolating ' + sVarCompIN_OUT + ' at time ' + sTime + ' ... SKIPPED --- METHOD NOT DEFINED!')
                            
                            # Variable maskering
                            iVarFillValue_OUT = int(oVarInfo_OUT['VarOp']['Op_Save']['_FillValue'])
                            oMethodMask = getattr(Lib_Data_Apps, 'maskVarFillValue')
                            a2dVar_MASK = oMethodMask(a2dVar_INTERP, iVarFillValue_OUT, oDataGeo)
                            #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            # Store data IN
                            oDataIN_OUT[sVarName_OUT] = a2dVar_MASK
                            #-------------------------------------------------------------------------------------
                            
                        # End cycle(s) component(s) variable(s) IN
                        #-------------------------------------------------------------------------------------
                        
                        #-------------------------------------------------------------------------------------
                        # Cycle(s) on component(s) variable(s) OUT
                        for sVarCompOUT_OUT in oVarCompOUT_OUT.values():
                            
                            #-------------------------------------------------------------------------------------
                            # Info
                            oLogStream.info( ' -----> Storing ' + sVarCompOUT_OUT + ' at time ' + sTime + ' ... ')
                            #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            # Save data OUT
                            oDataOUT_OUT[sVarName_OUT] = oDataIN_OUT[sVarCompOUT_OUT]
                            #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            # Info
                            oLogStream.info( ' -----> Storing ' + sVarCompOUT_OUT + ' at time ' + sTime + ' ... OK')
                            #-------------------------------------------------------------------------------------
                            
                        # End cycle(s) component(s) variable(s) OUT
                        #-------------------------------------------------------------------------------------
                        
                        #------------------------------------------------------------------------------------- 
                        # File and variable info
                        oLogStream.info( ' -----> Variable: ' + sVarName_OUT + ' ... OK')
                        #------------------------------------------------------------------------------------- 
                
                    else:
                    
                        #------------------------------------------------------------------------------------- 
                        # File and variable info
                        oLogStream.info( ' -----> Variable: ' + sVarName_OUT + ' ... SKIPPED --- VARIABLE WITHOUT IO/OUT COMPONENT(S)!')
                        #------------------------------------------------------------------------------------- 
                    
                    #-------------------------------------------------------------------------------------
                    
                # End Cycle(s) on variable name OUT
                #-------------------------------------------------------------------------------------
                
                #-------------------------------------------------------------------------------------
                # Remove temporary file(s)
                os.remove(sFileName_IN)
                oLogStream.info( ' -----> Getting data: ' + sFileName_IN + ' ... OK')
                #-------------------------------------------------------------------------------------
                
                #------------------------------------------------------------------------------------- 
                # Info
                self.oData_OUT = oDataOUT_OUT
                oLogStream.info( ' ====> COMPUTE DATA AT TIME: ' + sTime + ' ... OK')
                #------------------------------------------------------------------------------------- 
            
            else:
                
                #-------------------------------------------------------------------------------------
                # Info
                oLogStream.info( ' ====> COMPUTE DATA AT TIME: ' + sTime + ' ... FAILED --- FILES INPUT NOT FOUND ')
                self.oData_OUT = {}
                #-------------------------------------------------------------------------------------
        else:
            
            #-------------------------------------------------------------------------------------
            # Info
            oLogStream.info( ' ====> COMPUTE DATA AT TIME: ' + sTime + ' ... SKIPPED --- ALL DATA PROCESSED PREVIOUSLY!')
            self.oData_OUT = {}
            #-------------------------------------------------------------------------------------
            
        #-------------------------------------------------------------------------------------
        
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to save data
    def saveDynamicData(self, sTime):
        
        #------------------------------------------------------------------------------------- 
        # Info
        oLogStream.info( ' ====> SAVE DATA AT TIME: ' + sTime + ' ...  ')
        #------------------------------------------------------------------------------------- 
        
        #-------------------------------------------------------------------------------------
        # Check file availability and saving conditions
        if not ( np.all(self.oVarsInfo_CHECK.values()) == True ):
        
            #------------------------------------------------------------------------------------- 
            # Get information
            sPathData_OUT = self.oDataInfo.oInfoSettings.oPathInfo['DataDynamicOutcome']
            sPathCache_OUT = self.sPathCache
            
            oVarsInfo_OUT = self.oDataInfo.oInfoVarDynamic.oDataOutputDynamic
            oVarsData_OUT = self.oData_OUT
 
            # Get domain name
            sDomainName_OUT = self.oDataInfo.oInfoSettings.oParamsInfo['DomainName']
            #------------------------------------------------------------------------------------- 
    
            #------------------------------------------------------------------------------------- 
            # Check workspace field(s)
            if np.any(oVarsData_OUT):
                
                #------------------------------------------------------------------------------------- 
                # Get information for file IN
                bFileName_IN = self.bFileName_IN; sFileName_IN = self.sFileName_IN
                sFileProduct_IN = self.sFileProduct_IN; sFileVersion_IN = self.sFileVersion_IN; sFileComp_IN = self.sFileComp_IN
                a1sFileTile_IN = self.a1sFileTile_IN
                #------------------------------------------------------------------------------------- 
                
                #-------------------------------------------------------------------------------------
                # Cycle(s) on get var name
                for sVarName_OUT in oVarsData_OUT:
                
                    #-------------------------------------------------------------------------------------
                    # Info variable name
                    oLogStream.info( ' -----> Save variable: ' + sVarName_OUT + ' ... ')
                    #-------------------------------------------------------------------------------------
    
                    #-------------------------------------------------------------------------------------
                    # Time information
                    sVarTime_OUT = sTime
                    sVarYear_OUT = sVarTime_OUT[0:4]; sVarMonth_OUT = sVarTime_OUT[4:6]; sVarDay_OUT = sVarTime_OUT[6:8];
                    sVarHH_OUT = sVarTime_OUT[8:10]; sVarMM_OUT = sVarTime_OUT[10:12];
    
                    # Pathname NC OUT
                    sPathName_OUT = Lib_Data_IO_Utils.defineFolderName(sPathData_OUT,
                                                                 {'$yyyy' : sVarYear_OUT,'$mm' : sVarMonth_OUT,'$dd' : sVarDay_OUT, 
                                                                  '$HH' : sVarHH_OUT,'$MM' : sVarMM_OUT})
                    # Time Info
                    oLogStream.info( ' ------> Save time step (NC): ' + sVarTime_OUT)
                    #------------------------------------------------------------------------------------- 
                    
                    #-------------------------------------------------------------------------------------
                    # Get data
                    a2VarData_OUT = oVarsData_OUT[sVarName_OUT]
                    iVarLen_OUT = 1
                    # Save time information (for loading and saving function)
                    a1oVarTime_OUT = []; a1oVarTime_OUT.append(sVarTime_OUT)
                    #-------------------------------------------------------------------------------------
                    
                    #------------------------------------------------------------------------------------- 
                    # Filename NC OUT
                    sFileName_OUT = Lib_Data_IO_Utils.defineFileName(join(sPathName_OUT, oVarsInfo_OUT['NetCDF'][sVarName_OUT]['VarSource']), 
                                                             {'$yyyy' : sVarYear_OUT,'$mm' : sVarMonth_OUT,'$dd' : sVarDay_OUT, 
                                                              '$HH' : sVarHH_OUT,'$MM' : sVarMM_OUT, 
                                                              '$DOMAIN' : sDomainName_OUT,
                                                              '$PRODUCT' : sFileProduct_IN, '$VERSION' : sFileVersion_IN})
                    
                    # Check output file(s) availability 
                    bFileExist_OUT = Lib_Data_IO_Utils.checkFileExist(sFileName_OUT + '.' + 
                                                                        oVarsInfo_OUT['NetCDF'][sVarName_OUT]['VarOp']['Op_Save']['Zip'])
                    
                    # Info
                    oLogStream.info( ' -------> Saving file output (NC): ' + sFileName_OUT + ' ... ')
                    #-------------------------------------------------------------------------------------
                    
                    #-------------------------------------------------------------------------------------
                    # Check errors in code
                    a1bFileCheck_OUT = []; a1sFileName_OUT = []
                    try:
                        
                        #-------------------------------------------------------------------------------------
                        # Open NC file (in write or append mode)
                        bVarExist_OUT = False;
                        if bFileExist_OUT is False:
                            
                            #-------------------------------------------------------------------------------------
                            # Open NC file in write mode
                            oDrv_OUT = Drv_Data_IO(sFileName_OUT, 'w')
                            bVarExist_OUT = False;
                            #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            # Write global attributes (common and extra)
                            oDrv_OUT.oFileWorkspace.writeFileAttrsCommon(self.oDataInfo.oInfoSettings.oGeneralInfo)
                            oDrv_OUT.oFileWorkspace.writeFileAttrsExtra(self.oDataInfo.oInfoSettings.oParamsInfo,
                                                                           self.oDataGeo.a1oGeoInfo)
                            #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            # Write geo-system information
                            oDrv_OUT.oFileWorkspace.writeGeoSystem(self.oDataInfo.oInfoSettings.oGeoSystemInfo, 
                                                                      self.oDataGeo.oGeoData.a1dGeoBox)
                            #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            # Declare variable dimensions
                            sDimVarX = oVarsInfo_OUT['NetCDF']['Terrain']['VarDims']['X']
                            oDrv_OUT.oFileWorkspace.writeDims(sDimVarX, self.oDataGeo.oGeoData.iCols)
                            sDimVarY = oVarsInfo_OUT['NetCDF']['Terrain']['VarDims']['Y']
                            oDrv_OUT.oFileWorkspace.writeDims(sDimVarY, self.oDataGeo.oGeoData.iRows)
                            sDimVarT = 'time'; 
                            oDrv_OUT.oFileWorkspace.writeDims(sDimVarT, iVarLen_OUT)
                            # Declare extra dimension(s)
                            oDrv_OUT.oFileWorkspace.writeDims('nsim', 1)
                            oDrv_OUT.oFileWorkspace.writeDims('ntime', 2)
                            oDrv_OUT.oFileWorkspace.writeDims('nens', 1)
                            #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            # Write time information
                            oDrv_OUT.oFileWorkspace.writeTime(a1oVarTime_OUT, 'f8', 'time', iVarLen_OUT/iVarLen_OUT)
                            #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            # Try to save longitude
                            sVarGeoX = 'Longitude'
                            oLogStream.info( ' -------> Saving variable: ' + sVarGeoX + ' ... ')
                            try:
    
                                #-------------------------------------------------------------------------------------
                                # Get longitude
                                oDrvNC_WriteMethod = getattr(oDrv_OUT.oFileWorkspace,  
                                                             oVarsInfo_OUT['NetCDF'][sVarGeoX]['VarOp']['Op_Save']['Func'])
                                oDrvNC_WriteMethod(sVarGeoX, self.oDataGeo.oGeoData.a2dGeoX, 
                                                   oVarsInfo_OUT['NetCDF'][sVarGeoX]['VarAttributes'], 
                                                   oVarsInfo_OUT['NetCDF'][sVarGeoX]['VarOp']['Op_Save']['Format'], 
                                                   oVarsInfo_OUT['NetCDF'][sVarGeoX]['VarDims']['Y'], 
                                                   oVarsInfo_OUT['NetCDF'][sVarGeoX]['VarDims']['X'])
                                # Info
                                a1bFileCheck_OUT.append(True)
                                oLogStream.info( ' -------> Saving variable: ' + sVarGeoX + ' ... OK ')
                                #-------------------------------------------------------------------------------------
                            
                            except:
                                
                                #-------------------------------------------------------------------------------------
                                # Exit code
                                a1bFileCheck_OUT.append(False)
                                GetException(' -----> WARNING: variable not found in outcome workspace!', 2, 1)
                                oLogStream.info( ' -------> Saving variable: ' + sVarGeoX + ' ... FAILED --- VARIABLE NOT FOUND IN OUTCOME WORKSPACE ')
                                #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            # Try to save latitude
                            sVarGeoY = 'Latitude'
                            oLogStream.info( ' -------> Saving variable: ' + sVarGeoY + ' ... ')
                            try:
                            
                                #-------------------------------------------------------------------------------------
                                # Get latitude
                                oDrvNC_WriteMethod = getattr(oDrv_OUT.oFileWorkspace,  
                                                             oVarsInfo_OUT['NetCDF'][sVarGeoY]['VarOp']['Op_Save']['Func'])
                                oDrvNC_WriteMethod(sVarGeoY, self.oDataGeo.oGeoData.a2dGeoY, 
                                                   oVarsInfo_OUT['NetCDF'][sVarGeoY]['VarAttributes'], 
                                                   oVarsInfo_OUT['NetCDF'][sVarGeoY]['VarOp']['Op_Save']['Format'], 
                                                   oVarsInfo_OUT['NetCDF'][sVarGeoY]['VarDims']['Y'], 
                                                   oVarsInfo_OUT['NetCDF'][sVarGeoY]['VarDims']['X'])
                                # Info
                                a1bFileCheck_OUT.append(True)
                                oLogStream.info( ' -------> Saving variable: ' + sVarGeoY + ' ... OK ')
                                #-------------------------------------------------------------------------------------
                            
                            except:
                                
                                #-------------------------------------------------------------------------------------
                                # Exit code
                                a1bFileCheck_OUT.append(False)
                                GetException(' -----> WARNING: variable not found in outcome workspace!', 2, 1)
                                oLogStream.info( ' -------> Saving variable: ' + sVarGeoY + ' ... FAILED --- VARIABLE NOT FOUND IN OUTCOME WORKSPACE ')
                                #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            # Try to save terrain
                            sVarTerrain = 'Terrain'
                            oLogStream.info( ' -------> Saving variable: ' + sVarTerrain + ' ... ')
                            try:                     
                            
                                #-------------------------------------------------------------------------------------
                                # Get terrain  
                                a2dData = self.oDataGeo.a2dGeoData
                                a2dData[self.oDataGeo.a2bGeoDataNan] = self.oDataGeo.dNoData
                                 
                                oDrvNC_WriteMethod = getattr(oDrv_OUT.oFileWorkspace, 
                                                             oVarsInfo_OUT['NetCDF'][sVarTerrain]['VarOp']['Op_Save']['Func'])
                                oDrvNC_WriteMethod(sVarTerrain, a2dData, 
                                                   oVarsInfo_OUT['NetCDF'][sVarTerrain]['VarAttributes'],
                                                   oVarsInfo_OUT['NetCDF'][sVarTerrain]['VarOp']['Op_Save']['Format'], 
                                                   oVarsInfo_OUT['NetCDF'][sVarTerrain]['VarDims']['Y'], 
                                                   oVarsInfo_OUT['NetCDF'][sVarTerrain]['VarDims']['X'])
                                # Info
                                a1bFileCheck_OUT.append(True)
                                oLogStream.info( ' -------> Saving variable: ' + sVarTerrain + ' ... OK ')
                                #-------------------------------------------------------------------------------------
                            
                            except:
                                
                                #-------------------------------------------------------------------------------------
                                # Exit code
                                a1bFileCheck_OUT.append(False)
                                GetException(' -----> WARNING: variable not found in outcome workspace!', 2, 1)
                                oLogStream.info( ' -------> Saving variable: ' + sVarTerrain + ' ... FAILED --- VARIABLE NOT FOUND IN OUTCOME WORKSPACE ')
                                #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            # Try to save 3d variable
                            oLogStream.info( ' -------> Saving variable: ' + sVarName_OUT + ' ... ')
                            try:
                            
                                #-------------------------------------------------------------------------------------
                                # Get data dynamic
                                oDrvNC_WriteMethod = getattr(oDrv_OUT.oFileWorkspace, 
                                                             oVarsInfo_OUT['NetCDF'][sVarName_OUT]['VarOp']['Op_Save']['Func'])
                                oDrvNC_WriteMethod(sVarName_OUT, a2VarData_OUT, 
                                                   oVarsInfo_OUT['NetCDF'][sVarName_OUT]['VarAttributes'], 
                                                   oVarsInfo_OUT['NetCDF'][sVarName_OUT]['VarOp']['Op_Save']['Format'],
                                                   oVarsInfo_OUT['NetCDF'][sVarName_OUT]['VarDims']['Y'], 
                                                   oVarsInfo_OUT['NetCDF'][sVarName_OUT]['VarDims']['X'])
                            
                                # Info
                                a1bFileCheck_OUT.append(True)
                                oLogStream.info( ' -------> Saving variable: ' + sVarName_OUT + ' ... OK ')
                                #-------------------------------------------------------------------------------------
                            
                            except:
                                
                                #-------------------------------------------------------------------------------------
                                # Exit code
                                a1bFileCheck_OUT.append(False)
                                GetException(' -----> WARNING: variable not found in outcome workspace!', 2, 1)
                                oLogStream.info( ' -------> Saving variable: ' + sVarName_OUT + ' ... FAILED --- VARIABLE NOT FOUND IN OUTCOME WORKSPACE ')
                                #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            # Close NetCDF file
                            oDrv_OUT.oFileWorkspace.closeFile()
                            
                            # Zip file
                            Drv_Data_Zip(sFileName_OUT, 
                                         'z', 
                                         oVarsInfo_OUT['NetCDF'][sVarName_OUT]['VarOp']['Op_Save']['Zip'], 
                                         True)
                            
                            # Info
                            a1sFileName_OUT.append(sFileName_OUT + '.' + oVarsInfo_OUT['NetCDF'][sVarName_OUT]['VarOp']['Op_Save']['Zip'])
                            oLogStream.info( ' ------> Saving file output NetCDF: ' + sFileName_OUT + ' ... OK')
                            #-------------------------------------------------------------------------------------
                            
                        else:
                            
                            #-------------------------------------------------------------------------------------
                            # Unzip NC file (if file is compressed)
                            Drv_Data_Zip(sFileName_OUT + '.' +  oVarsInfo_OUT['NetCDF'][sVarName_OUT]['VarOp']['Op_Save']['Zip'],
                                         'u', 
                                         oVarsInfo_OUT['NetCDF'][sVarName_OUT]['VarOp']['Op_Save']['Zip'], 
                                         True)
                            
                            # Open NC file in append mode
                            oDrv_OUT = Drv_Data_IO(sFileName_OUT, 'a')
                            bVarExistNC_OUT = oDrv_OUT.oFileWorkspace.checkVarName(sVarName_OUT)
                            #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            # Check variable availability
                            oLogStream.info( ' -------> Saving variable: ' + sVarName_OUT + ' ... ')
                            if bVarExistNC_OUT is False:
                            
                                #-------------------------------------------------------------------------------------
                                # Try to save 3d variable
                                try:
                                
                                    #-------------------------------------------------------------------------------------
                                    # Get data dynamic
                                    oDrvNC_WriteMethod = getattr(oDrv_OUT.oFileWorkspace, 
                                                                 oVarsInfo_OUT['NetCDF'][sVarName_OUT]['VarOp']['Op_Save']['Func'])
                                    oDrvNC_WriteMethod(sVarName_OUT, a2VarData_OUT,  
                                                       oVarsInfo_OUT['NetCDF'][sVarName_OUT]['VarAttributes'], 
                                                       oVarsInfo_OUT['NetCDF'][sVarName_OUT]['VarOp']['Op_Save']['Format'], 
                                                       oVarsInfo_OUT['NetCDF'][sVarName_OUT]['VarDims']['Y'], 
                                                       oVarsInfo_OUT['NetCDF'][sVarName_OUT]['VarDims']['X'])
                                
                                    # Info
                                    a1bFileCheck_OUT.append(True)
                                    oLogStream.info( ' -------> Saving variable: ' + sVarName_OUT + ' ... OK ')
                                    #-------------------------------------------------------------------------------------
                                
                                except:
                                    
                                    #-------------------------------------------------------------------------------------
                                    # Exit code
                                    a1bFileCheck_OUT.append(False)
                                    GetException(' -----> WARNING: variable not found in outcome workspace!', 2, 1)
                                    oLogStream.info( ' -------> Saving variable: ' + sVarName_OUT + ' ... FAILED --- VARIABLE NOT FOUND IN OUTCOME WORKSPACE ')
                                    #-------------------------------------------------------------------------------------
                                
                                #-------------------------------------------------------------------------------------
                            
                            else:
                                #-------------------------------------------------------------------------------------
                                # Info
                                oLogStream.info( ' -------> Saving variable: ' + sVarName_OUT + ' ... SAVED PREVIOUSLY')
                                a1bFileCheck_OUT.append(True)
                                #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            
                            #-------------------------------------------------------------------------------------
                            # Close NetCDF file
                            oDrv_OUT.oFileWorkspace.closeFile()
                            
                            # Zip file
                            Drv_Data_Zip(sFileName_OUT, 
                                         'z', 
                                         oVarsInfo_OUT['NetCDF'][sVarName_OUT]['VarOp']['Op_Save']['Zip'], 
                                         True)
                            
                            # Info
                            a1sFileName_OUT.append(sFileName_OUT + '.' + oVarsInfo_OUT['NetCDF'][sVarName_OUT]['VarOp']['Op_Save']['Zip'])
                            oLogStream.info( ' ------> Saving file output NetCDF: ' + sFileName_OUT + ' ... OK')
                            #-------------------------------------------------------------------------------------
                        
                        #-------------------------------------------------------------------------------------
                            
                    except:
                        
                        #-------------------------------------------------------------------------------------
                        # Exit code
                        a1bFileCheck_OUT.append(False)
                        # Info
                        GetException(' ------> WARNING: errors occurred in saving file! Check your output data!', 2, 1)
                        oLogStream.info( ' ------> Saving file output (NC): ' + sFileName_OUT + ' ... FAILED --- ERRORS OCCURRED IN SAVING DATA!')
                        #-------------------------------------------------------------------------------------
                    
                    #-------------------------------------------------------------------------------------
    
                    #-------------------------------------------------------------------------------------
                    # Check saved data NC
                    if np.all(np.asarray(a1bFileCheck_OUT) == True ):
                        # Create hash handle
                        sFileCache_OUT = os.path.join(sPathCache_OUT, 'Satellite_MODIS-SNOW_FILENC_' + sVarTime_OUT + '_' + sVarName_OUT +'.history')
                        
                        # Adding filename(s) IN
                        for sFileTile_IN in a1sFileTile_IN: a1sFileName_OUT.append(sFileTile_IN)
                        
                        # Save history file for NC
                        writeFileHistory(sFileCache_OUT, zip(a1sFileName_OUT))
                    else:
                        # Info warning
                        GetException(' ------> WARNING: some files are not saved on disk! Check your data input!', 2, 1)
                    
                    # SAVE DATA IN NC FORMAT (END)
                    #-------------------------------------------------------------------------------------
                    
                #-------------------------------------------------------------------------------------
                
                #-------------------------------------------------------------------------------------
                # Info
                oLogStream.info( ' ====> SAVE DATA AT TIME: ' + sTime + ' ...  OK ')
                #-------------------------------------------------------------------------------------
                
            else:
                
                #-------------------------------------------------------------------------------------
                # Info
                oLogStream.info( ' ====> SAVE DATA AT TIME: ' + sTime + ' ...  SKIPPED - All data are empty! Check your input files!')
                #-------------------------------------------------------------------------------------
            
            
            #-------------------------------------------------------------------------------------
        
        else:
            
            #-------------------------------------------------------------------------------------
            # Info
            oLogStream.info( ' ====> SAVE DATA AT TIME: ' + sTime + ' ... SKIPPED --- ALL DATA PROCESSED PREVIOUSLY!')

            #-------------------------------------------------------------------------------------
        
    #-------------------------------------------------------------------------------------
    
#-------------------------------------------------------------------------------------
    
