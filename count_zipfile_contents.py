# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 15:21:57 2020

@author: eneemann

This script is used to count the number of files within zipped folder of a directory
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


#-----------------------Start Main Code------------------------#

# Set up variables
data_dir = r"G:\Shared drives\AGRC Projects\PLSS Fabric\Data\CountyData\Rich\Rich County Tie Sheets"


#-----------------------Functions------------------------#

def count_files(directory, total=0):
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
            count = len(zip_ref.infolist())
            total += count
            print(f'adding {count} to pdf_total')
            
    return total


#-----------------------Call Functions-----------------------#

print(f'Counting contents of zipped files in {data_dir} ...')
pdf_total = count_files(data_dir)

print(f'Total number of PDF files: {pdf_total}')


#-----------------------End Main Code------------------------#
print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))
