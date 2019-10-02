#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:44:11 2019

@author: hugo
"""

from utils import file_utils, pipeline_utils, spykingcircus_utils
import pipeline_params as prm
import sys
from analysis import waveform


# TODO : Kilosort support (or do I ?)
# TODO redo the debug file in a .py file
# TODO rewrite everything with proper naming convention ? :-(
# TODO merge pipeline and pipeline analysis

print('#########################')
print('# Pre-analysis pipeline #')
print('#########################\n\n')       

pipeline_utils.create_pipeline(prm.pipeline_name)

# First-level entry point : automated spike sorting has not taken place
if file_utils.variable_from_debugfile('SPIKE_SORTED', prm.pipeline_name) != 'True' :      
    
    # -------------------------------------------------------------------------
    # SPYKING CIRCUS 
    # supports data stream, so no merge is needed, thanks Pierre
    # -------------------------------------------------------------------------
    # Extracting data from raw.kwd
#    if prm.spike_sorter == 'Spyking-Circus' :
#        for i, kwd_file in enumerate(prm.kwd_path) :
#            print('# File %s / %s #' % (i+1, len(prm.kwd_path)))
#            file_utils.kwd_to_file(prm.kwd_path[i], prm.experiment_name[i], prm.pipeline_name,
#                                  prm.channel_map, prm.photodiode_index, 'bin', i,
#                                  verbose = prm.verbose)
#        
#        # Copying template files and calling spyking-circus
#        spykingcircus_utils.copy_file(prm.params_file, prm.pipeline_name, 'mydata_0.params')
#        spykingcircus_utils.copy_file(prm.prb_file, prm.pipeline_name, 'map.prb')
#        
#        spykingcircus_utils.call_circus(filename = 'mydata_0.bin',
#                                        n_cpu = prm.n_cpu,
#                                        hostfile = None, 
#                                        preview = prm.show_preview,
#                                        result = prm.show_results,
#                                        pipeline_name = prm.pipeline_name,
#                                        )
#        
#        
#            
#    # -------------------------------------------------------------------------
#    # KILOSORT 
#    # doesn't support data stream, so a merge is needed
#    # -------------------------------------------------------------------------        
#    elif prm.spike_sorter == 'Kilosort' :
#        if len(prm.kwd_path) > 1 :
#            for i, kwd_file in enumerate(prm.kwd_path) :
#                print('# File %s / %s #' % (i+1, len(prm.kwd_path)))
#                file_utils.kwd_to_file(prm.kwd_path[i], prm.experiment_name[i], prm.pipeline_name,
#                                      prm.channel_map, prm.photodiode_index,
#                                      'npy',
#                                      verbose = prm.verbose)
#            
#            file_utils.concatenate2D_from_disk(arrays_paths = [arr_name+'.npy' for arr_name in prm.experiment_name],
#                                               pipeline_name = prm.pipeline_name,
#                                               verbose = prm.verbose)
#            file_utils.concatenate1D_from_disk(arrays_paths = [arr_name+'_phtdiode.npy' for arr_name in prm.experiment_name],
#                                               pipeline_name = prm.pipeline_name,
#                                               output_name = 'phtdiode')
#            file_utils.concatenate1D_from_disk(arrays_paths = [arr_name+'_timestamps.npy' for arr_name in prm.experiment_name],
#                                               pipeline_name = prm.pipeline_name,
#                                               output_name = 'timestamps')
#        else :
#            print('# File 1 / 1 #' % (i+1, len(prm.kwd_path)))
#            file_utils.kwd_to_file(prm.kwd_path[i], prm.experiment_name[i], prm.pipeline_name,
#                                  prm.channel_map, prm.photodiode_index,
#                                  'bin',
#                                  verbose = prm.verbose)
#            
#    else :
#        print('Spike Sorter not supported')
    
    # Flags the Spike sorting as complete
    with open('./pipelines/%s/debugfile.txt' % prm.pipeline_name, 'a') as file:
                file.write('| SPIKE_SORTED = True | \n')
    print('# Spike sorting completed ! #')
        
    # Exit the pipeline to manually call phy, opening the folder if we're running from linux
    print('# Exiting pipeline for manual reviewing #')
    print('# Call Phy with phy template-gui params.py #')
    print('# Then rerun this script once more #')
          
    if sys.platform == 'linux' :
        pipeline_utils.open_sort_folder(prm.pipeline_name)
              
              
else :    
    print('# Data has already been spike sorted and curated #\n')
          
    if prm.do_clean :
        pipeline_utils.clean_up(prm.pipeline_name, prm.verbose)
        
    if prm.export :
        pipeline_utils.export_to_results(prm.pipeline_name, prm.verbose)
        
    print('# All done ! Run pipeline_analysis.py to continue #')
          
          