#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import multiprocessing

verbose = True

# --------------------------------------------------------------
# Pre-sorting parameters
# --------------------------------------------------------------
kwd_path = ['../rawdata/A005/experiment1_100.raw.kwd'] # path of the raw files, must be of same dimension as experiment_name
pipeline_name = 'V7_a17_B008' # name of the folder created under /pipelines/
experiment_name = ['V7_a17_B008'] # name of the temporary files for concatenation cases

channel_map = np.array([1, 17, 16, 32, 3, 19, 14, 30, 9, 25, 10, 20, 8, 24, 2, 29,
                        7, 26, 15, 21, 11, 23, 12, 28, 6, 18, 13, 22, 5, 27, 4, 31]) - 1  # channel map to extract from the raw file
photodiode_index = 70 # index of the photodiode signal in the raw files

# --------------------------------------------------------------
# Spike Sorting parameters
# --------------------------------------------------------------
spike_sorter = 'Spyking-Circus'
prb_file = 'SC_32chan_100um.prb'
params_file = 'single_file_MC2019.params' # in case of multiple files, the .params must include the multi-files flag
n_cpu = multiprocessing.cpu_count() #use max number of available CPUs

show_preview = True
show_results = True

# --------------------------------------------------------------
# Post-spike sorting cleaning parameters
# --------------------------------------------------------------
do_clean = False # moves useful files and removes useless ones
export = True # moves the files to result folder




# --------------------------------------------------------------
# Analysis metaparameters
# Usually wav_analysis_folders > other folders, as we want the maximum neurons to run a kmeans
# But not all of those neurons were recorded during MotionClouds or gratings sessions
# --------------------------------------------------------------
do_wav = True
wav_analysis_folders = ['V7_a17_B008'] # result subfolder to be considered in the waveform analysis process

do_photodiode = True
photodiode_folders = ['V7_a17_B008']

do_mc = True
mc_analysis_folders = ['V7_a17_B008'] # result subfolder to be considered in the MotionClouds analysis process

do_idcard = True
idcard_folders = ['V7_a17_B008']

# --------------------------------------------------------------
# Waveform analysis parameters
# --------------------------------------------------------------
lowcut = 300.0 # Hz
highcut = 3000.0 # Hz
order = 6
fs = 30000.0 # Hz

n_spikes = 1000 # number of spikes to extract to get the mean waveform
window_size = 30 # points/2 around the spiketime
debug_plot = False #show the carac points and mean waveform

n_clusters = 2 # K-means number of cluster
k_init = 'k-means++' # K-means init method, K++ uses the pca as barycenters

# --------------------------------------------------------------
# Photodiode extraction parameters 
# --------------------------------------------------------------
beg_index = 30 # int(len(signal)/beg_index), index at which to end the signal beg visualisation
end_index = 29 # end_index * int(len(signal)/beg_index), index at which to start the signal end visualisation
flash_height_percentile = 99 # np.percentile(signal, 99) height of photodiode blinks
baseline_height_percentile = 50 # height of the average signal, to distinguish start and end
width = 280 #units, if there is too much sequences compared to theoritical results, increase this param

# --------------------------------------------------------------
# Sequence generation
# --------------------------------------------------------------
seq_type = 'long_fix_mc' 

if seq_type == 'long_fix_mc' :
    N_thetas = 12 # np.linspace(min_theta, max_theta, N_thetas)
    min_theta = 0
    max_theta = np.pi
    
    N_Bthetas = 8 # np.linspace(min_btheta, max_btheta, N_Bthetas)
    min_btheta = np.pi/2 
    max_btheta = np.pi/32
    rectification_btheta = 2.5
    
    stim_duration = 2 # duration of stim for debug purposes
    repetition = 15 # nr of sequence repetition < ----------------------
    
    seed = 42 # random state during stim genration
    
elif seq_type == 'tc_fix_mc' :
    N_thetas = 12 # np.linspace(min_theta, max_theta, N_thetas)
    min_theta = 0
    max_theta = np.pi
    
    N_Bthetas = 8 # np.linspace(min_btheta, max_btheta, N_Bthetas)
    min_btheta = np.pi/2 
    max_btheta = np.pi/32
    rectification_btheta = 2.5
    
    stim_duration = 2 # duration of stim for debug purposes
    repetition = 5 # nr of sequence repetition
    
    seed = 42 # random state during stim genration

# --------------------------------------------------------------
# PSTH
# --------------------------------------------------------------
beg_psth = -0.5 #s
end_psth = 0.5 #s
binsize = 10 #ms

# --------------------------------------------------------------
# FR DYNAMICS
# --------------------------------------------------------------
win_size = .1 #s
step_size = .002 #s

# --------------------------------------------------------------
# Tuning curves
# --------------------------------------------------------------
end_TC = .2 #s, [0 - end_TC] interval in which to take spikes for TC analysis