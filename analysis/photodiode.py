#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:44:11 2019

@author: hugo
"""

import numpy as np
import matplotlib.pyplot as plt

def get_peak_times(signal, beg_index, end_index,
                   flash_height, baseline_height, width,
                   folder):
    '''
    Plots the [0:beg_index] and [end_index:-1] signal of the photodiode
    with detected sequences
    And returns the peaks
    '''
    
    # Get the end of plateaux, indicating the end of a stimulation
    flash_ends = np.asarray(custom_peak(signal, width = width, height = flash_height))[:,1]
    # Get the very first rise above no light levels
    beg_peak = custom_peak(signal, width = 1000, height = baseline_height)[0][0]
    # Get the first fall to no light levels, indicating the end of stimulation
    end_peak = custom_peak(signal[end_index:], width = 200, height = baseline_height)[0][1] + end_index
    
    # Create a tuple list of sequence beg, end
    sequences_times = []
    sequences_times.append((beg_peak, flash_ends[0]))
    for i, flash_end in enumerate(flash_ends) :
        try :
            sequences_times.append((flash_end, flash_ends[i+1]))
        except IndexError :
            sequences_times.append((flash_end, end_peak))
    
    # Remove any peak that would happen to occur after fall to no light levels
    # Likely me not being quick enough to stop recording before the screen flashes
    # back to Jupyter Notebook bright interface 
    del_indices = []
    for i, sequence_time in enumerate(list(sequences_times)) :
        if sequence_time[1] >= end_peak :
            del_indices.append(i)
    
    sequences_times2 = [i for j,i in enumerate(sequences_times) if j not in del_indices]
        
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
                          (y, y), c = 'g')
            
    ax[1].set_title('End of the photodiode signal')
    ax[1].plot(signal[end_index:-1], c = 'grey')
    for i,sequence_time in enumerate(sequences_times2) :
        if sequence_time[1] >= end_index :
            if i%2 == 0 : y = flash_height
            else : y = flash_height-25
            ax[1].plot((sequence_time[0]-end_index, sequence_time[1]-end_index),
                          (y, y), c = 'g')
    plt.suptitle(folder)
    fig.savefig('./results/%s/photodiode.pdf' % folder, format = 'pdf', bbox_inches = 'tight')
    plt.show()
    
    return sequences_times2
   
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


#signal = np.fromfile('../pipelines/A005_a17/phtdiode_0.bin', np.int16)
#get_peak_times(signal = signal,
#                beg_index = int(len(signal)/30), end_index = 29*int(len(signal)/30),
#                flash_height = np.percentile(signal, 99), 
#                baseline_height = np.percentile(signal, 50),
#                width = 200, folder = 'A005_a17')
