# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 13:42:56 2020
@author: eneemann

11 May 2021 - script to convert Excel to ArcGIS table
"""

import arcpy
from arcpy import env
import os
import time

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))

staging_db = r"C:\E911\Box Elder CO\BoxElder_Staging.gdb"
env.workspace = staging_db
excel = r"C:\E911\Box Elder CO\BECC Common Place updates_20220406.xlsx"
out_table = os.path.join(staging_db, 'BECC_CPs_20220406')


arcpy.conversion.ExcelToTable(excel, out_table)



print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))