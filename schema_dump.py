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

# Point to desired geodatabases and feature classes
geo_db = r"C:\E911\Layton\LaytonGeoValidation_updates.gdb"
county_db = r"C:\E911\Layton\DavisCoDispatchData_working.gdb"

layton = os.path.join(geo_db, "PointsOfInterest")
county = os.path.join(county_db, "CommonPlacePoints")


#classic_db = r'C:\E911\Layton\QuickestRoute.gdb\QuickestRouteWGS_September13'
#QR_streets = os.path.join(classic_db, 'LaytonStreetsSeptember13')
#classic_streets_cad = os.path.join(classic_db, 'TOC_Streets_CAD')

#SGID = r"C:\Users\eneemann\AppData\Roaming\ESRI\ArcGISPro\Favorites\internal@SGID@internal.agrc.utah.gov.sde"
#sgid = os.path.join(SGID, 'SOCIETY.PSAPBoundaries')
#
##NG911 = r"\\itwfpcap2\AGRC\agrc\data\ng911\SpatialStation_live_data\UtahNG911GIS.gdb"
#NG911 = r"C:\Users\eneemann\Desktop\Neemann\NG911\NG911_project\NG911_boundary_work_testing.gdb"
#ng911 = os.path.join(NG911, 'NG911_psap_bound_final_sgid_20210616')

layton_fields = arcpy.ListFields(layton)
print('Layton Field Info:')
for f in layton_fields:
    print(f'Field Name: {f.name}     Field Type: {f.type}     Field Length: {f.length}')
    
county_fields = arcpy.ListFields(county)
print('County Field Info:')
for f in county_fields:
    print(f'Field Name: {f.name}     Field Type: {f.type}     Field Length: {f.length}')
    
#QR_streets_fields = arcpy.ListFields(QR_streets)
#print('QR streets Field Info:')
#for f in QR_streets_fields:
#    print(f'Field Name: {f.name}     Field Type: {f.type}     Field Length: {f.length}')
#    
#classic_streets_cad_fields = arcpy.ListFields(classic_streets_cad)
#print('Classic Streets_CAD Field Info:')
#for f in classic_streets_cad_fields:
#    print(f'Field Name: {f.name}     Field Type: {f.type}     Field Length: {f.length}')
    
    
#sgid_fields = arcpy.ListFields(sgid)
#print('SGID Field Info:')
#for f in sgid_fields:
#    print(f'Field Name: {f.name}     Field Type: {f.type}     Field Length: {f.length}')
#    
#ng911_fields = arcpy.ListFields(ng911)
#print('NG911 Field Info:')
#for f in ng911_fields:
#    print(f'Field Name: {f.name}     Field Type: {f.type}     Field Length: {f.length}')