# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 14:12:41 2021
- Simple script to unzip all files in a directory
@author: eneemann
"""

# Import Libraries
import os
import time
import zipfile

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))
today = time.strftime("%Y%m%d")

# Define variable
data_dir = r"C:\Users\eneemann\Desktop\Zion Lidar"

# Define function
def unzip_files(directory):
    os.chdir(directory)
    zip_list = []
    for file in os.listdir(directory):
        if file.endswith(".zip"):
            zip_list.append(file)
    
    print("List of .zip files:")
    for zip in zip_list:
        print(zip)
    
    for zip in zip_list:
        print("Unzipping {} ...".format(zip))
        with zipfile.ZipFile(zip,"r") as zip_ref:
            zip_ref.extractall(directory)
            

# Call function  
unzip_files(data_dir)


print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))