# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 10:26:59 2019

@author: eneemann
"""

import time
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

##########################################
#   Step 1: Create point feature class   #
##########################################

# Set local variables
UETN_dir = r'C:\Users\eneemann\Desktop\Neemann\UETN Analysis'
os.chdir(UETN_dir)

UETN_gdb = r'C:\Users\eneemann\Desktop\Neemann\UETN Analysis\UETN.gdb'
out_path = UETN_dir
agg_fc = 'agg_sites_fc'
geometry_type = "POINT"
has_m = "DISABLED"
has_z = "DISABLED"
#spatial_reference = arcpy.SpatialReference(4326)
spatial_reference = arcpy.SpatialReference(26912)

excel_file = r'UETN_agg_sites.xlsx'
excel_sheet = 'Sheet1'
spreadsheet = os.path.join(UETN_dir, excel_file)
csv = os.path.join(UETN_dir, "UETN_agg_sites.csv")

table_name = 'agg_sites_table'
out_table = os.path.join(UETN_gdb, table_name)
arcpy.conversion.ExcelToTable(spreadsheet, out_table, excel_sheet)

# read in excel file as dataframe
agg_sites_df = pd.read_excel(spreadsheet)
agg_sites_df.head()
#agg_sites_df = pd.read_csv(csv)
#agg_sites_df.head()



# feed address to geocoder to populate x and y fields (UTM 12N, 26912)


# convert dataframe to numpy array

# build feature class from numpy array
arcpy.da.NumPyArrayToFeatureClass(array, agg_sties, ("X", "Y"), spatial_reference)


## create point feature class
#print('Creating feature class...')
#arcpy.management.CreateFeatureclass(UETN_gdb, agg_sites, geometry_type, "", has_m, has_z, spatial_reference)



##########################################
#   Step 4: Feed addresses to Geocoder   #
##########################################

# Input addresses
temp_address = trip['StartAdd']

# Test on addresses
add1 = address_parser(temp_address)
print(add1)

# def dict_to_json(dict_add):
self = 'AGRC-C65620FC695351'     # insert correct API token here
add1_loc = Geocoder(self).locate(add1['street'], add1['zone'],
                                         **{"acceptScore": 80, "spatialReference": 26912})
print(add1_loc)

temp['Y'] = str(add1_loc['y'])
temp['X'] = str(add1_loc['x'])

#################################################################
#   Step 5: Populate FC with point from Uber trip/html file   #
#################################################################



#if __name__ == "__main__":
#    """
#    Usage: Example usage is below. The dictionary passed in with ** can be any of the
#    optional parameters for the api.
#    """
#    geocoder = Geocoder('insert your api key here')
#    result = geocoder.locate("123 South Main Street", "SLC", **{"acceptScore": 90, "spatialReference": 4326})
#    
#    print result

print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))