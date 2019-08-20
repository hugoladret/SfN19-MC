#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:44:11 2019

@author: hugo
"""

from utils import file_utils, pipeline_utils

# Temporary autorun debug code
pipeline_name = 'Autobahn'
kwd_path = '../A005_a17/experiment1_100.raw.kwd'
experiment_name = 'A005_a17'

print('########################')
print('# THE ANALYZATOR 2019  #')
print('########################')   
      
print("\nLet's begin !!\n")   

print('# Creating a new pipeline #')
status = pipeline_utils.create_pipeline(pipeline_name)
print('\n')

print('# Converting a kwd file to numpy #')
file_utils.kwk_to_npy(kwd_path, experiment_name,
                      pipeline_name)
print('\n')

print('# Converting a npy file to bin #')
file_utils.np_to_bin(experiment_name, pipeline_name)