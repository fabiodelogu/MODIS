"""
Library Features:

Name:          Lib_Data_IO_Utils
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20150903'
Version:       '1.0.0'
"""

#################################################################################
# Logging
import logging
oLogStream = logging.getLogger('sLogger')

# Global libraries
import os
import time
import datetime

from os.path import join
from os.path import isfile
from os.path import split

from GetException import GetException

# Debug
import matplotlib.pylab as plt
#################################################################################

#--------------------------------------------------------------------------------
# Method to get file history
def getFileHistory(sFileHistory):
    import csv
    if os.path.exists(sFileHistory):
        oFileReader = csv.reader(open(sFileHistory, 'r'), delimiter=',')
        #[a1oFileTimeSave_PS, a1oFileType_PS, 
        #a1oFileTimeRef_PS, a1oFileName_PS, a1oFileExist_PS, a1oFileStatus_PS] = zip(*oFileReader)
        return zip(*oFileReader)
    else:
        return None
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to write file history
def writeFileHistory(sFileHistory, oDataHistory): 
    import csv
    with open(sFileHistory, 'wb') as oFile:
        oFileWriter = csv.writer(oFile, delimiter=',')
        oFileWriter.writerows(oDataHistory)
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to delete file
def deleteFile(sFileName):
    
    # Delete file if exist
    if os.path.exists(sFileName): os.remove(sFileName)

#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to create folder (and check if folder exists)
def createFolder(sPathName, sPathDeep=None):
    
    if sPathName != '':
        
        if sPathDeep:
            sPathNameSel = sPathName.split(sPathDeep)[0]
        else:
            sPathNameSel = sPathName
        
        if not os.path.exists(sPathNameSel): 
            os.makedirs(sPathNameSel)
        else:
            pass
            
    else:
        pass

#--------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------
# Method to check saving time of a file
def checkSavingTime(sTime, a1oTimeSteps, iTimeStep, iTimeUpd):

    #-------------------------------------------------------------------------------------
    # Saving condition (almost > 0)
    bSavingTime = False
    if iTimeUpd > 0:
        
        #-------------------------------------------------------------------------------------
        # Define timeto and timefrom (period)
        oTimeTo = datetime.datetime.strptime(a1oTimeSteps[-1], '%Y%m%d%H%M')
        oTimeFrom = oTimeTo - datetime.timedelta(seconds = int(iTimeStep)*int(iTimeUpd))
        
        # Define time 
        oTime = datetime.datetime.strptime(sTime, '%Y%m%d%H%M')
        #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------
        # Define file saving
        if (oTime >= oTimeFrom and oTime <= oTimeTo):
            bSavingTime = True
        else:
            bSavingTime = False
        #-------------------------------------------------------------------------------------
    
    elif iTimeUpd == 0:
        
        #-------------------------------------------------------------------------------------
        # Define timeto and timefrom (period)
        oTimeTo = datetime.datetime.strptime(a1oTimeSteps[-1], '%Y%m%d%H%M')
        # Define time 
        oTime = datetime.datetime.strptime(sTime, '%Y%m%d%H%M')
        #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------
        # Define file saving
        if (oTime == oTimeTo):
            bSavingTime = True
        else:
            bSavingTime = False
        #-------------------------------------------------------------------------------------
    
    elif iTimeUpd == -1:
        
        #-------------------------------------------------------------------------------------
        # Define file saving
        bSavingTime = False
        #-------------------------------------------------------------------------------------
    
    else: 
        
        #-------------------------------------------------------------------------------------
        # Define file saving
        bSavingTime = False
        #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Return variable(s)
    return bSavingTime
    #-------------------------------------------------------------------------------------
    
#-------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to define check file availability name
def checkFileExist(sFileName):
    
    bFileAvailability = False;
    
    if isfile(sFileName):
        bFileAvailability = True
    else:
        bFileAvailability = False
              
    return bFileAvailability
    
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to define dynamic folder name
def defineFolderName(sFolderName, oFileNameDict):
    
    if sFolderName != '':
    
        if not oFileNameDict:
            pass
        elif oFileNameDict:
            
            for sKey, sValue in oFileNameDict.items():
                
                sFolderName = sFolderName.replace(sKey,sValue)
        
        if not os.path.exists(sFolderName): os.makedirs(sFolderName)
    
    else:
        pass
    
    return sFolderName
    
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to define dynamic filename
def defineFileName(sFileName, oFileNameDict):
    
    if sFileName != '':
        if not oFileNameDict:
            pass
        elif oFileNameDict:
            for sKey, sValue in oFileNameDict.items():
                sFileName = sFileName.replace(sKey,sValue)
    else:
        pass
    return sFileName
    
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to join 2 dictionaries
def joinDict(oDictA, oDictB):
    
    from copy import deepcopy
    
    oDictAB = deepcopy(oDictA)
    oDictAB.update(oDictB)
    
    return oDictAB
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to define string
def defineString(sString, oDictTags):
    
    if sString != '':
        if not oDictTags:
            pass
        elif oDictTags:
            for sKey, oValue in oDictTags.items():
                if isinstance(oValue, basestring):
                    sString = sString.replace(sKey, oValue)
                elif isinstance(oValue, int):
                    sString = sString.replace(sKey, str(int(oValue)))
                elif isinstance(oValue, float):
                    sString = sString.replace(sKey, str(float(oValue)))
                else:
                    sString = sString.replace(sKey, str(oValue))
    else:
        pass
    return sString
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to define a unique value in multi key selection
def defineUniqueValue(oDict, iLevelKey, sMultiKey):
    
    a1sValueKeys = []
    for sDict in oDict:
        
        if iLevelKey == 1:
            
            sValueKeySel = str(oDict[sDict][sMultiKey])
        
        elif iLevelKey == 3:
        
            sValueKeySel = str(oDict[sDict]['VarOp']['Op_Save'][sMultiKey])
            
        else:
            GetException(' -----> ERROR: multi-key level not supported!',1,1)

        a1sValueKeys.append(sValueKeySel)
        
    sUniqueValue = set(a1sValueKeys).pop()
    
    return sUniqueValue
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Check process exit code
def checkProcess(sOut, sErr):
    
    if (sOut is None or sOut == '') and sErr is None:
        pass
    else:
        GetException(' -----> WARNING: error occurred during process execution!',2,1) 
    
    return
#--------------------------------------------------------------------------------
