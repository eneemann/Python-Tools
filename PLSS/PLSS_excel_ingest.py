# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 16:12:36 2019
@author: eneemann

Script to plot and project PLSS points from Excel spreadsheet
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

# Provide excel file info
excel_dir = r'C:\Users\eneemann\Desktop\Neemann\PLSS Data'
excel_file = r'Cache_AGRCPnts_Table_export_test.xls'
excel_sheet = 'Cache_Table_export_test'
new_dir = r'C:\Users\eneemann\Desktop\Neemann\PLSS Data\Test'
os.chdir(excel_dir)
spreadsheet = os.path.join(excel_dir, excel_file)

# Create geodatabase
gdb_name = 'Cache_PLSS_new_pts_' + today + '.gdb'
gdb = os.path.join(new_dir, gdb_name)
arcpy.management.CreateFileGDB(new_dir, gdb_name)
env.workspace = gdb
env.overwriteOutput = True

### Outline
# Excel to table
now = time.strftime("%Y%m%d_%H%M%S")
table_name = 'PLSS_new_pts_table'
out_table = os.path.join(gdb, table_name)
arcpy.conversion.ExcelToTable(spreadsheet, out_table, excel_sheet)

# Add new long/lat fields
arcpy.AddField_management(out_table, "new_LONG", "DOUBLE")
arcpy.AddField_management(out_table, "new_LAT", "DOUBLE")

# Function to convert DMS to DD
def dms2dd(dms):
    # receives dms as string input with special characters/spaces and returns float dd
    print(dms)
    # convert direction characters to - signs
    if 'N' in dms:
        dms.replace('N', '').strip()
    elif 'S' in dms:
        dms = '-' + dms.replace('S', '').strip()
    elif 'E' in dms:
        dms.replace('E', '').strip()
    elif 'W' in dms:
        dms = '-' + dms.replace('W', '').strip()
        
    # strip out special characters
    if '°' in dms:
        dms = dms.replace('°', '')
    if "'" in dms:
        dms = dms.replace("'", '')
    if '"' in dms:
        dms = dms.replace('"', '')
    
#    print(dms)
    # split into components
    d = float(dms.split()[0])
    m = float(dms.split()[1])
    s = float(dms.split()[2])
    
    # calculate dd value
    if '-' in dms:
        dd = d - (m/60) -(s/3600)
    else:
        dd = d + (m/60) + (s/3600)
    print(dd)
    
    return dd

# Calculate new field value
fields = ['LONG_NAD83', 'LAT_NAD83', 'new_LONG', 'new_LAT']
with arcpy.da.UpdateCursor(out_table, fields) as uCur:
    print("Looping through rows in FC ...")
    for row in uCur:
        row[2] = dms2dd(row[0])
        row[3] = dms2dd(row[1])
        uCur.updateRow(row)

# XY Event to Point (Using DMS..WGS84???)
spatial_ref = arcpy.SpatialReference(4269)      # NAD 1983
out_pts = os.path.join(gdb, 'PLSS_new_pts_fc')
x_field = 'new_LONG'
y_field = 'new_LAT'
arcpy.management.XYTableToPoint(out_table, out_pts, x_field, y_field, "", spatial_ref)

# Project to state plane N ft
pts_SP_ft = os.path.join(gdb, "PLSS_new_pts_SP_ft")
sr_6626 = arcpy.SpatialReference(6626)       # NAD 1983 2011 StatePlane UT North FIPS 4301 (US ft)
arcpy.management.Project(out_pts, pts_SP_ft, sr_6626)


# Project to state plane meters
pts_SP_m = os.path.join(gdb, "PLSS_new_pts_SP_m")
sr_6620 = arcpy.SpatialReference(6620)       # NAD 1983 2011 StatePlane UT North FIPS 4301 (m)
arcpy.management.Project(pts_SP_ft, pts_SP_m, sr_6620)

# Project to UTM 12 N
pts_UTM_12N = os.path.join(gdb, "PLSS_new_pts_UTM_12N_m")
sr_26912 = arcpy.SpatialReference(26912)       # NAD 1983 UTM Zone 12N (m)
arcpy.management.Project(pts_SP_m, pts_UTM_12N, sr_26912)



print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))