# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 14:02:53 2022
@author: eneemann

Script to pull list of MRRC points from G Drive update attributes
in the point layer for the PLSS Web App.
"""

import arcpy
import os
import time
import shutil

# Start timer and print start time
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print("The script start time is {}".format(readable_start))
today = time.strftime("%Y%m%d")

# Set up variables
mrrc_db = r'C:\GIS Data\PLSS\PLSS_update_20250307.gdb'
mrrc_pts = os.path.join(mrrc_db, 'PLSS_Monuments_MRRC_updates')

# Calculate new fields
# First, get list of pdfs from MRRC folder on G Drive
# pdf_dir = r"M:\Shared drives\AGRC Projects\PLSS\MRRC Tie Sheets 2016-2022\Erik_temp"
pdf_dir = r"M:\Shared drives\UGRC Projects\PLSS\Megafolder (ready to be processed)"
os.chdir(pdf_dir)

filenumber = 0
dir_list = os.listdir(pdf_dir)
pdf_dict = {}
total = len(dir_list)

for filename in dir_list:
    basename = filename.split('.pdf')[0]
    pdf_dict.setdefault(basename)

# Calculate fields based on PDFs in MRRC folder
print("Calculating MRRC fields ...")
update_count = 0
already_mrrc = 0
already_monument = 0

fields = ['point_id', 'mrrc', 'monument', 'point_category']
with arcpy.da.UpdateCursor(mrrc_pts, fields) as cursor:
    for row in cursor:
        if row[0] in pdf_dict:
            # update mrrc field
            if row[1] is not None and row[1] == 1:
                already_mrrc += 1
            else:
                row[1] = 1
            # update monument field
            if row[2] is not None and row[2] == 1:
                already_monument += 1
            else:
                row[2] = 1
            # update point_category field
            row[3] = 'Monument Record'
            update_count += 1
        else:
           pass
        
        cursor.updateRow(row)


print(f"Total count of points already showing 'mrrc': {already_mrrc}")
print(f"Total count of points already showing 'monument': {already_monument}")
print(f"Total count of MRRC updates to points: {update_count}")


print("Script shutting down ...")
# Stop timer and print end time
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))
