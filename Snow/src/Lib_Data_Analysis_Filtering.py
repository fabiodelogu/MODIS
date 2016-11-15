"""
Library Features:

Name:          Lib_Data_Analysis_Filtering
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20151019'
Version:       '1.0.0'
"""

#################################################################################
# Logging
import logging
oLogStream = logging.getLogger('sLogger')

# Global libraries
from scipy import ndimage

# Debug
#import matplotlib.pylab as plt
#################################################################################

#--------------------------------------------------------------------------------
# Filter variable using a uniform area
def aggregVarUniformArea(a2dVarData, iPixelSideLenght):

    # Compute filter
    a2dVarFilter = ndimage.uniform_filter(a2dVarData, size=iPixelSideLenght, mode='nearest')

    # Debug
    #plt.figure(1)
    #plt.imshow(a2dVarData,interpolation = 'none'); plt.colorbar(); plt.clim(0 ,1)
    #plt.figure(2)
    #plt.imshow(a2dVarFilter,interpolation = 'none'); plt.colorbar(); plt.clim(0 ,1)
    #plt.show()
    
    # Return value
    return a2dVarFilter
#-------------------------------------------------------------------------------------