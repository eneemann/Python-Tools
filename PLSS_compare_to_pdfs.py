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
counties = os.path.join(SGID, "SGID10.BOUNDARIES.Counties")

# Select only Cache County PLSS points and create layer
#where_clause = "NAME = 'CACHE'" 
## Need to make a layers
#if arcpy.Exists("county_lyr"):
#    arcpy.Delete_management("county_lyr")
#arcpy.MakeFeatureLayer_management(counties, "county_lyr", where_clause)
#if arcpy.Exists("PLSS_lyr"):
#    arcpy.Delete_management("PLSS_lyr")
#arcpy.MakeFeatureLayer_management(PLSS_pts, "PLSS_lyr")


# Select all features within 5m of current St George FC
#arcpy.SelectLayerByLocation_management("PLSS_lyr", "INTERSECT", "county_lyr")

PLSS_list = []
fields = ['TieSheet_Name']
#where_SGID = "CountyID = '49005'"       # Cache County is FIPS code 49005
with arcpy.da.SearchCursor(PLSS_pts, fields) as sCur:
    print("Looping through rows in {} ...".format(PLSS_pts))
#with arcpy.da.SearchCursor("PLSS_lyr", fields) as sCur:
#    print("Looping through rows in {} ...".format("PLSS_lyr"))
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

plss_df.dropna(subset=['PDF'], inplace=True)
plss_df.head()


# apply function
def in_pdf_dict(row):
    if row['PDF'] in pdf_dict:
        row['Exists'] = 1
        
    return row


# loop through rows in df with apply function
df = plss_df.apply(in_pdf_dict, axis=1)

# sum up 1s for total count
print(f"Number of matching PDFs: {df.sum()['Exists']}")


###############
#  Functions  #
###############


    

##########################
#  Call Functions Below  #
##########################


print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))