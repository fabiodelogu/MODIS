"""
Class Features

Name:          Drv_Apps_StaticData
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20150903'
Version:       '1.0.11'
"""

######################################################################################
# Logging
import logging
oLogStream = logging.getLogger('sLogger')

# Library
import os
import subprocess

import numpy as np

from os.path import join
from os.path import isfile

import Lib_Data_IO_Utils

from GetException import GetException
from Drv_Data_IO import Drv_Data_IO

# Debug
import matplotlib.pylab as plt
######################################################################################

#-------------------------------------------------------------------------------------
# Class
class Drv_Data_Land:

    #-------------------------------------------------------------------------------------
    # Method init class
    def __init__(self, oDataInfo=None):
        
        #-------------------------------------------------------------------------------------
        # Initialize common variable(s)
        self.oDataInfo = oDataInfo
        
        # Get input and output variable information
        self.oVarsIN = self.oDataInfo.oInfoVarStatic.oDataInputStatic
        self.oVarsOUT = self.oDataInfo.oInfoVarStatic.oDataOutputStatic
        
        # Get algorithm information
        self.oGeneralInfo = self.oDataInfo.oInfoSettings.oGeneralInfo
        self.oPathInfo = self.oDataInfo.oInfoSettings.oPathInfo
        self.oParamsInfo = self.oDataInfo.oInfoSettings.oParamsInfo
        self.oGeoSystemInfo = self.oDataInfo.oInfoSettings.oGeoSystemInfo
        #-------------------------------------------------------------------------------------
        
    #-------------------------------------------------------------------------------------  
    
    #------------------------------------------------------------------------------------- 
    # Method to define IA values
    def computeVegetationIA(self):
        
        #-------------------------------------------------------------------------------------
        # Check section
        oLogStream.info( ' ------> Compute Vegetation_IA data ... ')
        try:
        
            #-------------------------------------------------------------------------------------
            # Get information
            sFileName = join(self.oPathInfo['DataStaticSource'],
                             self.oVarsIN['ASCII']['VegetationIA']['VarSource'])
            #-------------------------------------------------------------------------------------
            
            
            #-------------------------------------------------------------------------------------
            # Define parameters maps using nested domains and parameters file definition
            if isfile(sFileName) :
                
                #-------------------------------------------------------------------------------------
                # File driver
                oFileDrv = Drv_Data_IO(sFileName,'r')              
                # Get read method selection
                oApps_ReadMethod = getattr(oFileDrv.oFileWorkspace, 
                                          self.oVarsIN['ASCII']['VegetationIA']['VarOp']['Op_Load']['Func'])
                # Get data components
                oFileComp = self.oVarsIN['ASCII']['VegetationIA']['VarOp']['Op_Load']['Comp']
                # Read file
                oFileData = oApps_ReadMethod(oFileComp)
                # Close file
                oFileDrv.oFileWorkspace.closeFile()
                #-------------------------------------------------------------------------------------
                
                #-------------------------------------------------------------------------------------
                # Data value(s)
                a1dData = oFileData['Data']['ia']
                # Data dim(s)
                iDataDim = a1dData.shape
                #-------------------------------------------------------------------------------------
                
                #-------------------------------------------------------------------------------------
                # Save value(s)
                sFileNameOUT = Lib_Data_IO_Utils.defineFileName(join(
                                                               self.oPathInfo['DataStaticOutcome'], 
                                                               self.oVarsOUT['ASCII']['VegetationIA']['VarSource']), 
                                                               {'domain' : self.oParamsInfo['DomainName']})

                # File driver
                oFileDrv = Drv_Data_IO(sFileNameOUT,'w')               
                # Get write method selection
                oApps_WriteMethod = getattr(oFileDrv.oFileWorkspace, 
                                            self.oVarsOUT['ASCII']['VegetationIA']['VarOp']['Op_Save']['Func'])
                # Get data components
                oFileComp = self.oVarsOUT['ASCII']['VegetationIA']['VarOp']['Op_Save']
                # Write file
                oApps_WriteMethod(a1dData, oFileComp['Format'])
                # Close file
                oFileDrv.oFileWorkspace.closeFile()
                #-------------------------------------------------------------------------------------
                
                #-------------------------------------------------------------------------------------
                # Exit status without errors
                oOut = None; oErr = None;
                oLogStream.info( ' ------> Compute Vegetation_IA data ... OK')
                
                # Return values    
                return(oOut, oErr, iDataDim)
                #-------------------------------------------------------------------------------------
                
            else:
                
                #-------------------------------------------------------------------------------------
                # Exit status with warnings
                GetException(' -----> WARNING: file is not available on source folder! Check your settings!',2,1)
                
                # Return values    
                return(oOut, oErr, -9999)
                #-------------------------------------------------------------------------------------
        
        except:
            
            #-------------------------------------------------------------------------------------
            # Exit status with errors
            GetException(' -----> ERROR: Compute Vegetation_IA data ... FAILED',1,1)
            #-------------------------------------------------------------------------------------
            
        #-------------------------------------------------------------------------------------    

    #-------------------------------------------------------------------------------------
        
    #-------------------------------------------------------------------------------------
    # Method to define gridded model parameters
    def computeModelParameters(self, oDataTerrain, oDataWaterMark=None):
        
        #-------------------------------------------------------------------------------------
        # Check section
        oLogStream.info( ' ------> Compute Model_Parameters data ... ')
        try:
        
            #-------------------------------------------------------------------------------------
            # Get information
            sFileName = join(self.oPathInfo['DataStaticSource'],
                             self.oVarsIN['ASCII']['ModelParameters']['VarSource'])
            # Get Mean model parameter
            oParameterMean = self.oParamsInfo['Model_Mean_Parameter']
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Get GeoData
            a2dGeoData = oDataTerrain.a2dGeoData
            dNoData = oDataTerrain.dNoData
            a2bGeoDataNan = oDataTerrain.a2bGeoDataNan
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Initialize grid parameter maps
            a2dDataUc = np.zeros([a2dGeoData.shape[0], a2dGeoData.shape[1]])
            a2dDataUc[:] = np.float32(oParameterMean['uc'])
            a2dDataUh = np.zeros([a2dGeoData.shape[0], a2dGeoData.shape[1]])
            a2dDataUh[:] = np.float32(oParameterMean['uh'])
            a2dDataCt = np.zeros([a2dGeoData.shape[0], a2dGeoData.shape[1]])
            a2dDataCt[:] = np.float32(oParameterMean['ct'])
            a2dDataCf = np.zeros([a2dGeoData.shape[0], a2dGeoData.shape[1]])
            a2dDataCf[:] = np.float32(oParameterMean['cf'])
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Define parameters maps using nested domains and parameters file definition
            if (oDataWaterMark is not None) and (isfile(sFileName)) :
                
                # File driver
                oFileDrv = Drv_Data_IO(sFileName,'r')              
                # Get read method selection
                oApps_ReadMethod = getattr(oFileDrv.oFileWorkspace, 
                                          self.oVarsIN['ASCII']['ModelParameters']['VarOp']['Op_Load']['Func'])
                # Get data components
                oFileComp = self.oVarsIN['ASCII']['ModelParameters']['VarOp']['Op_Load']['Comp']
                # Read file
                oFileData = oApps_ReadMethod(oFileComp)
                # Close file
                oFileDrv.oFileWorkspace.closeFile()
                # Data nested watermark
                a2dDataWaterMark = np.int32(oDataWaterMark.a2dGeoData)
                
                for sCode in oFileData['Data']['code']:
                    
                    if (np.int32(sCode) > 0):
                        iCodeIndex = np.where(np.int32(oFileData['Data']['code']) == np.int32(sCode)) 
                        a2dDataUc[np.where(a2dDataWaterMark == np.int32(sCode))] = oFileData['Data']['uc'][iCodeIndex]
                        a2dDataUh[np.where(a2dDataWaterMark == np.int32(sCode))] = oFileData['Data']['uh'][iCodeIndex]
                        a2dDataCt[np.where(a2dDataWaterMark == np.int32(sCode))] = oFileData['Data']['ct'][iCodeIndex]
                        a2dDataCf[np.where(a2dDataWaterMark == np.int32(sCode))] = oFileData['Data']['cf'][iCodeIndex]
                    else:
                        pass
            else:
                pass
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # PARAMETER Uc
            sParameterName = 'Uc'
            a2dDataUc[a2bGeoDataNan] = dNoData

            # Set boundaries with no data
            [a2dDataUc, oOut, oErr] = self.setNoDataBound(a2dDataUc, dNoData)
  
            # Save parameter map
            sFileNameOUT_Uc = Lib_Data_IO_Utils.defineFileName(join(
                                                              self.oPathInfo['DataStaticOutcome'], 
                                                              self.oVarsOUT['ASCII'][sParameterName]['VarSource']), 
                                                              {'domain' : self.oParamsInfo['DomainName']})
            # File driver
            oFileDrv = Drv_Data_IO(sFileNameOUT_Uc,'w')               
            # Get write method selection
            oApps_WriteMethod = getattr(oFileDrv.oFileWorkspace, 
                                      self.oVarsOUT['ASCII'][sParameterName]['VarOp']['Op_Save']['Func'])
            oFileComp = self.oVarsOUT['ASCII'][sParameterName]['VarOp']['Op_Save']
            # Write file
            oApps_WriteMethod(a2dDataUc, oDataTerrain.a1oGeoInfo, oFileComp['Format'])
            # Close file
            oFileDrv.oFileWorkspace.closeFile()
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # PARAMETER Uh
            sParameterName = 'Uh'
            a2dDataUh[a2bGeoDataNan] = dNoData
            
            # Set boundaries with no data
            [a2dDataUh, oOut, oErr] = self.setNoDataBound(a2dDataUh, dNoData)
            
            # Save parameter map
            sFileNameOUT_Uc = Lib_Data_IO_Utils.defineFileName(join(
                                                              self.oPathInfo['DataStaticOutcome'], 
                                                              self.oVarsOUT['ASCII'][sParameterName]['VarSource']), 
                                                              {'domain' : self.oParamsInfo['DomainName']})
            # File driver
            oFileDrv = Drv_Data_IO(sFileNameOUT_Uc,'w')               
            # Get write method selection
            oApps_WriteMethod = getattr(oFileDrv.oFileWorkspace, 
                                      self.oVarsOUT['ASCII'][sParameterName]['VarOp']['Op_Save']['Func'])
            oFileComp = self.oVarsOUT['ASCII'][sParameterName]['VarOp']['Op_Save']
            # Write file
            oApps_WriteMethod(a2dDataUh, oDataTerrain.a1oGeoInfo, oFileComp['Format'])
            # Close file
            oFileDrv.oFileWorkspace.closeFile()
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # PARAMETER Ct
            sParameterName = 'Ct'
            a2dDataCt[a2bGeoDataNan] = dNoData
            
            # Set boundaries with no data
            [a2dDataCt, oOut, oErr] = self.setNoDataBound(a2dDataCt, dNoData)
            
            # Save parameter map
            sFileNameOUT_Uc = Lib_Data_IO_Utils.defineFileName(join(
                                                              self.oPathInfo['DataStaticOutcome'], 
                                                              self.oVarsOUT['ASCII'][sParameterName]['VarSource']), 
                                                              {'domain' : self.oParamsInfo['DomainName']})
            # File driver
            oFileDrv = Drv_Data_IO(sFileNameOUT_Uc,'w')               
            # Get write method selection
            oApps_WriteMethod = getattr(oFileDrv.oFileWorkspace, 
                                      self.oVarsOUT['ASCII'][sParameterName]['VarOp']['Op_Save']['Func'])
            oFileComp = self.oVarsOUT['ASCII'][sParameterName]['VarOp']['Op_Save']
            # Write file
            oApps_WriteMethod(a2dDataCt, oDataTerrain.a1oGeoInfo, oFileComp['Format'])
            # Close file
            oFileDrv.oFileWorkspace.closeFile()
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # PARAMETER Cf
            sParameterName = 'Cf'
            a2dDataCf[a2bGeoDataNan] = dNoData
            
            # Set boundaries with no data
            [a2dDataCf, oOut, oErr] = self.setNoDataBound(a2dDataCf, dNoData)
            
            # Save parameter map
            sFileNameOUT_Uc = Lib_Data_IO_Utils.defineFileName(join(
                                                              self.oPathInfo['DataStaticOutcome'], 
                                                              self.oVarsOUT['ASCII'][sParameterName]['VarSource']), 
                                                              {'domain' : self.oParamsInfo['DomainName']})
            # File driver
            oFileDrv = Drv_Data_IO(sFileNameOUT_Uc,'w')               
            # Get write method selection
            oApps_WriteMethod = getattr(oFileDrv.oFileWorkspace, 
                                      self.oVarsOUT['ASCII'][sParameterName]['VarOp']['Op_Save']['Func'])
            oFileComp = self.oVarsOUT['ASCII'][sParameterName]['VarOp']['Op_Save']
            # Write file
            oApps_WriteMethod(a2dDataCf, oDataTerrain.a1oGeoInfo, oFileComp['Format'])
            # Close file
            oFileDrv.oFileWorkspace.closeFile()
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Exit status without errors
            oOut = None; oErr = None;
            oLogStream.info( ' ------> Compute Model_Parameters data ... OK')

            # Return values    
            return(oOut, oErr)
            #-------------------------------------------------------------------------------------
        
        except:
            
            #-------------------------------------------------------------------------------------
            # Exit status with errors
            GetException(' -----> ERROR: Compute Model_Parameters data ... FAILED',1,1)
            #-------------------------------------------------------------------------------------
            
        #-------------------------------------------------------------------------------------    

    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to calculate flow directions
    def computeTerrain(self, oDataTerrain):
        
        #-------------------------------------------------------------------------------------
        # Check section
        oLogStream.info( ' ------> Compute Terrain data ... ')
        try:
            
            #-------------------------------------------------------------------------------------
            # Define filename
            sFileNameOUT = Lib_Data_IO_Utils.defineFileName(join(
                                                           self.oPathInfo['DataStaticOutcome'], 
                                                           self.oVarsOUT['ASCII']['Terrain']['VarSource']), 
                                                           {'domain' : self.oParamsInfo['DomainName']})
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Data 
            dNoData = oDataTerrain.a1oGeoInfo['NODATA_value']
            a2dData = oDataTerrain.a2dGeoData
            a2dData[np.where(np.isnan(a2dData))] = dNoData
                
            # Set boundaries with no data
            [a2dData, oOut, oErr] = self.setNoDataBound(a2dData, dNoData)
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # File driver
            oFileDrv = Drv_Data_IO(sFileNameOUT,'w')   
            # Get write method selection
            oApps_WriteMethod = getattr(oFileDrv.oFileWorkspace, 
                                      self.oVarsOUT['ASCII']['Terrain']['VarOp']['Op_Save']['Func'])
            oFileComp = self.oVarsOUT['ASCII']['Terrain']['VarOp']['Op_Save']
            # Write file
            oApps_WriteMethod(a2dData, oDataTerrain.a1oGeoInfo, oFileComp['Format'])
            # Close file
            oFileDrv.oFileWorkspace.closeFile()
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Exit status without errors
            oOut = None; oErr = None;
            oLogStream.info( ' ------> Compute Terrain data ... OK ')
            
            # Return values
            return(oOut, oErr)
            #-------------------------------------------------------------------------------------
            
        except:
            
            #-------------------------------------------------------------------------------------
            # Exit status with errors
            GetException(' -----> ERROR: Compute Terrain data ... FAILED',1,1)
            #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to calculate flow directions
    def computeVegetationType(self, oDataVegType, oDataTerrain):
        
        #-------------------------------------------------------------------------------------
        # Check section
        oLogStream.info( ' ------> Compute VegetationType data ... ')
        try:
            
            #-------------------------------------------------------------------------------------
            # Define filename
            sFileNameOUT = Lib_Data_IO_Utils.defineFileName(join(
                                                           self.oPathInfo['DataStaticOutcome'], 
                                                           self.oVarsOUT['ASCII']['VegetationType']['VarSource']), 
                                                           {'domain' : self.oParamsInfo['DomainName']})
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Data 
            dNoData = oDataVegType.a1oGeoInfo['NODATA_value']
            a2dData = oDataVegType.a2dGeoData
            a2dData[np.where(np.isnan(a2dData))] = dNoData
            
            # Apply terrain nan value
            a2dData[oDataTerrain.a2bGeoDataNan] = dNoData
            
            # Set boundaries with no data
            [a2dData, oOut, oErr] = self.setNoDataBound(a2dData, dNoData)
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # File driver
            oFileDrv = Drv_Data_IO(sFileNameOUT,'w')             
            # Get write method selection
            oApps_WriteMethod = getattr(oFileDrv.oFileWorkspace, 
                                      self.oVarsOUT['ASCII']['VegetationType']['VarOp']['Op_Save']['Func'])
            oFileComp = self.oVarsOUT['ASCII']['VegetationType']['VarOp']['Op_Save']
            # Write file
            oApps_WriteMethod(a2dData, oDataVegType.a1oGeoInfo, oFileComp['Format'])
            # Close file
            oFileDrv.oFileWorkspace.closeFile()
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Exit status without errors
            oOut = None; oErr = None;
            oLogStream.info( ' ------> Compute VegetationType data ... OK')
            
            # Return values
            return(oOut, oErr)
            #-------------------------------------------------------------------------------------
        
        except:
            
            #-------------------------------------------------------------------------------------
            # Exit status with errors
            GetException(' -----> ERROR: Compute VegetationType data ... FAILED',1,1)
            #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to calculate flow directions
    def computeFlowDirections(self, oDataGeo):
        
        #-------------------------------------------------------------------------------------
        # Check section
        oLogStream.info( ' ------> Compute Flow_Directions data ... ')
        try:
            
            #-------------------------------------------------------------------------------------
            # Get and define filename IN (dem)
            sFileNameIN = Lib_Data_IO_Utils.defineFileName(join(
                                                          self.oPathInfo['DataStaticSource'], 
                                                          self.oVarsIN['ASCII']['Terrain']['VarSource']), 
                                                          {'domain' : self.oParamsInfo['DomainName']})
            # Get and define filename OUT (pnt)
            sFileNameOUT = Lib_Data_IO_Utils.defineFileName(join(
                                                          self.oPathInfo['DataStaticOutcome'], 
                                                          self.oVarsOUT['ASCII']['Flow_Directions']['VarSource']), 
                                                          {'domain' : self.oParamsInfo['DomainName']})
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Get path library information
            sPathLibrary = self.oPathInfo['Library']
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Define command line
            # ./flow_directions.x basin.dem.txt
            os.chdir(sPathLibrary)
            sLineCommand = './flow_directions.x ' + sFileNameIN + ' ' + sFileNameOUT
            oLogStream.info(sLineCommand)
            # Execute algorithm
            oPr = subprocess.Popen(sLineCommand, shell=True)
            oOut, oErr = oPr.communicate()
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Rewrite pnt
            #self.rewriteGrid(sFileNameOUT, self.oVarsOUT['ASCII']['Flow_Directions'] , oDataGeo)
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Exit status without errors
            oLogStream.info( ' ------> Compute Flow_Directions data ... OK')
        
            # Return values
            return(oOut, oErr)
            #-------------------------------------------------------------------------------------
        
        except:
            
            #-------------------------------------------------------------------------------------
            # Exit status with errors
            GetException(' -----> ERROR: Compute Flow_Directions data ... FAILED',1,1)
            #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to define mask domain
    def computeMask(self, oDataTerrain, oDataVegType, oDataMask):
        
        #-------------------------------------------------------------------------------------
        # Check section
        oLogStream.info( ' ------> Compute Mask data ... ')
        try:
            
            #-------------------------------------------------------------------------------------
            # Get and define filename OUT
            sFileNameOUT = Lib_Data_IO_Utils.defineFileName(join(
                                                           self.oPathInfo['DataStaticOutcome'], 
                                                           self.oVarsOUT['ASCII']['Mask']['VarSource']), 
                                                           {'domain' : self.oParamsInfo['DomainName']})
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Initialize mask map
            a2iMask = np.zeros([oDataTerrain.a2dGeoData.shape[0], oDataTerrain.a2dGeoData.shape[1]])
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Check data mask availability
            if oDataMask.oGeoData is None:
            
                #-------------------------------------------------------------------------------------
                # Checking terrain and vegtype finite values
                a2iMask[np.where(oDataTerrain.a2bGeoDataFinite==True)] = 1
                a2iMask[np.where(oDataVegType.a2bGeoDataFinite==False)] = 0
                
                # Set nodata value
                a2iMask[oDataTerrain.a2bGeoDataNan] = oDataTerrain.dNoData
                #-------------------------------------------------------------------------------------
                
            else:
                #-------------------------------------------------------------------------------------
                # Set nodata value
                a2iMask = oDataMask.a2dGeoData
                # Set nodata value
                a2iMask[oDataMask.a2bGeoDataNan] = oDataMask.dNoData
                a2iMask[a2iMask > 0] = 1
                #-------------------------------------------------------------------------------------
          
            #-------------------------------------------------------------------------------------
 
            #-------------------------------------------------------------------------------------
            # Set boundaries with no data
            [a2iMask, oOut, oErr] = self.setNoDataBound(a2iMask, oDataTerrain.dNoData)
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # File driver
            oFileDrv = Drv_Data_IO(sFileNameOUT,'w')            
            # Get write method selection
            oApps_WriteMethod = getattr(oFileDrv.oFileWorkspace, 
                                      self.oVarsOUT['ASCII']['Mask']['VarOp']['Op_Save']['Func'])
            oFileComp = self.oVarsOUT['ASCII']['Mask']['VarOp']['Op_Save']
            # Write file
            oApps_WriteMethod(a2iMask, oDataVegType.a1oGeoInfo, oFileComp['Format'])
            # Close file
            oFileDrv.oFileWorkspace.closeFile()
            #-------------------------------------------------------------------------------------
                        
            #-------------------------------------------------------------------------------------
            # Exit status without errors
            oOut = None; oErr = None;
            oLogStream.info( ' ------> Compute Mask data ... OK')
            
            # Return values
            return(oOut, oErr)
            #-------------------------------------------------------------------------------------
            
        except:
            
            #-------------------------------------------------------------------------------------
            # Exit status with errors
            GetException(' -----> ERROR: Compute Mask data ... FAILED',1,1)
            #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to calculate cell area
    def computeCellArea(self, oDataGeo):
        
        #-------------------------------------------------------------------------------------
        # Check section
        oLogStream.info( ' ------> Compute Cell_Area data ... ')
        try:
            
            #-------------------------------------------------------------------------------------
            # Get and define filename OUT
            sFileNameOUT = Lib_Data_IO_Utils.defineFileName(join(
                                                           self.oPathInfo['DataStaticOutcome'], 
                                                           self.oVarsOUT['ASCII']['Cell_Area']['VarSource']), 
                                                           {'domain' : self.oParamsInfo['DomainName']})
            #-------------------------------------------------------------------------------------
                        
            #-------------------------------------------------------------------------------------
            # Get Info
            a2dGeoX = oDataGeo.oGeoData.a2dGeoX; a2dGeoY = oDataGeo.oGeoData.a2dGeoY
            dGeoXCellSize = oDataGeo.oGeoData.dGeoXStep; 
            dGeoYCellSize = oDataGeo.oGeoData.dGeoYStep
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Dynamic values (NEW)
            dR = 6378388        # (Radius)
            dE = 0.00672267     # (Ellipsoid)
            
            # dx = (R * cos(lat)) / (sqrt(1 - e2 * sqr(sin(lat)))) * PI / 180
            a2dDX = ( dR*np.cos( a2dGeoY*np.pi/180 ) )/(np.sqrt(1 - dE*np.sqrt(np.sin( a2dGeoY*np.pi/180 ))))*np.pi/180                                 
            # dy = (R * (1 - e2)) / pow((1 - e2 * sqr(sin(lat))),1.5) * PI / 180
            a2dDY = ( dR*(1 - dE) )/ np.power((1 - dE*np.sqrt(np.sin( a2dGeoY/180) )), 1.5 )*np.pi/180
            
            a2dGeoAreaKm = ((a2dDX/(1/dGeoXCellSize)) * (a2dDY/(1/dGeoYCellSize))) / 1000000 # [km^2]
            a2dGeoAreaM = ((a2dDX/(1/dGeoXCellSize)) * (a2dDY/(1/dGeoYCellSize))) # [m^2]
            
            # Area, Mean Dx and Dy values (meters)
            a2dData = a2dGeoAreaM
            self.dGeoAreaMetersDxMean = np.sqrt(np.nanmean(a2dGeoAreaM)); 
            self.dGeoAreaMetersDyMean = np.sqrt(np.nanmean(a2dGeoAreaM));
            
            # Set nodata value
            a2dData[oDataGeo.a2bGeoDataNan] = oDataGeo.dNoData
            
            # Set boundaries with no data
            [a2dData, oOut, oErr] = self.setNoDataBound(a2dData, oDataGeo.dNoData)
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # File driver
            oFileDrv = Drv_Data_IO(sFileNameOUT,'w')
                                
            # Get write method selection
            oApps_WriteMethod = getattr(oFileDrv.oFileWorkspace, 
                                      self.oVarsOUT['ASCII']['Cell_Area']['VarOp']['Op_Save']['Func'])
            oFileComp = self.oVarsOUT['ASCII']['Cell_Area']['VarOp']['Op_Save']
            # Write file
            oApps_WriteMethod(a2dData, oDataGeo.a1oGeoInfo, oFileComp['Format'])
            # Close file
            oFileDrv.oFileWorkspace.closeFile()
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Exit status without errors
            oOut = None; oErr = None;
            oLogStream.info( ' ------> Compute Cell_Area data ... OK')
            
            # Return values
            return(oOut, oErr)
            #-------------------------------------------------------------------------------------
            
        except:
            
            #-------------------------------------------------------------------------------------
            # Exit status with errors
            GetException(' -----> ERROR: Compute Cell_Area data ... FAILED',1,1)
            #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to calculate channels network
    def computeChannelsDistinction(self, oDataGeo):
        
        #-------------------------------------------------------------------------------------
        # Check section
        oLogStream.info( ' ------> Compute Channels_Distinction data ... ')
        try:
            
            #-------------------------------------------------------------------------------------
            # Get and define filename IN (dem)
            sFileNameIN_1 = Lib_Data_IO_Utils.defineFileName(join(
                                                            self.oPathInfo['DataStaticOutcome'], 
                                                            self.oVarsOUT['ASCII']['Terrain']['VarSource']), 
                                                            {'domain' : self.oParamsInfo['DomainName']})
            # Get and define filename IN (pnt)
            sFileNameIN_2 = Lib_Data_IO_Utils.defineFileName(join(
                                                            self.oPathInfo['DataStaticOutcome'], 
                                                            self.oVarsOUT['ASCII']['Flow_Directions']['VarSource']), 
                                                            {'domain' : self.oParamsInfo['DomainName']})
            # Get and define filename OUT (area)
            sFileNameIN_3 = Lib_Data_IO_Utils.defineFileName(join(
                                                            self.oPathInfo['DataStaticOutcome'], 
                                                            self.oVarsOUT['ASCII']['Drainage_Area']['VarSource']), 
                                                            {'domain' : self.oParamsInfo['DomainName']})
            # Get and define filename OUT (choice)
            sFileNameOUT_1 = Lib_Data_IO_Utils.defineFileName(join(
                                                             self.oPathInfo['DataStaticOutcome'], 
                                                             self.oVarsOUT['ASCII']['Channels_Distinction']['VarSource']), 
                                                             {'domain' : self.oParamsInfo['DomainName']})
            # Get and define filename OUT (pdistance)
            sFileNameOUT_2 = Lib_Data_IO_Utils.defineFileName(join(
                                                             self.oPathInfo['DataStaticOutcome'], 
                                                             self.oVarsOUT['ASCII']['Partial_Distance']['VarSource']), 
                                                             {'domain' : self.oParamsInfo['DomainName']})
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Get information
            sPathLibrary = self.oPathInfo['Library']
            dASk = self.oParamsInfo['Channels_Distinction_Parameter']
            iGeoAreaMetersMean = np.int(np.around(np.mean([self.dGeoAreaMetersDxMean, self.dGeoAreaMetersDyMean])))
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Define command line
            # ./channels_distinction.x path_file domain_name dem_step_meters AS^k
            os.chdir(sPathLibrary)
            sLineCommand = ('./channels_distinction.x ' + sFileNameIN_1 + ' ' + sFileNameIN_2 + ' ' + sFileNameIN_3 + ' ' +
                            sFileNameOUT_1 + ' ' + sFileNameOUT_2 + ' ' +
                            str(iGeoAreaMetersMean) + ' ' + str(dASk) )
            oLogStream.info(sLineCommand)
            # Execute algorithm
            oPr = subprocess.Popen(sLineCommand, shell=True)
            oOut, oErr = oPr.communicate()
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Rewrite choice
            #self.rewriteGrid(sFileNameOUT_1, self.oVarsOUT['ASCII']['Channels_Distinction'] , oDataGeo)
            # Rewrite pdistance
            #self.rewriteGrid(sFileNameOUT_2, self.oVarsOUT['ASCII']['Partial_Distance'] , oDataGeo)
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Exit status without errors
            oOut = None; oErr = None;
            oLogStream.info( ' ------> Compute Channels_Distinction data ... OK')
            
            # Return values
            return(oOut, oErr)
            #-------------------------------------------------------------------------------------
            
        except:
            
            #-------------------------------------------------------------------------------------
            # Exit status with errors
            GetException(' -----> ERROR: Compute Channels_Distinction data ... FAILED',1,1)
            #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------
        
    #-------------------------------------------------------------------------------------
    # Method to calculate drainage area for each pixel domain
    def computeDrainageArea(self, oDataGeo):
        
        #-------------------------------------------------------------------------------------
        # Check section
        oLogStream.info( ' ------> Compute Drainage_Area data ... ')
        try:
            
            #-------------------------------------------------------------------------------------
            # Get and define filename IN (dem)
            sFileNameIN_1 = Lib_Data_IO_Utils.defineFileName(join(
                                                            self.oPathInfo['DataStaticOutcome'], 
                                                            self.oVarsOUT['ASCII']['Terrain']['VarSource']), 
                                                            {'domain' : self.oParamsInfo['DomainName']})
            # Get and define filename IN (pnt)
            sFileNameIN_2 = Lib_Data_IO_Utils.defineFileName(join(
                                                            self.oPathInfo['DataStaticOutcome'], 
                                                            self.oVarsOUT['ASCII']['Flow_Directions']['VarSource']), 
                                                            {'domain' : self.oParamsInfo['DomainName']})
            # Get and define filename OUT (area)
            sFileNameOUT = Lib_Data_IO_Utils.defineFileName(join(
                                                            self.oPathInfo['DataStaticOutcome'], 
                                                            self.oVarsOUT['ASCII']['Drainage_Area']['VarSource']), 
                                                            {'domain' : self.oParamsInfo['DomainName']})
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Get path library information
            sPathLibrary = self.oPathInfo['Library']
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Define command line
            # ./drainage_area.x path_file domain_name
            os.chdir(sPathLibrary)
            sLineCommand = './drainage_area.x ' + sFileNameIN_1 + ' ' + sFileNameIN_2 + ' ' + sFileNameOUT
            oLogStream.info(sLineCommand)
            # Execute algorithm
            oPr = subprocess.Popen(sLineCommand, shell=True)
            oOut, oErr = oPr.communicate()
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Rewrite area
            #self.rewriteGrid(sFileNameOUT, self.oVarsOUT['ASCII']['Drainage_Area'] , oDataGeo)
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Exit status without errors
            oOut = None; oErr = None;
            oLogStream.info( ' ------> Compute Drainage_Area data ... OK')
            
            # Return values
            return(oOut, oErr)
            #-------------------------------------------------------------------------------------
            
        except:
            
            #-------------------------------------------------------------------------------------
            # Exit status with errors
            GetException(' -----> ERROR: Compute Drainage_Area data ... FAILED',1,1)
            #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to calculate watertable slopes
    def computeWatertableSlopes(self, oDataGeo):
        
        #-------------------------------------------------------------------------------------
        # Check section
        oLogStream.info( ' ------> Compute Watertable_Slopes data ... ')
        try:
            
            #-------------------------------------------------------------------------------------
            # Get and define filename IN (dem)
            sFileNameIN_1 = Lib_Data_IO_Utils.defineFileName(join(
                                                            self.oPathInfo['DataStaticOutcome'], 
                                                            self.oVarsOUT['ASCII']['Terrain']['VarSource']), 
                                                            {'domain' : self.oParamsInfo['DomainName']})
            # Get and define filename IN (pnt)
            sFileNameIN_2 = Lib_Data_IO_Utils.defineFileName(join(
                                                            self.oPathInfo['DataStaticOutcome'], 
                                                            self.oVarsOUT['ASCII']['Flow_Directions']['VarSource']), 
                                                            {'domain' : self.oParamsInfo['DomainName']})
            # Get and define filename IN (choice)
            sFileNameIN_3 = Lib_Data_IO_Utils.defineFileName(join(
                                                            self.oPathInfo['DataStaticOutcome'], 
                                                            self.oVarsOUT['ASCII']['Channels_Distinction']['VarSource']), 
                                                            {'domain' : self.oParamsInfo['DomainName']})
            # Get and define filename IN (area cell)
            sFileNameIN_4 = Lib_Data_IO_Utils.defineFileName(join(
                                                            self.oPathInfo['DataStaticOutcome'], 
                                                            self.oVarsOUT['ASCII']['Cell_Area']['VarSource']), 
                                                            {'domain' : self.oParamsInfo['DomainName']})
            # Get and define filename OUT (alpha)
            sFileNameOUT_1 = Lib_Data_IO_Utils.defineFileName(join(
                                                             self.oPathInfo['DataStaticOutcome'], 
                                                             self.oVarsOUT['ASCII']['Wt_Alpha']['VarSource']), 
                                                             {'domain' : self.oParamsInfo['DomainName']})
            # Get and define filename IN (beta)
            sFileNameOUT_2 = Lib_Data_IO_Utils.defineFileName(join(
                                                             self.oPathInfo['DataStaticOutcome'], 
                                                             self.oVarsOUT['ASCII']['Wt_Beta']['VarSource']), 
                                                             {'domain' : self.oParamsInfo['DomainName']})
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Get information
            sPathLibrary = self.oPathInfo['Library']
            dWtDistance = self.oParamsInfo['Wt_Parameter']
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Define command line
            # ./watertable_slopes.x path_file domain_name wt_distance_influence
            os.chdir(sPathLibrary)
            sLineCommand = ('./watertable_slopes.x ' + sFileNameIN_1 + ' ' + sFileNameIN_2 + ' ' + 
                            sFileNameIN_3 + ' ' + sFileNameIN_4 + ' ' +
                            sFileNameOUT_1 + ' ' + sFileNameOUT_2 + ' ' +
                            str(dWtDistance))
            oLogStream.info(sLineCommand)
            
            # Execute algorithm
            oPr = subprocess.Popen(sLineCommand, shell=True)
            oOut, oErr = oPr.communicate()
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Rewrite alpha 
            #self.rewriteGrid(sFileNameOUT_1, self.oVarsOUT['ASCII']['Wt_Alpha'] , oDataGeo)
            # Rewrite beta
            #self.rewriteGrid(sFileNameOUT_2, self.oVarsOUT['ASCII']['Wt_Beta'] , oDataGeo)
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Exit status without errors
            oOut = None; oErr = None;
            oLogStream.info( ' ------> Compute Watertable_Slopes data ... OK')
            
            # Return values
            return(oOut, oErr)
            #-------------------------------------------------------------------------------------
        
        except:
            
            #-------------------------------------------------------------------------------------
            # Exit status with errors
            GetException(' -----> ERROR: Compute Watertable_Slopes data ... FAILED',1,1)
            #-------------------------------------------------------------------------------------
        
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to calculate coefficient resolution map
    def computeCoeffResMap(self, oDataGeo):
        
        #-------------------------------------------------------------------------------------
        # Check section
        oLogStream.info( ' ------> Compute Coeff_Res_Map data ... ')
        try:
            
            #-------------------------------------------------------------------------------------
            # Get and define filename IN (dem)
            sFileNameIN_1 = Lib_Data_IO_Utils.defineFileName(join(
                                                            self.oPathInfo['DataStaticOutcome'], 
                                                            self.oVarsOUT['ASCII']['Terrain']['VarSource']), 
                                                            {'domain' : self.oParamsInfo['DomainName']})
            # Get and define filename IN (area)
            sFileNameIN_2 = Lib_Data_IO_Utils.defineFileName(join(
                                                            self.oPathInfo['DataStaticOutcome'], 
                                                            self.oVarsOUT['ASCII']['Drainage_Area']['VarSource']), 
                                                            {'domain' : self.oParamsInfo['DomainName']})
            # Get and define filename IN (choice)
            sFileNameIN_3 = Lib_Data_IO_Utils.defineFileName(join(
                                                            self.oPathInfo['DataStaticOutcome'], 
                                                            self.oVarsOUT['ASCII']['Channels_Distinction']['VarSource']), 
                                                            {'domain' : self.oParamsInfo['DomainName']})
            # Get and define filename IN (area cell)
            sFileNameIN_4 = Lib_Data_IO_Utils.defineFileName(join(
                                                            self.oPathInfo['DataStaticOutcome'], 
                                                            self.oVarsOUT['ASCII']['Cell_Area']['VarSource']), 
                                                            {'domain' : self.oParamsInfo['DomainName']})
            # Get and define filename OUT (coeffresmap)
            sFileNameOUT = Lib_Data_IO_Utils.defineFileName(join(
                                                           self.oPathInfo['DataStaticOutcome'], 
                                                           self.oVarsOUT['ASCII']['Coeff_Resol_Map']['VarSource']), 
                                                           {'domain' : self.oParamsInfo['DomainName']})
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Get information
            sPathLibrary = self.oPathInfo['Library']
            dCoeffResDef = self.oParamsInfo['Coeff_Resol_Map_Parameter']
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Define command line
            # ./coeff_resolution_map.x demfile areafile choicefile cellareafiel outfile coeffresparameter 
            os.chdir(sPathLibrary)
            sLineCommand = ('./coeff_resolution_map.x ' + sFileNameIN_1 + ' ' + sFileNameIN_2 + ' ' + 
                            sFileNameIN_3 + ' ' + sFileNameIN_4 + ' ' +
                            sFileNameOUT + ' ' +
                            str(dCoeffResDef))
            oLogStream.info(sLineCommand)
            
            # Execute algorithm
            oPr = subprocess.Popen(sLineCommand, shell=True)
            oOut, oErr = oPr.communicate()
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Rewrite coefficient resolution map
            #self.rewriteGrid(sFileNameOUT, self.oVarsOUT['ASCII']['Coeff_Resol_Map'] , oDataGeo)
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Exit status without errors
            oOut = None; oErr = None;
            oLogStream.info( ' ------> Compute Coeff_Res_Map data ... OK')
            
            # Return values
            return(oOut, oErr)
            #-------------------------------------------------------------------------------------
        
        except:
            
            #-------------------------------------------------------------------------------------
            # Exit status with errors
            GetException(' -----> ERROR: Compute Coeff_Res_Map data ... FAILED',1,1)
            #-------------------------------------------------------------------------------------
        
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to set no-data values into data map boundaries
    def setNoDataBound(self, a2dData, dNoData):
           
        #-------------------------------------------------------------------------------------
        # Check section
        try:
            
            #-------------------------------------------------------------------------------------
            # Set boundaries with no-data value
            a2dData[0,:] = dNoData              # First row
            a2dData[:,0] = dNoData              # First column
            a2dData[-1,:] = dNoData             # Last row
            a2dData[:,-1] = dNoData             # Last column
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Exit status without errors
            oOut = None; oErr = None;
            
            # Return values
            return(a2dData, oOut, oErr)
            #-------------------------------------------------------------------------------------
            
        except:
            
            #-------------------------------------------------------------------------------------
            # Exit status with errors
            GetException(' -----> ERROR: setNoDataBoud function ... FAILED',1,1)
            #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to rewrite grid data in ascii format
    def rewriteArcGrid(self, sFileName, oDataVar, oDataGeo):
        
        #-------------------------------------------------------------------------------------
        # Check section
        try:
            
            #-------------------------------------------------------------------------------------
            # File driver
            oFileDrv = Drv_Data_IO(sFileName,'r')              
            # Get read method selection
            oApps_ReadMethod = getattr(oFileDrv.oFileWorkspace, 
                                      oDataVar['VarOp']['Op_Load']['Func'])
            # Read file
            oFileData = oApps_ReadMethod()
            # Close file
            oFileDrv.oFileWorkspace.closeFile()
            # Set no data value
            a2dData = oFileData['Data'] 
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Check array rank
            if np.rank(a2dData) == 2:
                
                #-------------------------------------------------------------------------------------
                # Set no data value
                a2dData[oDataGeo.a2bGeoDataNan] = oDataGeo.dNoData
                #-------------------------------------------------------------------------------------
                
                #-------------------------------------------------------------------------------------
                # Remove old file
                os.remove(sFileName)
                #-------------------------------------------------------------------------------------
                
                #-------------------------------------------------------------------------------------
                # Set boundaries with no data
                [a2dData, oOut, oErr] = self.setNoDataBound(a2dData, oDataGeo.dNoData)
                #-------------------------------------------------------------------------------------
                
                #-------------------------------------------------------------------------------------
                # File driver
                oFileDrv = Drv_Data_IO(sFileName,'w')
                # Get write method selection
                oApps_WriteMethod = getattr(oFileDrv.oFileWorkspace, 
                                          oDataVar['VarOp']['Op_Save']['Func'])
                oFileComp = oDataVar['VarOp']['Op_Save']
                # Write file
                oApps_WriteMethod(a2dData, oDataGeo.a1oGeoInfo, oFileComp['Format'])
                # Close file
                oFileDrv.oFileWorkspace.closeFile()
                #-------------------------------------------------------------------------------------
                
                #-------------------------------------------------------------------------------------
                # Exit status without errors
                oOut = None; oErr = None;
                
                # Return values
                return(oOut, oErr)
                #-------------------------------------------------------------------------------------
            
            else:
                
                #-------------------------------------------------------------------------------------
                # Exit status with warning
                GetException(' -----> WARNING: rewriteArcGrid function ... FAILED - Array rank is not 2! ',2,1)
                #-------------------------------------------------------------------------------------
                
        except:
            
            #-------------------------------------------------------------------------------------
            # Exit status with errors
            GetException(' -----> ERROR: rewriteArcGrid function ... FAILED',1,1)
            #-------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------
    
    
    
    
