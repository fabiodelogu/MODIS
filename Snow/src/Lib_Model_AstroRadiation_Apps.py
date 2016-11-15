"""
Library Features:

Name:          Lib_Model_AstroRadiation_Apps
Author(s):     Fabio Delogu     (fabio.delogu@cimafoundation.org)
               Simone Gabellani (simone.gabellani@cimafoundation.org)
               
Date:          '20151103'
Version:       '1.0.0'
"""

#################################################################################
# Logging
import logging
oLogStream = logging.getLogger('sLogger')

import numpy as np

#import matplotlib.pylab as plt
#################################################################################

#--------------------------------------------------------------------------------
# Method to compute cloud factor
def computeParameters(a2dGeoX, a2dGeoY):
    
    # Degree to rad factor
    dTor= np.pi/180.0;
    
    # Gsc solar constant =MJ m-2 day-1
    dGsc = 118.08; 
    # Gsc solar constant =MJ m-2 min-1
    dGsc = dGsc/(60.0*24.0)
    
    # longitude of the centre of the local time zone
    a2dLz = np.round(a2dGeoX/15) * 15
    
    # Lm longitude of the measurement site [degrees west of Greenwich],
    a2dLm = 360.0 - a2dGeoX;
    # Latitude [rad]
    a2dPhi = a2dGeoY*dTor
    
    # K astronomic parameter(s)
    dAS = 0.65; dBS = 2.0*10e-5;
    
    # Return
    return (a2dLz, a2dLm, a2dPhi, dGsc, dAS, dBS)
    
#--------------------------------------------------------------------------------