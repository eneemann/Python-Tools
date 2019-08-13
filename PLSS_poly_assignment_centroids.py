# -*- coding: utf-8 -*-
'''
Created on Fri Aug  9 08:27:12 2019
@author: eneemann
Script to assign attributes in PLSS quarter quarters from pt in poly spatial query
'''

import os
import time
import arcpy

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
print('The script start time is {}'.format(readable_start))


###############
#  Functions  #
###############


def assign_poly_attr(db, inner_poly, inner_field, outer_poly, outer_field):
    # Convert inner polygons to centroids for near table calculation
    inner_centroids = os.path.join(db, "inner_centroids")
    arcpy.management.FeatureToPoint(inner_poly, inner_centroids, "INSIDE")
    
    
    # Generate near table from inner polygons that grabs only the nearest outer polygon
    nearTBL = os.path.join(db, "nearTable")
    arcpy.analysis.GenerateNearTable(inner_centroids, outer_poly, nearTBL, '1 Meters', 'NO_LOCATION', 'NO_ANGLE', 'CLOSEST')
    
    # For each row in near table, find inner polygon with 'IN_FID' and outer polygon with 'NEAR_FID'
    with arcpy.da.SearchCursor(nearTBL, ['IN_FID', 'NEAR_FID', 'NEAR_DIST']) as nCur:
        count = 0
        print("Looping through near table ...")
        for nrow in nCur:
            where_clause1 = f"OBJECTID = {nrow[0]}"    # inner poly OID = 'IN_FID'
            with arcpy.da.UpdateCursor(inner_poly, [inner_field], where_clause1) as uCur:
                for urow in uCur:
                    where_clause2 = f"OBJECTID = {nrow[1]}"    # outer poly OID = 'NEAR_FID'
                    with arcpy.da.SearchCursor(outer_poly, [outer_field], where_clause2) as sCur:
                        for srow in sCur:
                            urow[0] = srow[0]
                    uCur.updateRow(urow)
            count += 1
    
    # Delete near table and centroid feature classes (comment these lines out when debugging)
    arcpy.management.Delete(nearTBL)
    arcpy.management.Delete(inner_centroids)
    
##########################
#  Call Functions Below  #
##########################

# Update variables below
database = r'C:\Users\eneemann\Desktop\Neemann\PLSS Fabric in Pro Test\TestDataWaterRights.gdb'
section_fc = 'T5SR1E_Sections'
section_field = 'FRSTDIVID'
qtr_qtr_fc =  'T5SR1E_Q_QuarterSections'
qtr_field = 'FRSTDIVID'
sections = os.path.join(database, section_fc)
qtr_qtrs = os.path.join(database, qtr_qtr_fc)


# Call function if script run as main program
if __name__ == '__main__':
    assign_poly_attr(database, qtr_qtrs, qtr_field, sections, section_field)


print('Script shutting down ...')
# Stop timer and print end time in UTC
readable_end = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
print('The script end time is {}'.format(readable_end))
print('Time elapsed: {:.2f}s'.format(time.time() - start_time))