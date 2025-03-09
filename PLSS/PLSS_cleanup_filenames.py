# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 14:02:53 2022
@author: eneemann

Script to pull list of MRRC points from G Drive update attributes
in the point layer for the PLSS Web App.
"""

import arcpy
import os
import time
import shutil

# Start timer and print start time
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print("The script start time is {}".format(readable_start))
today = time.strftime("%Y%m%d")

# Set up variables
mrrc_db = r'C:\GIS Data\PLSS\PLSS_update_20250307.gdb'
mrrc_pts = os.path.join(mrrc_db, 'PLSS_Monuments_MRRC_updates')

# Calculate new fields
# First, get list of pdfs from MRRC folder on G Drive
# pdf_dir = r"M:\Shared drives\AGRC Projects\PLSS\MRRC Tie Sheets 2016-2022\Erik_temp"
pdf_dir = r"M:\Shared drives\UGRC Projects\PLSS\Megafolder (ready to be processed)"
fix_dir = r"M:\Shared drives\UGRC Projects\PLSS\Megafolder (fixes needed)"
os.chdir(pdf_dir)

filenumber = 0
dir_list = os.listdir(pdf_dir)
pdf_dict = {}
total = len(dir_list)

bad_characters = ['(', ')', '__', '.', '-', ' ']
bad_count = 0

for filename in dir_list:
    basename = filename.split('.pdf')[0]
    pdf_dict.setdefault(basename)

    if len(basename) != 22:
        print(f'WARNING: filename length is not 22:   {basename}')

    # bad = False

    # for item in bad_characters:
    #     if item in basename:
    #         bad = True
            
    # if bad:
    #     print(f'WARNING: bad character found in {basename}')
    #     bad_count += 1
        
        # move bad filenames to another folder
        # source = os.path.join(pdf_dir, filename)
        # destination = os.path.join(fix_dir, filename)
        # shutil.move(source, destination)

print(f"Total count of odd filenames found: {bad_count}")
print(f"files moved to: {fix_dir}")

print("Script shutting down ...")
# Stop timer and print end time
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))