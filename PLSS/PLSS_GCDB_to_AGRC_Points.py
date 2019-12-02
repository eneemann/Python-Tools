# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 08:52:53 2019
@author: eneemann

Script to pull list of PLSS points and compare to PDFs on web server
"""

import arcpy
from arcpy import env
import os
import time
import pandas as pd

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))
today = time.strftime("%Y%m%d")

# Read in PLSS points from SGID
SGID = r"C:\Users\eneemann\AppData\Roaming\ESRI\ArcGISPro\Favorites\internal@SGID@internal.agrc.utah.gov.sde"
gcdb_pts = os.path.join(SGID, "SGID.CADASTRE.PLSSPoint_GCDB")
agrc_pts = os.path.join(SGID, "SGID.CADASTRE.PLSSPoint_AGRC")
counties = os.path.join(SGID, "SGID.BOUNDARIES.Counties")

test_db = r'C:\Users\eneemann\Desktop\Neemann\PLSS Data\PLSS Web App\TESTING.gdb'
test_pts = os.path.join(test_db, 'TEST_AGRC_Points_' + today)
control_pts = os.path.join(test_db, 'Control_noSGID')

gcdb_fields = arcpy.ListFields(gcdb_pts)
print('GCDB Field Info:')
for f in gcdb_fields:
    print(f'Field Name: {f.name}     Field Type: {f.type}     Field Length: {f.length}')
agrc_fields = arcpy.ListFields(agrc_pts)
print('AGRC Field Info:')
for f in agrc_fields:
    print(f'Field Name: {f.name}     Field Type: {f.type}     Field Length: {f.length}')


# Copy GDCB to Test AGRC Points
if arcpy.Exists(test_pts):
    arcpy.Delete_management(test_pts)
arcpy.management.CopyFeatures(gcdb_pts, test_pts)

# Alter current field names
print("Renaming ERROR fields ...")
arcpy.management.AlterField(test_pts, "ERRORX", "ERRORX_orig")
arcpy.management.AlterField(test_pts, "ERRORY", "ERRORY_orig")
arcpy.management.AlterField(test_pts, "ERRORZ", "ERRORZ_orig")

# Add new, needed fields
print("Adding new ERROR fields with correct type ...")
arcpy.management.AddField(test_pts, "ERRORX", "SHORT")
arcpy.management.AddField(test_pts, "ERRORY", "SHORT")
arcpy.management.AddField(test_pts, "ERRORZ", "SHORT")

print("Adding missing AGRC_Points fields ...")
arcpy.management.AddField(test_pts, "PntLb_Fst3", "TEXT", "", "", 3)
arcpy.management.AddField(test_pts, "PntLb_Lst3", "TEXT", "", "", 3)
arcpy.management.AddField(test_pts, "Coord_Source", "TEXT", "", "", 150)
arcpy.management.AddField(test_pts, "TieSheet_Name", "TEXT", "", "", 40)
#arcpy.management.AddField(test_pts, "LONG_NAD83", "TEXT", "", "", 25)
#arcpy.management.AddField(test_pts, "LAT_NAD83", "TEXT", "", "", 25)
#arcpy.management.AddField(test_pts, "DISPLAY_GRP", "TEXT", "", "", 20)
#arcpy.management.AddField(test_pts, "PointLabel", "TEXT", "", "", 50)
#arcpy.management.AddField(test_pts, "TNUM", "DOUBLE", "38", "8")
#arcpy.management.AddField(test_pts, "RNUM", "DOUBLE", "38", "8")
#arcpy.management.AddField(test_pts, "SNUM", "LONG", "10")
#arcpy.management.AddField(test_pts, "QNUM", "LONG", "10")
print("Adding new Point_Category field ...")
arcpy.management.AddField(test_pts, "Point_Category", "TEXT", "", "", 20)

# Calculate PntLb_Fst3 and PntLb_Lst3
print("Calculating new ERROR fields ...")
update_count = 0
fields = ['ERRORX', 'ERRORY', 'ERRORZ', 'ERRORX_orig', 'ERRORY_orig', 'ERRORZ_orig']
with arcpy.da.UpdateCursor(test_pts, fields) as cursor:
    for row in cursor:
        if row[3] is None:
            row[0] = None
        else:
            row[0] = int(row[3])
            
        if row[4] is None:
            row[1] = None
        else:
            row[1] = int(row[4])
            
        if row[5] is None:
            row[2] = None
        else:
            row[2] = int(row[5])
            
        update_count += 1
        cursor.updateRow(row)
print(f"Total count of updates to ERROR fields: {update_count}")

# Delete no longer needed fields
print("Deleting ERRORX_orig, ERRORY_orig, and ERRORZ_orig fields ...")
arcpy.management.DeleteField(test_pts, ["ERRORX_orig", "ERRORY_orig", "ERRORZ_orig"])

# Calculate new fields
# Calculate PntLb_Fst3 and PntLb_Lst3
print("Calculating PntLb_Fst3 and PntLb_Lst3 fields ...")
update_count = 0
fields = ['POINTLAB', 'PntLb_Fst3', 'PntLb_Lst3']
with arcpy.da.UpdateCursor(test_pts, fields) as cursor:
    for row in cursor:
        row[1] = row[0][0:3]
        row[2] = row[0][3:6]
        update_count += 1
        cursor.updateRow(row)
print(f"Total count of updates to PntLb_Fst3 and PntLb_Lst3: {update_count}")

# Calculate Coord_Source (leave null)

# Calculate TieSheet_Name (check against web share folder)
# First, get list of pdfs from web server
pdf_dir = r"Z:\TieSheets"
os.chdir(pdf_dir)

filenumber = 0
dir_list = os.listdir(pdf_dir)
pdf_dict = {}
total = len(dir_list)
for filename in dir_list:
    pdf_dict.setdefault(filename.split('.pdf')[0])

print("Calculating TieSheet_Name field ...")
update_count = 0
fields = ['POINTID', 'TieSheet_Name']
with arcpy.da.UpdateCursor(test_pts, fields) as cursor:
    for row in cursor:
        if row[0] in pdf_dict:
            row[1] = row[0] + '.pdf'
            update_count += 1
        cursor.updateRow(row)
print(f"Total count of updates to TieSheet_Name field: {update_count}")
    
# Calculate Point_Category (spatial?) - Calculated, Tie Sheet, Monumente Record, Control
# How determine monument record vs. tie sheet w/o knowing tie sheet contents
# First pass - all = 'Calculated'
print("First Pass calculating Point_Category field ...")
update_count = 0
fields = ['Point_Category']
with arcpy.da.UpdateCursor(test_pts, fields) as cursor:
    for row in cursor:
        row[0] = 'Calculated'
        update_count += 1
        cursor.updateRow(row)
print(f"Total count of updates to Point_Category: {update_count}")

# Second pass - if TieSheet_Name: 'Tie Sheet'
print("Second Pass calculating Point_Category field ...")
where = "TieSheet_Name LIKE '%.pdf'"
update_count = 0
fields = ['Point_Category', 'TieSheet_Name']
with arcpy.da.UpdateCursor(test_pts, fields) as cursor:
    for row in cursor:
        if '.pdf' in str(row[1]):
            row[0] = 'Tie Sheet'
            update_count += 1
        cursor.updateRow(row)
print(f"Total count of updates to Point_Category: {update_count}")

# Third pass - Spatial selection, if w/i 2m of control: 'Control'
print("Third Pass calculating Point_Category field ...") 
# Need to make a layer
arcpy.management.MakeFeatureLayer(test_pts, "test_pts_lyr")
print("test_pts_lyr feature count: {}".format(arcpy.GetCount_management("test_pts_lyr")[0]))

# Select all features within 2m of control points
arcpy.management.SelectLayerByLocation("test_pts_lyr", "WITHIN_A_DISTANCE_GEODESIC", control_pts,
                                                     "2 meters", "NEW_SELECTION")
# Add note that these points are likely duplicates
update_count = 0
fields = ['Point_Category']
with arcpy.da.UpdateCursor("test_pts_lyr", fields) as cursor:
    for row in cursor:
        row[0] = 'Control'
        update_count += 1
        cursor.updateRow(row)
print(f"Total count of updates to Point_Category: {update_count}")
        

print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))