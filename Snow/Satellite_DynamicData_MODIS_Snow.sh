#!/bin/bash

# MODIS Reprojection Tool
MRT_HOME="/home/gabellani/MODIS_Data_Processing/Library/"
PATH="$PATH:/home/gabellani/MODIS_Data_Processing/Library/bin"
MRT_DATA_DIR="/home/gabellani/MODIS_Data_Processing/Library/data"
export MRT_HOME PATH MRT_DATA_DIR

# Set HDF5 disable version check
export HDF5_DISABLE_VERSION_CHECK=1

# Execute Python Script
python Satellite_DynamicData_MODIS_Snow.py -settingfile /home/gabellani/MODIS_Data_Processing/Product_Snow_V2/config_algorithms/satellite_dynamicdata_modis-snow_algorithm_server_realtime.config -logfile /home/gabellani/MODIS_Data_Processing/Product_Snow_V2/config_logs/satellite_dynamicdata_modis-snow_logging_server_realtime.config

