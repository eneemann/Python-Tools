# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 11:39:29 2019

@author: eneemann

Script to assign attributes to points from point in polygon spatial query
- Tailored to use SGID polygon layers for assignment
- User must update:
    points path
    points field
    polygon path
    polygon field
- function accepts path to points layer and dictionary with field/polygon info
"""

import os
import time
import arcpy

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
print('The script start time is {}'.format(readable_start))

# Update variables below
database = r'\\itwfpcap2\AGRC\agrc\users\eneemann\Geocode_political_districts.gdb'
points = os.path.join(database, "Geocoded_FC_Erik")
sgid_path = r'C:\Users\eneemann\AppData\Roaming\ESRI\ArcGISPro\Favorites\internal@SGID@internal.agrc.utah.gov.sde'

congress_path = os.path.join(sgid_path, 'SGID.POLITICAL.USCongressDistricts2022to2032')
congress_field = 'DISTRICT'
senate_path = os.path.join(sgid_path, 'SGID.POLITICAL.UtahSenateDistricts2022to2032')
senate_field = 'DIST'
house_path = os.path.join(sgid_path, 'SGID.POLITICAL.UtahHouseDistricts2022to2032')
house_field = 'DIST'
school_path = os.path.join(sgid_path, 'SGID.POLITICAL.UtahSchoolBoardDistricts2022to2032')
school_field = 'DIST'

# create dictionary where key is name of field that needs updated in points layer
# format is
        # 'pt_field_name': {'poly_path': path, 'poly_field': field}
poly_dict = {
        'US_CONGRESS': {'poly_path': congress_path, 'poly_field': congress_field},
        'SEN_District': {'poly_path': senate_path, 'poly_field': senate_field},
        'REP_District': {'poly_path': house_path, 'poly_field': house_field}
#        'SCHOOL_Board': {'poly_path': USNG_path, 'poly_field': USNG_field}
        }

###############
#  Functions  #
###############


def assign_poly_attr(pts, polygonDict):
    
    arcpy.env.workspace = os.path.dirname(pts)
    arcpy.env.overwriteOutput = True
    
    for lyr in polygonDict:
        # set path to polygon layer
        polyFC = polygonDict[lyr]['poly_path']
        print (polyFC)
        
        # generate near table for each polygon layer
        neartable = 'in_memory\\near_table'
        arcpy.analysis.GenerateNearTable(pts, polyFC, neartable, '0.1 Meters', 'NO_LOCATION', 'NO_ANGLE', 'CLOSEST')
        
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
        with arcpy.da.UpdateCursor(pts, ['OID@', lyr]) as uCur:
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
    
        # Delete in memory near table
        arcpy.management.Delete(neartable)
    
##########################
#  Call Functions Below  #
##########################

# Call function if script run as main program
if __name__ == '__main__':
    assign_poly_attr(points, poly_dict)


print('Script shutting down ...')
# Stop timer and print end time in UTC
readable_end = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
print('The script end time is {}'.format(readable_end))
print('Time elapsed: {:.2f}s'.format(time.time() - start_time))