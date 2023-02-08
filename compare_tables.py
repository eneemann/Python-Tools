# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 13:01:15 2019
@author: eneemann
Script to compare two CSV tables for differences

"""

import time
import pandas as pd
import numpy as np


# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))

one_df = pd.read_csv(r"C:\Users\eneemann\Desktop\Neemann\NG911\0 Fire PDFs and Tables\Utah_FDID_Jun2022.csv")
two_df = pd.read_csv(r"C:\Users\eneemann\Desktop\Neemann\NG911\0 Fire PDFs and Tables\USFA_FDID_Jun2022.csv")

diff = []
for x in np.arange(one_df.shape[0]):
    if str(one_df.iloc[x,:]) == str(two_df.iloc[x,:]):
        diff.append('same')
    else:
        diff.append('different')
        
diff_df = pd.DataFrame({'Diff': diff})
diff_df.head()
#diff_df.to_csv(r'C:\Users\eneemann\Desktop\Neemann\NG911\0 Fire PDFs and Tables\FDID_diff.csv')

print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))
