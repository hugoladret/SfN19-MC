#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:44:11 2019

@author: hugo

Contains the functions to manipulate folders for the pipeline such as :
    Creating the pipeline folder and debugfile
"""

import os

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
        debugfile = open(path+'/debugfile.txt', 'w+')
        if verbose : print('Done !\n')
        return 1
    else:
        print('A pipeline already exists under this name !')
        return 0
    
    
