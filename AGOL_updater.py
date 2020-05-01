# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 08:44:43 2020

@author: eneemann

21 Apr 2020: Created initial code to update AGOL layer (EMN).
"""

import os
import time
import getpass
import arcpy
from arcgis.gis import GIS
import pandas as pd
import numpy as np
import datetime as dt
import pytz

print(dt.datetime.now())


# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))


portal_url = arcpy.GetActivePortalURL()
print(portal_url)

user = getpass.getpass(prompt='    Enter arcgis.com username:\n')
pw = getpass.getpass(prompt='    Enter arcgis.com password:\n')
# gis = GIS(portal_url, 'Erik.Neemann@UtahAGRC', pw)
arcpy.SignInToPortal(portal_url, user, pw)
del pw

# TEST layer
counts_service = r'https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services/EMN_Cases_by_LHD_TEST_v3/FeatureServer/0'
# TEST table
counts_by_day = r'https://services1.arcgis.com/99lidPhWCzftIe9K/arcgis/rest/services/EMN_Cases_by_LHD_by_Day_TEST_v3/FeatureServer/0'


work_dir = r'C:/Users/eneemann/Desktop/Neemann/COVID19'
updates = pd.read_csv(os.path.join(work_dir, 'COVID_Case_Counts_latest.csv'))
updates.sort_values('Jurisdiction', inplace=True)


# UPDATE LATEST CASE COUNTS LAYER FROM MOST RECENT CSV
count = 0
#             0                     1                      2                    3   
fields = ['DISTNAME', 'COVID_Cases_Utah_Resident', 'COVID_Cases_Total', 'Hospitalizations',
          #     4               5              6
          'Date_Updated', 'Population', 'Cases_per_100k']
with arcpy.da.UpdateCursor(counts_service, fields) as ucursor:
    print("Looping through rows to make updates ...")
    for row in ucursor:
        temp_df = updates.loc[updates['Jurisdiction'] == row[0]]
        print(temp_df.head())
        row[1] = temp_df.iloc[0]['Cases']
        row[2] = row[1]
        row[3] = temp_df.iloc[0]['Hospitalizations']
        row[4] = dt.datetime.now()
        row[6] = (row[2]/row[5])*100000.
        count += 1
        ucursor.updateRow(row)
print(f'Total count of COVID Case Count updates is: {count}')

# APPEND MOST RECENT CASE COUNTS TO COUNTS BY DAY TABLE

# Build Field Map for all fields from counts_service into counts_by_day
fms = arcpy.FieldMappings()

# Old Field Mapping
# fm_dict = {'DISTNAME': 'DISTNAME',
#             'COVID_Cases_Utah_Resident': 'COVID19_Cases_in_Utah_Residents',
#             'COVID_Cases_Non_Utah_Resident': 'COVID19_Cases_in_Non_Utah_Residents',
#             'COVID_Cases_Total': 'Total_COVID19_Cases_in_Utah',
#             'Date_Updated': 'Day',
#             'Hospitalizations': 'Hospitalizations',
#             'Population': 'Population',
#             'Cases_per_100k': 'Case_Rate_Per_100_000'}

# New Field Mapping
fm_dict = {'DISTNAME': 'DISTNAME',
            'COVID_Cases_Utah_Resident': 'COVID_Cases_Utah_Resident',
            'COVID_Cases_Non_Utah_Resident': 'COVID_Cases_Non_Utah_Resident',
            'COVID_Cases_Total': 'COVID_Cases_Total',
            'Date_Updated': 'Day',
            'Hospitalizations': 'Hospitalizations',
            'Population': 'Population',
            'Cases_per_100k': 'Cases_per_100k',
            'COVID_Cases_Daily_Increase': 'COVID_Cases_Daily_Increase',
            'COVID_Total_Recoveries': 'COVID_Total_Recoveries',
            'COVID_New_Daily_Recoveries': 'COVID_New_Daily_Recoveries',
            'COVID_Total_Deaths': 'COVID_Total_Deaths',
            'COVID_Deaths_Daily_Increase': 'COVID_Deaths_Daily_Increase'
            }

for key in fm_dict:
    fm = arcpy.FieldMap()
    fm.addInputField(counts_service, key)
    output = fm.outputField
    output.name = fm_dict[key]
    fm.outputField = output
    fms.addFieldMap(fm)

counts_fields = [f.name for f in arcpy.ListFields(counts_service)]
by_day_fields = [f.name for f in arcpy.ListFields(counts_by_day)]

print('Appending recent case counts to counts by day table ...')
arcpy.management.Append(counts_service, counts_by_day, "NO_TEST", field_mapping=fms)

# CALCULATE DAILY AND CUMULATIVE NUMBERS
print(by_day_fields)
keep_fields = ['DISTNAME', 'COVID_Cases_Utah_Resident', 'COVID_Cases_Non_Utah_Resident',
               'COVID_Cases_Total', 'Day', 'Hospitalizations', 'Population',
               'Cases_per_100k', 'COVID_Cases_Daily_Increase', 'COVID_Total_Recoveries',
               'COVID_New_Daily_Recoveries', 'COVID_Total_Deaths', 'COVID_Deaths_Daily_Increase']

if arcpy.Exists('in_memory\\temp_table'):
    print("Deleting 'in_memory\\temp_table' ...")
    arcpy.Delete_management('in_memory\\temp_table')

# Convert counts_by_day into pandas dataframe
arcpy.conversion.TableToTable(counts_by_day, 'in_memory', 'temp_table')
# temp_fields = [f.name for f in arcpy.ListFields('in_memory\\temp_table')]
day_arr = arcpy.da.TableToNumPyArray('in_memory\\temp_table', keep_fields)
day_df = pd.DataFrame(data=day_arr)

# Convert string entries of 'None' to zeros ('0')
mask = day_df.applymap(lambda x: x == 'None')
cols = day_df.columns[(mask).any()]
for col in day_df[cols]:
    day_df.loc[mask[col], col] = '0'

day_df.head()
day_df.sort_values('Day', inplace=True, ascending=True)
day_df.head().to_string()

# Load test data
test_df = pd.read_csv(os.path.join(work_dir, 'by_day_testing.csv'))

# Rename variables below to day_df after done testing

# Split table into individual dfs by health district
hd_list = test_df.DISTNAME.unique()
hd_dict = {}
for item in hd_list:
    temp = test_df[test_df.DISTNAME == item]
    hd_dict[item] = temp.reset_index()

for key in hd_dict:
    for i in np.arange(1, hd_dict[key].shape[0]):
        # Calculate daily case increase
        hd_dict[key].at[i, 'COVID_Cases_Daily_Increase'] = hd_dict[key].iloc[i]['COVID_Cases_Utah_Resident'] - hd_dict[key].iloc[i-1]['COVID_Cases_Utah_Resident']
        # Calculate daily death increase
        hd_dict[key].at[i, 'COVID_Deaths_Daily_Increase'] = int(hd_dict[key].iloc[i]['COVID_Total_Deaths']) - int(hd_dict[key].iloc[i-1]['COVID_Total_Deaths'])
        # Calculate daily total recoveries
        if i > 20:
            hd_dict[key].at[i, 'COVID_Total_Recoveries'] = int(hd_dict[key].iloc[i]['COVID_Cases_Utah_Resident']) - int(hd_dict[key].iloc[i]['COVID_Total_Deaths']) - ( int(hd_dict[key].iloc[i]['COVID_Cases_Utah_Resident']) - int(hd_dict[key].iloc[i-21]['COVID_Cases_Utah_Resident']) )
        # Calculate daily recovery increase
        hd_dict[key].at[i, 'COVID_New_Daily_Recoveries'] = int(hd_dict[key].iloc[i]['COVID_Total_Recoveries']) - int(hd_dict[key].iloc[i-1]['COVID_Total_Recoveries'])


# UPDATE COUNTS BY DAY TABLE WITH NEW NUMBERS
table_count = 0
#                   0                    1                           2   
table_fields = ['DISTNAME', 'COVID_Cases_Daily_Increase', 'COVID_Total_Recoveries',
          #            3                         4                          5
          'COVID_New_Daily_Recoveries', 'COVID_Total_Deaths', 'COVID_Deaths_Daily_Increase']
with arcpy.da.UpdateCursor(counts_by_day, table_fields) as ucursor:
    print("Looping through rows to make updates ...")
    for row in ucursor:
        temp_df = updates.loc[updates['Jurisdiction'] == row[0]]
        print(temp_df.head())
        row[1] = temp_df.iloc[0]['Cases']
        row[2] = row[1]
        row[3] = temp_df.iloc[0]['Hospitalizations']
        row[4] = dt.datetime.now()
        row[6] = (row[2]/row[5])*100000.
        table_count += 1
        ucursor.updateRow(row)
print(f'Total count of COVID Case Count updates is: {table_count}')      
    
# COPY DAILY AND CUMULATIVE NUMBERS BACK TO MOST RECENT CASE COUNTS LAYER



print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))




# TESTING

# 4/25 estimate for recovered
# total recovered = total cases - total deaths - cases within the last 21 days
# total recovered = total cases - total deaths - (total cases today - total cases 22 days ago)
# First attempt (older than 21 days) - using total cases on 4/4
r425 = 4140 - 45 - (4140 - 1592)
print(r425)

# Second attempt (older than 21 days) - using total cases on 4/3
r425_v2 = 4140 - 43 - (4123 - 1592)
print(r425_v2)

# What website is showing
# 4140 cumulative
# 1566 recovered