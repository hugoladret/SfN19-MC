#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 14:13:32 2019

@author: hugo
keep all the plotting code here not to fucking retype it all
"""
# ----------------------------------------------
# PSTH MERGED
# ---------------------------------------------
import numpy as np 
import matplotlib.pyplot as plt

arr = np.load('../results/A005_a17/cluster_22/sequences_contents.npy', allow_pickle = True)
sorted_arr_theta = sorted(arr, key = lambda x:x['sequence_theta'])


unique_thetas = np.linspace(0, np.pi, 12)
unique_bthetas = np.linspace(np.pi/2, np.pi/32, 8)/ 2.5
fs = 30000

spiketimes = np.load('../results/A005_a17/cluster_22/spiketimes.npy')
beg_PSTH = -0.5 * fs 
end_PSTH = 1.5 * fs

binsize = 5 # ms
n_bin = (end_PSTH/fs) - (beg_PSTH/fs) 
n_bin*=1000
n_bin/= binsize

# In case of merging all Bthetas
# Iterates through all possible thetas
PSTH_list = []
for u_theta in unique_thetas :
    
    # And through sequences to find them
    spikes_per_theta = []
    for seq in sorted_arr_theta :
        if seq['sequence_theta'] == u_theta :
            near_sequence_beg = np.where((spiketimes > seq['sequence_beg'] + beg_PSTH) & (spiketimes < seq['sequence_beg']  + end_PSTH))[0]
            spikes_per_theta.append( (spiketimes[near_sequence_beg]/fs) - (seq['sequence_beg']/fs))

    PSTH_list.append(spikes_per_theta)
    
fig, ax = plt.subplots(len(PSTH_list), 2, sharex = 'col', figsize = (10, 14))


for it_0, theta in enumerate(PSTH_list) : 
    for it_1, trial in enumerate(theta) :
        ax[it_0][0].scatter(trial, np.full_like(trial, it_1), s = .5)
        
    ax[it_0][0].set_xlim(beg_PSTH/fs, end_PSTH/fs)
    
    ax[it_0][1].hist(np.concatenate(theta), int(n_bin))
    
    if it_0 == len(PSTH_list)-1 :
            ax[it_0][0].set_xlabel('PST (s)')
            ax[it_0][0].set_ylabel('Trial')
            ax[it_0][1].set_xlabel('PST (s)')
            ax[it_0][1].set_ylabel('n spikes')
    
plt.suptitle('All bthetas merged - Histogram with %sms bin size' % binsize, y = .93)
plt.show()

np.save('plot_MC_PSTH_merged.npy', PSTH_list)

# ----------------------------------------------
# PSTH NONMERGED
# ---------------------------------------------

# In case of no merging All bthetas
# Iterates through all the possible bthetas
PSTH_list_btheta = []
for u_btheta in unique_bthetas :
    
    PSTH_list_theta = []
    for u_theta in unique_thetas : 
        # And through sequences to find them
        spikes_per_thetabtheta = []
        for seq in sorted_arr_theta :
            if seq['sequence_theta'] == u_theta and seq['sequence_btheta'] == u_btheta :
                near_sequence_beg = np.where((spiketimes > seq['sequence_beg'] + beg_PSTH) & (spiketimes < seq['sequence_beg']  + end_PSTH))[0]
                spikes_per_thetabtheta.append( (spiketimes[near_sequence_beg]/fs) - (seq['sequence_beg']/fs))
        PSTH_list_theta.append(spikes_per_thetabtheta)
    PSTH_list_btheta.append(PSTH_list_theta)
    
for i, PSTH_list in enumerate(PSTH_list_btheta) : 
    fig, ax = plt.subplots(len(PSTH_list), 2, sharex = 'col', figsize = (10, 14))
    for it_0, theta in enumerate(PSTH_list) : 
        for it_1, trial in enumerate(theta) :
            ax[it_0][0].scatter(trial, np.full_like(trial, it_1), s = .5)
            
        ax[it_0][0].set_xlim(beg_PSTH/fs, end_PSTH/fs)
        ax[it_0][0].set_ylabel('Theta = \n%2.f' % unique_thetas[it_0])
        
        ax[it_0][1].hist(np.concatenate(theta), int(n_bin))
        
        if it_0 == len(PSTH_list)-1 :
                ax[it_0][0].set_xlabel('PST (s)')
                ax[it_0][0].set_ylabel('Trial\n Theta = %2.f' % unique_thetas[it_0])
                ax[it_0][1].set_xlabel('PST (s)')
                ax[it_0][1].set_ylabel('n spikes')
        
    plt.suptitle('B theta = %.2f - Histogram with %sms bin size' % (unique_bthetas[i], binsize) , y = .93)
    plt.show()

np.save('plot_MC_PSTH_nonmerged.npy', PSTH_list_btheta)






# ----------------------------------------------
# TC MERGED
# ---------------------------------------------
TC_list = []
for u_theta in unique_thetas :
    
    # And through sequences to find them
    spikes_per_theta = []
    for seq in sorted_arr_theta :
        if seq['sequence_theta'] == u_theta :
            seq_duration = (seq['sequence_end'] - seq['sequence_beg']) / fs
            spikes_per_theta.append(seq['tot_spikes']/seq_duration)
            
    TC_list.append(spikes_per_theta)
      
means, stds = [], []
for theta in TC_list : 
    means.append(np.mean(theta))
    stds.append(np.std(theta))
    
plt.errorbar(np.arange(0, len(means)), means, yerr = stds)
plt.show()

# ----------------------------------------------
# TC NON MERGED
# ---------------------------------------------
# In case of no merging All bthetas
# Iterates through all the possible bthetas
TC_list_btheta = []
for u_btheta in unique_bthetas :
    
    # And all the thetas
    TC_list_theta =[] 
    for u_theta in unique_thetas :
        
        spikes_per_thetabtheta = []
        for seq in sorted_arr_theta :
            if seq['sequence_theta'] == u_theta and seq['sequence_btheta'] == u_btheta:
                seq_duration = (seq['sequence_end'] - seq['sequence_beg']) / fs
                spikes_per_thetabtheta.append(seq['tot_spikes']/seq_duration)
        TC_list_theta.append(spikes_per_thetabtheta)
    TC_list_btheta.append(TC_list_theta)
    
fig, ax = plt.subplots(1, len(TC_list_btheta), figsize = (15,6), sharex= 'col', sharey = 'row',)
fig.tight_layout()
all_means, all_stds = [], []
for i in range(len(TC_list_btheta)):
    means = np.mean(TC_list_btheta[i], axis = 1)
    stds = np.std(TC_list_btheta[i], axis = 1)
    
    ax[i].errorbar(np.arange(0, len(means)), means, yerr = stds)
    ax[i].set_title(unique_bthetas[i])
    
    all_means.append(means)
    all_stds.append(stds)
    
plt.show()


