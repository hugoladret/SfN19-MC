#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:44:11 2019

@author: hugo
"""

from PyPDF2 import PdfFileMerger
import numpy as np
import os
import imp
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

def create_ID_card(folder_list,
                   step_size,
                   verbose):
    '''
    Creates a full report on the cluster, merging multiple matplotlib fig saved as _tmp
    '''
    for folder in folder_list : 
        folder_path = '../results/%s/' % folder
        clusters_folders = [file for file in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, file))]
        
        for cluster_folder in clusters_folders :
            if verbose : print('Creating ID card for ./results/%s/%s' % (folder, cluster_folder))
            
            cluster_path = folder_path + cluster_folder
            make_pg1(folder = folder, cluster_folder = cluster_path, 
                     step_size = step_size)
            make_pg2(cluster_folder = cluster_path)
            make_pg3(cluster_folder = cluster_path)
            
            #evens are FR
            for i in np.arange(4, 20, 2) :
                make_pg4to19(cluster_folder = cluster_path,
                             n = i,
                             plot_type = 'FR')
            #odds are PSTH
            for i in np.arange(5, 21, 2) :
                make_pg4to19(cluster_folder = cluster_path,
                             n = i,
                             plot_type = 'PSTH')
                
            make_pg23(cluster_folder = cluster_path)
            
            pdfs = ['tmp%s.pdf' % x for x in np.arange(1,24)]
    
    # merge the pages
    
# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def make_pg1(folder, cluster_folder, step_size):
    '''
    Creates the first page, including cluster infos and waveform + spike stability
    '''
    cluster_info = get_var_from_file(cluster_folder + '/cluster_info.py')
    
    mean_waveform = np.load(cluster_folder + '/waveform_mean.npy')
    all_waveforms = np.load(cluster_folder + '/waveform_all.npy')
    plot_points = np.load(cluster_folder + '/waveform_plot_points.npy')
    std_waveform = np.std(all_waveforms, axis = 0)
    full_FR = np.load(cluster_folder + '/plot_MC_FR_all.npy')
    
    
    fig = plt.figure(figsize = (12,9))
    fig.tight_layout()
    gs = gridspec.GridSpec(2,2)
    axs1 = plt.subplot(gs[0, 0])
    axs2 = plt.subplot(gs[0, 1])
    axs3 = plt.subplot(gs[-1, :])
    
    # Waveform classification
    axs1.axhline(0, c = 'gray', linewidth = 2, alpha = .8)
    axs1.plot((plot_points[0], plot_points[0]),
              (plot_points[2], 0), c = 'k', linestyle = '--')
    axs1.plot((plot_points[1], plot_points[1]), 
              (plot_points[3], 0), c = 'k', linestyle = '--')
    axs1.plot((plot_points[4], plot_points[5]), 
              (plot_points[6], plot_points[7]), c = 'k', linestyle = '--')
    axs1.plot(mean_waveform, c = 'k')
    
    # Waveform shape
    axs2.plot(mean_waveform, c = 'w')
    axs2.fill_between(np.arange(0, len(mean_waveform)),
                      mean_waveform - std_waveform,
                      mean_waveform + std_waveform,
                      color = '#A62000' if cluster_info.putative_type == 'exc' else '#0B61A4')
    
    # Spike density
    axs3.plot(np.arange(0, len(full_FR))*step_size,
              full_FR, c = 'gray')
    
    axs1.set_title('Points use for waveform classification')
    axs1.set_ylabel('Amplitude')
    axs1.set_xlabel('Time (sample)')
    
    axs2.set_title('Average waveform and std')
    axs2.set_ylabel('Amplitude')
    axs2.set_xlabel('Time (sample)')
    
    axs3.set_title('Neuron activity over time of recording')
    axs3.set_ylabel('Firing rate (spk/s)')
    axs3.set_xlabel('Time (s)')
    
    plt.text(0.13, .95, 'Folder : %s' % cluster_folder, fontsize = 18, transform = plt.gcf().transFigure)
    
    plt.text(0.65, .95, 'Channel ID : %s' % cluster_info.channel_id, 
             fontsize = 15, transform = plt.gcf().transFigure)
    plt.text(0.65, .92, 'Channel depth : %s' % cluster_info.channel_depth,
             fontsize = 15, transform = plt.gcf().transFigure)
    
    plt.text(0.13, .92, 'Putative type : %s' % cluster_info.putative_type,
             fontsize = 15, transform = plt.gcf().transFigure,
             c = '#A62000' if cluster_info.putative_type == 'exc' else '#0B61A4')
             
    fig.savefig(cluster_folder + '/tmp1.pdf')
    plt.close(fig) # We don't want display
    #plt.show()

    
    
# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def make_pg2(cluster_folder) :
    '''
    Creates the second pages, with FR dynamics merged
    '''

# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def make_pg3(cluster_folder) :
    '''
    Creates the third page, with PSTH merged
    '''
  
# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def make_pg4to19(cluster_folder, n, plot_type):
    '''
    Creates the nth page, with either FR or PSTH non merged for increasing Btheta
    '''
   
# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def make_pg23(cluster_folder):
    '''
    Creates the final page, with merged and non merged tuning curve, as well
    as the neurometric curve
    '''
  
# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def get_var_from_file(filename):
    f = open(filename)
    cluster_info = imp.load_source('cluster_info', '', f)
    f.close()
    
    return cluster_info


create_ID_card(['A005_a17'], verbose = True, step_size = .002)
    