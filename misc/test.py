#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 14:13:32 2019

@author: hugo
"""

import numpy as np 
import matplotlib.pyplot as plt
from tqdm import tqdm

arr = np.load('../results/A005_a17/cluster_22/sequences_contents.npy', allow_pickle = True)
sorted_arr_theta = sorted(arr, key = lambda x:x['sequence_theta'])


unique_thetas = np.linspace(0, np.pi, 12)
unique_bthetas = np.linspace(np.pi/2, np.pi/32, 8)/ 2.5
fs = 30000

spiketimes = np.load('../results/A005_a17/cluster_22/spiketimes.npy')
test_arr = spiketimes / fs 
beg_PSTH = -0.5 * fs 
end_PSTH = 1.5 * fs

binsize = 5 # ms
n_bin = (end_PSTH/fs) - (beg_PSTH/fs) 
n_bin*=1000
n_bin/= binsize


beg_PST = -.5
end_PST = 1.5

window_size = 200 # ms
slide_size = 2 #ms
window_size *= .001
slide_size *= .001

#----------------------------------------------
# DYNAMICS MERGED
# ---------------------------------------------
n_spikes_list = []
for beg in tqdm( np.arange(0, max(test_arr), slide_size), 'Smoothing signal') :
    end = beg + window_size
    spikes_in_window = np.where((test_arr > beg) & (test_arr < end))[0]
    n_spikes_list.append(len(spikes_in_window))


# In case of merging all Bthetas
# Iterates through all possible thetas
PSTH_list = []
for u_theta in unique_thetas :
    
    # And through sequences to find them
    spikes_per_theta = []
    for seq in sorted_arr_theta :
        if seq['sequence_theta'] == u_theta :
            print(seq['sequence_beg'])
            seq_beg = seq['sequence_beg'] / fs
            
            seq_end = seq_beg + end_PST
            seq_beg += beg_PST
            
            ind_beg = int(seq_beg / slide_size)
            ind_end = int(seq_end / slide_size)
            
            spikes_per_theta.append(n_spikes_list[ind_beg : ind_end])
            print(seq_beg, seq_end)
            print(ind_beg, ind_end)
            print(n_spikes_list[ind_beg : ind_end])
            print('\n')

    PSTH_list.append(spikes_per_theta)

fig, ax  = plt.subplots(len(PSTH_list), 2, sharex = 'col', figsize = (10, 14))

for it_0, theta in enumerate(PSTH_list):
    for trial in theta :
        ax[it_0][0].plot(np.linspace(beg_PST, end_PST, len(trial)),
                         trial)
    ax[it_0][1].plot(np.linspace(beg_PST, end_PST, len(trial)),
                     np.mean(theta, axis = 0))
    
    if it_0 == len(PSTH_list) - 1 :
        ax[it_0][0].set_xlabel('PST (s)')
        ax[it_0][1].set_xlabel('PST (s)')
        
plt.suptitle('Merged all bthetas : [Left] All trials, [Right] Mean for all trials')
plt.show()



