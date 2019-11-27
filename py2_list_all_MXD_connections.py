# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 16:35:37 2019
@author: eneemann
Script to change SDE connections in MXDs

***Must use Python 2 Interpreter to use arcpy.mapping module and work with MXDs***
"""

import arcpy
import os
import time
import csv
import pandas as pd


# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))
today = time.strftime("%Y%m%d")

######################
#  Set up variables  #
######################

# Create variable for root directory to crawl
root_dir = r'C:\E911'
outfile = os.path.join(root_dir, 'mxdcrawler_{}.csv'.format(today))

###############
#  Functions  #
###############

def main(folder, outputfile):
    # Function to write of CSV with MXD, layer, and data source info
    with open(outputfile, "wb") as f:
        w = csv.writer(f)
        header = ("Map Document", "MXD Path", "DataFrame Name", "DataFrame Description", "Layer name", "Layer Datasource")
        w.writerow(header)
        rows = crawlmxds(folder)
        w.writerows(rows)


def crawlmxds(folder):
    # Function to crawl input folder and find layer and data source info for all MXDs
    count = 0
    for root, dirs, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(".mxd"):
                count += 1
                mxdName = os.path.splitext(f)[0]
                mxdPath = os.path.join(root, f)
                mxd = arcpy.mapping.MapDocument(mxdPath)
                dataframes = arcpy.mapping.ListDataFrames(mxd)
                for df in dataframes:
                    dfDesc = df.description if df.description != "" else "None"
                    layers = arcpy.mapping.ListLayers(mxd, "", df)
                    for lyr in layers:
                        lyrName = lyr.name
                        lyrDatasource = lyr.dataSource if lyr.supports("dataSource") else "N/A"
                        seq = (mxdName, mxdPath, df.name, dfDesc, lyrName, lyrDatasource);
                        yield seq
                if count % 10 == 0:
                    print('Done with file number: {}'.format(count))
                del mxd


def source_only(row):
    # Function to add column of only data sources (not including layer name)
    if row['Layer Datasource'] is not None:
        # row['source_only'] = row['Layer Datasource'].rsplit('\\', 1)[0]
        row['source_only'] = str(row['Layer Datasource']).split(row['Layer name'])[0]
    else:
        row['source_only'] = None
    return row


def check_sde(row):
    # Function check for non-UTRANS SDE connections and populate 'SDE' column with yes/no
    if '.sde' in row['source_only'] and row['source_only'] is not None and 'UTRANS' not in row['source_only']:
        # row['source_only'] = row['Layer Datasource'].rsplit('\\', 1)[0]
        row['SDE'] = 'yes'
    else:
        row['SDE'] = 'no'
    return row

##########################
#  Call Functions Below  #
##########################

# Call main function to crawl root directory and write output to CSV
main(root_dir, outfile)


# Read in output CSV and perform additional manipulation to identify unique SDE connections
df = pd.read_csv(outfile)
df.drop_duplicates(subset='Layer Datasource', inplace=True)

# Add 'source_only' column to dataframe
df2 = df.apply(source_only, axis=1)
df2.drop_duplicates(subset='source_only', inplace=True)     # Remove duplicate sources from dataframe
df2.to_csv(os.path.join(root_dir, 'mxdcrawler_{}_sources.csv'.format(today)))   # Save to CSV

# Add 'SDE' column to dataframe and populate as yes/no
df3 = df2.apply(check_sde, axis=1)

# Filter final dataframe down to unique SDE connections, save to CSV
df4 = df3[df3['SDE'] == 'yes']
df4.to_csv(os.path.join(root_dir, 'mxdcrawler_{}_final.csv'.format(today)))
print(df4.shape)


print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))
