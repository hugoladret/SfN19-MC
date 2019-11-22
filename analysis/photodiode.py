#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:44:11 2019

@author: hugo
"""

import numpy as np
import matplotlib.pyplot as plt

def export_sequences_times(folder_list, beg_index, end_index,
                           flash_height, baseline_height, width,
                           fs, verbose, debug_plot) :
    '''
    Loops through the folders and export photodiode times
    '''
    print('# Extracting sequences times from photodiode #')
    for folder in folder_list :
        if verbose : print('Extracting from %s folder' % folder)
        signal = np.fromfile('./pipelines/%s/photodiode.bin' % folder, np.int16)
        
        print(len(signal))        
        beg = int(len(signal)/beg_index)
        end = len(signal) - (end_index*fs)
        flash_height_level = np.percentile(signal, flash_height)
        baseline_height_level = np.percentile(signal, baseline_height)
        
        
        sequences_times = get_peak_times(signal = signal, beg_index = beg, end_index = end,
                   flash_height = flash_height_level, baseline_height = baseline_height_level,
                   width = width, folder = folder, debug_plot = debug_plot)
        if debug_plot : plot_sequences_length(sequences_times,fs, folder)
        np.save('./results/%s/sequences_times.npy' % folder, sequences_times)
    print('Photodiode analysis done !\n')
 
# --------------------------------------------------------------
# 
# --------------------------------------------------------------
       
def plot_sequences_length(sequences_times, fs, folder) :
    fig, ax = plt.subplots(figsize = (10,5))
    sequence_lengths = []
    for sequence in sequences_times :
        sequence_lengths.append((sequence[1]-sequence[0])/fs)
    ax.plot(sequence_lengths)
    
    ax.set_ylabel('Time (s)')
    ax.set_xlabel('Trial #')
    ax.set_title('Duration of trials, std = %.3f, mean = %.3f' % (np.std(sequence_lengths), np.mean(sequence_lengths)))
    
    fig.savefig('./results/%s/photodiode_stability.pdf' % folder,
                format = 'pdf', bbox_inches = 'tight')
    plt.show()
        
# --------------------------------------------------------------
# 
# --------------------------------------------------------------
       


def get_peak_times(signal, beg_index, end_index,
                   flash_height, baseline_height, width,
                   folder, debug_plot):
    '''
    Plots the [0:beg_index] and [end_index:-1] signal of the photodiode
    with detected sequences. Beg and end index are purely cosmetic.
    And returns the peaks
    '''
    
    #used to remove the very last peak
    end_peak = custom_peak(signal[end_index:], width = 200, height = baseline_height)[0][1] + end_index
    
    #the usual, get the chunks above flash_height
    chunk_list = custom_peak(signal, width = width, height = flash_height)
    
    #i %2 == 0 is a stim, otherwise it's a grey screen
    sequences_times = []
    for i, beg in enumerate(chunk_list) :
        if i%2 == 0 :
            stim_beg = chunk_list[i][0]
            stim_end = chunk_list[i+1][1]
            sequences_times.append((stim_beg, stim_end))
        else :
            pass

    del_indices = []
    for i, sequence_time in enumerate(list(sequences_times)) :
        if sequence_time[1] >= end_peak :
            del_indices.append(i)
    
    sequences_times2 = [i for j,i in enumerate(sequences_times) if j not in del_indices]
       
    if debug_plot : 
        fig, ax = plt.subplots(1, 2, sharex= 'col', sharey = 'row',
                               figsize = (12,6))
        fig.tight_layout()
        
    
        ax[0].set_title('Beginning of the photodiode signal')
        ax[0].set_ylabel('Absolute value of signal')
        ax[0].set_xlabel(' Time (points)')
        ax[0].plot(signal[0:beg_index], c = 'grey')
        for i,sequence_time in enumerate(sequences_times2) :
            if sequence_time[1] <= beg_index :
                if i%2 == 0 : y = flash_height
                else : y = flash_height-25
                ax[0].plot((sequence_time[0], sequence_time[1]),
                              (y, y), c = 'r')
                
        ax[1].set_title('End of the photodiode signal')
        ax[1].plot(signal[end_index:-1], c = 'grey')
        for i,sequence_time in enumerate(sequences_times2) :
            if sequence_time[1] >= end_index :
                if i%2 == 0 : y = flash_height
                else : y = flash_height-25
                ax[1].plot((sequence_time[0]-end_index, sequence_time[1]-end_index),
                              (y, y), c = 'r')
        plt.suptitle(folder)
        fig.savefig('./results/%s/photodiode.pdf' % folder, format = 'pdf', bbox_inches = 'tight')
    plt.show()
        
    return sequences_times2
# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def grouper(iterable, width):
    '''
    Black-magic powered iterator from :https://stackoverflow.com/questions/15800895/finding-clusters-of-numbers-in-a-list
    iterates through the list and generates n:[cluster] elements
    
    '''
    prev = None
    group = []
    for item in iterable:
        if not prev or item - prev <= width:
            group.append(item)
        else:
            yield group
            group = [item]
        prev = item
    if group:
        yield group

# --------------------------------------------------------------
# 
# --------------------------------------------------------------
        
def custom_peak(signal, width, height) :
    '''
    Wrapper for grouper, return a list of [(beg,end)] plateaux
    '''
    iterable = np.where(signal > height)[0]
    plateaux = list(enumerate(grouper(iterable, width), 1))
    
    real_peaks = []
    for plateau in plateaux :
        min_plat = plateau[1][0]
        max_plat = plateau[1][-1]
        real_peaks.append((min_plat, max_plat))
        
    return real_peaks
