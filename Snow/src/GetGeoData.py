"""
Class Features

Name:          GetGeoData
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20150715'
Version:       '1.0.7'
"""

######################################################################################
# Logging
import logging
oLogStream = logging.getLogger('sLogger')

# Libraries
import os
import numpy as np

from os.path import isfile
from os.path import split
from os.path import join
    
from GetException import GetException
from Drv_Data_IO import Drv_Data_IO, FileAscii, FileTiff

# Debug
import matplotlib.pylab as plt
######################################################################################

#-------------------------------------------------------------------------------------
# Function to define geographical information
def defineGeoData(dGeoYMin, dGeoXMin, dGeoYMax, dGeoXMax, dGeoYStep, dGeoXStep, iRows, iCols):
        
    #-------------------------------------------------------------------------------------
    # Creating geox and geoy references
    a1dGeoX = np.arange(dGeoXMin, dGeoXMax + np.abs(dGeoXStep/2), np.abs(dGeoXStep), float)
    a1dGeoY = np.arange(dGeoYMin, dGeoYMax + np.abs(dGeoYStep/2), np.abs(dGeoYStep), float)
    
    a2dGeoX, a2dGeoY = np.meshgrid(a1dGeoX, a1dGeoY)
    a2dGeoY = np.flipud(a2dGeoY)
    
    dGeoXMin = np.nanmin(a2dGeoX); dGeoXMax = np.nanmax(a2dGeoX)
    dGeoYMax = np.nanmax(a2dGeoY); dGeoYMin = np.nanmin(a2dGeoY)
    oGeoBox = [dGeoXMin, dGeoYMax, dGeoXMax, dGeoYMin]

    a1dGeoBox = np.around( oGeoBox, decimals=3)
    
    return a2dGeoX, a2dGeoY, a1dGeoBox
    #-------------------------------------------------------------------------------------
    
#-------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------
# Class geodata
class CreateGeoGrid:
    
    #-------------------------------------------------------------------------------------
    # Initializing data
    dGeoYMin = 0.0
    dGeoXMin = 0.0
    dGeoYMax = 0.0
    dGeoXMax = 0.0
      
    dGeoYStep = 0.0
    dGeoXStep = 0.0
    
    iRows = 0
    iCols = 0
    
    a2dGeoX = None
    a2dGeoY = None
    a1dGeoBox = None
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Initializing class
    def __init__(self, dGeoYMin, dGeoXMin, dGeoYMax, dGeoXMax, dGeoYStep, dGeoXStep, iRows, iCols):
        
        #-------------------------------------------------------------------------------------
        # Passing data to a global allocation
        self.dGeoYMin = dGeoYMin
        self.dGeoXMin = dGeoXMin
        self.dGeoYMax = dGeoYMax
        self.dGeoXMax = dGeoXMax
        
        self.dGeoYStep = dGeoYStep
        self.dGeoXStep = dGeoXStep
        
        self.iRows = iRows
        self.iCols = iCols
        #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------
        # Creating geox and geoy references
        a1dGeoX = np.arange(dGeoXMin, dGeoXMax + np.abs(dGeoXStep/2), np.abs(dGeoXStep), float)
        a1dGeoY = np.arange(dGeoYMin, dGeoYMax + np.abs(dGeoYStep/2), np.abs(dGeoYStep), float)
        
        self.a2dGeoX, self.a2dGeoY = np.meshgrid(a1dGeoX, a1dGeoY)
        self.a2dGeoY = np.flipud(self.a2dGeoY)
        
        dGeoXMin = np.nanmin(self.a2dGeoX); dGeoXMax = np.nanmax(self.a2dGeoX)
        dGeoYMax = np.nanmax(self.a2dGeoY); dGeoYMin = np.nanmin(self.a2dGeoY)
        oGeoBox = [dGeoXMin, dGeoYMax, dGeoXMax, dGeoYMin]
        #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------
        # GeoBox information
        self.a1dGeoBox = np.around( oGeoBox, decimals=3)
        #-------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------
# Class GetGeoData
class GetGeoData:
    
    #-------------------------------------------------------------------------------------
    # Initializing class
    def __init__(self, sFileName = None, oGeoBox = None):
        
        # Check if at least one of filename or geobox is defined
        if (sFileName is not None) or (oGeoBox is not None):
        
            # Check file availability
            if isfile(sFileName) or oGeoBox is not None:
            
                # Passing information to a global allocation
                self.sFileName = sFileName
                self.oGeoBox = oGeoBox
                
                # Checking data availability
                if self.sFileName:
                    # Reading ascii-grid file
                    self.readGrid()
                elif self.oGeoBox:
                    # Reading bounding box information
                    self.readBox()
                else:
                    # Otherwise exiting with error
                    GetException(' -----> ERROR: Getting geodata failed! Check file settings!', 1, 1)
                    
            else:
                # Otherwise exiting with warning
                GetException(' -----> WARNING: File does not exist! Check your source folder! ('+sFileName+')', 2, 1)
                self.oGeoData = None
        else:
            # Otherwise exiting with warning
            GetException(' -----> WARNING: both filename and geobox are undefined! ('+sFileName+')', 2, 1)
            self.oGeoData = None
                
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Getting geographical information using an ascii grid file
    def readGrid(self):
        
        # Read ascii grid file
        oFileDriver = Drv_Data_IO(self.sFileName,'r')
        oFileObject = oFileDriver.oFileWorkspace.readArcGrid()
        oFileDriver.oFileWorkspace.closeFile()
        
        # Load data 
        a2dGeoData = oFileObject['Data']; a1oFileInfo = oFileObject['GeoInfo']['Coords']
        
        # Cast data in float32 bit
        self.a2dGeoData = np.asarray(a2dGeoData, dtype=np.float32) 
     
        # Save info
        self.a1oGeoInfo = a1oFileInfo
        self.dNoData = np.float32(a1oFileInfo[FileAscii.getNODATAVALUE])
        self.a2bGeoDataFinite = (self.a2dGeoData != self.dNoData)
        self.a2bGeoDataNan = (self.a2dGeoData == self.dNoData)
        self.a2dGeoData[self.a2bGeoDataNan] = np.nan
        
        self.a1iGeoDataNaN = np.where(self.a2bGeoDataFinite.ravel() == False)[0]
        self.a1iGeoDataFinite = np.where(self.a2bGeoDataFinite.ravel() == True)[0]
        
        # Get information from ascii file
        dGeoXMin = a1oFileInfo[FileAscii.getXLLCORNER]
        dGeoXStep = a1oFileInfo[FileAscii.getCELLSIZE]
        dGeoYMin = a1oFileInfo[FileAscii.getYLLCORNER]
        dGeoYStep = a1oFileInfo[FileAscii.getCELLSIZE]
        iRows = a1oFileInfo[FileAscii.getNROWS]
        iCols = a1oFileInfo[FileAscii.getNCOLS]
        
        # Define cell center 
        dGeoXMin = dGeoXMin + dGeoXStep/2.
        dGeoYMin = dGeoYMin + dGeoYStep/2.
        dGeoXMax = dGeoXMin + (iCols-1) * dGeoXStep
        dGeoYMax = dGeoYMin + (iRows-1) * dGeoYStep
        
        self.oGeoData = CreateGeoGrid(dGeoYMin, dGeoXMin, dGeoYMax, dGeoXMax, dGeoYStep, dGeoXStep, iRows, iCols)
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Getting geographical information using a bounding box
    def readBox(self):
        
        # Retrieving data from global class allocation
        oGeoBox = self.oGeoBox
        
        dGeoXMin = oGeoBox['dGeoXMin']; dGeoXMax = oGeoBox['dGeoXMax']
        dGeoYMin = oGeoBox['dGeoYMin']; dGeoYMax = oGeoBox['dGeoYMax']
        
        dGeoXStep = oGeoBox['dGeoXStep']; dGeoYStep = oGeoBox['dGeoYStep']
        
        iCols = int(np.round((dGeoXMax - dGeoXMin)/dGeoXStep + 1))
        iRows = int(np.round((dGeoYMax - dGeoYMin)/dGeoYStep + 1))
        
        a2dGeoData = np.zeros((iCols, iRows)); a2dGeoData[:] = 1
        
        self.a2dGeoData = a2dGeoData
        self.dNoData = -9999.0
        
        self.a2bGeoDataFinite = (self.a2dGeoData != self.dNoData)
        self.a2bGeoDataNan = (self.a2dGeoData == self.dNoData)
        
        self.oGeoData = CreateGeoGrid(dGeoYMin, dGeoXMin, dGeoYMax, dGeoXMax, dGeoYStep, dGeoXStep, iRows, iCols)
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Geo data reprojection
    def reprojGrid(self, sGeoSystem_Start, sGeoSystem_End):
        
        # Check geo systems
        if (sGeoSystem_Start != sGeoSystem_End):
        
            import subprocess
            
            sFileName, sFileExt = os.path.splitext(self.sFileName)
            
            sFileNameTiffStart = sFileName + '_' + sGeoSystem_Start + '.tiff'
            sFileNameTiffEnd = sFileName + '_' + sGeoSystem_End + '.tiff'
            
            oFileDriver = FileAscii(Drv_Data_IO(self.sFileName, 'r'))
            oFileDriver.ascii2tiff(sFileNameTiffStart)
            
            # Save old file with a different name
            os.rename(self.sFileName, self.sFileName + '_OLD')
    
            # Reproj data
            sLineCommand = ('gdalwarp -s_srs ' +sGeoSystem_Start+ ' -t_srs ' +sGeoSystem_End+ ' ' + sFileNameTiffStart + ' ' + sFileNameTiffEnd )
            
            print(sLineCommand)
            oPr = subprocess.Popen(sLineCommand, shell=True)
            oOut, oErr = oPr.communicate()
            print oOut, oErr
            
            oFileDriver = FileTiff(Drv_Data_IO(sFileNameTiffEnd, 'r'))
            oFileDriver.tiff2ascii(self.sFileName)
        
        else:
            pass
        
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Remap data grid1 <---> grid2
    def resampleGrid(self, oDataTerrain, oDataVegType):
        
        #gdal_translate -of GTiff cn_epsg4326.txt cn_epsg4326.tif
        #gdalwarp -tr 0.001213449080 0.001213449080 -dstnodata -9999.000 -cutline muga_suelos_poly_diss_wgs84.shp cn_epsg4326.tif cn_epsg4326_cut.tif  
          
        pass
        
    #-------------------------------------------------------------------------------------
        
#-------------------------------------------------------------------------------------
# Class GetAnalyzedData
class GetAnalyzedData:
    
    #-------------------------------------------------------------------------------------
    # Initializing data
    oDataAnalyzed = {}
    oVarAnalyzed = {
                        'slope'     : { 'FileName': 'domain.var.txt', 'VarName': 'slope',     'VarParameter': '-s 111120'},
                        'aspect'    : { 'FileName': 'domain.var.txt', 'VarName': 'aspect',    'VarParameter': ''},
                        'roughness' : { 'FileName': 'domain.var.txt', 'VarName': 'roughness', 'VarParameter': ''},
                        'hillshade' : { 'FileName': 'domain.var.txt', 'VarName': 'hillshade', 'VarParameter': '-s 111120'},
                    }
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Initialize class
    def __init__(self, sFileName = None, sDomainName=None):
    
        # Check filename availability
        if (sFileName is not None):
        
            # Check file availability
            if isfile(sFileName):
                
                # Define filename
                self.sFilePath = split(sFileName)[0]
                self.sFileName = split(sFileName)[1]
                self.sDomainName = sDomainName
                
                # Compute data (on analyzed var definitio)
                for sVarName in self.oVarAnalyzed:
                    
                    self.CheckData(self.sDomainName, self.oVarAnalyzed[sVarName]['VarName'], self.oVarAnalyzed[sVarName]['FileName'])
                    
                    self.ComputeData(self.oVarAnalyzed[sVarName]['VarName'], self.oVarAnalyzed[sVarName]['VarParameter'])
                   
            else:
                # Otherwise exiting with warning
                GetException(' -----> WARNING: File does not exist! Check your source folder! ('+sFileName+')', 2, 1)
                self.oDataAnalyzed = None
                
        else:
            # Otherwise exiting with warning
            GetException(' -----> WARNING: filename is undefined!', 2, 1)
            self.oDataAnalyzed = None
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Check file availability
    def CheckData(self, sDomainName, sVarName, sFileNameVar):
        
        sFileNameVar = sFileNameVar.replace('domain',sDomainName)
        sFileNameVar = sFileNameVar.replace('var',sVarName)
        
        if os.path.isfile(join(self.sFilePath, sFileNameVar)):
            bFileExist = True
            self.a1oFileHeader = None
        else:
            bFileExist = False
            
            # Read ascii grid file
            oFileDriver = Drv_Data_IO(join(self.sFilePath,self.sFileName),'r')
            oFileObject = oFileDriver.oFileWorkspace.readArcGrid()
            oFileDriver.oFileWorkspace.closeFile()
            
            self.a1oFileHeader = oFileObject['GeoInfo']['Coords']
            
        
        self.bFileExist = bFileExist
        self.sFileNameVar = sFileNameVar
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to compute derived data
    def ComputeData(self, sVarName, sParameter=None):
        
        if self.bFileExist is False:
        
            #-------------------------------------------------------------------------------------
            # Import library
            import subprocess
            from PIL import Image
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Example:
            # 'gdaldem aspect dem.tif aspect.tif'
            # 'gdaldem slope dem.tif slope.tif -s 111120'
            # 'gdaldem roughness dem.tif roughness.tif'
            # 'gdaldem hillshade dem.tif hillshade.tif -s 111120'
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Define temporary tif filename
            sFileNameTemp = sVarName + '.tif'
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Define command line
            if sParameter:
                sCommandLine = 'gdaldem ' + sVarName + ' ' + join(self.sFilePath, self.sFileName) + ' ' + join(self.sFilePath, sFileNameTemp) + ' ' + sParameter
            else:
                sCommandLine = 'gdaldem ' + sVarName + ' ' + join(self.sFilePath, self.sFileName) + ' ' + join(self.sFilePath, sFileNameTemp)
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Compute derived data
            try:
                print(sCommandLine)
                oPr = subprocess.Popen(sCommandLine, shell=True)
                oOut, oErr = oPr.communicate()
                print oOut, oErr
                
            except IOError as oError:
                
                #-------------------------------------------------------------------------------------
                GetException(' -----> ERROR: in computing geographical derived data ' + ' [' + str(oError) + ']',1,1)
                #-------------------------------------------------------------------------------------
                
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Read tiff and store data      
            try:
                
                #-------------------------------------------------------------------------------------
                # Open file
                oFile = Image.open(join(self.sFilePath, sFileNameTemp), 'r')
                #-------------------------------------------------------------------------------------
                
                #-------------------------------------------------------------------------------------
                # Get data size and values
                a1dFileSize = oFile.size
                
                a1oFileData = list(oFile.getdata()) 
                a1dFileData = np.asarray(a1oFileData, dtype=np.float32) 
                a2dFileData = np.reshape(a1dFileData,(a1dFileSize[1],a1dFileSize[0]))
                #-------------------------------------------------------------------------------------

                #-------------------------------------------------------------------------------------
                # Save data in arcgrid file type
                oFileDriver = Drv_Data_IO(join(self.sFilePath, self.sFileNameVar),'w')
                oFileDriver.oFileWorkspace.writeArcGrid(a2dFileData, 
                                                            self.a1oFileHeader, 'f')
                oFileDriver.oFileWorkspace.closeFile()
                #-------------------------------------------------------------------------------------
                
                #-------------------------------------------------------------------------------------
                # Debug
                # a2dVarData[a2dVarData==-9999.0] = np.nan
                # plt.figure(1)
                # plt.imshow(a2dVarData); plt.colorbar()
                # plt.show()
                #-------------------------------------------------------------------------------------
                
                #-------------------------------------------------------------------------------------
                # Remove temporary data
                os.remove(join(self.sFilePath,sFileNameTemp))
                # Return computed data
                self.oDataAnalyzed[sVarName] = a2dFileData
                #-------------------------------------------------------------------------------------
                
            except IOError as oError:
                
                #-------------------------------------------------------------------------------------
                GetException(' -----> ERROR: in opening or reading file (TIFF I/O)' + ' [' + str(oError) + ']',1,1)
                #-------------------------------------------------------------------------------------
    
            #-------------------------------------------------------------------------------------
        
        else:
            
            #-------------------------------------------------------------------------------------
            # Get information from ascii grid file
            oFileDriver = Drv_Data_IO(join(self.sFilePath,self.sFileNameVar),'r')
            oFileObject = oFileDriver.oFileWorkspace.readArcGrid()
            oFileDriver.oFileWorkspace.closeFile()
            #-------------------------------------------------------------------------------------
            
            #-------------------------------------------------------------------------------------
            # Save information in dictionary
            self.oDataAnalyzed[sVarName] = oFileObject['Data']
            #-------------------------------------------------------------------------------------
            
    #-------------------------------------------------------------------------------------
        
#-------------------------------------------------------------------------------------








