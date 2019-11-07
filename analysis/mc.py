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
from tqdm import tqdm
from lmfit import Model, Parameters


def mc_analysis(folder_list,
                   N_thetas, min_theta, max_theta,
                   N_Bthetas, min_btheta, max_btheta, rectification_btheta,
                   stim_duration, repetition, seed,
                   fs, beg_psth, end_psth, binsize,
                   win_size, step_size, end_TC,
                   verbose) :
    '''
    Iterates through folders, linking spiketimes, stimulation info and timing together.
    Then, reloads this array and performs :
        orientation selectivity for Bthetas merged
        orientation selectivity for each B theta
        
        PSTH merged
        PSTH for each Btheta
        
        Time-series evolution around the PSTH merged
        Time-series evolution around the PSTH for each btheta
        
        B theta fit for each btheta stimulation (previously called neurometric curves)
    '''
    print('# Running MotionClouds analysis#')
    for folder in folder_list :
        sync_sequences(folder,
                       N_thetas, min_theta, max_theta,
                       N_Bthetas, min_btheta, max_btheta, rectification_btheta,
                       stim_duration, repetition, seed,
                       verbose)
        
        ori_selec(folder = folder, merged = True, fs = fs, end_TC = end_TC,
                  verbose = verbose)
        ori_selec(folder = folder, merged = False, fs = fs, end_TC = end_TC,
                  verbose = verbose)

        psth(folder = folder, merged = True, fs = fs, 
             beg_psth = beg_psth, end_psth = end_psth,
             binsize = binsize,
             verbose = verbose)
        psth(folder = folder, merged = False, fs = fs, 
             beg_psth = beg_psth, end_psth = end_psth,
             binsize = binsize,
             verbose = verbose)

        '''fr_dynamics(folder = folder, merged = True, fs = fs,
                beg_PST = beg_psth, end_PST = end_psth,
                win_size = win_size, step_size = step_size,
                verbose = verbose)
        fr_dynamics(folder = folder, merged = False, fs = fs,
                beg_PST = beg_psth, end_PST = end_psth,
                win_size = win_size, step_size = step_size,
                verbose = verbose)'''

        neurometric(folder = folder, verbose = verbose)
        
        print(' # All MotionClouds analysis have been successfully performed  #')

# --------------------------------------------------------------
# 
# --------------------------------------------------------------
        
def ori_maxFR_selec(folder, merged, fs,
              verbose) :
    '''
    Runs orientation selectivity analysis on each cluster subfolder in the folder
    saves directly as arrays for merged and non merged tuning curves of the cluster
    '''
    print('# Analyzing orientation selectivity #')
    folder_path = './results/%s/' % folder
    
    clusters_folders = [file for file in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, file))]
    
    for cluster_folder in clusters_folders :
        if verbose : print('analyzing ./results/%s/%s' % (folder, cluster_folder))
        
        sequences_contents = np.load(folder_path + cluster_folder + '/sequences_contents.npy',
                                     allow_pickle = True)
        sorted_arr_theta = sorted(sequences_contents, key = lambda x:x['sequence_theta'])
        
        unique_thetas = np.unique([x['sequence_theta'] for x in sorted_arr_theta])
        unique_bthetas = np.unique([x['sequence_btheta'] for x in sorted_arr_theta])
        
        spiketimes = np.load(folder_path + cluster_folder + '/spiketimes.npy')
        
        #for further plot purposes
        np.save(folder_path + cluster_folder + '/unique_thetas.npy', unique_thetas)
        np.save(folder_path + cluster_folder + '/unique_bthetas.npy', unique_bthetas)
        
        before = -.5 * fs
        after = .5 * fs
        #---------
        # Merged
        #---------
        if merged : 
        # Iterates through all possible thetas
            TC_list = []
            for u_theta in unique_thetas :
                
                # And through sequences to find them
                spikes_per_theta = []
                for seq in sorted_arr_theta :
                    if seq['sequence_theta'] == u_theta :
                        idx_FR_before = np.where((spiketimes > seq['sequence_beg'] + before) & (spiketimes < seq['sequence_beg']))
                        idx_FR_after = np.where((spiketimes > seq['sequence_beg']) & (spiketimes < seq['sequence_beg'] + after ))
                        
                        spikes_per_theta.append( (spiketimes[near_sequence_beg]/fs) - (seq['sequence_beg']/fs))
                        
                TC_list.append(spikes_per_theta)
                
            means, stds = [], []
            for theta in TC_list : 
                means.append(np.mean(theta))
                stds.append(np.std(theta))
                
            np.save(folder_path + cluster_folder + '/plot_MC_TC_merged_means.npy', means)
            np.save(folder_path + cluster_folder + '/plot_MC_TC_merged_stds.npy', stds)
            np.save(folder_path + cluster_folder + '/plot_MC_TC_merged_all.npy', TC_list)
                
                
        #-----------
        # Not merged
        #-----------
        else :
            TC_list_btheta = []
            for u_btheta in unique_bthetas :
                
                # And all the thetas
                TC_list_theta =[] 
                for u_theta in unique_thetas :
                    
                    spikes_per_thetabtheta = []
                    for seq in sorted_arr_theta :
                        if seq['sequence_theta'] == u_theta and seq['sequence_btheta'] == u_btheta:
#                            seq_duration = (seq['sequence_end'] - seq['sequence_beg']) / fs
#                            spikes_per_thetabtheta.append(seq['tot_spikes']/seq_duration)
                            sampled_length = 15000 # = .5s @ 30kHz
                            seq_duration = ( (seq['sequence_beg'] + sampled_length) - seq['sequence_beg']) / fs
                            spikes_per_thetabtheta.append(len(seq['spiketimes'][np.where(seq['spiketimes'] < seq['sequence_beg'] + sampled_length)[0]])/seq_duration)
                    TC_list_theta.append(spikes_per_thetabtheta)
                TC_list_btheta.append(TC_list_theta)
                
            all_means, all_stds = [], []
            for i in range(len(TC_list_btheta)):
                means = np.mean(TC_list_btheta[i], axis = 1)
                stds = np.std(TC_list_btheta[i], axis = 1)
                
                all_means.append(means)
                all_stds.append(stds)

            #saves a (b_theta, thetas) shaped arrays
            np.save(folder_path + cluster_folder + '/plot_MC_TC_nonmerged_means.npy', all_means)
            np.save(folder_path + cluster_folder + '/plot_MC_TC_nonmerged_stds.npy', all_stds)
            np.save(folder_path + cluster_folder + '/plot_MC_TC_nonmerged_all.npy', TC_list_btheta)
        
    print('Done !')
    
# --------------------------------------------------------------
# 
# --------------------------------------------------------------
        
def ori_selec(folder, merged, fs, end_TC,
              verbose) :
    '''
    Runs orientation selectivity analysis on each cluster subfolder in the folder
    saves directly as arrays for merged and non merged tuning curves of the cluster
    '''
    print('# Analyzing orientation selectivity #')
    folder_path = './results/%s/' % folder
    
    clusters_folders = [file for file in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, file))]
    
    for cluster_folder in clusters_folders :
        if verbose : print('analyzing ./results/%s/%s' % (folder, cluster_folder))
        
        sequences_contents = np.load(folder_path + cluster_folder + '/sequences_contents.npy',
                                     allow_pickle = True)
        sorted_arr_theta = sorted(sequences_contents, key = lambda x:x['sequence_theta'])
        
        unique_thetas = np.unique([x['sequence_theta'] for x in sorted_arr_theta])
        unique_bthetas = np.unique([x['sequence_btheta'] for x in sorted_arr_theta])
        
        #for further plot purposes
        np.save(folder_path + cluster_folder + '/unique_thetas.npy', unique_thetas)
        np.save(folder_path + cluster_folder + '/unique_bthetas.npy', unique_bthetas)
        
        #---------
        # Merged
        #---------
        if merged : 
        # Iterates through all possible thetas
            TC_list = []
            for u_theta in unique_thetas :
                
                # And through sequences to find them
                spikes_per_theta = []
                for seq in sorted_arr_theta :
                    if seq['sequence_theta'] == u_theta :
                        #seq_duration = (seq['sequence_end'] - seq['sequence_beg']) / fs
                        #spikes_per_theta.append(seq['tot_spikes']/seq_duration)
                        
                        sampled_length = int(end_TC*fs) # in hz
                        seq_duration = ( (seq['sequence_beg'] + sampled_length) - seq['sequence_beg']) / fs
                        spikes_per_theta.append(len(seq['spiketimes'][np.where(seq['spiketimes'] < seq['sequence_beg'] + sampled_length)[0]])/seq_duration)
                        
                TC_list.append(spikes_per_theta)
                
            means, stds = [], []
            for theta in TC_list : 
                means.append(np.mean(theta))
                stds.append(np.std(theta))
                
            np.save(folder_path + cluster_folder + '/plot_MC_TC_merged_means.npy', means)
            np.save(folder_path + cluster_folder + '/plot_MC_TC_merged_stds.npy', stds)
            np.save(folder_path + cluster_folder + '/plot_MC_TC_merged_all.npy', TC_list)
                
                
        #-----------
        # Not merged
        #-----------
        else :
            TC_list_btheta = []
            for u_btheta in unique_bthetas :
                
                # And all the thetas
                TC_list_theta =[] 
                for u_theta in unique_thetas :
                    
                    spikes_per_thetabtheta = []
                    for seq in sorted_arr_theta :
                        if seq['sequence_theta'] == u_theta and seq['sequence_btheta'] == u_btheta:
                            #seq_duration = (seq['sequence_end'] - seq['sequence_beg']) / fs
                            #spikes_per_thetabtheta.append(seq['tot_spikes']/seq_duration)
                            sampled_length = int(end_TC*fs) # in hz
                            seq_duration = ( (seq['sequence_beg'] + sampled_length) - seq['sequence_beg']) / fs
                            spikes_per_thetabtheta.append(len(seq['spiketimes'][np.where(seq['spiketimes'] < seq['sequence_beg'] + sampled_length)[0]])/seq_duration)
                    TC_list_theta.append(spikes_per_thetabtheta)
                TC_list_btheta.append(TC_list_theta)
                
            all_means, all_stds = [], []
            for i in range(len(TC_list_btheta)):
                means = np.mean(TC_list_btheta[i], axis = 1)
                stds = np.std(TC_list_btheta[i], axis = 1)
                
                all_means.append(means)
                all_stds.append(stds)

            #saves a (b_theta, thetas) shaped arrays
            np.save(folder_path + cluster_folder + '/plot_MC_TC_nonmerged_means.npy', all_means)
            np.save(folder_path + cluster_folder + '/plot_MC_TC_nonmerged_stds.npy', all_stds)
            np.save(folder_path + cluster_folder + '/plot_MC_TC_nonmerged_all.npy', TC_list_btheta)
        
    print('Done !')
    
# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def psth(folder, merged,fs, beg_psth, end_psth, binsize, verbose) :
    print('# Analyzing PSTH #')
          
    folder_path = './results/%s/' % folder
    clusters_folders = [file for file in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, file))]
    
    beg_psth = beg_psth * fs
    end_psth = end_psth * fs
    
    n_bin = (end_psth/fs) - (beg_psth/fs)
    n_bin *= 1000
    n_bin /= binsize
    
    for cluster_folder in clusters_folders :
        if verbose : print('analyzing ./results/%s/%s' % (folder, cluster_folder))
        
        sequences_contents = np.load(folder_path + cluster_folder + '/sequences_contents.npy',
                                     allow_pickle = True)
        sorted_arr_theta = sorted(sequences_contents, key = lambda x:x['sequence_theta'])
        spiketimes = np.load(folder_path + cluster_folder + '/spiketimes.npy')
        
        unique_thetas = np.unique([x['sequence_theta'] for x in sorted_arr_theta])
        unique_bthetas = np.unique([x['sequence_btheta'] for x in sorted_arr_theta])
        
        #---------
        # Merged
        #---------
        if merged : 
            PSTH_list = []
            for u_theta in unique_thetas :
                
                # And through sequences to find them
                spikes_per_theta = []
                for seq in sorted_arr_theta :
                    if seq['sequence_theta'] == u_theta :
                        near_sequence_beg = np.where((spiketimes > seq['sequence_beg'] + beg_psth) & (spiketimes < seq['sequence_beg']  + end_psth))[0]
                        spikes_per_theta.append( (spiketimes[near_sequence_beg]/fs) - (seq['sequence_beg']/fs))
                PSTH_list.append(spikes_per_theta)
                
            np.save(folder_path + cluster_folder + '/plot_MC_PSTH_merged.npy', PSTH_list)
         
        #-----------
        # Not merged
        #-----------
        else :
            PSTH_list_btheta = []
            for u_btheta in unique_bthetas :
                
                PSTH_list_theta = []
                for u_theta in unique_thetas : 
                    # And through sequences to find them
                    spikes_per_thetabtheta = []
                    for seq in sorted_arr_theta :
                        if seq['sequence_theta'] == u_theta and seq['sequence_btheta'] == u_btheta :
                            near_sequence_beg = np.where((spiketimes > seq['sequence_beg'] + beg_psth) & (spiketimes < seq['sequence_beg']  + end_psth))[0]
                            spikes_per_thetabtheta.append( (spiketimes[near_sequence_beg]/fs) - (seq['sequence_beg']/fs))
                    PSTH_list_theta.append(spikes_per_thetabtheta)
                PSTH_list_btheta.append(PSTH_list_theta)
                
            np.save(folder_path + cluster_folder + '/plot_MC_PSTH_nonmerged.npy', PSTH_list_btheta)
        
    print('Done ! ')
    
# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def fr_dynamics(folder, merged, fs,
                beg_PST, end_PST,
                win_size, step_size,
                verbose) :
    '''
    Slides a window over the spiketimes and computes the densities around the PST
    '''
    
    print('# Analyzing FR dynamics #')
          
    folder_path = './results/%s/' % folder
    clusters_folders = [file for file in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, file))]
    
    for cluster_folder in clusters_folders :
        
        sequences_contents = np.load(folder_path + cluster_folder + '/sequences_contents.npy',
                                     allow_pickle = True)
        sorted_arr_theta = sorted(sequences_contents, key = lambda x:x['sequence_theta'])
        spiketimes = np.load(folder_path + cluster_folder + '/spiketimes.npy') / fs

        unique_thetas = np.unique([x['sequence_theta'] for x in sorted_arr_theta])
        unique_bthetas = np.unique([x['sequence_btheta'] for x in sorted_arr_theta])
        
        n_spikes_list = []
        for beg in tqdm( np.arange(0, max(spiketimes), step_size), 'Doing %s densities' % (cluster_folder)) :
            end = beg + win_size
            spikes_in_window = np.where((spiketimes > beg) & (spiketimes < end))[0]
            n_spikes_list.append(len(spikes_in_window))
            
        np.save(folder_path + cluster_folder + '/plot_MC_FR_all.npy', n_spikes_list)
           
        #---------
        # Merged
        #---------
        if merged : 
            PSTH_list = []
            for u_theta in unique_thetas :
                # And through sequences to find them
                spikes_per_theta = []
                for seq in sorted_arr_theta :
                    if seq['sequence_theta'] == u_theta :

                        seq_beg = seq['sequence_beg'] / fs
                        seq_end = seq_beg + end_PST
                        seq_beg += beg_PST
                        
                        ind_beg = int(seq_beg / step_size)
                        ind_end = int(seq_end / step_size)
                        
                        spikes_per_theta.append(n_spikes_list[ind_beg : ind_end])

                        
            
                PSTH_list.append(spikes_per_theta)
            np.save(folder_path + cluster_folder + '/plot_MC_FR_dynamics_merged.npy', PSTH_list)
          
        #-----------
        # Not merged
        #-----------
        else : 
            PSTH_list_btheta = []
            for u_btheta in unique_bthetas :
                
                PSTH_list_theta = []
                for u_theta in unique_thetas : 
                    # And through sequences to find them
                    spikes_per_thetabtheta = []
                    for seq in sorted_arr_theta :
                        if seq['sequence_theta'] == u_theta and seq['sequence_btheta'] == u_btheta :
                            seq_beg = seq['sequence_beg'] / fs
                        
                            seq_end = seq_beg + end_PST
                            seq_beg += beg_PST
                            
                            ind_beg = int(seq_beg / step_size)
                            ind_end = int(seq_end / step_size)
                            
                            spikes_per_thetabtheta.append(n_spikes_list[ind_beg : ind_end])
                            
                    PSTH_list_theta.append(spikes_per_thetabtheta)
                PSTH_list_btheta.append(PSTH_list_theta)
                
            np.save(folder_path + cluster_folder + '/plot_MC_FR_dynamics_nonmerged.npy', PSTH_list_btheta)
            
    print('Done ! ')

# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def neurometric(folder, verbose) :
    '''
    Loads the TC data from the cluster folder, fits a von mises to it 
    and returns the neurometric curve (Btheta_fit vs btheta_stim) for each theta
    NOT the fits, which will be later called in the plotter
    '''
    
    print('# Fitting curve #')
          
    folder_path = './results/%s/' % folder
    clusters_folders = [file for file in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, file))]
    
    for cluster_folder in clusters_folders :
        if verbose : print('analyzing ./results/%s/%s' % (folder, cluster_folder))
        
        #Individual TC fits
        TC_data = np.load(folder_path + cluster_folder + '/plot_MC_TC_nonmerged_all.npy')

        B_theta_fit_list = []
        tuning_fits_list = []
        fit_reports_list = []
        for it_0, btheta in enumerate(TC_data) :
            # Make a tuning curve
            mean_fr = np.mean(btheta, axis = 1)
            xs = np.arange(0, len(mean_fr))
            
            best_vals, fit_report = fit_plot(mean_fr)
            
            B_theta_fit_list.append(best_vals['B'])
            tuning_fits_list.append(tuning_function(x=xs,
                                j=best_vals['j'], fmax=best_vals['fmax'],
                                B=best_vals['B']) + mean_fr.min())
            fit_reports_list.append(fit_report)
            
            np.save(folder_path + cluster_folder + '/plot_neurometric_Btheta_fits.npy', B_theta_fit_list)
            np.save(folder_path + cluster_folder + '/plot_neurometric_fitted_TC.npy', tuning_fits_list)
            np.save(folder_path + cluster_folder + '/plot_neurometric_fit_reports.npy', fit_reports_list)

        # Merged TC fit
        merged_TC_data = np.load(folder_path + cluster_folder + '/plot_MC_TC_merged_all.npy')
        B_theta_fit_list = []
        tuning_fits_list = []
        fit_reports_list = []
        # Make a tuning curve
        mean_fr = np.mean(merged_TC_data, axis = 1)
        xs = np.arange(0, len(mean_fr))
        
        best_vals, fit_report = fit_plot(mean_fr)
        B_theta_fit_list.append(best_vals['B'])
        tuning_fits_list.append(tuning_function(x=xs,
                            j=best_vals['j'], fmax=best_vals['fmax'],
                            B=best_vals['B']) + mean_fr.min())
        fit_reports_list.append(fit_report)
        
        np.save(folder_path + cluster_folder + '/plot_neurometric_merged_Btheta_fits.npy', B_theta_fit_list)
        np.save(folder_path + cluster_folder + '/plot_neurometric_merged_fitted_TC.npy', tuning_fits_list)
        np.save(folder_path + cluster_folder + '/plot_neurometric_merged_fit_reports.npy', fit_reports_list)
            
    print(' Done ! ')
           
    
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
    print('# Synchronizing sequences #')
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
                            'spiketimes' : spiketimes[spiketimes_in_seq],
                            'tot_spikes' : len(spiketimes_in_seq)}
            
            sequences_list_with_FR.append(new_seq_dict)

        spiketime_density = [sequence['tot_spikes'] for sequence in sequences_list_with_FR]

        np.save(folder_path + cluster_folder + '/plot_spiketime_density.npy', spiketime_density)
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

# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def tuning_function(x, j, B, fmax):  # von mises, baseline is the minimum neuron activity
    N = len(x)
    if B == np.inf:
        VM = np.ones_like(x)
    else:
        VM = np.exp((np.cos(2.*np.pi*(x-j)/N)-1.)/4/(B*np.pi/180)**2)
    #VM /= VM.sum(axis=0)
    return fmax * VM

# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def fit_plot(array, datacol='.b', fitcol='k', data_kws=None, do_title=True,
             seq_nbr=None):

    x = np.linspace(0, len(array), len(array))
    y = array
    N = len(array)

    mod = Model(tuning_function)
    pars = Parameters()
    y = y-np.min(y)
    pars.add_many(('j', y.argmax(), True,  0.0, N), ('B', 15., True,  0.1, 360),
                  ('fmax', y.max(), True,  0.0, 100.))


    out = mod.fit(y, pars, x=x, nan_policy='omit')


    return out.best_values, (1-out.residual.var() / np.var(y))
