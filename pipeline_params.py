#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import multiprocessing

verbose = True

# --------------------------------------------------------------
# Pre-sorting parameters
# --------------------------------------------------------------
kwd_path = ['../A005_a17/experiment1_100.raw.kwd'] # path of the raw files, must be of same dimension as experiment_name
pipeline_name = 'A005_a17' # name of the folder created under /pipelines/
experiment_name = ['A005_a17'] # name of the temporary files for concatenation cases
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
do_clean = True # moves useful files and removes useless ones
export = True # moves the files to result folder

# --------------------------------------------------------------
# Analysis metaparameters
# Usually wav_analysis_folders > other folders, as we want the maximum neurons to run a kmeans
# But not all of those neurons were recorded during MotionClouds or gratings sessions
# --------------------------------------------------------------
wav_analysis_folders = ['A005_a17'] # result subfolder to be considered in the waveform analysis process
mc_analysis_folders = ['A005_a17'] # result subfolder to be considered in the MotionClouds analysis process

# --------------------------------------------------------------
# Waveform analysis parameters
# --------------------------------------------------------------
lowcut = 300.0 # Hz
highcut = 3000.0 # Hz
order = 6
fs = 30000.0 # Hz

n_spikes = 1000 # number of spikes to extract to get the mean waveform
window_size = 30 # points/2 around the spiketime
debug_plot = True #show the carac points and mean waveform

n_clusters = 2 # K-means number of cluster
k_init = 'k-means++' # K-means init method, K++ uses the pca as barycenters
