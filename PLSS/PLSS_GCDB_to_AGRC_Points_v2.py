# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 08:52:53 2019
@author: eneemann

Script to pull list of PLSS points and compare to PDFs on web server
"""

import arcpy
import os
import time

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
county_list = ['DAVIS', 'DUCHESNE', 'SALT LAKE', 'UINTAH', 'UTAH', 'WASATCH', 'WEBER']

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
arcpy.management.AddField(test_pts, "Coord_Source", "TEXT", "", "", 150)
arcpy.management.AddField(test_pts, "TieSheet_Name", "TEXT", "", "", 40)
arcpy.management.AddField(test_pts, "DISPLAY_GRP", "TEXT", "", "", 20)
arcpy.management.AddField(test_pts, "LONG_NAD83", "TEXT", "", "", 25)
arcpy.management.AddField(test_pts, "LAT_NAD83", "TEXT", "", "", 25)

print("Adding new Point_Category fields ...")
arcpy.management.AddField(test_pts, "Point_Category", "TEXT", "", "", 20)
arcpy.management.AddField(test_pts, "isMonument", "TEXT", "", "", 3)
arcpy.management.AddField(test_pts, "isControl", "TEXT", "", "", 3)
arcpy.management.AddField(test_pts, "County", "TEXT", "", "", 20)

# Calculate point geometry in NAD 83
print("Calculating geometry fields ...")
spatial_ref = arcpy.SpatialReference(4269)      # NAD 1983
#arcpy.management.CalculateGeometryAttributes(test_pts, "POINT_X", "", "", spatial_ref)
#arcpy.management.CalculateGeometryAttributes(test_pts, "POINT_Y", "", "", spatial_ref)
arcpy.management.AddGeometryAttributes(test_pts, "POINT_X_Y_Z_M", "", "", spatial_ref)

# Calculate Error Fields
print("Copying geometry fields to LAT/LONG ...")
update_count = 0
fields = ['POINT_X', 'LONG_NAD83', 'POINT_Y', 'LAT_NAD83']
with arcpy.da.UpdateCursor(test_pts, fields) as cursor:
    for row in cursor:
        row[1] = str(row[0])
        row[3] = str(row[2])        
        update_count += 1
        cursor.updateRow(row)
print(f"Total count of updates to LAT/LONG fields: {update_count}")

# Delete POINT_X and POINT_Y fields
print("Deleting POINT_X and POINT_Y ...")
arcpy.management.DeleteField(test_pts, "POINT_X")
arcpy.management.DeleteField(test_pts, "POINT_Y")

# Calculate Error Fields
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
fields = ['POINTID', 'TieSheet_Name', 'DISPLAY_GRP']
with arcpy.da.UpdateCursor(test_pts, fields) as cursor:
    for row in cursor:
        if row[0] in pdf_dict:
            row[1] = row[0] + '.pdf'
            row[2] = 'Zoomed out'
            update_count += 1
#        else:
#            row[2] = 'Zoomed in'
#            update_count += 1
        cursor.updateRow(row)
print(f"Total count of updates to TieSheet_Name field: {update_count}")
    
# Calculate Point_Category (spatial?) - Calculated, Tie Sheet, Monument Record, Control
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
            row[0] = 'Monument Record'
            update_count += 1
        cursor.updateRow(row)
print(f"Total count of updates to Point_Category: {update_count}")

# Third pass - Spatial selection, if w/i 2m of control: 'Control'
print("Third Pass calculating Point_Category field ...") 
# Need to make a layer
if arcpy.Exists("test_pts_lyr"):
    arcpy.Delete_management("test_pts_lyr")
arcpy.management.MakeFeatureLayer(test_pts, "test_pts_lyr")
print("test_pts_lyr feature count: {}".format(arcpy.GetCount_management("test_pts_lyr")[0]))

# Select all features within 2m of control points
arcpy.management.SelectLayerByLocation("test_pts_lyr", "WITHIN_A_DISTANCE", control_pts,
                                                     "2 meters", "NEW_SELECTION")
# Update the field
update_count = 0
fields = ['Point_Category']
with arcpy.da.UpdateCursor("test_pts_lyr", fields) as cursor:
    for row in cursor:
        row[0] = 'Control'
        update_count += 1
        cursor.updateRow(row)
print(f"Total count of updates to Point_Category: {update_count}")

# Calculate isMonument and isControl fields; allows symbology to be stacked
print("Calculating isMonument and isControl fields ...")
update_count = 0
fields = ['isMonument', 'isControl', 'TieSheet_Name', 'Point_Category']
with arcpy.da.UpdateCursor(test_pts, fields) as cursor:
    for row in cursor:
        # Use TieSheet_Name to assign isMonument field
        if '.pdf' in str(row[2]):
            row[0] = 'yes'
            update_count += 1
        else:
            row[0] = 'no'
            update_count += 1
            
        # Use Point_Category to assign isControl field
        if row[3] == 'Control':
            row[1] = 'yes'
            update_count += 1
        else:
            row[1] = 'no'
            update_count += 1
                    
        cursor.updateRow(row)
print(f"Total count of updates to isMonument and isControl: {update_count}")

print("Updating DISPLAY_GRP field ...")
update_count = 0
fields = ['POINTID', 'TieSheet_Name', 'DISPLAY_GRP']
with arcpy.da.UpdateCursor(test_pts, fields) as cursor:
    for row in cursor:
        if row[0] in pdf_dict:
            row[2] = 'Zoomed out'
            update_count += 1
        else:
            row[2] = 'Zoomed in'
            update_count += 1
        cursor.updateRow(row)
print(f"Total count of updates to TieSheet_Name field: {update_count}")
        
# Update TieSheet_Name for counties with data on their website
# Loop through county_list and perform update for each county
for county in range(len(county_list)):
    # Select all features within county_lyr boundaries
    query = f"NAME = '{county_list[county]}'"
    print(f'County SQL Query:   {query}')
    lyr_name = f"county_lyr_{county}"
    arcpy.management.MakeFeatureLayer(counties, lyr_name, query)
    print("county_lyr feature count: {}".format(arcpy.GetCount_management(lyr_name)[0]))
    selection = arcpy.management.SelectLayerByLocation("test_pts_lyr", "INTERSECT", lyr_name,
                                                         "", "NEW_SELECTION")
    print(f"Calculating TieSheet_Name field for {county_list[county]} ...") 
    update_count = 0
    update_count_1 = 0
    fields = ['TieSheet_Name', 'County']
    with arcpy.da.UpdateCursor(selection, fields) as cursor:
        for row in cursor:
            row[1] = county_list[county]
            update_count += 1
            if '.pdf' not in str(row[0]):
                row[0] = county_list[county]
                update_count_1 += 1
            cursor.updateRow(row)
    print(f"Total count of updates to County field: {update_count}")
    print(f"Total count of updates to TieSheet_Name field: {update_count_1}")


print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))