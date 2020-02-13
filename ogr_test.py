# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 08:33:24 2020

@author: eneemann
"""

import os
import subprocess

directory = r'C:\Users\eneemann\Desktop\Temp'
os.chdir(directory)

data = 'UT_UVA_metadata_seam_2019.geojson'
filename = os.path.join(directory, data)
file_short = data
outname = os.path.join(directory, 'output_data.shp')
out_short = 'output_data.shp'
command = f"""ogr2ogr -nlt POLYGON -skipfailures -f "ESRI Shapefile" """ + f" {out_short} {file_short}"
print(command)
subprocess.check_call(command)