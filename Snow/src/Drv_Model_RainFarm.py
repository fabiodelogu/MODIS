"""
Class Features:

Name:          Drv_Model_RainFarm
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org); Mirko D'Andrea (mirko.dandrea@cimafoundation.org)
Date:          '20150823'
Version:       '3.0.0'
"""

#################################################################################
# Logging
import logging
oLogStream = logging.getLogger('sLogger')

import sys
import os
import numpy as np
import multiprocessing as mp

import Lib_Model_RainFarm_Utils as RFUtils
import Lib_Model_RainFarm_Apps  as RFApps
import Lib_Model_RainFarm_Regrid as RFRegrid

from Lib_Model_RainFarm_Utils import printMessage
from GetException import GetException

# Debug
import matplotlib.pylab as plt
#################################################################################



#--------------------------------------------------------------------------------
# Class to manage RainFarm model
class Drv_Model_RainFarm(object):
    
    #--------------------------------------------------------------------------------
    # Class init
    def __init__(self, a3dDataXYT_IN, 
                       sTimeFrom_IN, sTimeTo_IN, 
                       a2dGeoX_IN, a2dGeoY_IN,
                       a2dGeoX_REF, a2dGeoY_REF, dGeoXStep_REF, dGeoYStep_REF, 
                       dGeoKm_EXT=0,
                       iNEnsemble=1,
                       iCSsf=1, iCTsf=1,
                       iRatioS=None, iRatioT=None,
                       dSlopeS=None, dSlopeT=None, 
                       bMultiCore=False,
                       sPathCache=None):
        
        # Save in global workspaceoLogStream
        self.a3dDataXYT_IN = a3dDataXYT_IN
        
        self.sTimeFrom_IN = sTimeFrom_IN
        self.sTimeTo_IN = sTimeTo_IN
        
        self.a2dGeoX_IN = a2dGeoX_IN
        self.a2dGeoY_IN = a2dGeoY_IN
        
        self.a2dGeoX_REF = a2dGeoX_REF
        self.a2dGeoY_REF = a2dGeoY_REF
        self.dGeoXStep_REF = dGeoXStep_REF
        self.dGeoYStep_REF = dGeoYStep_REF
        self.dGeoKm_EXT = dGeoKm_EXT
        
        self.iNEnsemble = iNEnsemble
        
        self.iCSsf = iCSsf
        self.iCTsf = iCTsf
        self.iRatioS = iRatioS
        self.iRatioT = iRatioT
        self.dSlopeS = dSlopeS
        self.dSlopeT = dSlopeT
        
        self.a2dMetagauss_RF = None
        
        self.bMultiCore = bMultiCore
        
        self.sPathCache = sPathCache
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to initialize RF model
    @staticmethod
    def initializer(a3dDataXYT_IN,
                    sTimeFrom_IN, sTimeTo_IN,
                    a2dGeoX_IN, a2dGeoY_IN,
                    a2dGeoX_REF, a2dGeoY_REF, 
                    dGeoXStep_REF, dGeoYStep_REF, 
                    dGeoKm_EXT,
                    iRatioS, iRatioT,
                    dSlopeS, dSlopeT, 
                    sPathCache):
        
        #--------------------------------------------------------------------------------
        # Info start
        printMessage( ' ----->  Initialize RF model  ... ')
        oVol_CVOL = None; oVol_RF = None;
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Extend REF grid
        printMessage( ' ------>  Extend RF spatial domain  ... ')
        [a2dGeoX_REF, a2dGeoY_REF] = RFUtils.extendGrid(a2dGeoX_IN, a2dGeoY_IN, 
                                                        a2dGeoX_REF, a2dGeoY_REF, dGeoXStep_REF, dGeoYStep_REF, 
                                                        dGeoKm_EXT)
        printMessage( ' ------>  Extend RF spatial domain  ... OK')
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Compute RF grid
        printMessage( ' ------>  Compute RF grid  ... ')
        [a2dGeoX_RF, a2dGeoY_RF, a2iIndex_RF, 
         dGeoXLL_RF, dGeoYLL_RF, iIMin_RF, iIMax_RF, iJMin_RF, iJMax_RF,
         iRatioS, iResolution_RF, iNPixels_RF] = RFUtils.computeGrid(a2dGeoX_IN, a2dGeoY_IN, 
                                                                   a2dGeoX_REF, a2dGeoY_REF, 
                                                                   dGeoXStep_REF, dGeoYStep_REF, 
                                                                   iRatioS)
        printMessage( ' ------>  Compute RF grid  ... OK')
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Compute RF volume (to control values on grid boundaries)
        #printMessage( ' ------>  Compute RF volume  ... ')
        #[oVol_CVOL, oVol_RF] = RFUtils.computeVolume(a2dGeoX_IN, a2dGeoY_IN, 
        #                                                 a2dGeoX_REF, a2dGeoY_REF, 
        #                                                 a2dGeoX_RF, a2dGeoY_RF,
        #                                                 iIMin_RF, iIMax_RF, iJMin_RF, iJMax_RF,
        #                                                 sPathCache)
        #printMessage( ' ------>  Compute RF volume  ... OK')
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Compute RF variable in XYT dimensions
        printMessage( ' ------>  Compute RF variable  ... ')
        a3dDataXYT_RF = RFUtils.computeVar(a3dDataXYT_IN, iIMin_RF, iIMax_RF, iJMin_RF, iJMax_RF)
        printMessage( ' ------>  Compute RF variable  ... OK')
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Compute RF time steps
        printMessage( ' ------>  Compute RF time steps ... ')
        [a1oDataTime_RF, iDataStep_RF, iDataDelta_RF] = RFUtils.computeTimeSteps(sTimeFrom_IN, sTimeTo_IN, a3dDataXYT_RF.shape[2], iRatioT)
        printMessage( ' ------>  Compute RF time steps ... OK')
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Other RF variable(s)
        iNs = iResolution_RF
        iNsl = iNPixels_RF
        iNr = 1
        iNas = iNPixels_RF
        iNt = iDataStep_RF #iNt = a3dDataXYT_RF.shape[2]*iRatioT
        iNtl = a3dDataXYT_RF.shape[2]
        iNat = a3dDataXYT_RF.shape[2]
        iNDelta = iDataDelta_RF
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Info end
        printMessage( ' ----->  Initialize RF model  ... OK')
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Return variable(s)
        return (a3dDataXYT_RF, a1oDataTime_RF,
                a2dGeoX_RF, a2dGeoY_RF, a2iIndex_RF, oVol_CVOL, oVol_RF, 
                a2dGeoX_REF, a2dGeoY_REF, 
                iNs, iNsl, iNr, iNas, iNt, iNtl, iNat, iNDelta)
        #--------------------------------------------------------------------------------
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to get process id
    def getProcessInfo(self, sTitle):
        
        # Info
        printMessage( ' ------> Info: ' + str(sTitle) + ' ModuleName: ' + str(__name__))
        
        if hasattr(os, 'getppid'):  # only available on Unix
            printMessage( ' -------> Parent process id: ' + str(os.getppid()))
    
        printMessage( ' -------> Process id: ' + str(os.getppid()))
    
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to get process signal start
    def getProcessSignalStart(self):
        
        # Info
        printMessage( ' ------> Process: ' + str(mp.current_process().name) + ' ... START')

    #--------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------
    # Method to get process signal end
    def getProcessSignalEnd(self, oP):
        
        # Info
        printMessage( ' ------> Process: ' + str(oP.name) + ' ExitCode: ' + str(oP.exitcode) + ' ... CLOSED')

    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to manage RF model
    def main(self):
        
        #--------------------------------------------------------------------------------
        # Initialize RF workspace
        oWorkspace_RF = {}
        oWorkspace_RF['static'] = {}
        oWorkspace_RF['dynamic'] = {}
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Info start
        printMessage(' ====> RUN RAINFARM DRV ... ')
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Initialize RF model
        [self.a3dDataXYT_RF, self.a1oDataTime_RF,
         self.a2dGeoX_RF, self.a2dGeoY_RF, self.a2iIndex_RF, self.oVol_CVOL, self.oVol_RF,
         self.a2dGeoX_REF, self.a2dGeoY_REF,
         self.iNs, self.iNsl, self.iNr, self.iNas, 
         self.iNt, self.iNtl, self.iNat, 
         self.iNDelta] = self.initializer(self.a3dDataXYT_IN,
                                          self.sTimeFrom_IN, self.sTimeTo_IN,
                                          self.a2dGeoX_IN, self.a2dGeoY_IN,
                                          self.a2dGeoX_REF, self.a2dGeoY_REF, 
                                          self.dGeoXStep_REF, self.dGeoYStep_REF, 
                                          self.dGeoKm_EXT,
                                          self.iRatioS, self.iRatioT,
                                          self.dSlopeS, self.dSlopeT, 
                                          self.sPathCache)
        # Save static data in RF workspace
        oWorkspace_RF['static'] = vars(self)
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Info about process
        self.getProcessInfo((str(sys._getframe().f_code.co_name)))
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Run RF model using multicores or single core method 
        if self.bMultiCore:
            
            #--------------------------------------------------------------------------------
            # Run RF model using multicores method
            
            # Define an output queue
            oQueue_RF = mp.Queue()
            
            # Define processes 
            oProcesses = [mp.Process(target=self.builder_multicore, args=(iEns, oQueue_RF)) for iE, iEns in enumerate(np.linspace(1, self.iNEnsemble, self.iNEnsemble, endpoint=True))]
            
            # Run processes
            for oP in oProcesses: oP.start()
            # Get processes results from the output queue
            oResults_RF = [oQueue_RF.get() for oP in oProcesses]
            # Exit the completed processes
            for oP in oProcesses: oP.join(); self.getProcessSignalEnd(oP);
            #--------------------------------------------------------------------------------

        else:
            
            #--------------------------------------------------------------------------------
            # Run RF using single core method
            oResults_RF = self.builder_singlecore()
            #--------------------------------------------------------------------------------
        
        # Save dynamic data in output workspace
        oWorkspace_RF['dynamic'] = oResults_RF
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Info end
        printMessage(' ====> RUN RAINFARM DRV ... OK')
        # Return variable(s)
        return oWorkspace_RF
        #--------------------------------------------------------------------------------
            
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to execute RF using single core
    def builder_singlecore(self):
        
        #--------------------------------------------------------------------------------
        # Info start
        printMessage( ' -----> Build RF model (SINGLECORE MODE) ... ')
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Info about process
        self.getProcessInfo((str(sys._getframe().f_code.co_name)))
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Cycle(s) on ensemble(s)
        oResults_RF = {}
        a1iNEnsemble = np.linspace(1, self.iNEnsemble, self.iNEnsemble, endpoint=True)
        for iE, iNEn in enumerate(a1iNEnsemble):

            #--------------------------------------------------------------------------------
            # Run RF model
            if np.any(self.a3dDataXYT_RF):
                # Disaggregation (if some value(s) are not null)
                [a3dModelXYT_RF, a2dMetagauss_RF] = self.runner(self.a3dDataXYT_RF, 
                                                                self.iRatioS, self.iNt/self.iNat,
                                                                cssf = self.iCSsf, ctsf = self.iCTsf, 
                                                                f = self.a2dMetagauss_RF,
                                                                celle3_rainfarm=None,
                                                                sx=self.dSlopeS, 
                                                                st=self.dSlopeT)
            else:
                # Exit with null field(s) if all values are zeros
                printMessage( ' ------> WARNING: all values are null! RF SKIPPED!')
                a3dModelXYT_RF = np.zeros([self.a3dDataXYT_RF.shape[0]*self.iRatioS, self.a3dDataXYT_RF.shape[1]*self.iRatioS, 
                                           self.a3dDataXYT_RF.shape[2]*(self.iNt/self.iNat)])
            #--------------------------------------------------------------------------------
            
            #--------------------------------------------------------------------------------
            # Finalize RF model
            a1oDataXYT_OUT = self.finalizer(self.a3dDataXYT_RF, a3dModelXYT_RF, self.a1oDataTime_RF,
                                              self.a2dGeoX_REF, self.a2dGeoY_REF, 
                                              self.a2dGeoX_RF, self.a2dGeoY_RF, self.a2iIndex_RF, 
                                              self.iNt, self.iNat, 
                                              self.iCSsf, self.iCTsf)
            #--------------------------------------------------------------------------------
            
            #--------------------------------------------------------------------------------
            # Save dynamic data in RF workspace
            oResults_RF[str(int(iNEn))] = {}
            #oResults_RF[str(int(iNEn))]['a3dModelXYT_RF'] = a3dModelXYT_RF
            #oResults_RF[str(int(iNEn))]['a2dMetagauss_RF'] = a2dMetagauss_RF
            #oResults_RF[str(int(iNEn))]['a3dDataXYT_OUT'] = a3dDataXYT_OUT
            
            oResults_RF[str(int(iNEn))] = a1oDataXYT_OUT
            #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Info end
        printMessage( ' -----> Build RF model (SINGLECORE MODE) ... OK')
        # Return variable(s)
        return oResults_RF
        #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
        
    #--------------------------------------------------------------------------------
    # Method to execute RF using multicores
    def builder_multicore(self, iEns, oQueue):
        
        #--------------------------------------------------------------------------------
        # Info start
        printMessage( ' -----> Build RF model (MULTICORES MODE) ... ')
        sProcName = mp.current_process().name
        printMessage( ' ------> Process ' + sProcName + '  ... ')
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Info about process
        self.getProcessInfo((str(sys._getframe().f_code.co_name)))
        #--------------------------------------------------------------------------------
    
        #--------------------------------------------------------------------------------
        # Run RF model
        if np.any(self.a3dDataXYT_RF):
            # Disaggregation (if some value(s) are not null)
            [a3dModelXYT_RF, a2dMetagauss_RF] = self.runner(self.a3dDataXYT_RF, 
                                                            self.iRatioS, self.iNt/self.iNat,
                                                            cssf = self.iCSsf, ctsf = self.iCTsf, 
                                                            f = self.a2dMetagauss_RF,
                                                            celle3_rainfarm=None,
                                                            sx=self.dSlopeS, 
                                                            st=self.dSlopeT)
        else:
            # Exit with null field(s) if all values are zeros
            printMessage( ' ------> WARNING: all values are null! RF SKIPPED!')
            a3dModelXYT_RF = np.zeros([self.a3dDataXYT_RF.shape[0]*self.iRatioS, self.a3dDataXYT_RF.shape[1]*self.iRatioS, 
                                       self.a3dDataXYT_RF.shape[2]*(self.iNt/self.iNat)])
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Finalize RF model
        a1oDataXYT_OUT = self.finalizer(self.a3dDataXYT_RF, a3dModelXYT_RF, self.a1oDataTime_RF,
                                          self.a2dGeoX_REF, self.a2dGeoY_REF, 
                                          self.a2dGeoX_RF, self.a2dGeoY_RF, self.a2iIndex_RF,
                                          self.iNt, self.iNat, 
                                          self.iCSsf, self.iCTsf)
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Save dynamic data in RF queue
        #oDict_RF={}
        #oDict_RF['a3dModelXYT_RF'] = a3dModelXYT_RF
        #oDict_RF['a2dMetagauss_RF'] = a2dMetagauss_RF
        #oDict_RF[a3dDataXYT_OUT'] = a3dDataXYT_OUT
        oDict_RF = a1oDataXYT_OUT

        oQueue.put(oDict_RF)
        
        # Info end
        printMessage( ' ------> Process ' +sProcName + ' ... COMPLETED')
        printMessage( ' -----> Build RF model (MULTICORES MODE) ... OK')
        return
        #--------------------------------------------------------------------------------
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to finalize RF model
    @staticmethod
    def finalizer(a3dDataXYT_RF, a3dModelXYT_RF, a1oDataTime_RF,
                  a2dGeoX_REF, a2dGeoY_REF, 
                  a2dGeoX_RF, a2dGeoY_RF, a2iIndex_RF, 
                  iNt, iNat, 
                  iCSsf, iCTsf):
        
        #--------------------------------------------------------------------------------
        # Info start
        printMessage( ' ------> Finalize RF model ... ')
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Cycling on data
        printMessage( ' --------> Compute output fields ... ' )
        sVarName = 'Rain' 
        a1oDataXYT_OUT = {}; 
        a1oDataXYT_OUT[sVarName] = {}
        for iStep in range(0, a3dModelXYT_RF.shape[2]):
        
            # Get time sinformation
            sDataTime = str(a1oDataTime_RF[iStep])
            
            # Info
            printMessage( ' --------> TIME: ' + str(sDataTime) +' STEP_OUT: ' + str(iStep) + ' ... ')
            
            # Grid data
            a2dModelXY_RF = a3dModelXYT_RF[:,:, iStep]
            #a2dDataXY_REF = RFRegrid.gridData(a2dModelXY_RF, a2dGeoX_RF, a2dGeoY_RF, a2dGeoX_REF, a2dGeoY_REF)
            a1dDataXY_REF = a2dModelXY_RF.ravel()[a2iIndex_RF.ravel()]
            a2dDataXY_REF = np.reshape(a1dDataXY_REF, [a2dGeoX_REF.shape[0], a2dGeoY_REF.shape[1]])
            
            # Save data and time
            
            a1oDataXYT_OUT[sVarName][sDataTime] = a2dDataXY_REF
            
            # Info
            printMessage( ' --------> TIME: ' + str(sDataTime) +' STEP_OUT: ' + str(iStep) + ' ... OK')
        
        # Info
        printMessage( ' --------> Compute output fields ... OK ')
        #--------------------------------------------------------------------------------

        #--------------------------------------------------------------------------------
        # Info end
        printMessage( ' ------> Finalize RF model ... OK')

        # Return variable(s)
        return a1oDataXYT_OUT
        #--------------------------------------------------------------------------------
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to finalize RF model
    @staticmethod
    def finalizer_kvol(a3dDataXYT_RF, a3dModelXYT_RF, a1oDataTime_RF,
                  a2dGeoX_REF, a2dGeoY_REF, oVol_CVOL, oVol_RF, 
                  iNt, iNat, 
                  iCSsf, iCTsf):
        
        #--------------------------------------------------------------------------------
        # Info start
        printMessage( ' ------> Finalize RF model ... ')
        #--------------------------------------------------------------------------------
        
        #--------------------------------------------------------------------------------
        # Aggregate fields on time reliable scale
        a3dDataXYAggT_RF = RFApps.agg_xyt(a3dDataXYT_RF, 
                                   a3dDataXYT_RF.shape[0], a3dDataXYT_RF.shape[1], a3dDataXYT_RF.shape[2])
        
        a3dModelXYAggT_RF = RFApps.agg_xyt(a3dModelXYT_RF, 
                                           a3dModelXYT_RF.shape[0], a3dModelXYT_RF.shape[1], a3dModelXYT_RF.shape[2]/iCTsf)
        #--------------------------------------------------------------------------------
        
        
        #--------------------------------------------------------------------------------
        # Cycling on originial time shape 
        printMessage( ' --------> Compute output fields ... ' )
        #a3dDataXYT_OUT = np.zeros((a2dGeoX_REF.shape[0], a2dGeoY_REF.shape[1], a3dModelXYT_RF.shape[2]))
        a1oDataXYT_OUT = {}
        iTimeRatio = iNt/iNat; iTimeTotal = 0
        for iStep in range(0, a3dModelXYAggT_RF.shape[2]):
            
            #--------------------------------------------------------------------------------
            # Regridding rainfarm and input 2d data
            a2dModelRegXYAggT_RF = oVol_RF.applyBufferedRegrid(a3dModelXYAggT_RF[:, :, iStep])
            a2dDataRegXYAggT_RF = oVol_CVOL.applyBufferedRegrid(a3dDataXYAggT_RF[:,:,iStep])
            
            #plt.figure(1)
            #plt.imshow(a2dModelRegrigXYAggT_RF); plt.colorbar()
            #plt.figure(2)
            #plt.imshow(a2dDataRegridXY_RF); plt.colorbar()
            #plt.figure(3)
            #plt.imshow(a3dDataXYT_RF[:,:,iStep]); plt.colorbar()
            #plt.show()
        
            a2dDataRegXYAggTMasked_RF = np.ma.masked_array(a2dDataRegXYAggT_RF,np.isnan(a2dDataRegXYAggT_RF))
            a2dModelRegXYAggTMasked_RF = np.ma.masked_array(a2dModelRegXYAggT_RF,np.isnan(a2dModelRegXYAggT_RF))
            
            # Compute correction factor
            dCorrectionFactor = 0.0
            dModelRegXYAggTMaskedMean_RF = a2dModelRegXYAggTMasked_RF.mean()
            dDataRegXYAggTMaskedMean_RF = a2dDataRegXYAggTMasked_RF.mean()
            
            if dModelRegXYAggTMaskedMean_RF == 0.0 and dDataRegXYAggTMaskedMean_RF == 0.0:
                dCorrectionFactor = 0.0
            else:
                dCorrectionFactor = a2dDataRegXYAggTMasked_RF.mean()/a2dModelRegXYAggTMasked_RF.mean()
            
            # Checking correction factor value for infinity value in division
            if( np.isinf(dCorrectionFactor) ):
                dCorrectionFactor = 0.0
                printMessage( ' ---------> WARNING: all data input are equal to infinity! Check your data input!' ) 
            else:
                pass
            #--------------------------------------------------------------------------------
            
            #--------------------------------------------------------------------------------
            # Cycling on time sub-interval
            for iSubStep in range(0, iTimeRatio):
                
                # Get time step information
                sDataTime = str(a1oDataTime_RF[iTimeTotal])
                
                # Info storing field
                printMessage( ' --------> TIME: ' + str(sDataTime) +' STEP_OUT: ' + str(iTimeTotal) + ' STEP_IN: ' + str(iStep) + 
                              ' CFACTOR: ' + str(dCorrectionFactor) +' TIMERATIO: ' + str(iTimeRatio))

                # Compute data output 
                a2dModelXY_OUT = a3dModelXYT_RF[:, :, iTimeTotal]
                a2dDataXY_OUT = oVol_RF.applyBufferedRegrid(a2dModelXY_OUT)
                
                # Saving corrected output maps
                #a3dDataXYT_OUT[:, :, iTimeTotal] = a2dDataXY_OUT * dCorrectionFactor
                a1oDataXYT_OUT[sDataTime] = a2dDataXY_OUT * dCorrectionFactor
                
                # Counter
                iTimeTotal = iTimeTotal + 1

            #--------------------------------------------------------------------------------
        
        # Info
        printMessage( ' --------> Compute output fields ... OK ')
        #--------------------------------------------------------------------------------

        #--------------------------------------------------------------------------------
        # Info end
        printMessage( ' ------> Finalize RF model ... OK')

        # Return variable(s)
        return a1oDataXYT_OUT
        #--------------------------------------------------------------------------------
        
    #--------------------------------------------------------------------------------
    
    #--------------------------------------------------------------------------------
    # Method to run RF model
    @staticmethod
    def runner(X, xscale, tscale, cssf, ctsf, 
             f=None, celle3_rainfarm=None, sx=None, st=None):
        
        '''
        x=rainfarm(X,sx,st,xscale,cssf,csst)
        INPUT
            X = matrice 3D di dimensioni nx * nx * nt, nx
            xscale = fattore di scala spaziale (numero intero)
            tscale = fattore di scala temporale (numero intero)
            cssf = scala spaziale affidabile 
                    (numero intero, 1 = risoluzione nativa)
            ctsf = scala temporale affidabile 
                    (numero intero, 1 = risoluzione nativa)
            f = ampiezze per il campo metagaussiano,  OPZIONALE
            celle3_rainfarm = matrice per l'interpolazione,   OPZIONALE
            sx = penza spettrale spaziale,    OPZIONALE
            st = penza spettrale temporale,    OPZIONALE 
             
        OUTPUT
            x = matrice 3D con il campo disaggregato di dimensioni (nx*xscale) * 
                (nx*xscale) * (nt*tscale)
            f = ampiezze per il campo metagaussiano calcolate
        '''
        
        # Info start
        printMessage( ' ------> Run RF model ... ')
        
        alfa = 1
        nx, ny, nt = X.shape
        if cssf == 1 and ctsf == 1:
            pa = X
        else:
            pa = RFApps.agg_xyt(X[:, :, 0:nt], nx/cssf, ny/cssf, nt/ctsf)
         
        # ====> START DEBUG DATA
        #import scipy.io as sio
        #data = {}
        #data['rain'] = X
        #sio.savemat('rain_debug.mat',data)
         
        #plt.figure(1)
        #plt.imshow(X[:,:,0], interpolation='none'); plt.colorbar()
        #plt.show()
        # ====> END DEBUG DATA
         
        # Find spectral slopes
        if sx is None and st is None:
             
            fxp,fyp,ftp = RFApps.fft3d(X)
             
            kmin = 3
            kmax = min(15, len(fxp)-1)
            wmin = 3
            wmax = min(9, len(ftp)-1)
     
            sx,sy,st = RFApps.fitallslopes(fxp, fyp, ftp, 
                                           np.arange(kmin, kmax+1),
                                           np.arange(wmin, wmax+1)) 
             
            # INIT: prepare f field for metagauss
            #np.random.rand('state',sum(100*clock))  ##ok<RAND> # 
            #seme random differente per ogni run del modello
        
        # Info slope(s)
        printMessage(' -------> Slopes: sx=%f sy=%f st=%f'%(sx, sy, st))
        
        if f is None:
            f = RFApps.initmetagauss(sx, st, ny*xscale, nt*tscale)
            
        # Generate metagaussian field
        g = RFApps.metagauss(f)
     
        # Nonlinear transform
        r = np.exp(alfa * g[0:ny*xscale, 0:ny*xscale, 0:nt*tscale]) 
     
        # We want the aggregated field to be the same as pa
        ga = RFApps.agg_xyt(r, nx/cssf, ny/cssf, nt/ctsf)
        ca = pa/ga
        if  celle3_rainfarm is None:
            cai = RFApps.interpola_xyt(ca, nx*xscale, ny*xscale, nt*tscale)
        else:
            cai = np.reshape(ca[celle3_rainfarm], (nx*xscale, ny*xscale, nt*tscale),
                             order='F')
            
        # Define final rain field
        x = cai * r
        
        # Info end
        printMessage( ' ------> Run RF model ... OK')
        # Return variable(s)
        return x, f
    #--------------------------------------------------------------------------------
    
#--------------------------------------------------------------------------------


