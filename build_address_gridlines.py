# -*- coding: utf-8 -*-
"""
Created on Thu May 13 14:13:29 2021

@author: eneemann

EMN: Initial script to build address grid lines based on user input
"""

import arcpy
import os
import time
import numpy as np

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print(f"The script start time is {readable_start}")
today = time.strftime("%Y%m%d")

######################
#  Define Variables  #
######################
avg_block_distance = {}     # initialize dictionary to hold x/y distances
sr = arcpy.SpatialReference(26912)      # spatial reference

# Enter grid parameters in NAD 1983 UTM 12N (EPSG: 26912), units as meters
origin_x = 424796.3         # meters
origin_y = 4513534.7        # meters
num_blocks = 35
avg_block_distance['x'] = 241.4     # east-west distance in meters (SLC is 792 ft = 241.4 m)
avg_block_distance['y'] = 235       # north-south distance in meters (SLC is about 235 m)

# Enter grid name and root directory
grid_name = 'SLC'
work_dir = r"C:\Temp"

# Set database and feature class paths
working_db = f"Address_Grid_{today}.gdb"
db_path = os.path.join(work_dir, working_db)
block_dist = str(avg_block_distance['x']).split('.')[0]
out_name = f'{grid_name}_grid_{block_dist}m_{num_blocks}blocks'
out_path = os.path.join(db_path, out_name)

######################
#  Define Functions  #
######################

def build_files_folders():
    # Create output geodatabase and feature class  
    if not arcpy.Exists(db_path):
        print(f"Creating {db_path} ...")
        arcpy.management.CreateFileGDB(work_dir, working_db)
        
    if not arcpy.Exists(out_path):
        print(f"Creating {out_path} ...")
        arcpy.management.CreateFeatureclass(db_path, out_name, 'POLYLINE', spatial_reference=sr)
    
    arcpy.management.AddField(out_path, "Label", "TEXT", "", "", 20)

    
def build_center_axes(orig_x, orig_y, num, dist):
    # Calculate axes coordinates and store in dictionary
    ax = {}
    ax['NS_start_x'] = orig_x
    ax['NS_start_y'] = orig_y - num*dist['y']
    ax['NS_end_x'] = orig_x
    ax['NS_end_y'] = orig_y + num*dist['y']
    ax['EW_start_x'] = orig_x - num*dist['x']
    ax['EW_start_y'] = orig_y
    ax['EW_end_x'] = orig_x + num*dist['x']
    ax['EW_end_y'] = orig_y
    
    # Build north-south axis line
    NS_array = arcpy.Array([arcpy.Point(ax['NS_start_x'], ax['NS_start_y']),
                     arcpy.Point(ax['NS_end_x'], ax['NS_end_y'])])
    NS_shape = arcpy.Polyline(NS_array, sr) 
    NS_values = ['N-S Axis', NS_shape]
    
    # Build east-west axis line
    EW_array = arcpy.Array([arcpy.Point(ax['EW_start_x'], ax['EW_start_y']),
                            arcpy.Point(ax['EW_end_x'], ax['EW_end_y'])])
    EW_shape = arcpy.Polyline(EW_array, sr) 
    EW_values = ['E-W Axis', EW_shape]
    
    # # build north-south axis line
    # NS_array = arcpy.Array([arcpy.Point(orig_x, orig_y - num*dist),
    #                  arcpy.Point(orig_x, orig_y + num*dist)])
    # NS_shape = arcpy.Polyline(NS_array, sr) 
    # NS_values = ['N-S Axis', NS_shape]
    
    # # build east-west axis line
    # EW_array = arcpy.Array([arcpy.Point(orig_x - num*dist, orig_y),
    #                  arcpy.Point(orig_x + num*dist, orig_y)])
    # EW_shape = arcpy.Polyline(EW_array, sr) 
    # EW_values = ['E-W Axis', EW_shape]
        
    fields = ['Label', 'SHAPE@']
    
    # Add lines to FC
    print('Adding center axes to feature class ...')
    with arcpy.da.InsertCursor(out_path, fields) as insert_cursor:
        insert_cursor.insertRow(NS_values)
        insert_cursor.insertRow(EW_values)
        
    return ax
        
        

def build_N_S_line(ax, block, dist):
    # Build line to the east
    E_array = arcpy.Array([arcpy.Point(ax['NS_start_x'] + block*dist, ax['NS_start_y']),
                     arcpy.Point(ax['NS_end_x'] + block*dist, ax['NS_end_y'])])
    E_shape = arcpy.Polyline(E_array, sr) 
    E_values = [f'{block*100} E', E_shape]
    
    # Build line to the west
    W_array = arcpy.Array([arcpy.Point(ax['NS_start_x'] - block*dist, ax['NS_start_y']),
                     arcpy.Point(ax['NS_end_x'] - block*dist, ax['NS_end_y'])])
    W_shape = arcpy.Polyline(W_array, sr) 
    W_values = [f'{block*100} W', W_shape]
    
    fields = ['Label', 'SHAPE@']
    
    # Add lines to FC
    print('Adding north-south lines to feature class ...')
    with arcpy.da.InsertCursor(out_path, fields) as insert_cursor:
        insert_cursor.insertRow(E_values)
        insert_cursor.insertRow(W_values)
    
                                            
def build_E_W_line(ax, block, dist):
    # Build line to the north
    N_array = arcpy.Array([arcpy.Point(ax['EW_start_x'], ax['EW_start_y'] + block*dist),
                     arcpy.Point(ax['EW_end_x'], ax['EW_end_y'] + block*dist)])
    N_shape = arcpy.Polyline(N_array, sr) 
    N_values = [f'{block*100} N', N_shape]
    
    # Build line to the south
    S_array = arcpy.Array([arcpy.Point(ax['EW_start_x'], ax['EW_start_y'] - block*dist),
                     arcpy.Point(ax['EW_end_x'], ax['EW_end_y'] - block*dist)])
    S_shape = arcpy.Polyline(S_array, sr) 
    S_values = [f'{block*100} S', S_shape]
    
    fields = ['Label', 'SHAPE@']
    
    # Add lines to FC
    print('Adding east-west lines to feature class ...')
    with arcpy.da.InsertCursor(out_path, fields) as insert_cursor:
        insert_cursor.insertRow(N_values)
        insert_cursor.insertRow(S_values)
    
####################
#  Call Functions  #
####################
    
build_files_folders()
axes = build_center_axes(origin_x, origin_y, num_blocks, avg_block_distance)

for i in np.arange(1, num_blocks +1):
    print(f'Working on iteration: {i}')
    # build_N_S_line(axes, i, avg_block_distance)
    # build_E_W_line(axes, i, avg_block_distance)
    build_N_S_line(axes, i, avg_block_distance['x'])
    build_E_W_line(axes, i, avg_block_distance['y'])

print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print(f"The script end time is {readable_end}")
print(f"Time elapsed: {time.time() - start_time:.2f}s")
