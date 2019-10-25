# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 13:01:15 2019
@author: eneemann
Script to compare two CSV tables for differences

"""

import arcpy
from arcpy import env
import os
import time
import pandas as pd
import numpy as np
from Levenshtein import StringMatcher as Lv
from matplotlib import pyplot as plt

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))

near_df = pd.read_csv(r'C:\E911\Beaver Co\Addpts_working_folder\beaver_neartable_test.csv')
edit_df = pd.read_csv(r'C:\E911\Beaver Co\Addpts_working_folder\beaver_neartable_test_edit.csv')

diff = []
for x in np.arange(near_df.shape[0]):
    if str(near_df.iloc[x,:]) == str(edit_df.iloc[x,:]):
        diff.append('same')
    else:
        diff.append('different')
        
diff_df = pd.DataFrame({'Diff': diff})
diff_df.to_csv(r'C:\E911\Beaver Co\Addpts_working_folder\beaver_neartable_test_diff.csv')

print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))
