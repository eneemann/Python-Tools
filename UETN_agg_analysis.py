# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 10:26:59 2019

@author: eneemann
"""

import time
import random
import requests
import os
import arcpy
#from . import geocode
import pandas as pd

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))

#################
#   Functions   #
#################

class Geocoder(object):

    _api_key = None
    _url_template = "http://api.mapserv.utah.gov/api/v1/geocode/{}/{}"

    def __init__(self, api_key):
        """
        Create your api key at
        https://developer.mapserv.utah.gov/secure/KeyManagement
        """
        self._api_key = api_key

    def locate(self, street, zone, **kwargs):
        kwargs["apiKey"] = self._api_key

        r = requests.get(self._url_template.format(street, zone), params=kwargs)

        response = r.json()

        if r.status_code is not 200 or response["status"] is not 200:
            print("{} {} was not found. {}".format(street, zone, response["message"]))
            return None

        result = response["result"]

        print("match: {} score [{}]".format(result["score"], result["matchAddress"]))
        return result["location"]


def address_parser(full_address):
    print(full_address.split(','))
    # If missing street number, make destination the airport
    if len(full_address.split(',')) < 3:
        if full_address.split(',')[1].split(' ')[2] == '84116' or full_address.split(',')[1].split(' ')[2] == '84122':
            full_address = '776 N Terminal Dr, ' + full_address
        elif full_address.split(',')[1].split(' ')[2] == '84107':
            full_address = '140 W Vine St, ' + full_address

    print(full_address)

    # Determine if street number is provided as range, if so take endpoint
    if '-' in full_address.split(' ')[0]:
        clean = full_address.split('-', 1)[1]
    else:
        clean = full_address
    # Separate into street, city, zone
    street = clean.split(',')[0].strip()
    city = clean.split(',')[1].strip()
    zone = clean.split(',')[2].strip().split(' ')[1]
    # build dictionary & return
    dictadd = {"street": street,
               "city": city,
               "zone": zone}

    # Strip off unit numbers from "street"
    if '#' in dictadd['street']:
        clean = dictadd['street'].split('#')[0]
    elif ' Apt' in dictadd['street']:
        clean = dictadd['street'].split('Apt')[0]
    elif ' apt' in dictadd['street']:
        clean = dictadd['street'].split('apt')[0]
    elif 'Unit' in dictadd['street']:
        clean = dictadd['street'].split('#')[0]
    elif 'unit' in dictadd['street']:
        clean = dictadd['street'].split('#')[0]
    elif '&' in dictadd['street']:
        clean = dictadd['street'].replace('&', 'and')
    else:
        clean = dictadd['street']

    dictadd['street'] = clean
    print(dictadd['street'])

    return dictadd

#########################
#   Aggregation Sites   #
#########################

# Set local variables
UETN_dir = r'C:\Users\eneemann\Desktop\Neemann\UETN Analysis'
os.chdir(UETN_dir)

UETN_gdb = r'C:\Users\eneemann\Desktop\Neemann\UETN Analysis\UETN.gdb'
out_path = UETN_dir
agg_fc = os.path.join(UETN_gdb, 'agg_sites_final')
geometry_type = "POINT"
spatial_reference = arcpy.SpatialReference(26912)

excel_file = r'UETN_agg_sites.xlsx'
excel_sheet = 'Sheet1'
spreadsheet = os.path.join(UETN_dir, excel_file)
#csv = os.path.join(UETN_dir, "UETN_agg_sites.csv")

#table_name = 'agg_sites_table'
#out_table = os.path.join(UETN_gdb, table_name)
#arcpy.conversion.ExcelToTable(spreadsheet, out_table, excel_sheet)
#
## read in excel file as dataframe
#agg_sites_df = pd.read_excel(spreadsheet)
#agg_sites_df.head()
#agg_sites_df = pd.read_csv(csv)
#agg_sites_df.head()




## create point feature class
#print('Creating feature class...')
#arcpy.management.CreateFeatureclass(UETN_gdb, agg_sites, geometry_type, "", has_m, has_z, spatial_reference)



#########################
#   DTS Network Sites   #
#########################
#csv = os.path.join(UETN_dir, "clean_DTS_network_sites.csv")
#df = pd.read_csv(csv)
##dictionary = {'site': ['test 1', 'test 2'],
##     'address': ['2243 S 300 E, Bountiful, UT 84010', '190 E Belmont Ave, Salt Lake City, UT 84111']}
##df = pd.DataFrame.from_dict(dictionary)
#
## trim off whitespace
#df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
#df.head()
#
## calculate appropriate fields for geocoder (street, zone - city or zip code)
#def parse_street(row):
#    temp = row['Address'].split(',')[0].strip()
#    return temp
#
#def parse_zone(row):
#    temp = row['Address'].split(' ')[-1].strip()
#    return temp
#
#
##df['street'] = df.apply(parse_street, axis=1)
##df['zone'] = df.apply(parse_zone, axis=1)
#df['street'] = df['Address']
#df['zone'] = df['City']
#df.to_csv("test.csv")
#
## need to add x/y columns to df before running geocoder?
#df['x'] = ''
#df['y'] = ''
#df.head()
#
#
## send fields to geocoder, get x/y values back
#def geocode(row):
#    self = 'XXXXXXXXXX'     # insert correct API token here
#    result = Geocoder(self).locate(row['street'], row['zone'],
#                                         **{"acceptScore": 70, "spatialReference": 26912})
#    print(result)
##    if result['status'] == '404':
#    if result is None:
#        row['x'] = '0'
#        row['y'] = '0'
#    else:
#        row['x'] = result['x']
#        row['y'] = result['y']
#        
#    time.sleep(random.random()*.3)
#    return row
#
#
#section_time = time.time()
#geo_df = df.apply(geocode, axis=1)
#print(f'Time to geocode all rows: {time.time() - section_time}')
#
#geo_df.head()
#geo_df.to_csv("test_add.csv")
#geo_df.shape
#geo_df.columns


#######################
# read in geocoded results and add to current fc
#######################

good_csv = csv = os.path.join(UETN_dir, 'geocoded_DTS_network_sites.csv')
final_df = pd.read_csv(good_csv)
final_df.shape

# bring dataframe into a feature class

# create feature class and add fields
DTS_fc = os.path.join(UETN_gdb, 'DTS_sites_fc')
#arcpy.CreateFeatureclass_management(UETN_gdb, 'DTS_sites_fc', 'POINT', "", "", "", spatial_reference)
#arcpy.AddField_management(DTS_fc, "DTS_Location", "TEXT", "", "", 50)
#arcpy.AddField_management(DTS_fc, "DTS_Address", "TEXT", "", "", 50)
#arcpy.AddField_management(DTS_fc, "DTS_City", "TEXT", "", "", 30)
#arcpy.AddField_management(DTS_fc, "DTS_street", "TEXT", "", "", 40)
#arcpy.AddField_management(DTS_fc, "DTS_zone", "TEXT", "", "", 30)

fields = ['DTS_Location',
          'DTS_Address',
          'DTS_City',
          'DTS_street',
          'DTS_zone',
          'SHAPE@XY']
    
def insert_row(row):
    xy = (row['x'], row['y'])
    values = [row['Location'][:50],
              row['Address'][:50],
              row['City'][:30],
              row['street'][:40],
              row['zone'][:30],
              xy]
    print('Adding point to feature class...')
    with arcpy.da.InsertCursor(DTS_fc, fields) as insert_cursor:
        insert_cursor.insertRow(values)
        
final_df.apply(insert_row, axis=1)

#final_df.iloc[277]['Location'][:50]
#final_df.iloc[75]


###########################
#   Near Table Analysis   #
###########################

# Create table name (in memory) for neartable
neartable = 'in_memory\\near_table'
if arcpy.Exists(neartable):
    arcpy.Delete_management(neartable)
# Perform near table analysis
print("Generating near table ...")
arcpy.GenerateNearTable_analysis (DTS_fc, agg_fc, neartable, '', 'NO_LOCATION', 'NO_ANGLE', 'CLOSEST', '', 'GEODESIC')
print("Number of rows in Near Table: {}".format(arcpy.GetCount_management(neartable)))

# Convert neartable to pandas dataframe
neartable_arr = arcpy.da.TableToNumPyArray(neartable, '*')
near_df = pd.DataFrame(data = neartable_arr)
print(near_df.head(5).to_string())

# Convert DTS sites to pandas dataframe
DTS_fields = ['OBJECTID', 'DTS_Location', 'DTS_Address', 'DTS_City']
DTS_arr = arcpy.da.FeatureClassToNumPyArray(DTS_fc, DTS_fields)
DTS_df = pd.DataFrame(data = DTS_arr)
print(DTS_df.head(5).to_string())

# Convert aggregation sites to pandas dataframe
agg_fields = ['OBJECTID', 'Aggregation_Site', 'Agg_Type', 'Agg_Info', 'Agg_Address']
agg_arr = arcpy.da.FeatureClassToNumPyArray(agg_fc, agg_fields)
agg_df =pd.DataFrame(data = agg_arr)
print(agg_df.head(5).to_string())

# Join DTS sites to near table
join1_df = near_df.join(DTS_df.set_index('OBJECTID'), on='IN_FID')
print(join1_df.head(5).to_string())
path = r'C:\Users\eneemann\Desktop\Neemann\UETN Analysis\UETN_neartable_join1.csv'
join1_df.to_csv(path)

# Join aggregate sites to near table
join2_df = join1_df.join(agg_df.set_index('OBJECTID'), on='NEAR_FID')
print(join2_df.head(5).to_string())
path = r'C:\Users\eneemann\Desktop\Neemann\UETN Analysis\UETN_neartable_join2.csv'
join2_df.to_csv(path)

# Caculate distance in miles, reorder columns, sort, save to CSV
join2_df['Dist_miles'] = join2_df['NEAR_DIST']/1609.34
join2_df.columns
cols = ['OBJECTID', 'IN_FID', 'NEAR_FID', 'NEAR_DIST', 'Dist_miles', 'DTS_Location',
       'DTS_Address', 'DTS_City', 'Aggregation_Site', 'Agg_Type', 'Agg_Info',
       'Agg_Address']
join2_df = join2_df[cols]
UETN_df = join2_df.sort_values('Dist_miles', ascending=False)
path = r'C:\Users\eneemann\Desktop\Neemann\UETN Analysis\UETN_final.csv'
UETN_df.to_csv(path)


print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))