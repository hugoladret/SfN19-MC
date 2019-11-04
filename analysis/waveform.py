#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:44:11 2019

@author: hugo
"""

import numpy as np
import sys
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D 
from sklearn import cluster
import os 
import imp
import fileinput

def waveform_analysis(folder_list,
                          n_chan, 
                          lowcut, highcut, fs, order,
                          n_spikes, window_size,
                          n_clusters, k_init,
                          debug_plot, verbose) :
    '''
    Get waveforms for all clusters in folder_list's subfolders,
    characterizes them and classifies them with a KMean
    the output identity is saved in the neuron subfolder
    '''
    
    print('\n# Performing waveform analysis')
          
    # get the classif points using spiketimes and raw signals
    caracterise_waveforms(folder_list, n_chan, lowcut, highcut, fs, order,
                          n_spikes, window_size, verbose)
    
    # show caracterisation of waveform and mean + std waveform
    if debug_plot :
        if verbose : print('Plotting waveforms')
        plot_waveforms(folder_list)
    
    # perform the k-mean clustering
    if verbose : print('Running K-means')
    kmean_waveforms(folder_list, n_clusters, k_init, debug_plot)
    
    print('Waveform analysis complete !\n')

# --------------------------------------------------------------
#
# --------------------------------------------------------------
    
def caracterise_waveforms(folder_list, n_chan, 
                          lowcut, highcut, fs, order,
                          n_spikes, window_size, verbose):
    '''
    Using spiketimes under /results/ and raw data under /pipelines/
    caracterises the waveforms and saves everything as .npy files
    '''
    
    if verbose : print('Getting classification points from waveforms')
    
    # iterate through cluster groups (= former pipeline folders)
    for folder in folder_list :
        
        folder_path = './results/%s/' % folder
        raw_file_path = './pipelines/%s/mydata_0.bin' % folder
        
        if verbose : print('Loading data in %s' % raw_file_path )
        
        # Raw data
        raw_array = np.fromfile(raw_file_path, dtype = np.int16)
        raw_array = np.reshape(raw_array, (-1, n_chan))
        
        # iterate through clusters
        clusters_folders = [file for file in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, file))]
        for cluster_folder in clusters_folders :
            
            subfolder_path = folder_path + cluster_folder + '/'
            if verbose : print('Exporting waveform data in %s' % subfolder_path)
            
            cluster_info = get_var_from_file(subfolder_path+'cluster_info.py')
            spiketimes = np.load(subfolder_path+'spiketimes.npy')
            y = butter_bandpass_filter(raw_array[:, cluster_info.channel_id], lowcut, highcut, fs, order)
            
            waveform_list = []
            for spiketime in spiketimes[10:n_spikes] :
                beg = int(spiketime-(window_size/2))
                end = int(spiketime+(window_size*2))
                waveform_list.append(y[beg:end])
                
            mean_waveform = np.mean(waveform_list, axis = 0)
            classif_points = get_classif_points(mean_waveform)
            true_classif_points = classif_points[0:3]
            plot_classif_points = classif_points[3:]
            
            np.save(subfolder_path + 'waveform_mean.npy', mean_waveform)
            np.save(subfolder_path + 'waveform_all.npy', waveform_list)
            np.save(subfolder_path + 'waveform_classif_points.npy', true_classif_points)
            np.save(subfolder_path + 'waveform_plot_points.npy', plot_classif_points)

# --------------------------------------------------------------
#
# --------------------------------------------------------------
            
def kmean_waveforms(folder_list, n_clusters, k_init, debug_plot):
    '''
    Perform k-mean clustering from the available waveform caracterisation points in /results
    DO NOT FLIP THE ORDER OF FIRST AND SECOND CLASS TRIPLETS 
    '''
    
    all_carac_points = []
    path_to_carac_points = [] #use to write the kmeans info
    for folder in folder_list :
        
        folder_path = './results/%s/' % folder
        clusters_folders = [file for file in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, file))]
        
        for cluster_folder in clusters_folders :
            
            subfolder_path = folder_path + cluster_folder + '/'
            carac_points = np.load(subfolder_path + 'waveform_classif_points.npy')
            all_carac_points.append(carac_points)
            path_to_carac_points.append(subfolder_path)
            
            
    kmeans = cluster.KMeans(n_clusters = n_clusters, init = k_init,
                            n_init = 10, max_iter=1000).fit(all_carac_points)
    
    first_class_triplets = []
    second_class_triplets = []
    
    for i in range(len(kmeans.labels_)) :
        if kmeans.labels_[i] == 0 :
            first_class_triplets.append(all_carac_points[i])
            replace_if_exist(path_to_carac_points[i] + '/cluster_info.py',
                             'putative_type', 'putative_type = "inh"\n')
        else :
            second_class_triplets.append(all_carac_points[i])
            replace_if_exist(path_to_carac_points[i] + '/cluster_info.py',
                             'putative_type', 'putative_type = "exc"\n')

    xs1, ys1, zs1 = [], [], []
    for i in first_class_triplets :
            xs1.append(i[0])
            ys1.append(i[1])
            zs1.append(i[2])
            
    xs2, ys2, zs2 = [], [], []
    for i in second_class_triplets:
            xs2.append(i[0])
            ys2.append(i[1])
            zs2.append(i[2])
    
    if debug_plot :
        plot_KMeans(xs1, ys1, zs1,
                    xs2, ys2, zs2)

# --------------------------------------------------------------
#
# --------------------------------------------------------------
        
def plot_KMeans(xs1, ys1, zs1,
                xs2, ys2, zs2) :
    '''
    Plots Kmeans classification of all the clusters
    '''
    # todo : animate
    fig = plt.figure(figsize = (8,8))
    ax = fig.add_subplot(111, projection = '3d')
    
    ax.scatter(xs2, ys2, zs2,
                   c = 'r', label = 'Wide-spiking cells PC')
    ax.scatter(xs1, ys1, zs1,
               c = 'b', label = 'Narrow-spiking cells INs')
    
    ax.set_xlabel('Half width (points)')
    ax.set_ylabel('Trough to peak (points)')
    ax.set_zlabel('Peak amplitude asymetry')
    
    
    ax.view_init(elev=35, azim=45)
    plt.legend()
    fig.savefig('./results/Kmeans.pdf', format = 'pdf', bbox_inches = 'tight')
    plt.show()
    
# --------------------------------------------------------------
#
# --------------------------------------------------------------
            
def plot_waveforms(folder_list):
    '''
    Plots the caracterisation points and mean waveform of all clusters
    '''
    
    all_mean_waveforms, all_classif_points, all_waveform_plot_points, all_waveform_list = [],[],[],[]
    title_list = []
    
    #it's that good old double iteration with list generator to reload .npy data
    for folder in folder_list :
        
        folder_path = './results/%s/' % folder
        clusters_folders = [file for file in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, file))]
        
        for cluster_folder in clusters_folders :
            
            subfolder_path = folder_path + cluster_folder + '/'
            
            mean_waveform = np.load(subfolder_path + 'waveform_mean.npy')
            all_mean_waveforms.append(mean_waveform)
            
            all_waveforms = np.load(subfolder_path + 'waveform_all.npy')
            all_waveform_list.append(all_waveforms)
            
            classif_points = np.load(subfolder_path + 'waveform_classif_points.npy')
            all_classif_points.append(classif_points)
            
            plot_points = np.load(subfolder_path + 'waveform_plot_points.npy')
            all_waveform_plot_points.append(plot_points)
            
            title_list.append('/%s/%s' % (folder, cluster_folder))
        
    
    fig, ax = plt.subplots(len(all_mean_waveforms), 2, sharex= 'col', sharey = 'row',
                           figsize = (12,8))
    fig.tight_layout()
    
    # plotting, indices have been carefully triple checked
    for i in range(len(all_mean_waveforms)) :
        for j in range(2):
            if j == 0 : #plot the classif points
                ax[i,j].axhline(0, c = 'gray', linewidth = 2, alpha = .8)
                ax[i,j].plot((all_waveform_plot_points[i][0], all_waveform_plot_points[i][0]),
                              (all_waveform_plot_points[i][2], 0), c = 'k', linestyle = '--')
                ax[i,j].plot((all_waveform_plot_points[i][1], all_waveform_plot_points[i][1]), 
                              (all_waveform_plot_points[i][3], 0), c = 'k', linestyle = '--')
                ax[i,j].plot((all_waveform_plot_points[i][4], all_waveform_plot_points[i][5]), 
                              (all_waveform_plot_points[i][6], all_waveform_plot_points[i][7]), c = 'k', linestyle = '--')
                ax[i,j].plot(all_mean_waveforms[i])
                if i == 0 : ax[i,j].set_title(title_list[i] + ' - classification points')
                else : ax[i,j].set_title(title_list[i])
            elif j == 1 : #plot the mean waveforms
                mean_waveform = all_mean_waveforms[i]
                std_waveform = np.std(all_waveform_list[i], axis = 0)
                ax[i,j].plot(mean_waveform, c = 'w')
                ax[i,j].fill_between(np.arange(0, len(mean_waveform)),
                                     mean_waveform - std_waveform,
                                     mean_waveform + std_waveform)
                if i == 0 : ax[i,j].set_title(title_list[i] + ' - mean and std waveform')
                else : ax[i,j].set_title(title_list[i])
                
    fig.savefig('./results/Waveforms.pdf', format = 'pdf', bbox_inches = 'tight') 
    plt.show()
    
# --------------------------------------------------------------
#
# --------------------------------------------------------------
  
def get_classif_points(mean_waveform) :
    '''
    Returns the half width, trough to peak, peak amplitude asymetry for PCA classif
    as done in https://www.cell.com/neuron/fulltext/S0896-6273(09)00720-X?
    '''   

    # peak
    max_amp = np.max(mean_waveform)
    max_amp_time = np.where(mean_waveform == max_amp)[0]
    middle = max_amp_time[0]
    
    # both mins 
    first_min_amp = np.min(mean_waveform[:middle])
    first_min_time = np.where(mean_waveform == first_min_amp)[0]

    second_min_amp = np.min(mean_waveform[middle:])
    second_min_time = np.where(mean_waveform == second_min_amp)[0]
    
    #get the FWHM
    first_half_peak = find_nearest(mean_waveform[first_min_time[0]:max_amp_time[0]], max_amp/2)
    second_half_peak = find_nearest(mean_waveform[max_amp_time[0]:second_min_time[0]], max_amp/2)

    first_half_peak_time = np.where(mean_waveform == first_half_peak)[0]
    second_half_peak_time = np.where(mean_waveform == second_half_peak)[0]
    
    half_width = second_half_peak_time - first_half_peak_time
    trough_to_peak = second_min_time -max_amp_time
    peak_amplitude_asymetry = (second_min_amp - first_min_amp) / (second_min_amp + first_min_amp)
    
    return [half_width[0], trough_to_peak[0], peak_amplitude_asymetry, 
            first_min_time[0], second_min_time[0], first_min_amp, second_min_amp,
            first_half_peak_time[0], second_half_peak_time[0], first_half_peak, second_half_peak]      
             
# --------------------------------------------------------------
# https://stackoverflow.com/questions/924700/best-way-to-retrieve-variable-values-from-a-text-file-python-json
# --------------------------------------------------------------
    
def get_var_from_file(filename):
    f = open(filename)
    cluster_info = imp.load_source('cluster_info', filename, f)
    f.close()
    
    return cluster_info
    
# --------------------------------------------------------------
#
# --------------------------------------------------------------
    
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

# --------------------------------------------------------------
#
# --------------------------------------------------------------
    
def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

# --------------------------------------------------------------
#
# --------------------------------------------------------------
    
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]
 
# --------------------------------------------------------------
#
# --------------------------------------------------------------
    
def replace_if_exist(file, searchExp, replaceExp):
    '''
    Changes the value of a variable in a .py file if it exists, otherwise writes it
    replaceExp must contain \n for formatting
    '''
    
    infile = False
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = replaceExp
            infile = True
        sys.stdout.write(line)
     
    if infile == False :
        with open(file, 'a') as file :
            file.write(replaceExp)

            