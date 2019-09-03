#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:44:11 2019

@author: hugo
"""

import pipeline_params as prm
from analysis import waveform, photodiode, mc



print('########################')
print('#  Analysis pipeline   #')
print('########################\n\n')       

    
# Classifies the waveforms
if prm.do_wav :
    waveform.waveform_analysis(folder_list=prm.wav_analysis_folders, n_chan=len(prm.channel_map),
                               lowcut=prm.lowcut, highcut = prm.highcut, fs = prm.fs, order = prm.order,
                               n_spikes = prm.n_spikes, window_size = prm.window_size,
                               debug_plot = prm.debug_plot, verbose=prm.verbose,
                               n_clusters=prm.n_clusters, k_init = prm.k_init)    
        
# Extract the photodiode data 
if prm.do_photodiode :
    photodiode.export_sequences_times(folder_list = prm.photodiode_folders,
                                      beg_index = prm.beg_index, end_index = prm.end_index,
                                      flash_height = prm.flash_height_percentile,
                                      baseline_height = prm.baseline_height_percentile,
                                      width = prm.width, fs = prm.fs,
                                      verbose = prm.verbose)
    
# Does the full package analysis for MotionClouds    
if prm.do_mc : 
    mc.mc_analysis(folder_list = prm.mc_analysis_folders, 
                   N_thetas = prm.N_thetas, min_theta = prm.min_theta, max_theta = prm.max_theta,
                   N_Bthetas = prm.N_Bthetas, min_btheta = prm.min_btheta, max_btheta = prm.max_btheta,
                   rectification_btheta= prm.rectification_btheta,
                   stim_duration = prm.stim_duration, repetition = prm.repetition, seed = prm.seed,
                   fs = prm.fs, beg_psth = prm.beg_psth, end_psth = prm.end_psth, binsize = prm.binsize,
                   win_size = prm.win_size, step_size = prm.step_size,
                   verbose = prm.verbose)
