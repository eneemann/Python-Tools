# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 13:42:56 2020
@author: eneemann

11 May 2021 - script to convert Excel to ArcGIS table
"""

import arcpy
from arcpy import env
import os
import time

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))

in_db = r"C:\E911\Layton\Layton_staging.gdb"
in_fc = os.path.join(in_db, 'Davis_streets_build_20221021')

out_db = in_db
out_fc = os.path.join(out_db, 'aaa_test_back_to_UTM_12')

print(f"Projecting {in_fc} ...")
sr = arcpy.SpatialReference(26912)
arcpy.management.Project(in_fc, out_fc, sr, "WGS_1984_(ITRF00)_To_NAD_1983")




print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))