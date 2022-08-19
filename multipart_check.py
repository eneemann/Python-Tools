# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 15:11:45 2021
@author: eneemann

Script to identify and list multipart features
"""

import arcpy
import os
import time

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))

######################
#  Set up variables  #
######################

today = time.strftime("%Y%m%d")
db = r"C:\Users\eneemann\Desktop\Neemann\Vista\Political_Snapping_20220202.gdb"
FC = os.path.join(db, r'Topo_checks\VistaBallotAreas_Proposed_update_20220202_1')
arcpy.env.workspace = db


def multipart_check(fc):
    multi_count = 0
    multi_oids = []
    fields = ['OID@', 'SHAPE@']
    with arcpy.da.SearchCursor(fc, fields) as search_cursor:
        print("Looping through rows in FC to check for multipart features ...")
        for row in search_cursor:
            shape_obj = row[1]
            oid = row[0]
            # print(shape_obj)
            if shape_obj.partCount > 1:
                multi_oids.append(oid)
                multi_count += 1
                print(f'part count of OID {oid}: {shape_obj.partCount}')
                
    print(f'Total count of multipart features: {multi_count}')
    print('Multipart OIDs:')
    for o in multi_oids:
        print(o)
            

##########################
#  Call Functions Below  #
##########################

multipart_check(FC)

print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))