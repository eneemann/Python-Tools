# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 16:01:31 2022

@author: eneemann
"""

import os
import time
import arcpy


#: Start timer and print start time
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print("The script start time is {}".format(readable_start))
today = time.strftime("%Y%m%d")
   
today_db = r'C:\path_to.gdb'
fc = os.path.join(today_db, 'AddressPoints_WGS84')


del_count = 0
where_clause = "CountyID = '49011'"
fields = ['CountyID']
with arcpy.da.UpdateCursor(fc, fields, where_clause) as cursor:
    print("Looping through rows in FC ...")
    for row in cursor:
        if row[0] == '49011':
            cursor.deleteRow()
            del_count += 1
            
print(f"Total count of row deltions: {del_count}")


#: Stop timer and print end time
print("Script shutting down ...")
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))