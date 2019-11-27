# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 16:35:37 2019
@author: eneemann
Script to crawl directory and update all SDE connections in all MXDs

***Must use Python 2 Interpreter to use arcpy.mapping module and work with MXDs***
"""

import arcpy
import os
import time

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))

######################
#  Set up variables  #
######################

# ArcMap Connections (typically found in "Users\username" or "Database Connections")
# May need to run accompanying script to find all SDE connections first
# List all past connections to the old SGID10
old_1 = r"C:\Users\dbuell\AppData\Roaming\ESRI\Desktop10.5\ArcCatalog\Connection to sgid.agrc.utah.gov.sde"
old_2 = r"C:\Users\dbuell\AppData\Roaming\ESRI\Desktop10.3\ArcCatalog\DC_AGRC@SGID10@gdb10.agrc.utah.gov.sde"
old_3 = r"Database Connections\Connection to sgid.agrc.utah.gov.sde"
old_4 = r"Database Connections\sde@SGID10@sgid.agrc.utah.gov.sde"
old_5 = r"C:\Users\DBuell\AppData\Roaming\ESRI\Desktop10.0\ArcCatalog\DC_ AGRC@SGID10@ITDB104SP.DTS.UTAH.GOV.sde"
old_6 = r"C:\Users\dbuell\AppData\Roaming\ESRI\Desktop10.1\ArcCatalog\DC_AGRC@SGID10@gdb10.agrc.utah.gov.sde"
old_7 = r"Database Connections\sgid.agrc.utah.gov.sde"

# Combine past connections into a list; will use later for
old_list = [old_1, old_2, old_3, old_4, old_5, old_6, old_7]

# Create variables for new database connection and root directory to crawl
new_SGID_internal = r"Database Connections\internal@SGID@internal.agrc.utah.gov.sde"
root_dir = r'C:\E911'

###############
#  Functions  #
###############

def crawl_and_update_mxds(folder):
    # Function to update SDE connection to SGID10 in all MXDs
    count = 0
    # Crawl directory and get files
    for root, dirs, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(".mxd"):             # Only look at MXDs
                count += 1
                mxdName = os.path.splitext(f)[0]
                mxdPath = os.path.join(root, f)
                mxd = arcpy.mapping.MapDocument(mxdPath)
                dataframes = arcpy.mapping.ListDataFrames(mxd)
                # Go through each layer in in the MXD dataframes
                for df in dataframes:
                    dfDesc = df.description if df.description != "" else "None"
                    layers = arcpy.mapping.ListLayers(mxd, "", df)
                    for lyr in layers:
                        if lyr.supports("DATASOURCE"):
                            # GNIS layer is renamed in internal SGID, so just remove the layer from all MXDs
                            if 'gnis' in lyr.name.lower():
                                arcpy.mapping.RemoveLayer(df, lyr)
                            else:
                                # Make list to populate with full connection/layer paths
                                old_connections = []
                                name = lyr.name
                                # Build list of full connection/layer paths
                                for conn in old_list:
                                    old_connections.append(os.path.join(conn, name))
                                # Rename layer to new internal SGID name if it's source is the old SGID connection
                                if lyr.dataSource in old_connections:
                                    new_name = name.replace('SGID10', 'SGID')
                                    try:
                                        # Replace the data source/layer name with new connection and layer name
                                        lyr.replaceDataSource(new_SGID_internal, "SDE_WORKSPACE", new_name)
                                    # Catch potential errors and list MXD path and layer name that caused problem
                                    except arcpy.ExecuteError:
                                        print('MXD Path is: {}'.format(mxdPath))
                                        print('Layer is: {}'.format(lyr.name))
                                    except ValueError:
                                        print('MXD Path is: {}'.format(mxdPath))
                                        print('Layer is: {}'.format(lyr.name))

                                    # Rename layer in MXD to new layer name
                                    lyr.name = new_name
                # Save the MXD with new connection and layer names
                mxd.save()
                if count % 10 == 0:
                    print('Done with MXD number: {}'.format(count))
                del mxd


##########################
#  Call Functions Below  #
##########################

crawl_and_update_mxds(root_dir)


print("Script shutting down ...")
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script end time is {}".format(readable_end))
print("Time elapsed: {:.2f}s".format(time.time() - start_time))