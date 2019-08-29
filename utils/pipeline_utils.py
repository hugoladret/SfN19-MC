#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:44:11 2019

@author: hugo

Contains the functions to manipulate folders for the pipeline such as :
    Creating the pipeline folder and debugfile
"""

import os
import subprocess
import shutil
import fileinput
import sys
import numpy as np
import csv
from tqdm import tqdm


def create_pipeline(pipeline_name, verbose = True):
    '''
    Creates a pipeline folder, which will contain :
        In either case :
            The binary file sent to Spyking Circus
        In case of merging :
            Temporarily the multiple numpy arrays from the multiple raw kwd files
            Permanently the merged numpy array
    '''
    print('# Creating a new pipeline #')
          
    path = './pipelines/'+pipeline_name
    
    if verbose : print('Initializing a new pipeline in %s ...' % path)
    
    if not os.path.exists(path):
        os.makedirs(path)
        os.makedirs(path+'/bins')
        os.makedirs(path+'/sorted')
        with open('./pipelines/%s/debugfile.txt' %pipeline_name, 'a') as file:
                file.write('## Debug file, do not delete unless you want to spike sorting to rerun ##\n')
        if verbose : print('Done !\n')
        
    else:
        print('A pipeline already exists under this name !\n')
       
# --------------------------------------------------------------
# UNUSED
# --------------------------------------------------------------
        
def call_phy(pipeline_name, data_name) :
    try :
        subprocess.call(['phy', 'template-gui', 'params.py'], 
                        cwd = './pipelines/%s/%s/%s-merged.GUI/' % (pipeline_name, data_name, data_name))
    except AttributeError: 
        print('Closing Phy')

# --------------------------------------------------------------
#
# --------------------------------------------------------------
        
def open_sort_folder(pipeline_name) :
    subprocess.call(['nautilus', os.getcwd()+'/pipelines/%s/mydata_0/mydata_0-merged.GUI' % pipeline_name])
    
# --------------------------------------------------------------
#
# --------------------------------------------------------------
        
def clean_up(pipeline_name, verbose = True) :
    '''
    Restructure the pipeline folders to be a bit more user-friendly, my bad for poor initial structure
    
    moves photodiode and timestamps bin files back into the main folder
    removes the channel map and the parameter files
    move merged and clean data into the main folder - rewrites dat_path and dir_path accordingly
    '''
    print('# Cleaning up result folder #')
          
    binpath = './pipelines/%s/bins/' % pipeline_name
    mainpath = './pipelines/%s/' % pipeline_name
    npypath = './pipelines/%s/mydata_0/mydata_0-merged.GUI/' % pipeline_name
    sortingpath = './pipelines/%s/mydata_0/' % pipeline_name
    
    # Removes the spike sorting files
    main_files = [file for file in os.listdir(mainpath) if os.path.isfile(os.path.join(mainpath, file))]
    for main_file in main_files :
        if '.prb' in main_file or '.params' in main_file or '.log' in main_file :
            os.remove(mainpath + main_file)
    
    # Moves the bin files
    if os.path.exists(binpath) :
        extra_bins = [file for file in os.listdir(binpath) if os.path.isfile(os.path.join(binpath, file))]
        for extra_bin in tqdm(extra_bins) :
            shutil.move(binpath + extra_bin , mainpath + extra_bin)
        
        shutil.rmtree(binpath, ignore_errors = True) #in case of a read-only lock
    
    # Moves the npy files
    if os.path.exists(npypath) :
        for file in tqdm(os.listdir(npypath)) :
            shutil.move(npypath + file , mainpath + '/sorted/' + file)
            
        shutil.rmtree(npypath, ignore_errors = True)
    
    shutil.rmtree(sortingpath, ignore_errors = True)
    
    # Rewrites the paths accordingly
    # https://stackoverflow.com/questions/39086/search-and-replace-a-line-in-a-file-in-python
    file = mainpath + '/sorted/' +'params.py'
    searchExp = 'dir_path'
    replaceExp = 'dir_path = r"%s/pipelines/%s/sorted/"\n' % (os.getcwd(), pipeline_name)
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = replaceExp
        sys.stdout.write(line)
        
def export_to_results(pipeline_name, verbose):
    '''
    Exports the data to results folder/pipeline_name subfolder/clusters folders
    '''
    print('\n# Exporting results to /results/ #')
    path = './pipelines/'+pipeline_name
    resultpath = './results/'+pipeline_name
    
     # Spiketimes
    spiketimes = np.load(path+'/sorted/spike_times.npy')
    # Cluster ID per spiketimes
    spiketimes_clusters_id = np.load(path+'/sorted/spike_clusters.npy')
    
    # Spiketimes/clusters tuple table
    spike_cluster_table = []
    for i, spike in enumerate(spiketimes):
        spike_cluster_table.append((spike, spiketimes_clusters_id[i]))
        
    # Good clusters as labelled by phy
    good_clusters = []
    with open(path+'/sorted/cluster_info.tsv', 'r') as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            row_values = row[0].split('\t')
            cluster_id, channel, group = row_values[0], row_values[2], row_values[5]
            depth, n_spikes = row_values[3], row_values[6]
            if group == 'good' :
                good_clusters.append([int(cluster_id), int(channel), float(depth), int(n_spikes)])
                
    # Spiketimes for each good cluster
    good_spikes = []
    for good_cluster in good_clusters :
        tmp_lst = []
        for spike_cluster in spike_cluster_table :
            if spike_cluster[-1] == good_cluster[0] :
                tmp_lst.append(spike_cluster[0])
        good_spikes.append(tmp_lst)
        
    # and remerging structure
    merged_clusters = []
    for i, g_cluster in enumerate(good_clusters) :
        cluster_id, cluster_channel = g_cluster[0], g_cluster[1]
        cluster_depth, cluster_nspikes = g_cluster[2], g_cluster[3]
        cluster_spiketimes = good_spikes[i]
        
        merged_cluster = [cluster_id, cluster_channel, cluster_depth, cluster_nspikes, cluster_spiketimes]
        merged_clusters.append(merged_cluster)
        
    # export everything
    os.makedirs(resultpath)
    for merged_cluster in tqdm(merged_clusters, 'Moving into subfolders') :
        cluster_path = resultpath+ '/cluster_' + str(merged_cluster[0])
        os.makedirs(cluster_path)
        
        # save spiketimes
        np.save(cluster_path + '/spiketimes.npy', merged_cluster[-1])
        
        #save infos
        with open(cluster_path + '/cluster_info.py', 'w+') as file :
            file.write('channel_id = %d\n' % merged_cluster[1])
            file.write('channel_depth = %.2f\n' % merged_cluster[2])
            file.write('n_spikes = %d\n' % merged_cluster[3])
            file.write('raw_path = %s\n' % ('r"'+path+'"'))
            
        