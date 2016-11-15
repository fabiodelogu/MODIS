"""
Class Features

Name:          GetException
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20150403'
Version:       '1.0.0'

Example:

import logging                                              # import logging library
oLogStream = logging.getLogger('sLogger')
from GetException import GetException                       # import GetException class

GetException(' -----> ERROR: test error!', 1, 1)            # error mode
GetException(' -----> WARNING: test warning!', 2, 1)        # warning mode
GetException('',0,0)                                        # no error mode
"""

######################################################################################
# Logging
import logging
oLogStream = logging.getLogger('sLogger')
######################################################################################

#-------------------------------------------------------------------------------------
# Class
class GetException:

    #-------------------------------------------------------------------------------------
    # Method init class
    def __init__(self, sExcMessage, iExcType, iExcCode=None):

        # Get global information
        self.sExcMessage = sExcMessage
        self.iExcType = iExcType
        if iExcCode:
            self.iExcCode = str(iExcCode)
        else:
            self.iExcCode = 'undefined'
        
        # Get Exception
        if ( iExcType == 1 ):
            self.getError()
        elif( iExcType == 2 ):
            self.getWarning()
        elif( iExcType == 3 ):
            self.getCritical()
        if ( iExcType == 0 ):
            self.getNone()
        else:
            pass
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Get error 
    def getError(self):
        
        #-------------------------------------------------------------------------------------
        # Library
        import traceback
        import sys
        
        from os.path import split
        #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------
        # Get system information
        oExcType, oExcOBJ, oExcTB = sys.exc_info()
        
        sExpFileName = split(oExcTB.tb_frame.f_code.co_filename)[1]
        iExpFileLine = oExcTB.tb_lineno
 
        # Write EXC information on log
        oLogStream.info(self.sExcMessage)
        oLogStream.error('[EXC_FORMAT]: ' + str(traceback.format_exc()))
        oLogStream.error('[EXC_INFO]: ' + str(sys.exc_info()[0]))
        oLogStream.error('[EXC_CODE]: ' + str(self.iExcCode))   
        oLogStream.error('[EXC_FILENAME]: ' + sExpFileName)
        oLogStream.error('[EXC_FILELINE]: ' + str(iExpFileLine))              
                         
        # Fatal Error --> Exit the program with 1      
        sys.exit(1)
        #-------------------------------------------------------------------------------------
        
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Get warning
    def getWarning(self):
        
        #-------------------------------------------------------------------------------------
        # Write WARNING information on log
        oLogStream.info(self.sExcMessage)
        oLogStream.warning(self.sExcMessage)
        #-------------------------------------------------------------------------------------
        
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Get critical
    def getCritical(self):
    
        pass
    
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Get none
    def getNone(self):
        
        #-------------------------------------------------------------------------------------
        # Library
        import sys
        #-------------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------------
        # Write NO ERROR information on log
        oLogStream.info('[EXC_FORMAT]: None')
        oLogStream.info('[EXC_INFO]: None')
        oLogStream.info('[EXC_CODE]: None')   
        oLogStream.info('[EXC_FILENAME]: None')
        oLogStream.info('[EXC_FILELINE]: None')              
                         
        # No Error --> Exit the program with 0   
        sys.exit(0)
        #-------------------------------------------------------------------------------------
        
    #-------------------------------------------------------------------------------------
    
    
    
    
    
    
    
    
    

#-------------------------------------------------------------------------------------