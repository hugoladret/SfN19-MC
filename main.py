#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:44:11 2019

@author: hugo
"""

from utils import file_utils, pipeline_utils
import numpy as np

# Temporary autorun debug code
pipeline_name = 'Autobahn'
kwd_path = '../A005_a17/experiment1_100.raw.kwd'
experiment_name = 'A005_a17'
channel_map = np.array([1, 17, 16, 32, 3, 19, 14, 30, 9, 25, 10, 20, 8, 24, 2, 29, 7, 26, 15, 21, 11,
                        23, 12, 28, 6, 18, 13, 22, 5, 27, 4, 31]) - 1 #the chmap formerly known as matlab
photodiode_index = 70
verbosity = True

# Temporary autorun debug code, merge case
kwd_path = ['../A005_a17/experiment1_100.raw.kwd', '../A005_a17/experiment1_100.raw.kwd']
experiment_name = ['A005_a17', 'A005_a17bis']

print('########################')
print('# THE ANALYZATOR 2019  #')
print('########################')      
print("\n   Let's begin !!  \n")   

# TODO : write a sumup of the params and ask if its ok
# TODO : control progressx with loop

folder_status = pipeline_utils.create_pipeline(pipeline_name)

if file_utils.variable_from_debugfile('SPIKE_SORTED', pipeline_name) != 'True' :
    if type(kwd_path) != str and len(kwd_path) > 1 :
        print('Multiple files chosen as input, the pipeline includes a merge step.\n')
        
        for i, kwd_file in enumerate(kwd_path) :
            print('# File %s / %s #' % (i+1, len(kwd_path)))
            file_utils.kwd_to_file(kwd_path[i], experiment_name[i], pipeline_name,
                                  channel_map, photodiode_index,
                                  'npy',
                                  verbose = verbosity)
        
        file_utils.concatenate2D_from_disk(arrays_paths = [arr_name+'.npy' for arr_name in experiment_name],
                                           pipeline_name = pipeline_name,
                                           verbose = verbosity)
        file_utils.concatenate1D_from_disk(arrays_paths = [arr_name+'_phtdiode.npy' for arr_name in experiment_name],
                                           pipeline_name = pipeline_name,
                                           output_name = 'phtdiode')
        file_utils.concatenate1D_from_disk(arrays_paths = [arr_name+'_timestamps.npy' for arr_name in experiment_name],
                                           pipeline_name = pipeline_name,
                                           output_name = 'timestamps')
        
        # Spike sorting takes place here
        
        with open('./pipelines/%s/debugfile.txt' %pipeline_name, 'a') as file:
                    file.write('| SPIKE_SORTED = True | \n')
        
    
    else :
        print('A single file was chosen as input, no merge step is needed.\n')
        file_utils.kwd_to_file(kwd_path, experiment_name, pipeline_name,
                              channel_map, photodiode_index,
                              'bin',
                              verbose = verbosity)
        
else :
    print('Post sorting')