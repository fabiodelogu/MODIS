"""
Class Features

Name:          GetSettings
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20151022'
Version:       '1.0.9'
"""

######################################################################################
# Logging
import logging
oLogStream = logging.getLogger('sLogger')

# Library
import imp
import os

from GetException import GetException
######################################################################################

#-------------------------------------------------------------------------------------
# Class
class GetSettings:
     
    #-------------------------------------------------------------------------------------
    # Variable(s) initialization
    oInfoSettings = None
    oInfoVarStatic = None
    oInfoVarDynamic = None
    #-------------------------------------------------------------------------------------
     
    #-------------------------------------------------------------------------------------
    # Method init class
    def __init__(self, sFileName=None, sTimeNow=None):
 
        # Open settings file
        self.oInfoSettings = imp.load_source('info_settings', '', open(sFileName))
        self.sFileName = sFileName
        self.sTimeNow = sTimeNow
        
        self.sFilePath = os.path.split(sFileName)[0]
        self.sFileName = os.path.split(sFileName)[1]
        
        # Get domain name
        self.__getDomainName()
        
        # Get run name
        self.__getRunName()
        
        # Read settings file 
        self.__setPathName()
         
        # Set configuration file(s)
        self.__setConfigFile()
        
        # Set time now
        if sTimeNow:
            self.__setTimeNow()
        else:
            pass
        
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to set time now (if is a input of function    
    def __setTimeNow(self):
        
        sTimeNow_File = self.oInfoSettings.oParamsInfo['TimeNow']
        sTimeNow_Arg = self.sTimeNow
        
        sTimeNow = ''
        if sTimeNow_Arg != '' and sTimeNow_File != '':
            
            if sTimeNow_Arg == sTimeNow_File:
                oLogStream.info(' ----> TIMENOW_FILE: DEFINED -- TIMENOW_ARG: DEFINED ==> EQUAL')
                sTimeNow = sTimeNow_File
                oLogStream.info(' ----> TimeNow Selection: TIMENOW_FILE ')
            elif sTimeNow_Arg != sTimeNow_File:
                oLogStream.info(' ----> TIMENOW_FILE: DEFINED -- TIMENOW_ARG: DEFINED ==> NOT EQUAL')
                sTimeNow = sTimeNow_Arg
                oLogStream.info(' ----> TimeNow Selection: TIMENOW_ARG')
        
        elif sTimeNow_Arg == '' and sTimeNow_File != '':
            
            oLogStream.info(' ----> TIMENOW_FILE: DEFINED -- TIMENOW_ARG: N/A')
            sTimeNow = sTimeNow_File
            oLogStream.info(' ----> TimeNow Selection: FILE TIME')
            
        elif sTimeNow_Arg != '' and sTimeNow_File == '':
            
            oLogStream.info(' ----> TIMENOW_FILE: N/A -- TIMENOW_ARG: DEFINED')
            sTimeNow = sTimeNow_Arg
            oLogStream.info(' ----> TimeNow Selection: TIMENOW_ARG')
            
        elif sTimeNow_Arg == '' and sTimeNow_File == '':
            oLogStream.info(' ----> TIMENOW_FILE: N/A -- TIMENOW_ARG: N/A')
            sTimeNow = ''
            oLogStream.info(' ----> TimeNow Selection: NOT SELECTED ==> WILL BE SELECTED IN TIME FUNCTION')
            
        # Selected timenow saved in workspace
        self.oInfoSettings.oParamsInfo['TimeNow'] = sTimeNow

    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to get domain name
    def __getDomainName(self):
        try:
            self.sDomainName = self.oInfoSettings.oParamsInfo['DomainName'].lower()
        except:
            self.sDomainName = None
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to get run name
    def __getRunName(self):
        try:
            self.sRunName = self.oInfoSettings.oParamsInfo['RunName'].lower()
        except:
            self.sRunName = None
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Set configuration file(s)
    def __setConfigFile(self):
          
        try:
            sFileNameStatic = self.oInfoSettings.oParamsInfo['FileConfigStatic']
            sFileNameStatic = defineString(sFileNameStatic, self.sDomainName, self.sRunName)
            
            #[sFileStaticPath, sFileStaticName] = os.path.split(sFileNameStatic)
            #if not sFileStaticPath == '':
            #    os.chdir(sFileStaticPath)
            #else:
            #    os.chdir(self.sFilePath)
    
            self.oInfoVarStatic = imp.load_source('info_datastatic', '',  open(sFileNameStatic))
        except:
            self.oInfoVarStatic = None
            GetException(' -----> ERROR: Getting FileConfigStatic FAILED!', 1, 1)
          
        try:
            sFileNameDynamic = self.oInfoSettings.oParamsInfo['FileConfigDynamic']
            sFileNameDynamic = defineString(sFileNameDynamic, self.sDomainName, self.sRunName)

            #[sFileDynamicPath, sFileDynamicName] = os.path.split(sFileNameDynamic)
            #if not sFileDynamicPath == '':
            #    os.chdir(sFileDynamicPath)
            #else:
            #    os.chdir(self.sFilePath)
            
            self.oInfoVarDynamic = imp.load_source('info_datadynamic', '',  open(sFileNameDynamic))

        except:
            self.oInfoVarDynamic = None
            GetException(' -----> ERROR: Getting FileConfigDynamic FAILED!', 1, 1)

    #-------------------------------------------------------------------------------------
     
    #-------------------------------------------------------------------------------------
    # Set path(s)
    def __setPathName(self):
         
        # Get paths dictionary
        oPathInfo = self.oInfoSettings.oPathInfo
         
        # Cycle on path definition
        for sPathKey in oPathInfo.keys():
             
            sPathName = oPathInfo[sPathKey]
            sPathName = defineString(sPathName, self.sDomainName, self.sRunName)
             
            if '$' in sPathName:
                sPathName = sPathName.split('$')[0]
            else:
                pass
             
            if not os.path.exists(sPathName): 
                # Check for multiprocessing tasks
                try:
                    os.makedirs(sPathName)
                except:
                    pass
            else:
                pass
             
        #-------------------------------------------------------------------------------------
         
    #-------------------------------------------------------------------------------------
    
#-------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------
# Method to define string using domain and run name
def defineString(sString, sDomainName, sRunName):
    
    if sDomainName:
        sString = sString.replace('$DOMAIN', sDomainName)
    else:
        pass
    if sRunName:
        sString = sString.replace('$RUN', sRunName)
    else:
        pass
    
    return sString
#-------------------------------------------------------------------------------------



















