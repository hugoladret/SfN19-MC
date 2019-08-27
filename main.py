#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:44:11 2019

@author: hugo
"""

from utils import file_utils, pipeline_utils, spykingcircus_utils
import numpy as np
import multiprocessing


# -------------------------------------------------------------------------
# Parameters
# TODO : make it a separate file
# -------------------------------------------------------------------------

# Pre-sorting params
pipeline_name = 'A005_a17'
verbose = True

experiment_name = ['A005_a17', 'A005_a17bis']
experiment_name = ['A005_a17']

kwd_path = ['../A005_a17/experiment1_100.raw.kwd', '../A005_a17/experiment1_100.raw.kwd']
kwd_path = ['../A005_a17/experiment1_100.raw.kwd']

channel_map = np.array([1, 17, 16, 32, 3, 19, 14, 30, 9, 25, 10, 20, 8, 24, 2, 29,
                        7, 26, 15, 21, 11, 23, 12, 28, 6, 18, 13, 22, 5, 27, 4, 31]) - 1 
photodiode_index = 70

# Spike sorting params
spike_sorter = 'Spyking-Circus'
prb_file = 'SC_32chan_100um.prb'
params_file = 'single_file_MC2019.params' # in case of multiple files, the .params must include the multi-files flag
n_cpu = multiprocessing.cpu_count() #use max number of available CPUs

show_preview = True
show_results = True

# Manual curation params
do_phy = True

# File sorting params
do_clean = True #moves useful files and removes useless ones


# -------------------------------------------------------------------------
# Main Script
# -------------------------------------------------------------------------

print('########################')
print('# THE ANALYZATOR 2019  #')
print('########################\n\n')       

pipeline_utils.create_pipeline(pipeline_name)

# First-level entry point : automated spike sorting has not taken place
if file_utils.variable_from_debugfile('SPIKE_SORTED', pipeline_name) != 'True' :      
    
    # -------------------------------------------------------------------------
    # SPYKING CIRCUS 
    # supports data stream, so no merge is needed, thanks Pierre
    # -------------------------------------------------------------------------
    # Extracting data from raw.kwd
    if spike_sorter == 'Spyking-Circus' :
        for i, kwd_file in enumerate(kwd_path) :
            print('# File %s / %s #' % (i+1, len(kwd_path)))
            file_utils.kwd_to_file(kwd_path[i], experiment_name[i], pipeline_name,
                                  channel_map, photodiode_index, 'bin', i,
                                  verbose = verbose)
        
        # Copying template files and calling spyking-circus
        spykingcircus_utils.copy_file(params_file, pipeline_name, 'mydata_0.params')
        spykingcircus_utils.copy_file(prb_file, pipeline_name, 'map.prb')
        
        spykingcircus_utils.call_circus(filename = 'mydata_0.bin',
                                        n_cpu = n_cpu,
                                        hostfile = None, 
                                        preview = show_preview,
                                        result = show_results,
                                        pipeline_name = pipeline_name,
                                        )
        
        
            
    # -------------------------------------------------------------------------
    # KILOSORT 
    # doesn't support data stream, so a merge is needed
    # TODO : finish support of Kilosort, requires matlab licence
    # -------------------------------------------------------------------------        
    elif spike_sorter == 'Kilosort' :
        if len(kwd_path) > 1 :
            for i, kwd_file in enumerate(kwd_path) :
                print('# File %s / %s #' % (i+1, len(kwd_path)))
                file_utils.kwd_to_file(kwd_path[i], experiment_name[i], pipeline_name,
                                      channel_map, photodiode_index,
                                      'npy',
                                      verbose = verbose)
            
            file_utils.concatenate2D_from_disk(arrays_paths = [arr_name+'.npy' for arr_name in experiment_name],
                                               pipeline_name = pipeline_name,
                                               verbose = verbose)
            file_utils.concatenate1D_from_disk(arrays_paths = [arr_name+'_phtdiode.npy' for arr_name in experiment_name],
                                               pipeline_name = pipeline_name,
                                               output_name = 'phtdiode')
            file_utils.concatenate1D_from_disk(arrays_paths = [arr_name+'_timestamps.npy' for arr_name in experiment_name],
                                               pipeline_name = pipeline_name,
                                               output_name = 'timestamps')
        else :
            print('# File 1 / 1 #' % (i+1, len(kwd_path)))
            file_utils.kwd_to_file(kwd_path[i], experiment_name[i], pipeline_name,
                                  channel_map, photodiode_index,
                                  'bin',
                                  verbose = verbose)
            
    else :
        print('Spike Sorter not supported')
    
    # Flags the Spike sorting as complete
    with open('./pipelines/%s/debugfile.txt' %pipeline_name, 'a') as file:
                file.write('| SPIKE_SORTED = True | \n')
    print('# Spike sorting completed ! #')
          
    # Open the phy template-gui for manual reviewing
    if do_phy :
        pipeline_utils.call_phy(pipeline_name, 'mydata_0')
    else :
        print('# Exiting pipeline for manual reviewing #')
              
else :    
    print('# Data has already been spike sorted and curated #')
    if do_clean :
        pipeline_utils.clean_up(pipeline_name)
    
    