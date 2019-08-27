#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:44:11 2019

@author: hugo

Contains the functions to manipulate folders for the pipeline such as :
    Creating the pipeline folder and debugfile
"""

import os
import subprocess
import shutil
import fileinput
import sys


def create_pipeline(pipeline_name, verbose = True):
    '''
    Creates a pipeline folder, which will contain :
        In either case :
            The binary file sent to Spyking Circus
        In case of merging :
            Temporarily the multiple numpy arrays from the multiple raw kwd files
            Permanently the merged numpy array
    '''
    print('# Creating a new pipeline #')
          
    path = './pipelines/'+pipeline_name
    
    if verbose : print('Initializing a new pipeline in %s ...' % path)
    
    if not os.path.exists(path):
        os.makedirs(path)
        os.makedirs(path+'/bins')
        os.makedirs(path+'/sorted')
        with open('./pipelines/%s/debugfile.txt' %pipeline_name, 'a') as file:
                file.write('## Debug file, do not delete unless you want to spike sorting to rerun ##\n')
        if verbose : print('Done !\n')
        
    else:
        print('A pipeline already exists under this name !\n')
       
# --------------------------------------------------------------
#
# --------------------------------------------------------------
        
def call_phy(pipeline_name, data_name) :
    try :
        subprocess.call(['phy', 'template-gui', 'params.py'], 
                        cwd = './pipelines/%s/%s/%s-merged.GUI/' % (pipeline_name, data_name, data_name))
    except AttributeError: 
        print('Closing Phy')

# --------------------------------------------------------------
#
# --------------------------------------------------------------
    
def clean_up(pipeline_name, verbose = True) :
    '''
    Restructure the pipeline folders to be a bit more user-friendly, my bad for poor initial structure
    
    moves photodiode and timestamps bin files back into the main folder
    removes the channel map and the parameter files
    move merged and clean data into the main folder - rewrites dat_path and dir_path accordingly
    '''
    print('# Moving files around #')
          
    binpath = './pipelines/%s/bins/' % pipeline_name
    mainpath = './pipelines/%s/' % pipeline_name
    npypath = './pipelines/%s/mydata_0/mydata_0-merged.GUI/' % pipeline_name
    sortingpath = './pipelines/%s/mydata_0/' % pipeline_name
    
    # Removes the spike sorting files
    main_files = [file for file in os.listdir(mainpath) if os.path.isfile(os.path.join(mainpath, file))]
    for main_file in main_files :
        if '.prb' in main_file or '.params' in main_file or '.log' in main_file :
            os.remove(mainpath + main_file)
    
    # Moves the bin files
    if os.path.exists(binpath) :
        extra_bins = [file for file in os.listdir(binpath) if os.path.isfile(os.path.join(binpath, file))]
        for extra_bin in extra_bins :
            shutil.move(binpath + extra_bin , mainpath + extra_bin)
            if verbose : print('Moving %s' % extra_bin)
        
        shutil.rmtree(binpath, ignore_errors = True) #in case of a read-only lock
    
    # Moves the npy files
    if os.path.exists(npypath) :
        for file in os.listdir(npypath) :
            shutil.move(npypath + file , mainpath + '/sorted/' + file)
            if verbose : print('Moving %s' % file)
            
        shutil.rmtree(npypath, ignore_errors = True)
    
    shutil.rmtree(sortingpath, ignore_errors = True)
    
    # Rewrites the paths accordingly
    # https://stackoverflow.com/questions/39086/search-and-replace-a-line-in-a-file-in-python
    file = mainpath + '/sorted/' +'params.py'
    searchExp = 'dir_path'
    replaceExp = 'dir_path = r"%s/pipelines/%s/sorted/"\n' % (os.getcwd(), pipeline_name)
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = replaceExp
        sys.stdout.write(line)
        