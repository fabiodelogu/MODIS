"""
Library Features:

Name:          Lib_Model_RainFarm_Utils
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org); Mirko D'Andrea (mirko.dandrea@cimafoundation.org)
Date:          '20150823'
Version:       '3.0.0'
"""

#################################################################################
# Logging
import logging
oLogStream = logging.getLogger('sLogger')

import datetime
import numpy as np

import matplotlib.pylab as plt
#################################################################################

#--------------------------------------------------------------------------------
# Method to print message or write in a log file
def printMessage(sMsg):
    
    if not oLogStream.handlers:
        print(sMsg)
    else:
        oLogStream.info(sMsg)
          
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to compute Julian Date 
def getJDate(sTime):
    
    # sTime yyyymmddHHMM 
    sTimeFormat = '%Y%m%d%H%M'
    oTime = datetime.datetime.strptime(sTime, sTimeFormat)
    
    a1oTime = oTime.timetuple()
    iJDate = int(a1oTime.tm_yday)
    
    return iJDate

#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to convert decimal degrees to km (2)
def convertDeg2Km_2(deg, lat=None):

    if lat is None:
        km = deg * 110.54
    else:
        km = deg * 111.32 * np.cos(np.deg2rad(lat))
    return km

#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to convert decimal degrees to km (1)
def convertDeg2Km(deg): 
    
    # Earth radius (dRE = 6371 in matlab)
    dRE = 6378.1370 
    km = deg * (np.pi * dRE) / 180;
    return km

#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to convert km to decimal degrees
def convertKm2Deg(km): 
    
    # Earth radius (dRE = 6371 in matlab)
    dRE = 6378.1370 
    deg = 180 * km / (np.pi * dRE);
    return deg

#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to extend reference grid
def extendGrid(a2dGeoX_IN, a2dGeoY_IN, 
               a2dGeoX_REF, a2dGeoY_REF, dGeoXStep_REF, dGeoYStep_REF, 
               dGeoKm_EXT):
    
    #--------------------------------------------------------------------------------
    # Check EXT definition
    if dGeoKm_EXT > 0:
    
        #--------------------------------------------------------------------------------
        # Check grids (IN vs Ref)
        dGeoXMin_IN = np.min(a2dGeoX_IN); dGeoXMax_IN = np.max(a2dGeoX_IN); 
        dGeoYMin_IN = np.min(a2dGeoY_IN); dGeoYMax_IN = np.max(a2dGeoY_IN);
        
        dGeoXMin_REF = np.min(a2dGeoX_REF); dGeoXMax_REF = np.max(a2dGeoX_REF); 
        dGeoYMin_REF = np.min(a2dGeoY_REF); dGeoYMax_REF = np.max(a2dGeoY_REF);
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Convert Km to decimal degree
        dGeoDeg_EXT = convertKm2Deg(dGeoKm_EXT)
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Compute EXT point(s)
        dGeoXMin_EXT = dGeoXMin_REF - dGeoDeg_EXT/2; dGeoXMax_EXT = dGeoXMax_REF + dGeoDeg_EXT/2
        dGeoYMin_EXT = dGeoYMin_REF - dGeoDeg_EXT/2; dGeoYMax_EXT = dGeoYMax_REF + dGeoDeg_EXT/2
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Check EXT vs IN grid
        if (dGeoXMin_EXT <= dGeoXMin_IN):
            dGeoXMin_EXT = dGeoXMin_IN + 0.5*dGeoXStep_REF
        
        if (dGeoXMax_EXT >= dGeoXMax_IN):
            dGeoXMax_EXT = dGeoXMax_IN - 0.5*dGeoXStep_REF
        
        if (dGeoYMin_EXT <= dGeoYMin_IN):
            dGeoYMin_EXT = dGeoYMin_IN + 0.5*dGeoYStep_REF
        
        if (dGeoYMax_EXT >= dGeoYMax_IN):
            dGeoYMax_EXT = dGeoYMax_IN - 0.5*dGeoYStep_REF
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Compute dimensions of new grid
        iJ = int((dGeoXMax_EXT - dGeoXMin_EXT)/dGeoXStep_REF)
        iI = int((dGeoYMax_EXT - dGeoYMin_EXT)/dGeoYStep_REF)
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Create EXT grid
        a1dGeoX_EXT = np.linspace(dGeoXMin_EXT, dGeoXMax_EXT, iJ, endpoint=True)
        a1dGeoY_EXT = np.linspace(dGeoYMin_EXT, dGeoYMax_EXT, iI, endpoint=True)
        
        a2dGeoX_EXT, a2dGeoY_EXT = np.meshgrid(a1dGeoX_EXT, a1dGeoY_EXT)
        a2dGeoY_EXT = np.flipud(a2dGeoY_EXT)
        #--------------------------------------------------------------------------------
    
    else:
        
        #--------------------------------------------------------------------------------
        # No grid EXT (if dGeoKm_EXT == 0)
        a2dGeoX_EXT = a2dGeoX_REF
        a2dGeoY_EXT = a2dGeoY_REF
        dGeoDeg_EXT = 0.0
        #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Info
    dGeoXMin_EXT = np.min(a2dGeoX_EXT); dGeoXMax_EXT = np.max(a2dGeoX_EXT); 
    dGeoYMin_EXT = np.min(a2dGeoY_EXT); dGeoYMax_EXT = np.max(a2dGeoY_EXT);
    
    dGeoXMin_REF = np.min(a2dGeoX_REF); dGeoXMax_REF = np.max(a2dGeoX_REF); 
    dGeoYMin_REF = np.min(a2dGeoY_REF); dGeoYMax_REF = np.max(a2dGeoY_REF);
    
    printMessage( ' -------> Grid EXT Value: ' + str(dGeoDeg_EXT) + ' degree')
    printMessage( ' -------> Grid REF -- GeoXMin: ' + str(dGeoXMin_REF) + ' GeoXMax: ' + str(dGeoXMax_REF) + 
                  ' GeoYMin: ' + str(dGeoYMin_REF) + ' GeoYMax: ' + str(dGeoYMax_REF) )
    printMessage( ' -------> Grid EXT -- GeoXMin: ' + str(dGeoXMin_EXT) + ' GeoXMax: ' + str(dGeoXMax_EXT) + 
                  ' GeoYMin: ' + str(dGeoYMin_EXT) + ' GeoYMax: ' + str(dGeoYMax_EXT) )
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Return variable(s)
    return a2dGeoX_EXT, a2dGeoY_EXT
    #--------------------------------------------------------------------------------
    
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to compute time steps
def computeTimeSteps(sTimeFrom_IN, sTimeTo_IN, iTimeStep_IN, iTimeRatio_OUT):
    
    #--------------------------------------------------------------------------------
    # Get time from and time to information
    oTimeFrom_IN = datetime.datetime.strptime(sTimeFrom_IN,'%Y%m%d%H%M')
    oTimeTo_IN = datetime.datetime.strptime(sTimeTo_IN,'%Y%m%d%H%M')
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Compute time difference in seconds
    oTimeDiff_IN = oTimeTo_IN - oTimeFrom_IN; iTimeDiff_IN = oTimeDiff_IN.total_seconds()
    # Compute time delta (IN)
    iTimeDelta_IN = int(iTimeDiff_IN)/int(iTimeStep_IN-1) # step -1
    # Compute time delta and step (OUT)
    iTimeDelta_OUT = int(iTimeDelta_IN)/int(iTimeRatio_OUT)
    oTimeDelta_OUT = datetime.timedelta(seconds = iTimeDelta_OUT)
    iTimeStep_OUT = iTimeStep_IN * iTimeRatio_OUT
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Compute initial step
    oTimeStep_IN = oTimeFrom_IN - datetime.timedelta(seconds = iTimeDelta_IN)
    oTimeStep_OUT = oTimeStep_IN + datetime.timedelta(seconds = iTimeDelta_OUT)
    
    # Compute time steps OUT
    a1oTimeSteps_OUT = []
    while oTimeStep_OUT <= oTimeTo_IN:
        a1oTimeSteps_OUT.append(oTimeStep_OUT.strftime('%Y%m%d%H%M'))
        oTimeStep_OUT += oTimeDelta_OUT
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Info
    sTimeFrom = a1oTimeSteps_OUT[0]; sTimeTo = a1oTimeSteps_OUT[-1]
    printMessage( ' -------> Time RF -- From: ' + sTimeFrom + ' To: ' + str(sTimeTo))
    
    # Return variable(s)
    return a1oTimeSteps_OUT, iTimeStep_OUT, iTimeDelta_OUT
    #--------------------------------------------------------------------------------
    
#-------------------------------------------------------------------------------- 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#--------------------------------------------------------------------------------