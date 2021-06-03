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
geo_db = r"C:\E911\TOC\TOC_Geovalidation_WGS84.gdb"
streets = os.path.join(geo_db, "Streets")
streets_map = os.path.join(geo_db, "Streets_Map")


classic_db = r'C:\E911\TOC\TOC_Spillman_WGS_84.gdb'
classic_streets = os.path.join(classic_db, 'TOC_Streets')
classic_streets_cad = os.path.join(classic_db, 'TOC_Streets_CAD')

streets_fields = arcpy.ListFields(streets)
print('Streets Field Info:')
for f in streets_fields:
    print(f'Field Name: {f.name}     Field Type: {f.type}     Field Length: {f.length}')
    
streets_map_fields = arcpy.ListFields(streets_map)
print('Streets_Map Field Info:')
for f in streets_map_fields:
    print(f'Field Name: {f.name}     Field Type: {f.type}     Field Length: {f.length}')
    
classic_streets_fields = arcpy.ListFields(classic_streets)
print('Classic Streets Field Info:')
for f in classic_streets_fields:
    print(f'Field Name: {f.name}     Field Type: {f.type}     Field Length: {f.length}')
    
classic_streets_cad_fields = arcpy.ListFields(classic_streets_cad)
print('Classic Streets_CAD Field Info:')
for f in classic_streets_cad_fields:
    print(f'Field Name: {f.name}     Field Type: {f.type}     Field Length: {f.length}')