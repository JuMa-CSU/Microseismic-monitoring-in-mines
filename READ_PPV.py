# -*- coding: utf-8 -*-
"""
READ_PPV

Created on Mon Mar  7 09:40:34 2016

@author:Ju Ma           Savka Dineva 
EMAIL:  ju.ma@ltu.se    sdineva@ltu.se


THIS SCRIPT IS USED TO READ IMS ASCII DATA AND WRITE THE PPVs IN EACH TRIGGER INTO A NEW FILE
THE OUTPUT WILL BE STORED IN 'PPV.txt'.

Copyright 2016 

"""


import os
import time
import shutil
import datetime
from distutils.dir_util import copy_tree

inputfiles=os.path.realpath(__file__)[:-15]+'ASCII'
outputfiles1=os.path.realpath(__file__)[:-15]+'ASCII_CR'#CR MEANS COMMA REPLACED
#outputfiles2=os.path.realpath(__file__)[:-15]+'ASCII_PPV'#PPV MEANS PEAK PARTICLE VELOCITY
#outputfiles2=os.path.realpath(__file__)[:-15]+'PPV/PPV.txt'#RFC MEANS READY FOR CONVERT
#outputfiles4=os.path.realpath(__file__)[:-15]+'MSEED'

####### STEP1 REPLACE ',' IN FLOAT WITH '.' && DELETE THE HEADER LINE #########


copy_tree(inputfiles, outputfiles1)

def FIND_FILES(directory):
    FILES_LIST=[]
    for path, subdirs, files in os.walk(directory): 
        for filename in files:
            FILES_LIST.append(os.path.join(path, filename))
    FILES_LIST.sort()
    return FILES_LIST


ASCII_files_list=FIND_FILES(inputfiles)
ASCII_files_list_comma_replaced= FIND_FILES(outputfiles1)
   

for i in range(len(ASCII_files_list)): 
    lines = file(ASCII_files_list[i], 'r').readlines() 
    
    del lines[0]
    
    for j in range(len(lines)): 
        lines[j]=lines[j][:2]+'.'+lines[j][3:18]+'.'+lines[j][19:34]+'.'+lines[j][35:]
    
    file(ASCII_files_list_comma_replaced[i], 'w').writelines(lines)
     

#################### STEP2 GENERATE THE PPV.TXT FILE ##########################


ASCII_files_list_comma_replaced= FIND_FILES(outputfiles1)

for i in range(len(ASCII_files_list_comma_replaced)): 
    lines = file(ASCII_files_list_comma_replaced[i], 'r').readlines()
    f=open(ASCII_files_list_comma_replaced[i],'r')
    
    data_channel_x=[]
    data_channel_y=[]
    data_channel_z=[]
    
    for line in f: 
        line = line.strip()
        columns=line.split(',')
        
        data_channel_x.append(float(columns[0]))
        data_channel_y.append(float(columns[1]))
        data_channel_z.append(float(columns[2]))
        
    data_channel_x_abs=map(abs,data_channel_x)
    data_channel_y_abs=map(abs,data_channel_y)
    data_channel_z_abs=map(abs,data_channel_z)
        
    ppv=max(max(data_channel_x_abs),max(data_channel_y_abs),max(data_channel_z_abs))
        
    index_ppv_x=data_channel_x_abs.index(max(data_channel_x_abs))
    index_ppv_y=data_channel_y_abs.index(max(data_channel_y_abs))
    index_ppv_z=data_channel_z_abs.index(max(data_channel_z_abs))
    
    if ppv in data_channel_x_abs:
        index_ppv=index_ppv_x
    elif ppv in data_channel_y_abs:
        index_ppv=index_ppv_y
    else:
        index_ppv=index_ppv_z
    
    sensor_sampling_rate=file(ASCII_files_list[i], 'r').readlines()[0].split(',')[1][:-2]
    sample_number_of_triggrt_time_relative_to_first_seismogram_sample=file(ASCII_files_list[i], 'r').readlines()[0].split(',')[10]
    trigger_time_seconds=file(ASCII_files_list[i], 'r').readlines()[0].split(',')[5]
    trigger_time_microseconds=file(ASCII_files_list[i], 'r').readlines()[0].split(',')[6]  
    
    Eventname=time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(float(trigger_time_seconds)))  
    ppv_ARRIVAL=float(trigger_time_microseconds+'e-06')+(index_ppv-int(sample_number_of_triggrt_time_relative_to_first_seismogram_sample))/float(sensor_sampling_rate)#relative to the trigger time
    PEAK_PARTICLE_VELOCITY=ppv
    Sensor_name=ASCII_files_list[i][-10:-6]
    
            
    with open('PPV_temp1.txt', 'a') as ppv_file:
        ppv_file.write(str(Eventname)+','+str("{0:.20f}".format(ppv_ARRIVAL))+','+str("{0:.20f}".format(PEAK_PARTICLE_VELOCITY))+','+str(Sensor_name)+'\n')
        
   
shutil.rmtree(outputfiles1)

############################ STEP3 ADD TITLE LINE TO PPV.txt ##################

f= open('PPV_temp1.txt', 'r')
content=f.read()
f.close()

lines = file('PPV_temp1.txt', 'r').readlines()#separate different event by blank line
for i in range(len(ASCII_files_list)-1):
    if ASCII_files_list[i][:-23]==ASCII_files_list[i+1][:-23]:
        f= open('PPV_temp2.txt', 'a')
        f.write(lines[i])
        f.close()       
    else: 
        f= open('PPV_temp2.txt', 'a')   
        f.write(lines[i])
        f.write('\n')
        f.close()
f= open('PPV_temp2.txt', 'a')   
f.write(lines[-1])
f.close()

f= open('PPV_temp2.txt', 'r')
content=f.read()
f.close()

f= open('PPV.txt', 'w')
f.write ('EVENT(NAMED BY TRIGGER TIME)'+','+'PPV_ARRIVAL(RELATIVE TO TRIGGER TIME(S))'+',' +'PEAK_PARTICLE_VELOCITY(M/S)'+','+'SENSOR ID'+'\n')
f.write(content)
f.close()

os.remove('PPV_temp1.txt')
os.remove('PPV_temp2.txt')

print 'WELL DONE, FINISH !'

