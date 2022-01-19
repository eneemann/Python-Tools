# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 15:11:45 2021
@author: eneemann

Script to identify and list curvepart features
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
db = r"L:\agrc\data\ng911\Submitted_to_911DM\UtahNG911GIS_20220106.gdb"
FC = os.path.join(db, r'PSAP_Boundaries')
arcpy.env.workspace = db


def curve_check(fc):
    curve_count = 0
    curve_oids = []
    fields = ['OID@', 'SHAPE@JSON']
    with arcpy.da.SearchCursor(fc, fields) as search_cursor:
        print("Looping through rows in FC to check for true curve features ...")
        for row in search_cursor:
            j = row[1]
            oid = row[0]
            if 'curve' in j:
                curve_oids.append(oid)
                curve_count += 1
                print(f'OID {oid} has a curve!')
                
    print(f'Total count of curve features: {curve_count}')
    print('curve OIDs:')
    for o in curve_oids:
        print(o)
            

##########################
#  Call Functions Below  #
##########################

curve_check(FC)

# 2nd version of curve check from StackExchange: https://gis.stackexchange.com/questions/37793/identifying-true-curves-arcs-in-arcmap/179155#179155
# This version doesn't apper to work
# import json
# geometries = arcpy.CopyFeatures_management(FC, arcpy.Geometry())
# for g in geometries:
#     j = json.loads(g.JSON)
#     if 'curve' in j:
#         print("You have true curves!")
#     else:
#         print("No curves here")


print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))