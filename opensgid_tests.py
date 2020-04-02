# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 19:38:49 2020

@author: eneemann
Script to test and reproduce opensgid errors

31 Mar 2020: Created initial version of code (EMN).
"""

import arcpy
from arcpy import env
import os
import time


# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))

today = time.strftime("%Y%m%d")
staging_db = r"C:\E911\WeberArea\Staging103\Weber_Staging.gdb"
weber_db = r"C:\E911\WeberArea\Staging103\WeberSGB.gdb"
SGID = r"C:\Users\eneemann\AppData\Roaming\ESRI\ArcGISPro\Favorites\agrc@opensgid@opensgid.agrc.utah.gov.sde"
current_streets = os.path.join(weber_db, "Streets_Map")
citycd = os.path.join(weber_db, "CityCodes")
sgid_roads = os.path.join(SGID, "opensgid.transportation.roads")
sgid_munis = os.path.join(SGID, "opensgid.boundaries.municipal_boundaries")
env.workspace = staging_db
env.overwriteOutput = True

# Set up databases (SGID must be changed based on user's path)
ng911_L = r"L:\agrc\data\ng911\NG911_boundary_work.gdb\EMS_Boundaries"
ng911_emn = r"C:\Users\eneemann\Desktop\Neemann\NG911\NG911_project\NG911_project.gdb"

# Set up environments
arcpy.env.workspace = ng911_emn
arcpy.env.overwriteOutput = True
arcpy.env.qualifiedFieldNames = False

# Set up feature classes and tables
law_bounds = os.path.join(ng911_emn, 'NG911_law_bound_final_WGS84_20191017')
out_name_identity = os.path.join(ng911_emn, 'identity_test_' + today)

# This fails
arcpy.analysis.Identity(law_bounds, sgid_munis, out_name_identity, "NO_FID", None, "NO_RELATIONSHIPS")

# This works
arcpy.management.CopyFeatures(sgid_munis, "muni_lyr")
arcpy.analysis.Identity(law_bounds, "muni_lyr", out_name_identity, "NO_FID", None, "NO_RELATIONSHIPS")


# This fails
out_name_buff = os.path.join(ng911_emn, 'buffer_test_' + today)
arcpy.analysis.Buffer(sgid_munis, out_name_buff, "50 Meters", "FULL", "ROUND", "ALL", "", "")

# This works
out_name = os.path.join(ng911_emn, 'buffer_test_' + today)
temp_features = r'in_memory\temp_features'
arcpy.management.CopyFeatures(sgid_munis, temp_features)
arcpy.analysis.Buffer(temp_features, out_name_buff, "50 Meters", "FULL", "ROUND", "ALL", "", "")

print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))
