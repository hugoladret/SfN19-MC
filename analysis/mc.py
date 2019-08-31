#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:44:11 2019

@author: hugo
I do realise that using sequence in that sense is not correct english but 
it's too late to change all the variables names
"""

import numpy as np
import itertools
import os

def mc_analysis (folder_list,
                   N_thetas, min_theta, max_theta,
                   N_Bthetas, min_btheta, max_btheta, rectification_btheta,
                   stim_duration, repetition, seed,
                   verbose) :
    '''
    Iterates through folders, linking spiketimes, stimulation info and timing together.
    Then, reloads this array and performs :
        orientation selectivity for each B theta
        orientation selectivity for Bthetas merged
        PSTH for each Btheta
        PSTH merged
        Time-series evolution around the PSTH for each btheta
        Time-series evolution around the PSTH merged
        B theta fit for each btheta stimulation (previously called neurometric curves)
    '''
    
    for folder in folder_list :
        sync_sequences(folder,
                       N_thetas, min_theta, max_theta,
                       N_Bthetas, min_btheta, max_btheta, rectification_btheta,
                       stim_duration, repetition, seed,
                       verbose)
        ori_selec(merged = False)
        ori_selec(merged = True)
        psth(merged = False)
        psth(merged = True)
        fr_dynamics(merged = False)
        fr_dynamics(merged = True)
        neurometric()

def ori_selec(folder, merged) :
    print('Not implemented')
    
def psth(folder, merged) :
    print('Not implemented')
    
def fr_dynamics(folder, merged) :
    print('Not implemented')
    
def neurometric(folder) :
    print('Not implemented')
# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def sync_sequences(folder,
                   N_thetas, min_theta, max_theta,
                   N_Bthetas, min_btheta, max_btheta, rectification_btheta,
                   stim_duration, repetition, seed,
                   verbose) :
    '''
    Starts by regenerating the infos in the stimulation sequences, then matching it with
    the stimulation times extracted by the photodiode.
    Then, for each cluster in the folder, saves a npy array that for each trial contains
    beg time, end time, theta, btheta, FR 
    '''
    # Info regeneration
    full_sequence = generate_sequence_info(N_thetas = N_thetas, min_theta = min_theta, max_theta = max_theta,
                           N_Bthetas = N_Bthetas, min_btheta = min_btheta, max_btheta = max_btheta, 
                           rectification_btheta = rectification_btheta,
                           stim_duration = stim_duration, repetition = repetition, seed = seed,
                           verbose= verbose)
    
    # Getting sequence times
    sequences_times = np.load('./results/%s/sequences_times.npy' % folder)
    
    # Synchronizing both
    if len(sequences_times) == len(full_sequence) :
        print('Length of extracted sequences matches length of sequences infos.')
        
        sequences_list = []
        for i, sequence in enumerate(sequences_times):
            seq_dict = {'sequence_beg' : sequences_times[i][0],
                        'sequence_end' : sequences_times[i][1],
                        'sequence_theta' : full_sequence[i][0],
                        'sequence_btheta' : full_sequence[i][1]}
            sequences_list.append(seq_dict)
    
    else :
        print('Non matching dimension between photdiode and sequence infos')
        print('Length of sequences from photodiode = %d ' % (len(sequences_times)))
        print('Length of sequences from sequence infos parameters = %d ' % (len(full_sequence)))
        raise ValueError('len error')
        
    # Loading clusters and adding firing rates
    folder_path = './results/%s/' % folder
    clusters_folders = [file for file in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, file))]
    
    for cluster_folder in clusters_folders :
        if verbose : print('Exporting sequence data in ./results/%s/%s' % (folder, cluster_folder))
        spiketimes = np.load(folder_path + cluster_folder + '/spiketimes.npy')

        sequences_list_with_FR = []
        for i, sequence in enumerate(sequences_list):
            spiketimes_in_seq = np.where((spiketimes > sequence['sequence_beg']) & (spiketimes < sequence['sequence_end']))[0]
            new_seq_dict = {'sequence_beg' : sequence['sequence_beg'],
                            'sequence_end' : sequence['sequence_end'],
                            'sequence_theta' : sequence['sequence_theta'],
                            'sequence_btheta' : sequence['sequence_btheta'],
                            'spiketimes' : spiketimes_in_seq,
                            'tot_spikes' : len(spiketimes_in_seq)}
            
            sequences_list_with_FR.append(new_seq_dict)
            
        np.save(folder_path + cluster_folder + '/sequences_contents.npy', sequences_list_with_FR)
    
# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def generate_sequence_info(N_thetas, min_theta, max_theta,
                           N_Bthetas, min_btheta, max_btheta, rectification_btheta,
                           stim_duration, repetition, seed,
                           verbose) :
    '''
    During the stimulations, we set the seed to a fix number, which allows 
    us to regenerate the stimulation sequence afterwards
    '''
    thetas = np.linspace(min_theta, max_theta, N_thetas)
    B_thetas = np.linspace(min_btheta, max_btheta, N_Bthetas)/rectification_btheta
    
    rng = np.random.RandomState(seed)
    
    sequence = list(itertools.product(thetas, B_thetas))
    rng.shuffle(sequence)
    
    full_sequence = sequence * repetition

    if verbose : print('Stimulation sequence of %sx%s = %s trials, totalling %ss'
                       % (repetition, len(sequence), len(full_sequence), len(full_sequence)*stim_duration))
    return full_sequence 


