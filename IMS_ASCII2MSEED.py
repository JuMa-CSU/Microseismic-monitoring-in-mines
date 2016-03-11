# -*- coding: utf-8 -*-
"""
IMS_ASCII2MSEED

Created on Mon Mar  7 09:40:34 2016

@author:Ju Ma           Savka Dineva 
EMAIL:  ju.ma@ltu.se    sdineva@ltu.se


JUST KEEP THIS IMS_ASCII2MSEED.py IN THE SAME FOLDER WITH YOUR IMS_ASCII DATA AND 
ENSURE THAT THE FOLDER IS NAMED 'ASCII'. ALL THE IMS_ASCII DATA WILL BE CONVERTED
TO MINISEED FOMATE AFTER YOU RUN THE SCUPIT. THE OUTPUT WILL BE STORED IN 'MSEED' FOLDER.

Requires:ascii2mseed(IRIS SeisCode) should be installed on your computer.
In most environments a simple 'make' will build the program.
Don't forget copy the executable ascii2mseed file to /usr/bin/.


Copyright 2016 

"""


import os
import csv
import time
import shutil
import datetime
import subprocess
from distutils.dir_util import copy_tree
start = time.time()#Measuring Execution Times

inputfiles=os.path.realpath(__file__)[:-22]+'ASCII'
outputfiles1=os.path.realpath(__file__)[:-22]+'ASCII_CR'#CR MEANS COMMA REPLACED
outputfiles2=os.path.realpath(__file__)[:-22]+'ASCII_CI'#CI MEANS CHANNEL INDIVIDUALIZED
outputfiles3=os.path.realpath(__file__)[:-22]+'ASCII_RFC'#RFC MEANS READY FOR CONVERT
outputfiles4=os.path.realpath(__file__)[:-22]+'MSEED'

################ STEP1 REPLACE ',' IN FLOAT WITH '.' ##########################

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
        
    for j in range(len(lines)): 
        lines[j]=lines[j][:2]+'.'+lines[j][3:18]+'.'+lines[j][19:34]+'.'+lines[j][35:]
    
    file(ASCII_files_list_comma_replaced[i], 'w').writelines(lines)
     

############# STEP2 SAVE EACH CHANNEL DATA TO AN INDIVIDUALLY FILE ############

copy_tree(outputfiles1, outputfiles2)

ASCII_files_list_comma_replaced= FIND_FILES(outputfiles1)
ASCII_files_list_channel_individualized=FIND_FILES(outputfiles2)
 
for i in range(len(ASCII_files_list_comma_replaced)): 
    
    f= open(ASCII_files_list_comma_replaced[i], 'rb') 
    reader = csv.reader(f, delimiter=',')
    header = reader.next()
    zipped = zip(*reader)
    
    channelX=zipped[0]
    channelY=zipped[1]
    channelZ=zipped[2]
    
    with open(ASCII_files_list_channel_individualized[i].replace('.asc','.Channel_X'), 'w') as f:
        for tuple in channelX:
            f.write('%s \n' % tuple)
    with open(ASCII_files_list_channel_individualized[i].replace('.asc','.Channel_Y'), 'w') as f:
        for tuple in channelY:
            f.write('%s \n' % tuple)
    with open(ASCII_files_list_channel_individualized[i].replace('.asc','.Channel_Z'), 'w') as f:
        for tuple in channelZ:
            f.write('%s \n' % tuple)
    

for f in ASCII_files_list_channel_individualized:
    os.remove(f)

##################### STEP3 PREPARE DATA FOR CONVERT ##########################

copy_tree(outputfiles2, outputfiles3)

ASCII_files_list_channel_individualized=FIND_FILES(outputfiles2)
ASCII_files_list_ready_for_convert=FIND_FILES(outputfiles3)

for i in range(len(ASCII_files_list_ready_for_convert)): 
    
    f = open(ASCII_files_list_ready_for_convert[i])
    text = f.read()
    f.close()

    f = open(ASCII_files_list_ready_for_convert[i], 'w')
    f1=open(ASCII_files_list_channel_individualized[i])
    
    SourceName='TIMESERIES IMS'+ASCII_files_list_ready_for_convert[i][-17:-11]+'_'+ASCII_files_list_ready_for_convert[i][-1]
    lines=f1.readlines()
    samples=str(len(lines))+' samples'
    
    sensor_sampling_rate=file(ASCII_files_list[i/3], 'r').readlines()[0].split(',')[1][:-2]
    sps=sensor_sampling_rate+' sps'   
      
    trigger_time_seconds=file(ASCII_files_list[i/3], 'r').readlines()[0].split(',')[5]
    trigger_time_microseconds=file(ASCII_files_list[i/3], 'r').readlines()[0].split(',')[6]  
    sample_number_of_triggrt_time_relative_to_first_seismogram_sample=file(ASCII_files_list[i/3], 'r').readlines()[0].split(',')[10]
    first_sample_time_prior_to_trigger_time=int(sample_number_of_triggrt_time_relative_to_first_seismogram_sample)/float(sensor_sampling_rate)
    
    trigger_time_in_local_time_formate=time.strftime("%Y,%m,%d,%H,%M,%S", time.gmtime(float(trigger_time_seconds)))
 
    Time=datetime.datetime.strptime(trigger_time_in_local_time_formate, '%Y,%m,%d,%H,%M,%S')+datetime.timedelta(seconds=float(trigger_time_microseconds+'e-06'))-datetime.timedelta(seconds=first_sample_time_prior_to_trigger_time)  #Time of first sample in ISO YYYY-MM-DDTHH:MM:SS.FFFFFF    
    Time=Time.strftime("%Y-%m-%dT%H:%M:%S.%f")
    
    Format='SLIST'
    Type='FLOAT'
    Units='M/S'
    
    f.write(SourceName+', '+samples+', ' +sps+', '+Time+', '+Format+', '+Type+', '+Units+'\n')

    f.write(text)
    f.close()

##################### STEP4 CONVERT ASCII TO MINISEED #########################

copy_tree(outputfiles3, outputfiles4)

ASCII_files_list_ready_for_convert=FIND_FILES(outputfiles3)
miniseed_file_list=FIND_FILES(outputfiles4)


for i in range(len(ASCII_files_list_ready_for_convert)):
    inputfile_final=ASCII_files_list_ready_for_convert[i]
    outputfile_final=miniseed_file_list[i]
    subprocess.call(["ascii2mseed",inputfile_final,"-o",outputfile_final])
    
shutil.rmtree(outputfiles1)
shutil.rmtree(outputfiles2)
shutil.rmtree(outputfiles3)



print 'WELL DONE, FINISH !'
print 'Execution Time %s Seconds' %(time.time() -start )

