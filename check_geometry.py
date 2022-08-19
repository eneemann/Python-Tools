# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 15:11:45 2021
@author: eneemann

Script to identify and list curvepart features
"""

import arcpy
import os
import time
import pandas as pd

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))

######################
#  Set up variables  #
######################

t = time.localtime()
today = time.strftime("%Y%m%d_%H%M%S", t)
#db = r"L:\agrc\data\ng911\Submitted_to_911DM\UtahNG911GIS_20220106.gdb"
#db = r"\\itwfpcap2\AGRC\agrc\data\ng911\Working Folder\NG911_working_database.gdb"
#db = r"\\itwfpcap2\AGRC\agrc\data\ng911\SpatialStation_live_data\UtahNG911GIS.gdb"
#db = r'C:\Users\eneemann\Desktop\Neemann\NG911\NG911_project\NG911_project.gdb\EMS_Boundaries'
#db = r'C:\Users\eneemann\Desktop\Neemann\NG911\NG911_project\NG911_project.gdb'
db = r'C:\Users\eneemann\Desktop\Neemann\NG911\NG911_project\NG911_data_updates.gdb'
#db = r"C:\Users\eneemann\AppData\Roaming\ESRI\ArcGISPro\Favorites\internal@SGID@internal.agrc.utah.gov.sde"

#FC = os.path.join(db, r'EMS_import_from_shapefile_20220211')
#FC = os.path.join(db, r'NG911_Fire_bounds_20220411')
FC = os.path.join(db, r'PSAP_euclid_outside_only')
#FC = os.path.join(db, r'SGID.BOUNDARIES.Municipalities')
#FC = os.path.join(db, r'a_Law_import_from_shapefile_20220216')

#FC = r'C:\Users\eneemann\Desktop\Neemann\NG911\NG911_project\0 NG911_Law_Shapefile_20220216\UT_Law_WGS84_20220216.shp'
FC = r'C:\Users\eneemann\Desktop\Neemann\NG911\NG911_project\0 NG911_Fire_Shapefile_20220705\NG911_Fire_bounds_20220705.shp'

print(f"Working on: {FC}")
arcpy.env.workspace = db
scratch_db = db

if '.sde' in db:
    scratch_db = arcpy.env.scratchGDB
    
print(f'Scratch database: {scratch_db}')

error_table = os.path.join(scratch_db, f'geometry_check_{today}')

arcpy.management.CheckGeometry(FC, error_table, 'ESRI')
print(f'Total count of geometry errors found: {arcpy.management.GetCount(error_table)[0]}')

# Convert neartable to pandas dataframe
error_arr = arcpy.da.TableToNumPyArray(error_table, '*')
error_df = pd.DataFrame(data = error_arr)
print(error_df['PROBLEM'].value_counts())


fields = ['FEATURE_ID', 'PROBLEM']
with arcpy.da.SearchCursor(error_table, fields) as search_cursor:
    print("Looping through rows in error table ...")
    for row in search_cursor:
        print(f'OID {row[0]}: {row[1]}')


print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))


