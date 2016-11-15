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
import math, os, pickle, hashlib
import numpy as np

import Lib_Model_RainFarm_Regrid as RFRegrid

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
# Method to check if number is odd or even
def checkMod(iNum, iDiv):
    # Return True or False, depending on if the input number is odd. 
    # Odd numbers are 1, 3, 5, 7, and so on. 
    # Even numbers are 0, 2, 4, 6, and so on.
    
    iMod = iNum % iDiv
     
    return iMod
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
# Method to find closest point
def findClosestIndex(a2dGeoX, a2dGeoY, dGeoX, dGeoY):
    
    #--------------------------------------------------------------------------------
    # Compute distance
    a2dGeoDistance = ((a2dGeoX - dGeoX)**2 + (a2dGeoY - dGeoY)**2);
    dGeoDistanceMin = np.min(a2dGeoDistance);
    a1iGeoIndex = np.where(a2dGeoDistance == dGeoDistanceMin)
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Indexes of the point in the reference grid
    iPointI = a1iGeoIndex[0][0];
    iPointJ = a1iGeoIndex[1][0];
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Return variable(s)
    return iPointI, iPointJ
    #--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to select variable field(s)
def computeVar(a3dDataXYT_IN, 
               iIMin_RF, iIMax_RF, iJMin_RF, iJMax_RF):
    
    # RF 3D fields in XYT dimensions
    a3dDataXYT_RF = a3dDataXYT_IN[iIMin_RF : iIMax_RF + 1, iJMin_RF : iJMax_RF + 1, :];
    a3dDataXYT_RF[a3dDataXYT_RF<0.01] = 0; # Just in case

    return a3dDataXYT_RF
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
# Method to create RF grid
def computeGrid(a2dGeoX_IN, a2dGeoY_IN, 
               a2dGeoX_REF, a2dGeoY_REF, dGeoXStep_REF, dGeoYStep_REF, 
               iRatioS):

    #--------------------------------------------------------------------------------
    # Check grids (IN vs Ref)
    dGeoXMin_IN = np.min(a2dGeoX_IN); dGeoXMax_IN = np.max(a2dGeoX_IN); 
    dGeoYMin_IN = np.min(a2dGeoY_IN); dGeoYMax_IN = np.max(a2dGeoY_IN);
    
    dGeoXMin_REF = np.min(a2dGeoX_REF); dGeoXMax_REF = np.max(a2dGeoX_REF); 
    dGeoYMin_REF = np.min(a2dGeoY_REF); dGeoYMax_REF = np.max(a2dGeoY_REF);
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Choose type grid
    bGrid = 0;
    if( ( (dGeoYMin_IN == dGeoYMin_REF) and (dGeoYMax_IN == dGeoYMax_REF) ) and 
        ( (dGeoXMin_IN == dGeoXMin_REF) and (dGeoXMax_IN == dGeoXMax_REF) ) ):
        
        # ==> Grids are equal
        printMessage( ' -------> Grid IN == Grid REF')
        # Lower Left Corner 
        iIMax_REF = a2dGeoX_IN.shape[0] - 1; iJMin_REF = 0;
        # Upper Right Corner 
        iIMin_REF = 0; iJMax_REF = a2dGeoX_IN.shape[1] - 1;
        # Type Grid
        bGrid = 1;
        
    else: 
        
        # ==> Grids are different
        printMessage( ' -------> Grid IN != Grid REF')
        # Lower Left Corner
        iIMax_REF, iJMin_REF = findClosestIndex(a2dGeoX_IN, a2dGeoY_IN, dGeoXMin_REF, dGeoYMin_REF)
        # Upper Right Corner
        iIMin_REF, iJMax_REF = findClosestIndex(a2dGeoX_IN, a2dGeoY_IN, dGeoXMax_REF, dGeoYMax_REF)
        
        # Check corner(s)
        if a2dGeoX_IN[iIMax_REF, iJMin_REF] > dGeoXMin_REF:
            iJMin_REF = iJMin_REF - 1
        if a2dGeoX_IN[iIMin_REF, iJMax_REF] < dGeoXMax_REF:
            iJMax_REF = iJMax_REF + 1
    
        if a2dGeoY_IN[iIMax_REF, iJMin_REF] > dGeoYMin_REF:
            iIMax_REF = iIMax_REF + 1
        if a2dGeoY_IN[iIMin_REF, iJMax_REF] < dGeoYMax_REF:
            iIMin_REF = iIMin_REF - 1
            
        # Type Grid
        bGrid = 2;
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Find values of x, y and steps of grid RF
    dGeoXMin_CUT = a2dGeoX_IN[iIMax_REF, iJMin_REF]
    dGeoXMax_CUT = a2dGeoX_IN[iIMin_REF, iJMax_REF]
    dGeoYMin_CUT = a2dGeoY_IN[iIMax_REF, iJMin_REF]
    dGeoYMax_CUT = a2dGeoY_IN[iIMin_REF, iJMax_REF]

    dGeoXStep_CUT = (dGeoXMax_CUT - dGeoXMin_CUT)/(iJMax_REF - iJMin_REF)
    dGeoYStep_CUT = (dGeoYMax_CUT - dGeoYMin_CUT)/(iIMax_REF - iIMin_REF)
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Define pixels number (max dimension for square matrix) and redefine spatial ratio
    if (bGrid == 1):
        iNPixels_REF = min((iJMax_REF - iJMin_REF) + 1, (iIMax_REF - iIMin_REF) + 1)
    elif (bGrid == 2):
        iNPixels_REF = max((iJMax_REF - iJMin_REF) + 1, (iIMax_REF - iIMin_REF) + 1)
    else:
        pass

    iResolution_REF = 0; dRatioS = float(iRatioS)
    if (dRatioS == 0):
        dRatioS = np.max((dGeoXStep_CUT/dGeoXStep_REF),dGeoYStep_CUT/dGeoYStep_REF)
        iRatioS = int(2**(math.floor(math.log(dRatioS,2))))
        iResolution_REF = int(iNPixels_REF*iRatioS)
    else:
        iResolution_REF = int(iNPixels_REF*iRatioS)
        
    # Cast spatial ratio to float
    dRatioS = float(iRatioS)
    #--------------------------------------------------------------------------------
    
    # Default method
    #iIMax_RF = iIMax_REF
    #iJMin_RF = iJMin_REF
    #iIMin_RF = iIMax_REF - (iNPixels - 1)
    #iJMax_RF = iJMin_REF + (iNPixels - 1)
    
    #--------------------------------------------------------------------------------
    # Method to search grid index
    [iIMin_RF, iIMax_RF, 
     iJMin_RF, iJMax_RF,
     iNPixels_RF, iResolution_RF] = searchGridIndex(iIMax_REF, iJMin_REF, 
                                                    a2dGeoX_REF.shape[0], a2dGeoY_REF.shape[1],
                                                    iNPixels_REF, iRatioS)
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Define grid rainfarm
    dGeoXMin_RF = a2dGeoX_IN[iIMax_RF, iJMin_RF] - .5*((dRatioS - 1)/dRatioS)*dGeoXStep_CUT
    dGeoYMin_RF = a2dGeoY_IN[iIMax_RF, iJMin_RF] - .5*((dRatioS - 1)/dRatioS)*dGeoYStep_CUT
    dGeoXMax_RF = a2dGeoX_IN[iIMin_RF, iJMax_RF] + .5*((dRatioS - 1)/dRatioS)*dGeoXStep_CUT
    dGeoYMax_RF = a2dGeoY_IN[iIMin_RF, iJMax_RF] + .5*((dRatioS - 1)/dRatioS)*dGeoYStep_CUT
    
    a1dGeoX_RF = np.linspace(dGeoXMin_RF, dGeoXMax_RF, iResolution_RF, endpoint=True)
    a1dGeoY_RF = np.linspace(dGeoYMin_RF, dGeoYMax_RF, iResolution_RF, endpoint=True)
    
    a2dGeoX_RF, a2dGeoY_RF = np.meshgrid(a1dGeoX_RF, a1dGeoY_RF)
    a2dGeoY_RF = np.flipud(a2dGeoY_RF)
    
    # LL corner
    dGeoXLL_RF = a2dGeoX_IN[iIMax_RF, iJMin_RF]
    dGeoYLL_RF = a2dGeoX_IN[iIMax_RF, iJMin_RF]
    
    # Compute grid indexes using nearest interpolation
    a2iIndex_RF = RFRegrid.gridIndex(a2dGeoX_RF, a2dGeoY_RF, a2dGeoX_REF, a2dGeoY_REF)
    
    # Info
    printMessage( ' -------> Grid IN -- GeoXMin: ' + str(dGeoXMin_IN) + ' GeoXMax: ' + str(dGeoXMax_IN) + 
                  ' GeoYMin: ' + str(dGeoYMin_IN) + ' GeoYMax: ' + str(dGeoYMax_IN) )
    printMessage( ' -------> Grid REF -- GeoXMin: ' + str(dGeoXMin_REF) + ' GeoXMax: ' + str(dGeoXMax_REF) + 
                  ' GeoYMin: ' + str(dGeoYMin_REF) + ' GeoYMax: ' + str(dGeoYMax_REF) )
    printMessage( ' -------> Grid RF -- GeoXMin: ' + str(dGeoXMin_RF) + ' GeoXMax: ' + str(dGeoXMax_RF) + 
                  ' GeoYMin: ' + str(dGeoYMin_RF) + ' GeoYMax: ' + str(dGeoYMax_RF) )
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Define output
    return(a2dGeoX_RF, a2dGeoY_RF, a2iIndex_RF, 
           dGeoXLL_RF, dGeoYLL_RF, iIMin_RF, iIMax_RF, iJMin_RF, iJMax_RF,
           iRatioS, iResolution_RF, iNPixels_RF)
    #--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Method to compute volume 
def computeVolume(a2dGeoX_IN, a2dGeoY_IN, a2dGeoX_REF, a2dGeoY_REF, a2dGeoX_RF, a2dGeoY_RF,
                  iIMin_RF, iIMax_RF, iJMin_RF, iJMax_RF,
                  sPathCache):
    
    #--------------------------------------------------------------------------------
    # Initialize GeoX and GeoY to volume control
    a2dGeoX_CVOL = a2dGeoX_IN[iIMin_RF : iIMax_RF + 1, iJMin_RF : iJMax_RF + 1]
    a2dGeoY_CVOL = a2dGeoY_IN[iIMin_RF : iIMax_RF + 1, iJMin_RF : iJMax_RF + 1]
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Check cache folder availability
    if sPathCache:
        
        #--------------------------------------------------------------------------------
        # Create cache folder 
        if not os.path.isdir(sPathCache):
            os.makedirs(sPathCache)
        else:
            pass
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Create re-grid filenames
        sHash_CVOL = hashlib.sha1(np.dstack((a2dGeoX_CVOL, a2dGeoY_CVOL)).ravel()).hexdigest()
        sHash_RF = hashlib.sha1(np.dstack((a2dGeoX_RF, a2dGeoY_RF)).ravel()).hexdigest()
        sHash_REF = hashlib.sha1(np.dstack((a2dGeoX_REF, a2dGeoY_REF)).ravel()).hexdigest()
  
        sFileCache_CVOL = os.path.join(sPathCache, 'RF_KVol_' + sHash_CVOL + '_' + sHash_REF + '.pk')
        sFileCache_RF = os.path.join(sPathCache,'RF_KVol_' + sHash_RF + '_' + sHash_REF + '.pk')
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Load or compute re-grid files
        try:
            
            #--------------------------------------------------------------------------------
            # Load re-grid files (if re-grid files are computed previously)
            oVol_CVOL = pickle.load(open(sFileCache_CVOL, 'r'))
            oVol_RF = pickle.load(open(sFileCache_RF,'r'))
            #--------------------------------------------------------------------------------
   
        except Exception:
            
            #--------------------------------------------------------------------------------
            # Compute re-grid files (if re-grid files are not computed previously) 
            oVol_RF = RFRegrid.KVolumeRegridder(a2dGeoX_RF, a2dGeoY_RF,
                                                      a2dGeoX_REF, a2dGeoY_REF)
            
            oVol_CVOL = RFRegrid.KVolumeRegridder(a2dGeoX_CVOL, a2dGeoY_CVOL,
                                                                   a2dGeoX_REF, a2dGeoY_REF)
            
            # Save re-grid files in cache folder
            with open(sFileCache_CVOL, 'wb') as oFile:
                pickle.dump(oVol_CVOL, oFile, pickle.HIGHEST_PROTOCOL)
   
            with open(sFileCache_RF, 'wb') as oFile:
                pickle.dump(oVol_RF, oFile, pickle.HIGHEST_PROTOCOL)
            #--------------------------------------------------------------------------------
                
        #--------------------------------------------------------------------------------
    else:
        
        #--------------------------------------------------------------------------------
        # Compute re-grid method (if cache is not available) 
        oVol_CVOL = RFRegrid.KVolumeRegridder(a2dGeoX_CVOL, a2dGeoY_CVOL,
                                              a2dGeoX_REF, a2dGeoY_REF)

        oVol_RF = RFRegrid.KVolumeRegridder(a2dGeoX_RF, a2dGeoY_RF,
                                            a2dGeoX_REF, a2dGeoY_REF)
        #--------------------------------------------------------------------------------
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Return variable(s)
    return(oVol_CVOL, oVol_RF)
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
# Method to define grid index
def searchGridIndex(iIMax_REF, iJMin_REF, iRows_REF, iCols_REF, iNPixels, 
                    iRatioS):
    
    #--------------------------------------------------------------------------------
    # Define IJ CUT indexes
    iIMax_RF = iIMax_REF
    iJMin_RF = iJMin_REF
    iIMin_RF = iIMax_REF - (iNPixels - 1)
    iJMax_RF = iJMin_REF + (iNPixels - 1)
    
    # Check mod
    iIDelta_RF = iIMax_RF - iIMin_RF + 1
    iJDelta_RF = iJMax_RF - iJMin_RF + 1
    iIMod_RF = checkMod(iIDelta_RF, iRatioS)
    iJMod_RF = checkMod(iJDelta_RF, iRatioS)
    
    # Info
    printMessage( ' -------> Grid RF Index -- Initial Values -- IMin: ' + str(iIMin_RF) + ' IMax: ' + str(iIMax_RF) + 
                  ' JMin: ' + str(iJMin_RF) + ' JMax: ' + str(iJMax_RF)  )
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Check if grid CUT is almost 8x8 grids --> to take care fft properties
    while (iIDelta_RF < 8 + 2*iIMod_RF):
        iIMax_RF = iIMax_RF + 1
        iIMin_RF = iIMin_RF - 1
        iIDelta_RF = iIMax_RF - iIMin_RF + 1
    while (iJDelta_RF < 8 + 2*iJMod_RF):
        iJMax_RF = iJMax_RF + 1
        iJMin_RF = iJMin_RF - 1
        iJDelta_RF = iJMax_RF - iJMin_RF + 1
    
    # Check mod
    iIDelta_RF = iIMax_RF - iIMin_RF + 1
    iJDelta_RF = iJMax_RF - iJMin_RF + 1
    iIMod_RF = checkMod(iIDelta_RF, iRatioS)
    iJMod_RF = checkMod(iJDelta_RF, iRatioS)
    
    # Info
    printMessage( ' -------> Grid RF Index -- After corrections for FFT -- IMin: ' + str(iIMin_RF) + ' IMax: ' + str(iIMax_RF) + 
                  ' JMin: ' + str(iJMin_RF) + ' JMax: ' + str(iJMax_RF)  )
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Check if grid CUT is included in grid IN (squared grid) --> latitude and longitude adjustment
    if (iIMin_RF < 0):
        iIMinShift_RF = -iIMin_RF
        iIMin_RF = iIMin_RF + iIMinShift_RF
        iIMax_RF = iIMax_RF + iIMinShift_RF
    else: pass 
  
    if (iIMax_RF >= iCols_REF):
        iIMaxShift_RF = iIMax_RF - (iCols_REF - 1)
        iIMax_RF = iIMax_RF - iIMaxShift_RF
        iIMin_RF = iIMin_RF - iIMaxShift_RF
    else: pass 
    
    if (iJMin_RF < 0):
        iJMinShift_RF = -iJMin_RF
        iJMin_RF = iJMin_RF + iJMinShift_RF
        iJMax_RF = iJMax_RF + iJMinShift_RF 
    else: pass 
  
    if (iJMax_RF >= iRows_REF):
        iJMaxShift_RF = iJMax_RF - (iRows_REF - 1)
        iJMax_RF = iJMax_RF - iJMaxShift_RF
        iJMin_RF = iJMin_RF - iJMaxShift_RF
    else: pass 
    
    # Check mod
    iIDelta_RF = iIMax_RF - iIMin_RF + 1
    iJDelta_RF = iJMax_RF - iJMin_RF + 1
    iIMod_RF = checkMod(iIDelta_RF, iRatioS)
    iJMod_RF = checkMod(iJDelta_RF, iRatioS)
    
    # Info
    printMessage( ' -------> Grid RF Index -- After corrections for domain dims -- IMin: ' + str(iIMin_RF) + ' IMax: ' + str(iIMax_RF) + 
                  ' JMin: ' + str(iJMin_RF) + ' JMax: ' + str(iJMax_RF)  )
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Compute grid index taking care spatial disaggregation factor
    # I index
    while iIDelta_RF%iRatioS != 0:
        
        if iIMax_RF < iCols_REF:
            iIMax_RF = iIMax_RF + 1
        elif iIMax_RF >= iCols_REF:
            
            printMessage( ' -------> WARNING: IMax_RF >= Cols_REF ')
            if iIMin_RF > 0:
                iIMin_RF = iIMin_RF - 1
            elif iIMin_RF <= 0:
                printMessage( ' -------> WARNING: IMin_RF <= 0 ')
                pass
        
        iIDelta_RF = iIMax_RF - iIMin_RF + 1
    # J index
    while iJDelta_RF%iRatioS != 0:
        
        if iJMax_RF < iRows_REF:
            iJMax_RF = iJMax_RF + 1
        elif iJMax_RF >= iRows_REF:
            
            printMessage( ' -------> WARNING: JMax_RF >= Rows_REF ')
            if iJMin_RF > 0:
                iJMin_RF = iJMin_RF - 1
            else:
                printMessage( ' -------> WARNING: JMin_RF <= 0 ')
                pass
        
        iJDelta_RF = iJMax_RF - iJMin_RF + 1
    
    # Control mod
    iIMod_RF = checkMod(iIDelta_RF, iRatioS)
    iJMod_RF = checkMod(iJDelta_RF, iRatioS)
    
    if (iIMod_RF != 0) or (iJMod_RF != 0):
        printMessage( ' --------> WARNING: grid RF is not divisible to spatial resolution! Check grid RF!')
    else:pass
    
    # Info
    printMessage( ' -------> Grid RF Index -- Final Values -- IMin: ' + str(iIMin_RF) + ' IMax: ' + str(iIMax_RF) + 
                  ' JMin: ' + str(iJMin_RF) + ' JMax: ' + str(iJMax_RF)  )
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Define pixels number (max dimension for square matrix) and redefine spatial ratio
    iNPixels_RF = max((iJMax_RF - iJMin_RF) + 1, (iIMax_RF - iIMin_RF) + 1)
    iResolution_RF = int(iNPixels_RF*iRatioS)
    #--------------------------------------------------------------------------------
    
    
    #--------------------------------------------------------------------------------
    # Return variable(s)
    return iIMin_RF, iIMax_RF, iJMin_RF, iJMax_RF, iNPixels_RF, iResolution_RF
    #--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------  
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#--------------------------------------------------------------------------------