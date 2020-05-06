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
import pandas as pd
import numpy as np
import datetime as dt

print(f'Current date and time: {dt.datetime.now()}')


# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))


# Set variables, get AGOL username and password
portal_url = arcpy.GetActivePortalURL()
print(portal_url)

user = getpass.getpass(prompt='    Enter arcgis.com username:\n')
pw = getpass.getpass(prompt='    Enter arcgis.com password:\n')
arcpy.SignInToPortal(portal_url, user, pw)
del pw

# Updated count numbers are copied from table at 'https://coronavirus.utah.gov/case-counts/'
# CSV file with updates should be named 'COVID_Case_Counts_latest.csv'
# Update this 'work_dir' variable with the folder you store the updated CSV in
work_dir = r'C:\COVID19'
updates = pd.read_csv(os.path.join(work_dir, 'COVID_Case_Counts_latest.csv'))
updates.sort_values('Jurisdiction', inplace=True)


# TEST layer
# counts_service = r'https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services/EMN_Cases_by_LHD_TEST_v3/FeatureServer/0'
# TEST table
# counts_by_day = r'https://services1.arcgis.com/99lidPhWCzftIe9K/arcgis/rest/services/EMN_Cases_by_LHD_by_Day_TEST_v3/FeatureServer/0'

# # Josh's LIVE layer (Utah_COVID19_Cases_by_Local_Health_Department)
counts_service = r'https://services6.arcgis.com/KaHXE9OkiB9e63uE/arcgis/rest/services/Utah_COVID19_Cases_by_Local_Health_Department/FeatureServer/0'
# # Josh's LIVE table (Utah_COVID19_Case_Counts_by_LHD_by_Day)
counts_by_day = r'https://services6.arcgis.com/KaHXE9OkiB9e63uE/arcgis/rest/services/Utah_COVID19_Case_Counts_by_LHD_by_Day/FeatureServer/0'


# 1) UPDATE LATEST CASE COUNTS LAYER FROM MOST RECENT CSV
count = 0
#             0                     1                      2                    3   
fields = ['DISTNAME', 'COVID_Cases_Utah_Resident', 'COVID_Cases_Total', 'Hospitalizations',
          #     4               5              6                   7
          'Date_Updated', 'Population', 'Cases_per_100k', 'COVID_Total_Deaths']
with arcpy.da.UpdateCursor(counts_service, fields) as ucursor:
    print("Looping through rows to make updates ...")
    for row in ucursor:
        jurisdiction = row[0]
        if 'San Juan' in jurisdiction.title():
            jurisdiction = 'San Juan'
        temp_df = updates.loc[updates['Jurisdiction'] == jurisdiction]
        print(temp_df.head())
        row[1] = temp_df.iloc[0]['Cases']
        row[2] = row[1]
        row[3] = temp_df.iloc[0]['Hospitalizations']
        row[4] = dt.datetime.now()
        row[6] = (row[2]/row[5])*100000.
        row[7] = temp_df.iloc[0]['Deaths']
        count += 1
        ucursor.updateRow(row)
print(f'Total count of COVID Case Count updates is: {count}')


# 2) APPEND MOST RECENT CASE COUNTS TO COUNTS BY DAY TABLE
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

# Get list of field names to compare them
counts_fields = [f.name for f in arcpy.ListFields(counts_service)]
by_day_fields = [f.name for f in arcpy.ListFields(counts_by_day)]

# Append the new data
print('Appending recent case counts to counts by day table ...')
arcpy.management.Append(counts_service, counts_by_day, "NO_TEST", field_mapping=fms)


# 3) CALCULATE DAILY AND CUMULATIVE NUMBERS IN PANDAS DATAFRAME
print(by_day_fields)
keep_fields = ['DISTNAME', 'COVID_Cases_Utah_Resident', 'COVID_Cases_Non_Utah_Resident',
               'COVID_Cases_Total', 'Day', 'Hospitalizations', 'Population',
               'Cases_per_100k', 'COVID_Cases_Daily_Increase', 'COVID_Total_Recoveries',
               'COVID_New_Daily_Recoveries', 'COVID_Total_Deaths', 'COVID_Deaths_Daily_Increase']

# Delete in-memory table that will be used (if it already exists)
if arcpy.Exists('in_memory\\temp_table'):
    print("Deleting 'in_memory\\temp_table' ...")
    arcpy.Delete_management('in_memory\\temp_table')
    time.sleep(3)

# Convert counts_by_day into pandas dataframe (table --> numpy array --> dataframe)
arcpy.conversion.TableToTable(counts_by_day, 'in_memory', 'temp_table')
day_arr = arcpy.da.TableToNumPyArray('in_memory\\temp_table', keep_fields)
day_df = pd.DataFrame(data=day_arr)

# Clean up San Juan district name, if necessary
for i in np.arange(day_df.shape[0]):
    if 'San Juan' in day_df.iloc[i]['DISTNAME'].title():
        day_df.at[i, 'DISTNAME'] = 'San Juan'

# Convert string entries of 'None' to zeros ('0')
mask = day_df.applymap(lambda x: x == 'None')
cols = day_df.columns[(mask).any()]
for col in day_df[cols]:
    day_df.loc[mask[col], col] = '0'

# Sort data ascending so most recent dates are at the bottom (highest index)
day_df.head()
day_df.sort_values('Day', inplace=True, ascending=True)
day_df.head().to_string()

# Load test data during the test process
# Rename variables below back to day_df after done testing
# test_df = pd.read_csv(os.path.join(work_dir, 'by_day_testing.csv'))

# Split table into individual dataframes by health district
# Create a dictionary to hold each dataframe, DISTNAME becomes the key
hd_list = day_df.DISTNAME.unique()
hd_dict = {}
for item in hd_list:
    temp = day_df[day_df.DISTNAME == item]
    hd_dict[item] = temp.reset_index()

# Calculate values for new fields by iterating through the dataframes
for key in hd_dict:
    for i in np.arange(1, hd_dict[key].shape[0]):
        # Calculate daily case increase
        hd_dict[key].at[i, 'COVID_Cases_Daily_Increase'] = hd_dict[key].iloc[i]['COVID_Cases_Utah_Resident'] - hd_dict[key].iloc[i-1]['COVID_Cases_Utah_Resident']
        # Calculate daily death increase
        hd_dict[key].at[i, 'COVID_Deaths_Daily_Increase'] = int(hd_dict[key].iloc[i]['COVID_Total_Deaths']) - int(hd_dict[key].iloc[i-1]['COVID_Total_Deaths'])
        # Calculate daily total recoveries = total cases - total deaths - (total cases today - total cases 21 days ago)
        if i > 20:
            hd_dict[key].at[i, 'COVID_Total_Recoveries'] = int(hd_dict[key].iloc[i]['COVID_Cases_Utah_Resident']) - int(hd_dict[key].iloc[i]['COVID_Total_Deaths']) - ( int(hd_dict[key].iloc[i]['COVID_Cases_Utah_Resident']) - int(hd_dict[key].iloc[i-21]['COVID_Cases_Utah_Resident']) )
        # Calculate daily recovery increase
        hd_dict[key].at[i, 'COVID_New_Daily_Recoveries'] = int(hd_dict[key].iloc[i]['COVID_Total_Recoveries']) - int(hd_dict[key].iloc[i-1]['COVID_Total_Recoveries'])


# 4a) UPDATE ***ONLY TODAY'S ROW*** IN COUNTS BY DAY TABLE WITH NEW NUMBERS
# start_time = time.time()
table_count = 0
#                   0         1                2                           3   
table_fields = ['DISTNAME', 'Day', 'COVID_Cases_Daily_Increase', 'COVID_Total_Recoveries',
          #            4                         5                          6
          'COVID_New_Daily_Recoveries', 'COVID_Total_Deaths', 'COVID_Deaths_Daily_Increase']
with arcpy.da.UpdateCursor(counts_by_day, table_fields) as ucursor:
    print("Looping through rows to make updates ...")
    for row in ucursor:
        if dt.datetime.now().date() == row[1].date():
            print(row[0] + '   ' + str(row[1]))
            jurisdiction = row[0]
            if 'San Juan' in jurisdiction.title():
                jurisdiction = 'San Juan'
            # select row of jurisdiction's dataframe where date == date in hosted 'by day' table
            temp_df = hd_dict[jurisdiction].loc[hd_dict[jurisdiction]['Day'] == row[1]]
            # print(temp_df.head())
            row[2] = temp_df.iloc[0]['COVID_Cases_Daily_Increase']
            row[3] = temp_df.iloc[0]['COVID_Total_Recoveries']
            row[4] = temp_df.iloc[0]['COVID_New_Daily_Recoveries']
            row[5] = temp_df.iloc[0]['COVID_Total_Deaths']
            row[6] = temp_df.iloc[0]['COVID_Deaths_Daily_Increase']
            table_count += 1
            ucursor.updateRow(row)
print(f'Total count of COVID Counts By Day Table updates is: {table_count}') 


# 4b) UPDATE ***ALL ROWS*** IN COUNTS BY DAY TABLE WITH NEW NUMBERS
# Should only need to run this once to make the calculations for all previous rows
# start_time = time.time()
# table_count = 0
# #                   0         1                2                           3   
# table_fields = ['DISTNAME', 'Day', 'COVID_Cases_Daily_Increase', 'COVID_Total_Recoveries',
#           #            4                         5                          6
#           'COVID_New_Daily_Recoveries', 'COVID_Total_Deaths', 'COVID_Deaths_Daily_Increase']
# with arcpy.da.UpdateCursor(counts_by_day, table_fields) as ucursor:
#     print("Looping through rows to make updates ...")
#     for row in ucursor:
#         print(row[0] + '   ' + str(row[1]))
#         jurisdiction = row[0]
#         if 'San Juan' in jurisdiction.title():
#             jurisdiction = 'San Juan'
#         # select row of jurisdiction's dataframe where date == date in hosted 'by day' table
#         temp_df = hd_dict[jurisdiction].loc[hd_dict[jurisdiction]['Day'] == row[1]]
#         # print(temp_df.head())
#         row[2] = temp_df.iloc[0]['COVID_Cases_Daily_Increase']
#         row[3] = temp_df.iloc[0]['COVID_Total_Recoveries']
#         row[4] = temp_df.iloc[0]['COVID_New_Daily_Recoveries']
#         row[5] = temp_df.iloc[0]['COVID_Total_Deaths']
#         row[6] = temp_df.iloc[0]['COVID_Deaths_Daily_Increase']
#         table_count += 1
#         ucursor.updateRow(row)
# print(f'Total count of COVID Counts By Day Table updates is: {table_count}')      
    


# 5) COPY DAILY AND CUMULATIVE NUMBERS BACK TO MOST RECENT CASE COUNTS LAYER
# start_time = time.time()
lhd_count = 0
#                  0            1                     2                           3   
lhd_fields = ['DISTNAME', 'Date_Updated', 'COVID_Cases_Daily_Increase', 'COVID_Total_Recoveries',
          #            4                         5                          6
          'COVID_New_Daily_Recoveries', 'COVID_Total_Deaths', 'COVID_Deaths_Daily_Increase']
with arcpy.da.UpdateCursor(counts_service, lhd_fields) as ucursor:
    print("Looping through rows to make updates ...")
    for row in ucursor:
        jurisdiction = row[0]
        if 'San Juan' in jurisdiction.title():
            jurisdiction = 'San Juan'
        # select last row (most recent) of jurisdiction's dataframe and copy into counts_service layer
        temp_row = hd_dict[jurisdiction].iloc[-1]
        row[2] = temp_row.loc['COVID_Cases_Daily_Increase']
        row[3] = temp_row.loc['COVID_Total_Recoveries']
        row[4] = temp_row.loc['COVID_New_Daily_Recoveries']
        row[5] = temp_row.loc['COVID_Total_Deaths']
        row[6] = temp_row.loc['COVID_Deaths_Daily_Increase']
        lhd_count += 1
        ucursor.updateRow(row)
print(f'Total count of COVID updates by local health district: {lhd_count}')      
    

print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))
