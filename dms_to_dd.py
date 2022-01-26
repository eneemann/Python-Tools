# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 09:57:36 2022
@author: eneemann

Script to convert DMS coordinates to DD
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

# geodatabase
gdb = r'C:\E911\Beaver Co\Beaver_Staging.gdb'
# table
table_name = 'Smithfield_redo_20220126_updated'
table = os.path.join(gdb, table_name)


# Add new long/lat fields, if necessary
#arcpy.AddField_management(out_table, "new_LONG", "DOUBLE")
#arcpy.AddField_management(out_table, "new_LAT", "DOUBLE")

# Function to convert DMS to DD
def dms2dd(dms):
    # receives dms as string input with special characters/spaces and returns float dd
    print(dms)
    # convert direction characters to - signs
    if 'N' in dms:
        dms = dms.replace('N', '').strip()
    elif 'S' in dms:
        dms = '-' + dms.replace('S', '').strip()
    elif 'E' in dms:
        dms = dms.replace('E', '').strip()
    elif 'W' in dms:
        dms = '-' + dms.replace('W', '').strip()
    
    print(dms)    
    # strip out special characters
    if '°' in dms:
        dms = dms.replace('°', ' ')
    if "'" in dms:
        dms = dms.replace("'", ' ')
    if '"' in dms:
        dms = dms.replace('"', ' ')
    
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
fields = ['Longitude', 'Latitude', 'lon_dd', 'lat_dd']
with arcpy.da.UpdateCursor(table, fields) as uCur:
    print("Looping through rows in FC ...")
    for row in uCur:
        row[2] = dms2dd(row[0])
        row[3] = dms2dd(row[1])
        uCur.updateRow(row)


print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))
