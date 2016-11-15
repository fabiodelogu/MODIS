"""
Class Features:

Name:          Drv_Data_Zip
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20150325'
Version:       '1.0.2'

ZIP values:
sZipType: 'NoZip', 'GZip'
"""

#################################################################################
# Logging
import logging
oLogStream = logging.getLogger('sLogger')

# Global libraries
import os
import bz2

from os.path import join
from os.path import isfile
from os.path import splitext

from GetException import GetException

#import matplotlib.pylab as plt
#################################################################################

#--------------------------------------------------------------------------------
# Class to manage IO files
class Drv_Data_Zip:
    
    #--------------------------------------------------------------------------------
    # Class init
    def __init__(self, sFileName, sZipMode, sZipType=None, bFileNameRm=False):
        
        # Pass to global declaration
        self.bFileNameRm = bFileNameRm
        self.sFileName = sFileName
        
        # Define filename
        sFilePath = os.path.split(sFileName)[0]
        sFileNameIN = os.path.split(sFileName)[1]
        
        sFileNameRoot, sFileNameExt = splitext(sFileNameIN)
        iFileNameExtLen = len(sFileNameExt)
        
        # Define FileType and FileWorkspace
        if sFileName.endswith('gz') or sZipType == 'gz':
            
            sZipType = 'GZip'
            self.oFileWorkspace = GZip(sFilePath, sFileNameIN, sZipMode)

        elif sFileName.endswith('7z') or sZipType == '7z':
            
            sZipType = '7Zip'
            pass
        
        elif sFileName.endswith('bz2') or sZipType == 'bz2':
            
            sZipType = 'BZ2Zip'
            pass
            
        elif sZipType == 'NoZip' or sZipType == None:
            
            pass
        
        else:
            
            if sZipMode == 'z': 
                GetException(' -----> ERROR: zip or unzip functions are not selected! Please check zip tag!', 1, 1) 
            elif sZipMode == 'u': 
                oLogStream.info( ' ------> UNZIPPING FILE  ... FILE NOT ZIPPED')
    
        # Function to remove filename
        if sZipMode == 'z': 
            self.removeFileName()
        else:
            pass
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to delete FileName
    def removeFileName(self):
        
        if self.bFileNameRm is True:
            
            if isfile(self.sFileName):
                
                os.remove(self.sFileName)
                
            else:
                pass
            
        else:
            pass
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to remove only compressed extension 
    @staticmethod
    def removeZipExt(sFileName):
        
        # Zip format dictionary
        oZipDic = { 'Type_1': '.gz', 'Type_2': '.bz2', 'Type_3': '.zip'};

        # Define filename
        try:
            sFilePathUpd = os.path.split(sFileName)[0]
            sFileNameUpd = os.path.split(sFileName)[1]
        except:
            sFilePathUpd = ''
            sFileNameUpd = sFileName
        
        sFileNameUpd, sExtFileUpd = os.path.splitext(sFileNameUpd)
        
        sFileNameWE = ''; bFileNameZip = False
  
        if sExtFileUpd in oZipDic.values():
            sFileNameWE = sFileNameUpd
            bFileNameZip = True
        else:
            sFileNameWE = sFileName
            bFileNameZip = False
         
        return (sFileNameWE, bFileNameZip)
    #--------------------------------------------------------------------------------
    
#--------------------------------------------------------------------------------
# Class to use GZip compression 
class GZip:
    
    #--------------------------------------------------------------------------------
    # Class init
    def __init__(self, sFilePath, sFileNameIN, sZipMode):
        
        self.sFilePath = sFilePath
        self.sFileNameIN = sFileNameIN
        self.sZipMode = sZipMode

        # Choose method using zip mode selection
        if sZipMode == 'z':
            self.zipFile(); 
        elif sZipMode == 'u':
            self.unzipFile(); 
        else:
            GetException(' -----> ERROR: zip mode uncorrect! Check your file settings!', 1, 1)

    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to zip file
    def zipFile(self):
        
        import gzip
        
        self.sFileNameOUT = join(self.sFilePath ,self.sFileNameIN + '.gz')
        
        oFileIN = open(join(self.sFilePath, self.sFileNameIN),'rb')
        oFileOUT = gzip.open(self.sFileNameOUT, 'wb')
        oFileOUT.writelines(oFileIN)
        oFileOUT.close()
        oFileIN.close()

    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to unzip file
    def unzipFile(self):
        
        # Import library
        import gzip
        
        # Define output file
        self.sFileNameOUT, self.bFileNameOUT = Drv_Data_Zip.removeZipExt(self.sFileNameIN)
        
        # Unzip file
        oCompressData = gzip.GzipFile(join(self.sFilePath,self.sFileNameIN), "rb")
        oDecompressData = oCompressData.read()
        oFileUnzip = open(join(self.sFilePath, self.sFileNameOUT), "wb")
        oFileUnzip.write(oDecompressData)
        
        # Updating filename 
        self.sFileNameOUT = join(self.sFilePath,self.sFileNameOUT)

    #--------------------------------------------------------------------------------
    

    
#         # Choosing compressed format
#         if(sFileNameZip.endswith('bz2')):
#             
#             # Uncompressed file 
#             print(' -----> File Zipped using bz2')
#             oCompressData = bz2.BZ2File(join(sFilePath, sFileNameZip))
#             oDecompressData = oCompressData.read()
#             oFileUnzip = open(join(sFilePath, sFileNameUnzip), "wb")
#             oFileUnzip.write(oDecompressData)
#             
#             # Removing zipped file
#             os.remove(join(sFilePath, sFileNameZip))
#             
#             # Updating filename 
#             self.sFileName = join(sFilePath,sFileNameUnzip)
#             
# 
#     
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    