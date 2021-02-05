# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 13:22:19 2021
@author: eneemann
30 Jan 2021: Created initial code to ETL SGID data in Google Geo Data Upload program schema.
"""

import os
import time
import arcpy
import datetime as dt

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))
today = time.strftime("%Y%m%d")

SGID = r"C:\Users\eneemann\AppData\Roaming\ESRI\ArcGISPro\Favorites\internal@SGID@internal.agrc.utah.gov.sde"
work_dir = r"C:\Users\eneemann\Desktop\Neemann\Google Geo Data Upload"
# working_db = r"C:\Users\eneemann\Desktop\Neemann\Google Geo Data Upload\SGID_dumps_20210130.gdb"
working_db = os.path.join(work_dir, f"SGID_dumps_{today}.gdb")
sgid_roads = os.path.join(SGID, "SGID.TRANSPORTATION.Roads")
sgid_addpts = os.path.join(SGID, "SGID.LOCATION.AddressPoints")
working_roads = os.path.join(working_db, "Roads")
working_addpts = os.path.join(working_db, "AddressPoints")

gdu_road_schema = os.path.join(work_dir, "gdu_roads_schema.shp")
gdu_addpt_schema = os.path.join(work_dir, "gdu_addpts_schema.shp")

out_folder = f"Shapefiles_{today}"
out_dir = os.path.join(work_dir, out_folder)

gdu_roads = os.path.join(out_dir, "Utah_Roads.shp")
gdu_addpts = os.path.join(out_dir, "Utah_AddressPoints.shp")


# # List SGID layer fields
# road_fields = arcpy.ListFields(working_roads)
# print('Roads Field Info:')
# for f in road_fields:
#     print(f'Field Name: {f.name}     Field Type: {f.type}     Field Length: {f.length}')
# addpt_fields = arcpy.ListFields(working_addpts)
# print('Address Point Field Info:')
# for f in addpt_fields:
#     print(f'Field Name: {f.name}     Field Type: {f.type}     Field Length: {f.length}')
    
    
# # Add fields to working SGID Data
# arcpy.management.AddField(working_roads, "STREET", "TEXT", "", "", 60)
# arcpy.management.AddField(working_roads, "ALIAS1", "TEXT", "", "", 60)
# arcpy.management.AddField(working_roads, "ALIAS2", "TEXT", "", "", 60)
# arcpy.management.AddField(working_roads, "CAR", "TEXT", "", "", 20)
# arcpy.management.AddField(working_roads, "ELEVATION", "TEXT", "", "", 30)

# arcpy.management.AddField(working_addpts, "STREET", "TEXT", "", "", 60)
# arcpy.management.AddField(working_addpts, "APT_NUM", "TEXT", "", "", 20)
# arcpy.management.AddField(working_addpts, "G_CITY", "TEXT", "", "", 50)

###############
#  Functions  #
###############

def build_files_folders():
    # Create output folder
    if os.path.isdir(out_dir) == False:
        print(f"Creating {out_dir} ...")
        os.mkdir(out_dir)
    
    if not arcpy.Exists(gdu_roads):
        print(f"Creating {gdu_roads} ...")
        arcpy.management.CopyFeatures(gdu_road_schema, gdu_roads)
    
    if not arcpy.Exists(gdu_addpts):
        print(f"Creating {gdu_addpts} ...")
        arcpy.management.CopyFeatures(gdu_addpt_schema, gdu_addpts)


def get_sgid_data():
    if not arcpy.Exists(working_db):
        print(f"Creating {working_db} ...")
        arcpy.management.CreateFileGDB(work_dir, f"SGID_dumps_{today}.gdb")
    print("Copying roads from SGID ...")
    arcpy.management.CopyFeatures(sgid_roads, working_roads)
    print("Copying address points from SGID ...")
    arcpy.management.CopyFeatures(sgid_addpts, working_addpts)
    
    # Add fields to working data
    print("Adding fields to working feature classes ...")
    # Roads
    arcpy.management.AddField(working_roads, "STREET", "TEXT", "", "", 60)
    arcpy.management.AddField(working_roads, "ALIAS1", "TEXT", "", "", 60)
    arcpy.management.AddField(working_roads, "ALIAS2", "TEXT", "", "", 60)
    arcpy.management.AddField(working_roads, "CAR", "TEXT", "", "", 20)
    arcpy.management.AddField(working_roads, "ELEVATION", "TEXT", "", "", 30)
    # Address points
    arcpy.management.AddField(working_addpts, "STREET", "TEXT", "", "", 60)
    arcpy.management.AddField(working_addpts, "APT_NUM", "TEXT", "", "", 20)
    arcpy.management.AddField(working_addpts, "G_CITY", "TEXT", "", "", 50)


def build_schemas(rds, addpts):
    # Add road fields
    # arcpy.management.AddField(rds, "ID", "TEXT", "", "", 50)
    arcpy.management.AddField(rds, "ST_NAME", "TEXT", "", "", 50)       # preferred
    arcpy.management.AddField(rds, "ST_NM_A1", "TEXT", "", "", 50)
    arcpy.management.AddField(rds, "ST_NM_A2", "TEXT", "", "", 50)
    arcpy.management.AddField(rds, "NEIGHBH", "TEXT", "", "", 50)
    arcpy.management.AddField(rds, "CITY", "TEXT", "", "", 50)          # preferred
    arcpy.management.AddField(rds, "STATE", "TEXT", "", "", 50)         # preferred
    arcpy.management.AddField(rds, "ZIP", "TEXT", "", "", 5)            # preferred
    arcpy.management.AddField(rds, "CNT_NAME", "TEXT", "", "", 50)
    arcpy.management.AddField(rds, "AR_RT_FR", "TEXT", "", "", 50)
    arcpy.management.AddField(rds, "AR_RT_TO", "TEXT", "", "", 50)
    arcpy.management.AddField(rds, "AR_LT_FR", "TEXT", "", "", 50)
    arcpy.management.AddField(rds, "AR_LT_TO", "TEXT", "", "", 50)
    arcpy.management.AddField(rds, "SURFACE", "TEXT", "", "", 50)
    arcpy.management.AddField(rds, "SPEED_LM", "TEXT", "", "", 50)
    arcpy.management.AddField(rds, "CAR", "TEXT", "", "", 50)           # required: Allowed, Small vehicles only (mopeds), None, Disallowed
    arcpy.management.AddField(rds, "PEDEST", "TEXT", "", "", 50)
    arcpy.management.AddField(rds, "BIKE", "TEXT", "", "", 50)
    arcpy.management.AddField(rds, "SEPARATED", "TEXT", "", "", 50)
    arcpy.management.AddField(rds, "TURN_R", "TEXT", "", "", 50)
    arcpy.management.AddField(rds, "ELEVATION", "TEXT", "", "", 50)     # One of: bridge, tunnel, overpass, underpass
    
    # Add addpt fields
    arcpy.management.AddField(addpts, "ST_NUM", "TEXT", "", "", 10)     # required
    arcpy.management.AddField(addpts, "APT_NUM", "TEXT", "", "", 20)
    arcpy.management.AddField(addpts, "BLDG_NAME", "TEXT", "", "", 75)
    arcpy.management.AddField(addpts, "ST_NAME", "TEXT", "", "", 50)    # required
    arcpy.management.AddField(addpts, "NEIGHBH", "TEXT", "", "", 50)
    arcpy.management.AddField(addpts, "CITY", "TEXT", "", "", 50)       # required
    arcpy.management.AddField(addpts, "STATE", "TEXT", "", "", 2)       # required
    arcpy.management.AddField(addpts, "ZIP", "TEXT", "", "", 5)         # required
    arcpy.management.AddField(addpts, "CNT_NAME", "TEXT", "", "", 30)
    arcpy.management.AddField(addpts, "CNT_FIPS", "TEXT", "", "", 15)
    
    # Delete auto-generated ID fields
    arcpy.management.DeleteField(rds, "Id")
    arcpy.management.DeleteField(addpts, "Id")


def build_roads(work_rd, gdu_rd):
    # Calculate Road fields
    count = 0
    #             0         1          2        3         4             5
    fields = ['PREDIR', 'FULLNAME', 'STREET', 'CAR', 'VERT_LEVEL', 'ELEVATION',
    #   6           7            8            9           10             11     
    'AN_NAME', 'AN_POSTDIR', 'A1_PREDIR', 'A1_NAME', 'A1_POSTTYPE', 'A1_POSTDIR',
    #   12           13           14            15          16        17          18
    'A2_PREDIR', 'A2_NAME', 'A2_POSTTYPE', 'A2_POSTDIR', 'ALIAS1', 'ALIAS2', 'DOT_HWYNAM' ]
    with arcpy.da.UpdateCursor(work_rd, fields) as ucursor:
        print("Calculating Road fields ...")
        for row in ucursor:
            if row[0] is None: row[0] = ''
            if row[1] is None: row[1] = ''
            parts = [row[0], row[1]]
            row[2] = " ".join(parts)
            row[2] = row[2].strip().replace("  ", " ").replace("  ", " ").replace("  ", " ")
            row[2] = row[2][:60]
            row[3] = 'Allowed'
            if row[4] is None: row[4] = ''
            if row[4] in ('1', '2', '3'):
                row[5] = 'Overpass'
            else:
                row[5] = None
            
            # If numeric alias, numeric is alias1    
            if row[6] is not None and row[6] not in ('', ' '):
                row[16] = f'{row[0]} {row[6]} {row[7]}'
                row[16] = ' '.join(row[16].split()).strip()
                # If hwyname, hwyname is alias 2
                if row[18] is not None and row[18] not in ('', ' '):
                    row[17] = f'{row[0]} {row[18]}'
                    row[17] = ' '.join(row[17].split()).strip()
                # If no hwyname, a1 is alias 2
                else:
                    if row[9] is not None and row[9] not in ('', ' '):
                        row[17] = f'{row[0]} {row[9]} {row[10]} {row[11]}'
                        row[17] = ' '.join(row[17].split()).strip()
            # If no numeric alias, a1 is alias1  
            else:
                if row[9] is not None and row[9] not in ('', ' '):
                    row[16] = f'{row[0]} {row[9]} {row[10]} {row[11]}'
                    row[16] = ' '.join(row[16].split()).strip()
                # If hwyname, hwyname is alias 2
                if row[18] is not None and row[18] not in ('', ' '):
                    row[17] = f'{row[0]} {row[18]}'
                    row[17] = ' '.join(row[17].split()).strip()
                else:
                    if row[13] is not None and row[13] not in ('', ' '):
                        row[17] = f'{row[0]} {row[13]} {row[14]} {row[15]}'
                        row[17] = ' '.join(row[17].split()).strip()
        
            count += 1
            ucursor.updateRow(row)
    print(f'Total count of Road field updates: {count}')

    # Create Field Mapping for Roads
    fms_rds = arcpy.FieldMappings()
    
    fm_dict_rds = {'STREET': 'ST_NAME',
               'ALIAS1': 'ST_NM_A1',
               'ALIAS2': 'ST_NM_A2',
               'INCMUNI_L': 'CITY',
               'STATE_L': 'STATE',
               'ZIPCODE_L': 'ZIP',
               'FROMADDR_R': 'AR_RT_FR',
               'TOADDR_R': 'AR_RT_TO',
               'FROMADDR_L': 'AR_LT_FR',
               'TOADDR_L': 'AR_LT_TO',
               'SPEED_LMT': 'SPEED_LM',
               'CAR': 'CAR',
               'ELEVATION': 'ELEVATION',
               }
    
    for key in fm_dict_rds:
        fm_rds = arcpy.FieldMap()
        fm_rds.addInputField(working_roads, key)
        output_rds = fm_rds.outputField
        output_rds.name = fm_dict_rds[key]
        fm_rds.outputField = output_rds
        fms_rds.addFieldMap(fm_rds)
    
    # Append the new data
    print('Appending roads into GDU shapefile ...')
    query = """STATUS <> 'Planned' AND CARTOCODE NOT IN ('99', '15')"""
    arcpy.management.Append(work_rd, gdu_rd, "NO_TEST", field_mapping=fms_rds, expression=query)


def build_addpts(work_ap, gdu_ap):
    # Calculate Address point fields
    count = 0
    #             0             1             2             3          4         5          6        7          8           9
    fields = ['PrefixDir', 'StreetName', 'StreetType', 'SuffixDir', 'STREET', 'UnitID', 'APT_NUM', 'City', 'AddSystem', 'G_CITY']
    with arcpy.da.UpdateCursor(work_ap, fields) as ucursor:
        print("Calculating Address Point fields ...")
        for row in ucursor:
            if row[0] is None: row[0] = ''
            if row[1] is None: row[1] = ''
            if row[2] is None: row[2] = ''
            if row[3] is None: row[3] = ''
            parts = [row[0], row[1], row[2], row[3]]
            row[4] = " ".join(parts)
            row[4] = row[4].strip().replace("  ", " ").replace("  ", " ").replace("  ", " ")
            row[4] = row[4][:60]
            if row[5] is not None and row[5] not in ('', ' '):
                row[6] = f'#{row[5]}'
            if row[7] is not None and row[7] not in ('', ' '):
                row[9] = row[7]
            else:
                row[9] = row[8]
            count += 1
            ucursor.updateRow(row)
    print(f'Total count of Address Point field updates: {count}')
    
    # Create Field Mapping for Address Points
    fms_addpt = arcpy.FieldMappings()
    
    fm_dict_addpt = {'AddNum': 'ST_NUM',
                'APT_NUM': 'APT_NUM',
                'STREET': 'ST_NAME',
                'G_CITY': 'CITY',
                'State': 'STATE',
                'ZipCode': 'ZIP',
                'CountyID': 'CNT_FIPS'
                }
    
    for key in fm_dict_addpt:
        fm_addpt = arcpy.FieldMap()
        fm_addpt.addInputField(work_ap, key)
        output_addpt = fm_addpt.outputField
        output_addpt.name = fm_dict_addpt[key]
        fm_addpt.outputField = output_addpt
        fms_addpt.addFieldMap(fm_addpt)
    
    # Append the new data
    print('Appending address points into GDU shapefile ...')
    arcpy.management.Append(work_ap, gdu_ap, "NO_TEST", field_mapping=fms_addpt)
    

##########################
#  Call Functions Below  #
##########################
build_files_folders()
get_sgid_data()
# build_schemas(gdu_road_schema, gdu_addpt_schema)
build_roads(working_roads, gdu_roads)
build_addpts(working_addpts, gdu_addpts)


print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))
