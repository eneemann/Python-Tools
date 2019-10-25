# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 08:52:53 2019
@author: eneemann

Script to pull list of PLSS points and compare to PDFs on web server
"""

import arcpy
from arcpy import env
import os
import time
import pandas as pd

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))
today = time.strftime("%Y%m%d")

# Read in PLSS points from SGID
SGID = r"C:\Users\eneemann\AppData\Roaming\ESRI\ArcGISPro\Favorites\sgid.agrc.utah.gov.sde"
PLSS_pts = os.path.join(SGID, "SGID10.CADASTRE.PLSSPoint_AGRC")
#PLSS_pts = r'C:\Users\eneemann\Desktop\Neemann\PLSS Data\Test\Cache_PLSS_new_pts_20191025.gdb\PLSS_new_pts_UTM_12N_m'
counties = os.path.join(SGID, "SGID10.BOUNDARIES.Counties")

# Select only Cache County PLSS points and create layer
where_clause = "NAME = 'CACHE'" 
# Need to make a layers
if arcpy.Exists("county_lyr"):
    arcpy.Delete_management("county_lyr")
arcpy.MakeFeatureLayer_management(counties, "county_lyr", where_clause)
if arcpy.Exists("PLSS_lyr"):
    arcpy.Delete_management("PLSS_lyr")
arcpy.MakeFeatureLayer_management(PLSS_pts, "PLSS_lyr")


# Select all features within 5m of current St George FC
arcpy.SelectLayerByLocation_management("PLSS_lyr", "INTERSECT", "county_lyr")

PLSS_list = []
fields = ['TieSheet_Name']
#fields = ['TieSheet_N']
#with arcpy.da.SearchCursor(PLSS_pts, fields) as sCur:
#    print("Looping through rows in {} ...".format(PLSS_pts))
with arcpy.da.SearchCursor("PLSS_lyr", fields) as sCur:
    print("Looping through rows in {} ...".format("PLSS_lyr"))
    for row in sCur:
        PLSS_list.append(row[0])
print(f"Total current PLSS points: {len(PLSS_list)}")

# Get list of pdfs from web server
pdf_dir = r"Z:\TieSheets"
os.chdir(pdf_dir)

filenumber = 0
dir_list = os.listdir(pdf_dir)
pdf_dict = {}
total = len(dir_list)
for filename in dir_list:
    pdf_dict.setdefault(filename)

print(f"Total pdf files in directory: {len(pdf_dict)}")

# Compare PLSS listing to pdf listing
# create dataframe (PLSS sheet, pdf exists)
data_dict = {'PDF': PLSS_list, 'Exists': None}
plss_df = pd.DataFrame(data = data_dict)
print(plss_df.head(5))

plss_df.dropna(subset=['PDF'], inplace=True)    # delete rows without a PDF listed
plss_df.head()

# function to check if PDF listed is actually in web share dictionary
def in_pdf_dict(row):
    if row['PDF'] in pdf_dict:
        row['Exists'] = 1     
    return row

# loop through rows in df with apply function, populate Exists column (1, or None)
df = plss_df.apply(in_pdf_dict, axis=1)

# sum up 1s for total count
print(f"Number of matching PDFs: {df.sum()['Exists']}")

# Now check to remove the meander corners (part of PLSS label >= 800)
label_df = plss_df
def get_label(row):
    if '.pdf' in row['PDF']:
        return row['PDF'].split(".")[0].split("_")[1]
    else:
        return None

# Populate label field, drop rows without a label (no PDF listed)
label_df['Label'] = label_df.apply(get_label, axis=1)
label_df.dropna(subset=['Label'], inplace=True)

# function to populate 'Keep' field based on label values
keep_df = label_df
def parse_label(row):
    first3 = int(row['Label'][0:3])
    last3 = int(row['Label'][3:6])
    if first3 >= 800 or last3 >= 800:
        return 'no'
    else:
        return 'yes'

# Populate 'Keep' field, drop rows == 'no', then drop rows where 'Exists' == None
keep_df['Keep'] = keep_df.apply(parse_label, axis=1)
keep_df = keep_df[keep_df.Keep != 'no']
keep_df.dropna(subset=['Exists'], inplace=True)

# loop through rows in df with apply function, populate Exists column (1, or None)
final_df = keep_df.apply(in_pdf_dict, axis=1)

# sum up yes's for total count
print(f"Number of matching PDFs (excluding meander points): {final_df.Keep.count()}")

# Optionally export to csv if you need to explore the data
path = r'C:\Users\eneemann\Desktop\final_df.csv'
final_df.to_csv(path)


print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))