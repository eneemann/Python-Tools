# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 13:01:15 2019
@author: eneemann
Script to move multiple alias rows with the same joining ID into multiple columns on the same row

"""

import os
import time
import pandas as pd
import numpy as np


# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))

work_dir = r'C:\E911\Layton\working_data'
alias = pd.read_csv(os.path.join(work_dir, 'CP_Aliases.csv'))

max_alias = alias['CommonPlacePointID'].value_counts().max()

working = alias.copy().sort_values('CommonPlacePointID')

for i in np.arange(max_alias):
    working[f'Alias_{i+2}'] = None

cp_id = list(set(working['CommonPlacePointID'].to_list()))

completed_ids = []

for idx, row in working.iterrows():
    temp_id = row['CommonPlacePointID']
    if temp_id not in completed_ids:
        temp_df = working[working['CommonPlacePointID'] == temp_id]
        new_aliases = temp_df['CommonPlaceAlias Name'].to_list()
        if len(new_aliases) > 1:
            print(new_aliases)
            # Update row for each alias in a new column
            for i in np.arange(1, len(new_aliases)):
                col_name = f'Alias_{i+1}'
                working.loc[idx, col_name] = new_aliases[i]
        
        del temp_df
        del temp_id
    
    completed_ids.append(temp_id)
    
work2 = working.drop_duplicates('CommonPlacePointID') 
work2.to_csv(os.path.join(work_dir, 'CP_multiple_Aliases.csv'))

print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))
