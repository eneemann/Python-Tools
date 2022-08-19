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
import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))
today = time.strftime("%Y%m%d")

# Define variables
gdb = r'C:\Users\eneemann\Desktop\Neemann\PLSS Data\Test\Test_Data_RebuildingQuarterSections_EMN.gdb'
quarter_quarters = os.path.join(gdb, 'SGID_PLSS_QuarterQuarters_GCDB')
working_QQs = os.path.join(gdb, f'QQs_working_{today}')
new_quarters = os.path.join(gdb, f'quarters_output_{today}')

env.workspace = gdb
env.overwriteOutput = True
env.qualifiedFieldNames = False

# Copy original data into working layer geodatabase
arcpy.management.CopyFeatures(quarter_quarters, working_QQs)

# Add new field for concatenated values and calculate the values
arcpy.management.AddField(working_QQs, "QSEC", "TEXT", "", "", 5)
arcpy.management.AddField(working_QQs, "FRSTDIVID_QSEC", "TEXT", "", "", 50)

# Calculate new field value
# Currently, the FRSTDIVID (section) gets calculated into the concatenated field
# The means each lot within a section will get dissolved together
# Only calculate where QSEC IS NOT NULL to recalc unique numbers on lots later
update_count = 0
#query = 'OBJECTID < 100'
fields = ['FRSTDIVID', 'QSEC', 'FRSTDIVID_QSEC', 'SECDIVLAB']
with arcpy.da.UpdateCursor(working_QQs, fields) as uCur:
    print("Calculating concatenated field ...")
    for row in uCur:
#        print(len(row[3]))
        if row[3] is not None and len(row[3]) > 3:
            row[1] = row[3][-2:]
        elif row[3] is not None and len(row[3]) == 3:
            row[1] = row[3]
        else:
            row[1] = None
        if row[0] is None: row[0] = ''
        if row[1] is None: row[1] = ''
        row[2] = row[0] + row[1]
        update_count += 1
        uCur.updateRow(row)
    print(f"Count of updates to {fields[2]} is: {update_count}")
        
## Recalculate new field value for NULLs remaining after first calculation
## Now calculate them as a unique values (1 to n) so they don't get dissolved in the next step
#update_count = 0
#query = "FRSTDIVID_QSEC IS NULL OR FRSTDIVID_QSEC IN ('', ' ', '  ')"
#fields = ['FRSTDIVID_QSEC']
#with arcpy.da.UpdateCursor(working_QQs, fields, query) as uCur:
#    print("Recalculating concatenated field on NULLs ...")
#    rec = 0
#    pStart = 1
#    pInterval = 1
#    for row in uCur:
#        if rec == 0:
#            rec = pStart
#        else:
#            rec += pInterval
#        
#        row[0] = str(rec)
#        update_count += 1
#        uCur.updateRow(row)
#    print(f"Count of remaining NULLS updated in {fields[0]} is: {update_count}")
        

# Dissolve QQs in quarters on the new field
arcpy.management.Dissolve(working_QQs, new_quarters, 'FRSTDIVID_QSEC')

# Join original fields back to the dissolved data using the FRSTDIVID_QSEC field
# Use spatial dataframe to de-duplicate the rows and perform the join, then return to FC
# Convert feature class to spatial data frame
print("Converting working data to spatial dataframe ...")
working_QQs_sdf = pd.DataFrame.spatial.from_featureclass(working_QQs)
new_df = pd.DataFrame.spatial.from_featureclass(new_quarters)


# Drop the unneeded columns and deduplicate original data
#working_QQs_sdf.drop(['OBJECTID', 'SECDIVLAB'], 1, inplace=True)
working_QQs_sdf.drop(['OBJECTID', 'SECDIVID', 'SECDIVNO', 'SECDIVSUF', 'SECDIVTYP', 'SECDIVTXT', 'ACRES', 'SECDIVLAB', 'SHAPE'], 1, inplace=True)
print(f"Working QQs size including duplicates: {working_QQs_sdf.shape[0]}")
no_dups = working_QQs_sdf.drop_duplicates()
#no_dups.drop(['SHAPE'], 1, inplace=True)

print(f"Working QQs size without duplicates: {no_dups.shape[0]}")
print(f"New quarters size : {new_df.shape[0]}")

# Join data from original (no_dups) to new quarters
print("Joining original fields back to the quarters ...")
new_joined = new_df.merge(no_dups, how='left', left_on='FRSTDIVID_QSEC', right_on='FRSTDIVID_QSEC')
#new_joined.drop(['OBJECTID_x', 'OBJECTID_y'], 1)
new_joined.drop(['OBJECTID'], 1)
#new_joined.set_geometry('SHAPE_y')
new_joined_shapes = GeoAccessor.from_df(new_joined, geometry_column='SHAPE')

# Export final SDF to FC
new_quarters_final = os.path.join(gdb, f'quarters_output_{today}_final')
new_joined_shapes.spatial.to_featureclass(location=new_quarters_final)

arcpy.management.CalculateGeometryAttributes(new_quarters_final, [['ACRES', 'AREA']], area_unit='ACRES')


print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))
