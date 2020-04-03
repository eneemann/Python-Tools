# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 06:20:14 2020

@author: eneemann
"""

import os
import time
import arcpy
from arcpy import env

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print("The script start time is {}".format(readable_start))

today = time.strftime("%Y%m%d")

work_dir = r'C:\Users\eneemann\Desktop\Python Code\Python Tools\PLSS'
out_file = os.path.join(work_dir, 'PLSS_GDrive_file_list_' + today + '.txt')

target_dir = r'G:\Shared drives\AGRC Projects\PLSS Fabric\Data\CountyData'

pdf_total = 0
gdb_total = 0
fc_total = 0
gdb_row_total = 0
with open(out_file, 'w') as writer:
    print(f'Crawling through {work_dir} ...')
    writer.write(f'Crawling through {target_dir} ...' + '\n')
    for directory, subdirlist, filelist in os.walk(target_dir):
        subdirlist.sort()
        print('\t' + directory)
        writer.write('\t' + directory + '\n')
        if directory.endswith('.gdb'):
            print('\t' + '\t' + 'Geodatabase found:')
            writer.write('\t' + '\t' + 'Geodatabase found:' + '\n')
            print('\t' + '\t' + '\t' + directory)
            writer.write('\t' + '\t' + '\t' + directory + '\n')
            gdb_total += 1
            env.workspace = directory
            fclist = arcpy.ListFeatureClasses()
            fclist.sort()
            for fc in fclist:
                fc_total += 1
                rows = int(arcpy.management.GetCount(fc).getOutput(0)) 
                gdb_row_total += rows
                print('\t' + '\t' + '\t' + '\t' + f'{fc} ({rows} rows)')
                writer.write('\t' + '\t' + '\t' + '\t' + f'{fc} ({rows} rows)' + '\n')
            del fclist
            
        count = 0
        for f in sorted(filelist):
            # print(f'f is {f}')
            # if '.gdb' not in f and '00000' not in f:
            # if '00000' not in f and not f.endswith('.gdb') and not f.endswith('.lock'):
            if '00000' not in f and not f.endswith('.lock'):
                print('\t' + '\t' + f)
                writer.write('\t' + '\t' + f + '\n')
                if f.endswith('.pdf') or f.endswith('.PDF'):
                    count += 1
                    pdf_total += 1
            # if f.endswith('.gdb'):
            #     print('\t' + '\t' + 'Geodatabase found:')
            #     writer.write('\t' + '\t' + 'Geodatabase found:' + '\n')
            #     print('\t' + '\t' + '\t' + f)
            #     writer.write('\t' + '\t' + '\t' + f + '\n')
        if count > 0:
            print(f'Number of PDFs in directory: {count}')
            writer.write('\t' + '\t' + f'Number of PDFs in directory: {count}' + '\n')
                
    print(f'Total number of PDFs: {pdf_total}')
    writer.write('\n')
    writer.write((f'Total number of PDFs: {pdf_total}' + '\n'))
    print(f'Total number of geodatabases: {gdb_total}')
    writer.write((f'Total number of geodatabases: {gdb_total}' + '\n'))
    print(f'Total number of feature classes: {fc_total}')
    writer.write((f'Total number of feature classes: {fc_total}' + '\n'))
    print(f'Total number of feature class rows: {gdb_row_total}')
    writer.write((f'Total number of feature class rows: {gdb_row_total}' + '\n'))
    writer.write('\n')
           
    
print('Script shutting down ...')
writer.write('Script shutting down ...' + '\n'))
# Stop timer and print end time in UTC
readable_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print('The script end time is {}'.format(readable_end))
writer.write('The script end time is {}'.format(readable_end) + '\n')
print('Time elapsed: {:.2f}s'.format(time.time() - start_time))
writer.write('Time elapsed: {:.2f}s'.format(time.time() - start_time) + '\n')