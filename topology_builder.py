# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:09:25 2026

@author: eneemann
Script to build, validate, and report the results of a polygon topology
- built with Google Gemini
"""

import os
import time
import arcpy

# start timer and print start time
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print("The script start time is {}".format(readable_start))
today = time.strftime("%Y%m%d")
now = time.strftime("%Y%m%d_%H%M%S")


# --- 1. Define Paths and Inputs ---
# UPDATE these two variable to point to your data and desired output location
input_fc = r"C:\GIS Data\Temp.gdb\polygons_to_check"
output_folder = r"C:\Temp"

gdb_name = f"Topology_Check_{now}.gdb"
dataset_name = "Topo_Dataset"
topology_name = "Polygon_Topology"

# Construct paths
gdb_path = os.path.join(output_folder, gdb_name)
dataset_path = os.path.join(gdb_path, dataset_name)
topology_path = os.path.join(dataset_path, topology_name)

arcpy.env.overwriteOutput = True

# --- 2. Create GDB and Feature Dataset ---
print("Step 1: Creating File Geodatabase...")
arcpy.management.CreateFileGDB(output_folder, gdb_name)

print("Step 2: Acquiring spatial reference from input data...")
spatial_ref = arcpy.Describe(input_fc).spatialReference

print("Step 3: Creating Feature Dataset...")
arcpy.management.CreateFeatureDataset(gdb_path, dataset_name, spatial_ref)

# --- 3. Move Data and Set Up Topology Containers ---
print("Step 4: Importing feature class into the dataset...")
fc_name = os.path.basename(input_fc)
target_fc = os.path.join(dataset_path, fc_name)
arcpy.management.CopyFeatures(input_fc, target_fc)

print("Step 5: Building Topology container...")
arcpy.management.CreateTopology(dataset_path, topology_name)

print("Step 6: Associating Feature Class with the Topology...")
# Parameters: input topology, target feature class, rank, coordinate class rank
arcpy.management.AddFeatureClassToTopology(topology_path, target_fc, 1, 1)

# --- 4. Establish QA/QC Rules ---
print("Step 7: Adding 'Must Not Overlap' rule...")
arcpy.management.AddRuleToTopology(topology_path, "Must Not Overlap (Area)", target_fc)

print("Step 8: Adding 'Must Not Have Gaps' rule...")
arcpy.management.AddRuleToTopology(topology_path, "Must Not Have Gaps (Area)", target_fc)

# --- 5. Validate and Audit Results ---
print("Step 9: Validating Topology (Analyzing geometric errors)...")
arcpy.management.ValidateTopology(topology_path)

print("Step 10: Exporting topology errors to count them...")
error_base_name = "topo_export"
arcpy.management.ExportTopologyErrors(topology_path, dataset_path, error_base_name)

# ExportTopologyErrors creates 3 specific feature classes inside the dataset:
# point errors, line errors (gaps), and polygon errors (overlaps)
err_point = os.path.join(dataset_path, f"{error_base_name}_point")
err_line = os.path.join(dataset_path, f"{error_base_name}_line")
err_poly = os.path.join(dataset_path, f"{error_base_name}_poly")

# Quick helper function to get feature counts safely
def count_errors(layer_path):
    if arcpy.Exists(layer_path):
        return int(arcpy.management.GetCount(layer_path)[0])
    return 0

overlap_errors = count_errors(err_poly)
gap_errors = count_errors(err_line)
point_errors = count_errors(err_point)
total_errors = overlap_errors + gap_errors + point_errors

# --- 6. Print Summary Report ---
print("\n" + "="*40)
print("           TOPOLOGY AUDIT REPORT        ")
print("="*40)
print(f"Target Feature Class: {fc_name}")
print(f"Overlap Errors (Polygons): {overlap_errors}")
print(f"Gap Errors (Lines):        {gap_errors}")
print(f"Point Errors:              {point_errors}")
print("-"*40)
print(f"TOTAL CRITICAL ERRORS:     {total_errors}")
print("="*40)

print("Script shutting down ...")
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))
