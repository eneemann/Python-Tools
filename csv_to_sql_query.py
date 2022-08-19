# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 07:55:51 2022

@author: eneemann
"""

import os
import time
import pandas as pd

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))


work_dir =r'C:\Users\eneemann\Documents\ArcGIS\Projects\DABC\Licensees_20220810'

csv = os.path.join(work_dir, 'correct_tab.csv')
correct = pd.read_csv(csv)

correct_list = correct['license_no'].to_list()

SQL = f"""LICENSE_NO IN ('{"','".join([(str(item)) for item in correct_list])}')"""
print(SQL)


print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))