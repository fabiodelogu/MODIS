"""
Class Features

Name:          Drv_Data_FTP (using lftp service)
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
import datetime
import glob
import shutil
import numpy as np
import time

import subprocess

from os.path import join

from GetException import GetException
from Lib_Data_IO_Utils import defineFolderName

#import matplotlib.pylab as plt
######################################################################################

#-------------------------------------------------------------------------------------
# Class reading settings
class Drv_Data_FTP:


    #--------------------------------------------------------------------------------
    # Class init
    def __init__(self, oInfoData=None, sProductName=None, sTime=None):
        
        # Set global information
        self.oInfoData = oInfoData
        self.sTime = sTime

        # Define FTPType and FileWorkspace
        if sProductName == 'MODIS':
            
            # Get settings and var information
            oInfoSettings = oInfoData.oInfoSettings
            oInfoVar = oInfoData.oInfoVarDynamic.oDataInputDynamic['FTP']
            # Call class
            self.oFileWorkspace = MODIS(oInfoSettings, oInfoVar, self.sTime)
        
        else:
            # Exit code
            self.oFileWorkspace = {}
            GetException(' -----> ERROR: product name unknown! Please check your settings file!',1,1)

    #-------------------------------------------------------------------------------------
    
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Class to get MODIS File
class MODIS:
    
    #--------------------------------------------------------------------------------
    # Class init
    def __init__(self, oInfoSettings, oInfoVar, sTime):
        
        # Set global class information
        self.oInfoSettings = oInfoSettings
        self.oInfoVar = oInfoVar
        self.sTime = sTime
        
        # Cycle on variable name
        for sVarName in oInfoVar.keys():
        
            # Select file type
            if  sVarName == 'MOD10A1.005':
            
                # Get file and return filename
                [self.sFileName, self.bFileName, 
                 self.sFileProduct, self.sFileVersion, self.sFileComp, 
                 self.a1sFileTile] = self.getFileSnow(sVarName); 
                 
            elif  sVarName == 'MYD10A1.005':
            
                # Get file and return filename
                [self.sFileName, self.bFileName, 
                 self.sFileProduct, self.sFileVersion, self.sFileComp, 
                 self.a1sFileTile] = self.getFileSnow(sVarName); 

            else:
                # Exit code
                GetException(' -----> ERROR: variable name unknown! Please check your settings file!',1,1)
    #--------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------
    # Get data
    def getFileSnow(self, sVarName):
        
        # Check method
        try:
            
            '''
            MODIS NAMING CONVENTIONS:
            
            MODIS filenames (i.e., the local granule ID) 
            follow a naming convention which gives useful information 
            regarding the specific product. For example, 
            the filename MOD09A1.A2006001.h08v05.005.2006012234657.hdf 
            indicates:
            
            .MOD09A1 - Product Short Name
            .A2006001 - Julian Date of Acquisition (A-YYYYDDD)
            .h08v05 - Tile Identifier (horizontalXXverticalYY)
            .005 - Collection Version
            .2006012234567 - Julian Date of Production (YYYYDDDHHMMSS)
            .hdf - Data Format (HDF-EOS)
            '''
            
            #-------------------------------------------------------------------------------------
            # Select time information
            oTimeGet = datetime.datetime.strptime(self.sTime,'%Y%m%d%H%M%S')
            sTimeGet = oTimeGet.strftime('%Y.%m.%d')
            sYearGet = oTimeGet.strftime('%Y'); sMonthGet = oTimeGet.strftime('%m')
            sDayGet = oTimeGet.strftime('%d')
            
            sTimeSave = oTimeGet.strftime('%Y%m%d')
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Get variable information
            oVarInfo = self.oInfoVar[sVarName]
            # Get FTP and Library information
            oMRTInfo = self.oInfoSettings.oParamsInfo['MRT']
            oFTPInfo = self.oInfoSettings.oParamsInfo['FTP']
            # Get paths information
            sPathTemp = self.oInfoSettings.oPathInfo['DataTemp']
            sPathDataSource = self.oInfoSettings.oPathInfo['DataDynamicSource']
            sPathLibrary = self.oInfoSettings.oPathInfo['Library']
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Define product settings
            oVarName = oVarInfo['VarOp']['Op_GetEx']['Name']
            oVarComp = oVarInfo['VarOp']['Op_GetEx']['Comp']
            
            sVarIndexFormat = '%02d';   iVarIndexN = len(oVarComp)  
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Define FTP Settings
            sFTPFolder = oFTPInfo['Folder']
            sFTPSite = oFTPInfo['Site']; sFTPUser = oFTPInfo['User']; sFTPPass = oFTPInfo['Password']
            sFTPProxy = oFTPInfo['Proxy']
            
            # Define MRT Settings (Modis Reprojection Tool)
            sMRTOptSpacialSubset = oMRTInfo['SpacialSubset'] 
            sMRTOptResampling = oMRTInfo['Resampling']            
            sMRTOptOutputProj = oMRTInfo['OutProj']               
            sMRTOptDatum = oMRTInfo['OutDatum']                        
                
            # Cycling on time steps
            sFileNameFTP = 'modis_ftp_downloader.sh'
            sFileNameMRTResample = 'modis_mrt_params.txt'
            sFileNameMRTMosaic = 'modis_tmp_mosaic.prm'
            sFileNameMRTExec = 'modis_mrt_reproj.sh'
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Removing all old data
            oFileNameOld = glob.glob(sPathTemp + '*')
            for sFileNameOld in oFileNameOld: os.remove(sFileNameOld)
            
            # Source path name
            sPathVarSource = defineFolderName(sPathDataSource,
                                              {'$yyyy' : sYearGet,'$mm' : sMonthGet,'$dd' : sDayGet })
            
            # Defining product folder
            sVarFolder = oVarName['Product'] + '.' + oVarName['Version']     
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Cycle(s) on tile(s)
            oTileLines = {}; bFileNameOUT = False
            a1iTileCheck = np.zeros([iVarIndexN]); a1sFileNameHDF = []
            sVarTile = ''; sVarIndexStep = ''; iTileCounter = 0;
            for sTile in oVarComp:
                
                #-------------------------------------------------------------------------------------
                # Get tile(s) information
                sVarIndexH = 'h' + str(sVarIndexFormat%(int(oVarComp[sTile]['H'])))
                sVarIndexV = 'v' + str(sVarIndexFormat%(int(oVarComp[sTile]['V'])))
                
                # Concatenate string
                sVarTile = sVarTile + '_' + sVarIndexH + sVarIndexV; 
                sVarIndexStep = sVarIndexH + sVarIndexV;
                
                # Info tile
                oLogStream.info( ' ------> Analyze Image Tile: ' + sVarIndexStep + ' ...  ')
                #-------------------------------------------------------------------------------------
    
                #-------------------------------------------------------------------------------------
                # Checking file availability
                oLogStream.info( ' -------> Download data from FTP site ...  ')
                if not glob.glob(sPathVarSource + '*'+ str(sVarIndexStep) +'*.hdf'):
                    
                    #-------------------------------------------------------------------------------------
                    ''' 
                    MODIS DOWNLOADER FILE LINES:
                    
                    #!/bin/bash
                    lftp <<endftp
                    set ftp:proxy http://130.251.104.8:3128
                    open n5eil01u.ecs.nsidc.org
                    user anonymous anonymous
                    cd MOST/MOD10A1.005/2014.07.29
                    mget *h19v04*
                    bye
                    endftp
                    '''
                    oFileLines = {}
                    oFileLines[0] = str('#!/bin/bash') + '\n'
                    oFileLines[1] = str('lftp <<endftp') + '\n'
                    
                    if sFTPProxy != '':
                        oFileLines[2] = str('set ftp:proxy ' + sFTPProxy) + '\n'
                    else:
                        pass
                    
                    oFileLines[3] = str('set net:reconnect-interval-base 5') + '\n'
                    oFileLines[4] = str('set net:max-retries 2') + '\n'
                    oFileLines[5] = str('open ' + sFTPSite) + '\n'
                    oFileLines[6] = str('user ' + sFTPUser + ' ' + sFTPPass) + '\n'
                    oFileLines[7] = str('cd ' + join(sFTPFolder, sVarFolder, sTimeGet) ) + '\n'
                    oFileLines[8] = str('mget *' + sVarIndexH + sVarIndexV + '*') + '\n'
                    oFileLines[9] = str('bye') + '\n'
                    oFileLines[10] = str('endftp') + '\n'
        
                    # Opening, writing and closing sh file
                    oFile = open(join(sPathTemp,sFileNameFTP), 'w')
                    oFile.writelines(oFileLines.values())
                    oFile.close()
                    
                    # FTP 
                    os.chdir(sPathTemp)
                    os.system('chmod +x ' + sFileNameFTP)
                    os.system('./' + sFileNameFTP)
                    #-------------------------------------------------------------------------------------
                    
                    #-------------------------------------------------------------------------------------
                    # Check file availability into temp folder
                    if glob.glob(sPathTemp + '*' + str(sVarIndexStep) + '*.hdf'):
                        
                        #-------------------------------------------------------------------------------------
                        # Selecting filename(s) for hdf and xml extension
                        sFileNameHDFComplete = glob.glob(sPathTemp + '*' + str(sVarIndexStep) + '*.hdf')[0]
    
                        # Split path and filename
                        sPathNameHDF, sFileNameHDF = os.path.split(sFileNameHDFComplete)
                        
                        # Saving file with result name
                        oLogStream.info( ' --------> Save FileName HDF: ' + str(sFileNameHDFComplete) + ' ... ')
                        try:
                            shutil.copyfile(sFileNameHDFComplete, join(sPathVarSource,sFileNameHDF))
                            sFileName = glob.glob(sPathVarSource + '*' +str(sYearGet) + '*'+ str(sVarIndexStep) + '*.hdf') 
                            oLogStream.info( ' --------> Save FileName HDF: ' + str(sFileNameHDFComplete) + ' ... OK (ATTEMPT 1)')
                        except:
                            time.sleep(3)
                            shutil.copyfile(sFileNameHDFComplete, join(sPathVarSource,sFileNameHDF))
                            sFileName = glob.glob(sPathVarSource + '*' +str(sYearGet) + '*'+ str(sVarIndexStep) + '*.hdf')
                            oLogStream.info( ' --------> Save FileName HDF: ' + str(sFileNameHDFComplete) + ' ... OK (ATTEMPT 2)')
                        
                        # Printing time information
                        oLogStream.info( ' -------> Download data from FTP site ...  OK')
    
                        # Storing tile counter
                        oTileLines[iTileCounter] = str(sFileName[0]) + '\n'
                        a1iTileCheck[iTileCounter] = 1
                        #-------------------------------------------------------------------------------------
    
                    else:
                        #-------------------------------------------------------------------------------------
                        oLogStream.info( ' -------> Download data from FTP site ...  FAILED ')
                        a1iTileCheck[iTileCounter] = 0
                        #-------------------------------------------------------------------------------------
                else:
                    
                    #-------------------------------------------------------------------------------------
                    # Printing time information
                    oLogStream.info( ' -------> Download data from FTP site ...  FILE(S) PREVIOUSLY DOWNLOADED ')
                    sFileName = glob.glob(sPathVarSource + '*' +str(sYearGet) + '*'+ str(sVarIndexStep) + '*.hdf')
                    oTileLines[iTileCounter] = str(sFileName[0]) + '\n'
                    a1iTileCheck[iTileCounter] = 1
                    #-------------------------------------------------------------------------------------
                    
                #-------------------------------------------------------------------------------------
                # Tile counter step
                iTileCounter = iTileCounter + 1
                #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------

            #-------------------------------------------------------------------------------------
            # Output filename
            sVarTile = sVarTile[1:]
            sFileNameRootSave = sVarFolder + '.' + sVarTile + '.' + sTimeSave + '.hdf'
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Check product availability
            if (np.any(a1iTileCheck == 1)):
            
                #-------------------------------------------------------------------------------------
                # Mosaicking multiple tile(s)
                oLogStream.info( ' ------> Tiling data using MRT_MOSAIC ...  ')
                if (iVarIndexN > 1):
                    
                    #-------------------------------------------------------------------------------------
                    # Defining mosaic output filename
                    sFileNameMRTosaicTEMP = join(sPathVarSource, 
                                               oVarName['Product'] + '.' + oVarName['Version'] +'.'+ sVarTile +'.' + sTimeSave + '_TEMP.hdf')
                    # Defining paramters filename
                    sFileNameMRTMosaic = join(sPathVarSource, sFileNameMRTMosaic)
                    #-------------------------------------------------------------------------------------
                    
                    #-------------------------------------------------------------------------------------
                    # Check mosaic file availabilty
                    if not glob.glob(sPathVarSource + sFileNameRootSave):
                        
                        # Removing all old data
                        if os.path.isfile(sFileNameMRTosaicTEMP): os.remove(sFileNameMRTosaicTEMP)
                        if os.path.isfile(sFileNameMRTMosaic): os.remove(sFileNameMRTMosaic)
                        
                        # Open and save file with tile(s) to mosaic
                        oFileMosaic = open(join(sPathVarSource,sFileNameMRTMosaic), 'w')
                        oFileMosaic.writelines(oTileLines.values())
                        oFileMosaic.close()
                        
                        # Command line
                        sLineCommand = ( './mrtmosaic -i '+ sFileNameMRTMosaic + ' -o ' + sFileNameMRTosaicTEMP )
                        
                        # Execute algorithm
                        os.chdir(sPathLibrary)
                        oPr = subprocess.Popen(sLineCommand, shell=True)
                        oOut, oErr = oPr.communicate()
                        
                        # Info mosaic condition
                        oLogStream.info( ' ------> Tiling data using MRT_MOSAIC ...  OK ')
                        #-------------------------------------------------------------------------------------
                    
                    else:
                        
                        #-------------------------------------------------------------------------------------
                        # Info mosaic previously done
                        oLogStream.info( ' ------> Tiling data using MRT_MOSAIC ...  PREVIOUSLY DONE ')
                        #-------------------------------------------------------------------------------------
                else:
                    
                    #-------------------------------------------------------------------------------------
                    # Info no mosaic condition
                    oLogStream.info( ' ------> Tiling data using MRT_MOSAIC ...  SKIPPED (ONLY ONE TILE) ')
                    sFileNameMosaicTEMP = ""
                    #-------------------------------------------------------------------------------------
                    
                #-------------------------------------------------------------------------------------
            
                #-------------------------------------------------------------------------------------
                # Checking file availability
                oLogStream.info( ' ------> Reprojecting data using MRT_RESAMPLE ...  ')
                if glob.glob(sPathVarSource + '*' + sVarTile + '*.hdf'):
      
                    #-------------------------------------------------------------------------------------
                    # Checking availability of output file
                    if not glob.glob(sPathVarSource + sFileNameRootSave):
                        
                        #-------------------------------------------------------------------------------------
                        # Remove old file(s)
                        if os.path.isfile(sFileNameMRTMosaic): os.remove(sFileNameMRTMosaic)
                        if os.path.isfile(sFileNameMRTExec): os.remove(sFileNameMRTExec)
                        if os.path.isfile(sFileNameMRTResample): os.remove(sFileNameMRTResample)
                        #-------------------------------------------------------------------------------------
                        
                        #-------------------------------------------------------------------------------------
                        # Searching file(s) in folder and defining saving root filename
                        if (iVarIndexN > 1):
                            sFileNameHDF = join(sPathVarSource, 
                                               oVarName['Product'] + '.' + oVarName['Version'] +'.'+ sVarTile +'.' + sTimeSave + '_TEMP.hdf')
                        else:
                            sFileNameHDF = glob.glob(sPathVarSource + '*' + sVarTile + '*.hdf')
                        #-------------------------------------------------------------------------------------
                        
                        #-------------------------------------------------------------------------------------
                        '''
                        MODIS MRT PARAMETERS FILE LINES:
                        
                        INPUT_FILENAME = "/home/fabio/Desktop/EclipseKeplerProjects/Python/MODIS/MOD10A1.A2014209.h19v04.005.2014211060936.hdf"
                        SPATIAL_SUBSET_TYPE = OUTPUT_PROJ_COORDS
                        OUTPUT_FILENAME = "/home/fabio/Desktop/EclipseKeplerProjects/Python/MODIS/prova.tif"
                        RESAMPLING_TYPE =  NN
                        OUTPUT_PROJECTION_TYPE =  UTM
                        UTM_ZONE = 34
                        DATUM = WGS84
                        '''
                        oFileLines = {}
                        oFileLines[0] = str('INPUT_FILENAME = ' +sFileNameHDF) + '\n'
                        oFileLines[1] = str('SPATIAL_SUBSET_TYPE = ' + sMRTOptSpacialSubset) + '\n'
                        oFileLines[2] = str('OUTPUT_FILENAME =  ' + join(sPathVarSource + sFileNameRootSave)) + '\n'
                        oFileLines[3] = str('RESAMPLING_TYPE = ' + sMRTOptResampling) + '\n'
                        oFileLines[4] = str('OUTPUT_PROJECTION_TYPE = ' + sMRTOptOutputProj) + '\n'
                        oFileLines[5] = str('DATUM =  ' + sMRTOptDatum) + '\n'
            
                        # Opening, writing and closing sh file
                        oFileResample = open(join(sPathVarSource,sFileNameMRTResample), 'w')
                        oFileResample.writelines(oFileLines.values())
                        oFileResample.close()
                        #-------------------------------------------------------------------------------------
                        
                        #-------------------------------------------------------------------------------------
                        '''
                        MODIS MRT EXEC FILE LINES:
                        
                        #!/bin/bash
                        cd /home/fabio/Desktop/Programmazione/Modis_Reproj_Tool/bin/
                        pwd
                        ls
                        ./resample -p /home/fabio/Desktop/EclipseKeplerProjects/Python/MODIS/parameter.txt
                        '''
                        oFileLines = {}
                        oFileLines[0] = str('#!/bin/bash') + '\n'
                        oFileLines[1] = str('cd ' + sPathLibrary) + '\n'
                        oFileLines[2] = str('pwd') + '\n'
                        oFileLines[3] = str('ls') + '\n'
                        oFileLines[4] = str('./resample -p '+ join(sPathVarSource,sFileNameMRTResample)) + '\n'
                        
                        # Opening, writing and closing sh file
                        oFileExec = open(join(sPathVarSource,sFileNameMRTExec), 'w')
                        oFileExec.writelines(oFileLines.values())
                        oFileExec.close()
                        #-------------------------------------------------------------------------------------
                        
                        #-------------------------------------------------------------------------------------
                        # Reprojection - Execute algorithm
                        os.chdir(sPathVarSource)
                        sLineCommand = 'chmod +x ' + sFileNameMRTExec
                        oPr = subprocess.Popen(sLineCommand, shell=True)
                        oOutX, oErrX = oPr.communicate()
                        sLineCommand = './' + sFileNameMRTExec
                        oPr = subprocess.Popen(sLineCommand, shell=True)
                        oOutR, oErrR = oPr.communicate()
                        
                        # Rename file from .hdf to hdf4
                        os.chdir(sPathVarSource)
                        sFileBase = os.path.splitext(sFileNameRootSave)[0]
                        os.rename(sFileNameRootSave, sFileBase + ".hdf4")
                        #-------------------------------------------------------------------------------------
                        
                        #-------------------------------------------------------------------------------------
                        # Info reproj
                        oLogStream.info( ' ------> Reprojecting  data using MRT_RESAMPLE ...  OK ')
    
                        # Removing all old data
                        if os.path.isfile(sFileNameMRTosaicTEMP): os.remove(sFileNameMRTosaicTEMP)
                        if os.path.isfile(sFileNameMRTMosaic): os.remove(sFileNameMRTMosaic)
                        if os.path.isfile(sFileNameMRTExec): os.remove(sFileNameMRTExec)
                        if os.path.isfile(sFileNameMRTResample): os.remove(sFileNameMRTResample)
                        
                        # Check file OUT availability
                        bFileNameOUT = True
                        #-------------------------------------------------------------------------------------
                        
                    else:
                        
                        #-------------------------------------------------------------------------------------
                        # Exit reproj
                        oLogStream.info( ' ------> Reprojecting  data using MRT_RESAMPLE ...  PREVIOUSLY DONE ')
                        # Check file OUT availability
                        bFileNameOUT = True
                        #-------------------------------------------------------------------------------------
                    
                    #-------------------------------------------------------------------------------------
                    
                else:
                    
                    #-------------------------------------------------------------------------------------
                    # Exit error message: reprojection problems
                    oLogStream.info( ' ------> Reprojecting  data using MRT_RESAMPLE ...  FAILED (REPROJ EXCEPTION)')
                    sFileNameRootSave = ''
                    # Check file OUT availability
                    bFileNameOUT = False
                    #-------------------------------------------------------------------------------------
                    
            else:
                
                #-------------------------------------------------------------------------------------
                # Exit error message: no data available
                oLogStream.info( ' ------> Reprojecting  data using MRT_RESAMPLE ...  FAILED (NO DATA AVAILABLE)')
                sFileNameRootSave = ''
                # Check file OUT availability
                bFileNameOUT = False
                #-------------------------------------------------------------------------------------
                
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Store all HDF file(s)
            a1sFileNameHDF = glob.glob(sPathVarSource + '*.hdf')
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Return output filename
            sFileNameOUT = join(sPathVarSource, sFileNameRootSave.replace('.hdf','.hdf4'))
            sFileCompOUT = sVarTile; sFileProductOUT = oVarName['Product']; sFileVersionOUT = oVarName['Version']
            a1sFileNameOUT = a1sFileNameHDF
            return (sFileNameOUT, bFileNameOUT, sFileProductOUT, sFileVersionOUT, sFileCompOUT, a1sFileNameOUT)
            #-------------------------------------------------------------------------------------
        
        except:
            
            #-------------------------------------------------------------------------------------
            # Exit with errors
            GetException(' -----> ERROR: using FTP for MODIS Snow ... FAILED',1,1)
            #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------
    
#-------------------------------------------------------------------------------------

    
