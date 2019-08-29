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



print('########################')
print('#  Analysis pipeline   #')
print('########################\n\n')       

    
# -------------------------------------------------------------------------
# Main Script
# -------------------------------------------------------------------------    
waveform.waveform_analysis(folder_list=prm.analysis_folders, n_chan=len(prm.channel_map),
                           lowcut=prm.lowcut, highcut = prm.highcut, fs = prm.fs, order = prm.order,
                           n_spikes = prm.n_spikes, window_size = prm.window_size,
                           debug_plot = prm.debug_plot, verbose=prm.verbose,
                           n_clusters=prm.n_clusters, k_init = prm.k_init)    
    