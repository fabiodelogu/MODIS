"""
Class Features

Name:          GetTime
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20150319'
Version:       '2.0.2'
"""

######################################################################################
# Logging
import logging
oLogStream = logging.getLogger('sLogger')

# Library
import time
import datetime

from GetException import GetException

from array import array
######################################################################################

#-------------------------------------------------------------------------------------
# Method to convert local time to GMT time and viceversa (sTimeLocal  --> 'yyyymmddHHMM')
def convertTimeLOCxGMT(sTime_IN, iTimeDiff):
    
    oTime_IN = datetime.datetime.strptime(sTime_IN,'%Y%m%d%H%M')
    oTime_IN = oTime_IN.replace(minute = 0, second = 0, microsecond = 0)
    oTime_OUT = oTime_IN + datetime.timedelta(seconds = iTimeDiff*3600)
    sTime_OUT = oTime_OUT.strftime('%Y%m%d%H%M')
    return sTime_OUT
    
#-------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------
# Class GetTime
class GetTime:

    #-------------------------------------------------------------------------------------
    # Variable(s)
    oTimeNow = None
    oTimeFrom = None
    oTimeTo = None
    a1oTimeSteps = None
    
    sTimeNow = None
    sTimeFrom = None
    sTimeTo = None
    #-------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------
    # Method time info
    def __init__(self, timenow=None, timestep=None, 
                       timeperiodpast=None, timeperiodfut=None, timerefHH='',
                       timerefworld=None):
        
        # Store information in global workspace
        self.sTimeNow = timenow
        self.iTimeStep = timestep
        self.iTimePeriodPast = timeperiodpast
        self.iTimePeriodFuture = timeperiodfut
        
        self.sTimeHHRef = timerefHH
        
        self.oTimeWorldRef = timerefworld
    
        # Get and check sTimeNow format
        self.getTimeNow()
            
        if self.iTimePeriodPast>=0:
        
            # Get TimeFrom and TimeTo
            self.getTimePeriod()
            # Get TimeSteps (between TimeFrom and TimeTo)
            self.getTimeSteps()
            # Get TimeBnds (in indexes)
            self.getTimeBnds()
        
        else:
            pass
            

    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to define TimePeriod (TimeFrom and TimeTo) 
    def getTimePeriod(self):
        
        # Define TimeTo
        self.oTimeTo = self.oTimeNow
        
        if self.iTimePeriodFuture:
            self.oTimeTo = self.oTimeTo + datetime.timedelta(seconds = self.iTimeStep*self.iTimePeriodFuture)
        
        self.sTimeTo = self.oTimeTo.strftime('%Y%m%d%H%M')
        
        # Define TimeFrom
        self.oTimeFrom = self.oTimeNow - datetime.timedelta(seconds = self.iTimeStep*self.iTimePeriodPast)
        self.sTimeFrom = self.oTimeFrom.strftime('%Y%m%d%H%M')

    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to define TimeSteps (between TimeFrom and TimeTo)
    def getTimeSteps(self):
        
        oTimeStep = self.oTimeFrom
        iTimeStep = datetime.timedelta(seconds = self.iTimeStep)
        
        a1oTimeSteps = []
        while oTimeStep <= self.oTimeTo:
            a1oTimeSteps.append(oTimeStep.strftime('%Y%m%d%H%M'))
            oTimeStep += iTimeStep
        
        self.a1oTimeSteps = a1oTimeSteps
        
    #-------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------
    # Method to get and check sTimeNow format and convert in datetime object
    def getTimeNow(self):
        
        # Define time length
        iTimeLength = len(self.sTimeNow)
        
        # Get time reference
        try:
            sTimeRefType = str(self.oTimeWorldRef['TimeType'])
            iTimeRefLoad = int(self.oTimeWorldRef['TimeLoad'])
            iTimeRefSave = int(self.oTimeWorldRef['TimeSave'])
        except:
            GetException(' -----> WARNING: TimeRefence format is not correct. Please check your settings file!', 2, 1) 
            GetException(' -----> WARNING: TimeRefence initialized in default mode (local time)!', 2, 1) 
            sTimeRefType = 'local'; iTimeRefLoad = 0; iTimeRefSave = 0;
        
        # Check time length 
        if iTimeLength == 12:
            
            oTimeNow = datetime.datetime.strptime(self.sTimeNow,'%Y%m%d%H%M')
            oTimeNow = oTimeNow.replace(minute = 0, second = 0, microsecond = 0)
            
        elif iTimeLength >= 8 and iTimeLength < 12:
            
            iTimeLessDigits = 12 - iTimeLength
            sTimeLessFormat = '0'*iTimeLessDigits
            
            self.sTimeNow = self.sTimeNow + sTimeLessFormat
            oTimeNow = datetime.datetime.strptime(self.sTimeNow,'%Y%m%d%H%M')
            oTimeNow = oTimeNow.replace(minute = 0, second = 0, microsecond = 0)
            
        elif iTimeLength == 0:
            
            if (self.sTimeNow == ''):
                    
                    if sTimeRefType == 'gmt':
                        self.sTimeNow = time.strftime("%Y%m%d%H%M", time.gmtime()) # ---> GMT TIME
                    
                    elif sTimeRefType == 'local':
                        self.sTimeNow = time.strftime("%Y%m%d%H%M", time.localtime()) # ---> LOCAL TIME
                    else:
                        GetException(' -----> WARNING: TimeType format is not correct. Please check your settings file!', 2, 1) 
                        GetException(' -----> WARNING: TimeType initialized in default mode (local time)!', 2, 1) 
                        self.sTimeNow = time.strftime("%Y%m%d%H%M", time.localtime()) # ---> LOCAL TIME
                        sTimeRefType == 'local'; iTimeRefLoad = 0; iTimeRefSave = 0;
                         
            else:
                GetException(' -----> ERROR: TimeNow format is unknown. Please check your settings file!', 1, 1) 
        else:
            GetException(' -----> ERROR: TimeNow format is unknown. Please check your settings file!', 1, 1) 
        
        # Check if HH time reference is defined
        if (self.sTimeHHRef == ''):
            oTimeNow = datetime.datetime.strptime(self.sTimeNow,'%Y%m%d%H%M')
            oTimeNow = oTimeNow.replace(minute = 0, second = 0, microsecond = 0)
        else:
            oTimeNow = datetime.datetime.strptime(self.sTimeNow,'%Y%m%d%H%M')
            oTimeNow = oTimeNow.replace(hour= int(self.sTimeHHRef), minute = 0, second = 0, microsecond = 0)
        
        # Update time now 
        self.sTimeNow = oTimeNow.strftime('%Y%m%d%H%M')
        oLogStream.info(' ----> Defining TimeNow: ' + str(self.sTimeNow))
        
        # Create oTimeNow object in global workspace
        self.oTimeNow = oTimeNow
        self.sTimeRefType = sTimeRefType
        self.iTimeRefLoad = iTimeRefLoad
        self.iTimeRefSave = iTimeRefSave
        
    #-------------------------------------------------------------------------------------    
    
    #-------------------------------------------------------------------------------------
    # Method to define TimeBnds in index format (between TimeFrom and TimeTo)
    def getTimeBnds(self):
        
        pass
   
    #-------------------------------------------------------------------------------------
   
    
   
#     #-------------------------------------------------------------------------------------
#     # Getting date bounds
#     def getTimeBnds(self):
#         
#         a1oTimePeriod = self.a1oTimePeriod
#         
#         iTemporalRatio = self.iTemporalRatio
#         
#         iAntSteps = (3600/self.iTimeDelta - 1)/numpy.float(iTemporalRatio)
#         #iAntSteps = 0
#         
#         sTimeFrom = a1oTimePeriod[0]
#         sTimeTo = a1oTimePeriod[-1]
#         
#         iSteps = 0;
#         a1oTimeBnds = []; a1dTimeElapsed = []
#         a2iTimeBnds = numpy.zeros((self.iTimeSteps,2))
#         for sTimeRun in a1oTimePeriod:
#             
#             iStepsUpd = numpy.float(iSteps)/numpy.float(iTemporalRatio)
#             
#             a2iTimeBnds[iSteps][0] = (iStepsUpd - iAntSteps)
#             a2iTimeBnds[iSteps][1] = (iStepsUpd)
#         
#             a1oTimeBnds.append((iStepsUpd - iAntSteps))
#             a1oTimeBnds.append((iStepsUpd))
#             
#             a1dTimeElapsed.append(iStepsUpd)
#             
#             iSteps = iSteps + 1
#         
#         # a2iTimeBnds is labelled in panoply
#         
#         # Saving time variable(s)
#         self.a2iTimeBnds = a2iTimeBnds
#         self.a1oTimeBnds = a1oTimeBnds
#         self.a1dTimeElapsed = a1dTimeElapsed
#     #-------------------------------------------------------------------------------------
