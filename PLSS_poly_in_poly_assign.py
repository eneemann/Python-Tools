# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 11:34:29 2019

@author: eneemann

Script to assign attributes an inner polygon based on an outer polygon
- Uses inner polygon centroid for a point-in-polygon spatial query
- User must update the following variables:
    database
    inner_poly
    inner_field
    outer_path
    outer_field
- function accepts a path to inner polygon layer, and a dictionary that holds
"""

import os
import time
import arcpy

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
print('The script start time is {}'.format(readable_start))

# Update variables below
database = r'C:\Users\eneemann\Desktop\Neemann\PLSS Fabric in Pro Test\TestDataWaterRights.gdb'
inner_poly = os.path.join(database, "T5SR1E_Q_QuarterSections_TEST")
inner_field = 'FRSTDIVID'

outer_path = os.path.join(database, 'T5SR1E_Sections')
outer_field = 'FRSTDIVID'

# create dictionary where key is name of field that needs updated in points layer
# format is
        # 'pt_field_name': {'poly_path': path, 'poly_field': field}
poly_dict = {
        inner_field: {'poly_path': outer_path, 'poly_field': outer_field}
        }

###############
#  Functions  #
###############


def assign_poly_attr(inner, polygonDict):
    
    arcpy.env.workspace = os.path.dirname(inner)
    db = os.path.dirname(inner)
    arcpy.env.overwriteOutput = True
    
    for lyr in polygonDict:
        # set path to polygon layer
        polyFC = polygonDict[lyr]['poly_path']
        print (polyFC)

        # Convert inner polygons to centroids for near table calculation
        inner_centroids = os.path.join(db, "inner_centroids")
        arcpy.management.FeatureToPoint(inner, inner_centroids, "INSIDE")

        # Create dictionary to link originals OID to new OIDs
        centroid_link = {}
        # set key as new OID, value as ORIG_FID
        with arcpy.da.SearchCursor(inner_centroids, ['OID@', 'ORIG_FID']) as sCur:
            for row in sCur:
                centroid_link[row[0]] = row[1]       # OID will return ORIG_FID

        # generate near table for each polygon layer
        neartable = 'in_memory\\near_table'
        arcpy.analysis.GenerateNearTable(inner_centroids, polyFC, neartable, '1 Meters', 'NO_LOCATION', 'NO_ANGLE', 'CLOSEST')

        # replace near table's IN_FID with original inner polygon OID's
        # *** this accounts for OID renumbering if there are gaps in OID sequence ***
        with arcpy.da.UpdateCursor(neartable, ['IN_FID']) as Cur:
            for row in Cur:
                # print(f"In near table, replacing {row[0]} with {centroid_link[row[0]]}.")
                row[0] = centroid_link[row[0]]       # IN_FID becomes the ORIG_FID
                Cur.updateRow(row)

        # create dictionaries to store data
        pt_poly_link = {}       # dictionary to link points and polygons by OIDs 
        poly_OID_field = {}     # dictionary to store polygon NEAR_FID as key, polygon field as value
    
        # loop through near table, store point IN_FID (key) and polygon NEAR_FID (value) in dictionary (links two features)
        with arcpy.da.SearchCursor(neartable, ['IN_FID', 'NEAR_FID', 'NEAR_DIST']) as nearCur:
            for row in nearCur:
                pt_poly_link[row[0]] = row[1]       # IN_FID will return NEAR_FID
                # add all polygon OIDs as key in dictionary
                poly_OID_field.setdefault(row[1])
        
        # loop through polygon layer, if NEAR_FID key in poly_OID_field, set value to poly field name
        with arcpy.da.SearchCursor(polyFC, ['OID@', polygonDict[lyr]['poly_field']]) as polyCur:
            for row in polyCur:
                if row[0] in poly_OID_field:
                    poly_OID_field[row[0]] = row[1]
        
        # loop through points layer, using only OID and field to be updated
        with arcpy.da.UpdateCursor(inner, ['OID@', lyr]) as uCur:
            for urow in uCur:
                try:
                    # search for corresponding polygon OID in polygon dictionay (polyDict)
                    if pt_poly_link[urow[0]] in poly_OID_field:
                        # if found, set point field equal to polygon field
                        # IN_FID in pt_poly_link returns NEAR_FID, which is key in poly_OID_field that returns value of polygon field
                        urow[1] =  poly_OID_field[pt_poly_link[urow[0]]]
                except:         # if error raised, just put a blank in the field
                    urow[1] = ''
                uCur.updateRow(urow)
    
        # Delete in temporary table and feature class
        arcpy.management.Delete(neartable)
        arcpy.management.Delete(inner_centroids)
    
##########################
#  Call Functions Below  #
##########################

# Call function if script run as main program
if __name__ == '__main__':
    assign_poly_attr(inner_poly, poly_dict)


print('Script shutting down ...')
# Stop timer and print end time in UTC
readable_end = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
print('The script end time is {}'.format(readable_end))
print('Time elapsed: {:.2f}s'.format(time.time() - start_time))