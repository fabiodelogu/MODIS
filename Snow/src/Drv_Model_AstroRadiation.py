"""
Class Features:

Name:          Drv_Model_AstroRadiation
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org); Mirko D'Andrea (mirko.dandrea@cimafoundation.org)
Date:          '20151103'
Version:       '1.0.0'
"""

#################################################################################
# Logging
import logging
oLogStream = logging.getLogger('sLogger')

import numpy as np
import datetime

import Lib_Model_AstroRadiation_Utils as ARUtils
import Lib_Model_AstroRadiation_Apps as ARApps

from Lib_Model_AstroRadiation_Utils import printMessage
from GetException import GetException

# Debug
import matplotlib.pylab as plt
#################################################################################

#--------------------------------------------------------------------------------
# Class to manage AstroRadiation model
class Drv_Model_AstroRadiation(object):
    
    #--------------------------------------------------------------------------------
    # Class init
    def __init__(self, a3dDataXYT_CF, 
                       sTimeFrom, sTimeTo, iTimeStep,
                       a2dGeoX, a2dGeoY, a2dGeoZ):
        
        # Save in global workspaceoLogStream
        self.a3dDataXYT_CF = a3dDataXYT_CF
        
        self.sTimeFrom = sTimeFrom
        self.sTimeTo = sTimeTo
        self.iTimeStep = iTimeStep
        
        self.a2dGeoX = a2dGeoX
        self.a2dGeoY = a2dGeoY
        self.a2dGeoZ = a2dGeoZ
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to initialize RF model
    @staticmethod
    def initializer(sTimeFrom, sTimeTo, iTimeStep,
                    a2dGeoX, a2dGeoY):
        
        #--------------------------------------------------------------------------------
        # Info start
        printMessage( ' ----->  Initialize ARad model  ... ')
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Compute time steps
        [a1oDataSteps, 
         iDataStep, iDataDelta] = ARUtils.computeTimeSteps(sTimeFrom, sTimeTo, iTimeStep, 1)
        #-------------------------------------------------------------------------------- 
        
        #--------------------------------------------------------------------------------
        # Compute parameters
        [a2dModelLz, a2dModelLm, a2dModelPhi, 
         dModeldGsc, dModelAS, dModelBS] = ARApps.computeParameters(a2dGeoX, a2dGeoY)
        #-------------------------------------------------------------------------------- 
         
        #--------------------------------------------------------------------------------
        # Info end
        printMessage( ' ----->  Initialize ARad model  ... OK')
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Return variable(s)
        return (a2dModelLz, a2dModelLm, a2dModelPhi, dModeldGsc, dModelAS, dModelBS, 
                a1oDataSteps, iDataStep, iDataDelta)
        #--------------------------------------------------------------------------------
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to manage RF model
    def main(self):
        
        #--------------------------------------------------------------------------------
        # Initialize RF workspace
        oWorkspace_AR = {}
        oWorkspace_AR['static'] = {}
        oWorkspace_AR['dynamic'] = {}
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Info start
        printMessage(' ====> RUN ASTRORADIATION DRV ... ')
        #--------------------------------------------------------------------------------
        
        #-------------------------------------------------------------------------------
        # Initialize RF model
        [self.a2dModelLz, self.a2dModelLm, self.a2dModelPhi, 
         self.dModelGsc, self.dModelAS, self.dModelBS, 
         self.a1oDataTime, self.iDataStep, self.iDataDelta] = self.initializer(self.sTimeFrom, self.sTimeTo, self.iTimeStep,
                                                                                self.a2dGeoX, self.a2dGeoY)
        # Save static data in RF workspace
        oWorkspace_AR['static'] = vars(self)
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Run RF using single core method
        oResults_AR = self.builder()
        #--------------------------------------------------------------------------------
        
        # Save dynamic data in output workspace
        oWorkspace_AR['dynamic'] = oResults_AR
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Info end
        printMessage(' ====> RUN ASTRORADIATION DRV ... OK')
        # Return variable(s)
        return oWorkspace_AR
        #--------------------------------------------------------------------------------
            
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to execute RF using single core
    def builder(self):
        
        #--------------------------------------------------------------------------------
        # Info start
        printMessage( ' -----> Build AR model ... ')
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Run RF model
        [self.a3dModelXYT_AR, self.a3dModelXYT_K] = self.runner(self.a3dDataXYT_CF, self.a2dGeoZ, 
                                                              self.a1oDataTime, self.iDataDelta, 
                                                              self.a2dModelLz, self.a2dModelLm, self.a2dModelPhi, 
                                                              self.dModelGsc, self.dModelAS, self.dModelBS)
        #--------------------------------------------------------------------------------
            
        #--------------------------------------------------------------------------------
        # Finalize RF model
        a1oDataXYT_OUT = self.finalizer(self.a3dModelXYT_AR, self.a3dModelXYT_K, self.a3dDataXYT_CF, 
                                        self.a1oDataTime,
                                        self.a2dGeoX, self.a2dGeoY)
        # Store result(s)
        oResults_AR = a1oDataXYT_OUT
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Info end
        printMessage( ' -----> Build AR model ... OK')
        # Return variable(s)
        return oResults_AR
        #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
        
    #--------------------------------------------------------------------------------
    # Method to finalize AR model
    @staticmethod
    def finalizer(a3dModelXYT_AR, a3dModelXYT_K, a3dDataXYT_CF, 
                  a1oDataTime, a2dGeoX, a2dGeoY):
        
        #--------------------------------------------------------------------------------
        # Info start
        printMessage( ' ------> Finalize AR model ... ')
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Cycling on data
        printMessage( ' --------> Compute output fields ... ' )
        sVarName_AR = 'AstroRadiation'; sVarName_K = 'IncRadiation'; sVarName_CF = 'CloudFactor'
        a1oDataXYT_OUT = {}; 
        a1oDataXYT_OUT[sVarName_AR] = {}; a1oDataXYT_OUT[sVarName_K] = {}; a1oDataXYT_OUT[sVarName_CF] = {}
        for iStep in range(0, a3dModelXYT_AR.shape[2]):
            
            # Get time sinformation
            sDataTime = str(a1oDataTime[iStep])
            a2dModelXY_AR = a3dModelXYT_AR[:,:,iStep];
            a2dModelXY_K = a3dModelXYT_K[:,:,iStep] 
            a2dDataXY_CF = a3dDataXYT_CF[:,:,iStep]
            
            # Info
            printMessage( ' --------> TIME: ' + str(sDataTime) +' STEP_OUT: ' + str(iStep) + ' ... ')
            
            # Save data and time
            a1oDataXYT_OUT[sVarName_AR][sDataTime] = a2dModelXY_AR
            a1oDataXYT_OUT[sVarName_K][sDataTime] = a2dModelXY_K
            a1oDataXYT_OUT[sVarName_CF][sDataTime] = a2dDataXY_CF
            
            # Info
            printMessage( ' --------> TIME: ' + str(sDataTime) +' STEP_OUT: ' + str(iStep) + ' ... OK')
        
        # Info
        printMessage( ' --------> Compute output fields ... OK ')
        #--------------------------------------------------------------------------------

        #--------------------------------------------------------------------------------
        # Info end
        printMessage( ' ------> Finalize AR model ... OK')

        # Return variable(s)
        return a1oDataXYT_OUT
        #--------------------------------------------------------------------------------
        
    #--------------------------------------------------------------------------------
        
    #--------------------------------------------------------------------------------
    # Method to run AR model
    @staticmethod
    def runner(a3dDataXYT_CF, a2dGeoZ,
               a1oDataTime, iDataDelta,
               a2dLz, a2dLm, a2dPhi, 
               dGsc, dAS, dBS):
        
        # Time information
        iDeltaMidT = iDataDelta/3600; iInputStep = iDataDelta/60
                
        # Info end
        printMessage( ' ------> Run AR model ... ')
        
        # Cycle(s) on time steps
        a3dModelXYT_K = np.zeros([a2dGeoZ.shape[0], a2dGeoZ.shape[1], len(a1oDataTime)])
        a3dModelXYT_AR = np.zeros([a2dGeoZ.shape[0], a2dGeoZ.shape[1], len(a1oDataTime)])
        for iTime, sTime in enumerate(a1oDataTime):
            
            # Compute cloud factor
            a2dDataXY_CF = a3dDataXYT_CF[:,:,iTime]
            
            # Compute HH
            oTimeDelta = datetime.timedelta(seconds = iDataDelta/2)
            oTime = datetime.datetime.strptime(sTime,'%Y%m%d%H%M')
            oTime = oTime.replace(minute = 0, second = 0, microsecond = 0)
            oTimeMid = oTime - oTimeDelta
            sTimeMid = oTimeMid.strftime('%Y%m%d%H%M')
            dHH = float(sTimeMid[8:10])
                        
            # Get JulianDate
            iJDate = ARUtils.getJDate(sTimeMid)
            # Inverse relative distance Earth-Sun
            dIRD = 1.0 + 0.033*np.cos(2*np.pi/365*iJDate)
            dB = 2*np.pi*(iJDate - 81)/364.0;
            
            # Seasonal correction for solar time [h]
            iSolarCorr = 0.1645*np.sin(2*dB) - 0.1255*np.cos(dB) - 0.025*np.sin(dB)
            
            # Solar declination [rad]
            dSolarDecl = 0.4093*np.sin(2*np.pi/365*iJDate - 1.405)
            
            # Solar time angle at midpoint of hourly or shorter period [rad]
            a2dSolarTA = np.pi/12.0*(dHH + 0.06667*(a2dLz - a2dLm) + iSolarCorr - 12.0);
    
            # Solar time angle at beginning of period [rad]
            a2dSolarTA_Start = a2dSolarTA - np.pi*iDeltaMidT/24.0;
            # Solar time angle at end of period [rad]
            a2dSolarTA_End = a2dSolarTA + np.pi*iDeltaMidT/24.0;
            
            # Extraterrestrial Radiation [MJ/m^2/interval] (Duffie & Beckman, 1980)
            a2dModel_AR = (12*iInputStep/np.pi*dGsc*dIRD*(
                             (a2dSolarTA_End - a2dSolarTA_Start)*np.sin(a2dPhi)*np.sin(dSolarDecl) + 
                             np.cos(a2dPhi)*np.cos(dSolarDecl)*(np.sin(a2dSolarTA_End) - np.sin(a2dSolarTA_Start)) ) )
            
            # Extraterrestrial Radiation [W/m^2]
            a2dModel_AR = a2dModel_AR*10**6/iDataDelta
            a2dModel_AR[a2dModel_AR <= 0.0] = 0.0
            a2dModel_AR[np.isnan(a2dGeoZ)] = np.nan
            dModel_AR = np.nanmean(a2dModel_AR)
    
            # Clear-sky shortwave radiation
            a2dModel_K = a2dDataXY_CF*(dAS + dBS*a2dGeoZ)*a2dModel_AR
            dModel_K = np.nanmean(a2dModel_K)
            
            # Info
            printMessage( ' -------> Time: ' + sTime + ' AR_Mean: ' + str(dModel_AR) + ' K_Mean: ' + str(dModel_K) )
            
            # Debug
            #plt.figure(1); plt.imshow(a2dModel_AR); plt.colorbar()
            #plt.figure(2); plt.imshow(a2dModel_K); plt.colorbar()
            #plt.show()
            
            # Store K and AR results
            a3dModelXYT_K[:,:,iTime] = a2dModel_K
            a3dModelXYT_AR[:,:,iTime] = a2dModel_AR
        
        # Info end
        printMessage( ' ------> Run AR model ... OK')
        
        # Return variable(s)
        return (a3dModelXYT_AR, a3dModelXYT_K)
    #--------------------------------------------------------------------------------
    
#--------------------------------------------------------------------------------


