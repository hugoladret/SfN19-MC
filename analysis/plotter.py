#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:44:11 2019

@author: hugo
"""

from PyPDF2 import PdfFileMerger
import numpy as np
import os, glob 
import imp
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from tqdm import tqdm

def create_ID_card(folder_list,
                   step_size, win_size,
                   beg_PST, end_PST,
                   fs, binsize, end_TC,
                   verbose):
    '''
    Creates a full report on the cluster, merging multiple matplotlib fig saved as _tmp
    '''
    for folder in folder_list : 
        folder_path = './results/%s/' % folder
        clusters_folders = [file for file in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, file))]
        
        for cluster_folder in clusters_folders :
            if verbose : print('Creating ID card for ./results/%s/%s ...' % (folder, cluster_folder))
            pbar = tqdm(total = 11)
            cluster_path = folder_path + cluster_folder
            
            make_pg1(folder = folder, cluster_folder = cluster_path, 
                     step_size = step_size, fs = fs)
            pbar.update(1)
            
            '''make_pg2(cluster_folder = cluster_path,
                     step_size = step_size, win_size = win_size,
                     beg_PST = beg_PST, end_PST = end_PST)
            pbar.update(1)'''
            
            make_pg3(cluster_folder = cluster_path,
                     step_size = step_size, win_size = win_size,
                     beg_PST = beg_PST, end_PST = end_PST,
                     fs = fs, binsize = binsize) 
            
            pbar.update(1)
            '''#evens are FR
            for i in np.arange(4, 20, 2) :
                make_pg4to19(cluster_folder = cluster_path,
                             n = i, plot_type = 'FR', 
                             beg_PST = beg_PST, end_PST = end_PST,
                             win_size = win_size, step_size = step_size,
                             binsize = binsize)
                pbar.update(1)'''
                
            #odds are PSTH
            for i in np.arange(4, 12, 1) :
                make_pg4to19(cluster_folder = cluster_path,
                             n = i, plot_type = 'PSTH',
                             beg_PST = beg_PST, end_PST = end_PST,
                             win_size = win_size, step_size = step_size,
                             binsize = binsize)
                pbar.update(1)
                
            make_pg20(cluster_folder = cluster_path, end_TC = end_TC, fs = fs)
            pbar.update(1)
            
            pbar.close()
            
            pdfs = [cluster_path + '/tmp%s.pdf' % x for x in np.arange(1,12)]
            merger = PdfFileMerger()

            for pdf in pdfs:
                merger.append(pdf)
            
            merger.write(cluster_path + 'ID_card.pdf')
            merger.close()
            
            
            for filename in glob.glob(cluster_path + '/tmp*'):
                os.remove(filename) 
                
            print('Done !')
            
    # merge the pages
    
# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def make_pg1(folder, cluster_folder, step_size, fs):
    '''
    Creates the first page, including cluster infos and waveform + spike stability
    '''
    cluster_info = get_var_from_file(cluster_folder + '/cluster_info.py')
    
    mean_waveform = np.load(cluster_folder + '/waveform_mean.npy')
    all_waveforms = np.load(cluster_folder + '/waveform_all.npy')
    plot_points = np.load(cluster_folder + '/waveform_plot_points.npy')
    std_waveform = np.std(all_waveforms, axis = 0)

    r_squareds = np.load(cluster_folder + '/plot_neurometric_fit_reports.npy')
    unique_bthetas = np.load(cluster_folder + '/unique_bthetas.npy') *  180 / np.pi

    spiketimes = np.load(cluster_folder + '/spiketimes.npy')
    #full_FR = np.load(cluster_folder + '/plot_MC_FR_all.npy')
    
    
    fig = plt.figure(figsize = (12,9))
    fig.tight_layout()
    gs = gridspec.GridSpec(2,2)
    axs1 = plt.subplot(gs[0, 0])
    axs2 = plt.subplot(gs[0, 1])
    axs3 = plt.subplot(gs[-1, :])
    
    # Waveform classification
    axs1.plot(unique_bthetas, r_squareds, c = 'k')
    
    # Waveform shape
    axs2.plot(mean_waveform, c = 'w')
    axs2.fill_between(np.arange(0, len(mean_waveform)),
                      mean_waveform - std_waveform,
                      mean_waveform + std_waveform,
                      color = '#A62000' if cluster_info.putative_type == 'exc' else '#0B61A4')
    
    # Spike density
    axs3.hist(spiketimes, int(np.max(spiketimes) /fs), color = 'gray')
    
    axs1.set_title('Goodness of fits - max r² = %.2f' % np.max(r_squareds))
    axs1.set_ylabel('r²')
    axs1.set_xlabel(r'$B_\theta$' + ' stim')
    
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
    
def make_pg2(cluster_folder, step_size, win_size,
             beg_PST, end_PST) :
    '''
    Creates the second pages, with FR dynamics merged
    '''
    
    PSTH_FR_list = np.load(cluster_folder + '/plot_MC_FR_dynamics_merged.npy') / win_size # makes it in FR not in spikes per window
    unique_thetas = np.load(cluster_folder + '/unique_thetas.npy') *  180 / np.pi
    
    ys = np.linspace(.85, .13, len(PSTH_FR_list))
    colors = plt.cm.viridis(np.linspace(0, .8, len(PSTH_FR_list)))
    
    fig, ax  = plt.subplots(len(PSTH_FR_list), 2, sharex = 'col', figsize = (12, 9))
    
    means = [np.mean(theta, axis = 0) for theta in PSTH_FR_list]
    min_mean = np.min(means)
    max_mean = np.max(means)
    
    for it_0, theta in enumerate(PSTH_FR_list):
        for trial in theta :
            ax[it_0][0].plot(np.linspace(beg_PST, end_PST, len(trial)),
                         trial, color = colors[it_0], linewidth = .3)
            
        ax[it_0][1].plot(np.linspace(beg_PST, end_PST, len(trial)),
                         np.mean(theta, axis = 0),
                         color = colors[it_0])
        
        plt.text(0.02, ys[it_0], r'$\theta$' + '=%.1f°' % unique_thetas[it_0], fontsize = 9, transform = plt.gcf().transFigure, 
                 c = colors[it_0])
        
        ax[it_0][0].set_ylim(0, np.max(theta))
        ax[it_0][1].set_ylim(min_mean,
                             max_mean)
        
        if it_0 == len(PSTH_FR_list) - 1 :
            ax[it_0][0].set_xlabel('PST (s)')
            ax[it_0][0].set_ylabel('Mean FR\n(sp/s)')
            
            ax[it_0][1].set_xlabel('PST (s)')
            ax[it_0][1].set_ylabel('Mean FR\n(sp/s)')
        
    plt.suptitle('Firing rate dynamics around PST \nAll ' +  r'$B_\theta$' + ' stim. merged',
                 y = .95, fontsize = 15, )
    
    #plt.show()
    fig.savefig(cluster_folder + '/tmp2.pdf', bbox_inches = 'tight')
    plt.close(fig) # We don't want display
        
     

# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def make_pg3(cluster_folder, step_size, win_size,
             beg_PST, end_PST, 
             fs, binsize) :
    '''
    Creates the third page, with PSTH merged
    '''
    
    PSTH_list = np.load(cluster_folder + '/plot_MC_PSTH_merged.npy', allow_pickle = True)
    unique_thetas = np.load(cluster_folder + '/unique_thetas.npy') *  180 / np.pi
    
    n_bin = (end_PST) - (beg_PST) 
    n_bin*=1000
    n_bin/= binsize
 
    ys = np.linspace(.85, .13, len(PSTH_list))
    colors = plt.cm.viridis(np.linspace(0, .8, len(PSTH_list)))
    
    fig, ax = plt.subplots(len(PSTH_list), 2, sharex = 'col', figsize = (12, 9))
    
    hists = [np.histogram(np.concatenate(theta), int(n_bin))[0] for theta in PSTH_list]
    min_hist = np.min(hists)
    max_hist = np.max(hists)
    
    for it_0, theta in enumerate(PSTH_list) : 
        for it_1, trial in enumerate(theta) :
            ax[it_0][0].scatter(trial, np.full_like(trial, it_1), s =  .3,
                                color = colors[it_0])
        
        
        ax[it_0][1].hist(np.concatenate(theta), int(n_bin), color = colors[it_0])
        
        plt.text(0.02, ys[it_0], r'$\theta$' + '=%.1f°' % unique_thetas[it_0], fontsize = 9, transform = plt.gcf().transFigure, 
                 c = colors[it_0])
        
        ax[it_0][0].set_xlim(beg_PST, end_PST)
        ax[it_0][1].set_xlim(beg_PST, end_PST)
        ax[it_0][1].set_ylim(min_hist, max_hist)
        
        if it_0 == len(PSTH_list)-1 :
                ax[it_0][0].set_xlabel('PST (s)')
                ax[it_0][0].set_ylabel('Trial')
                ax[it_0][1].set_xlabel('PST (s)')
                ax[it_0][1].set_ylabel('sp/bin')
        
    plt.suptitle('PSTH, All ' +  r'$B_\theta$' + ' stim. merged\n Histogram with %sms bin size' % binsize,  y = .95, fontsize = 15, )
    
    fig.savefig(cluster_folder + '/tmp3.pdf', bbox_inches = 'tight')
    plt.close(fig)
  
# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def make_pg4to19(cluster_folder,
                 beg_PST, end_PST,
                 win_size, step_size,
                 binsize,
                 n, plot_type):
    '''
    Creates the nth page, with either FR or PSTH non merged for increasing Btheta
    '''
    
    # ------------
    # FR
    # ------------
    if plot_type == 'FR' : 
        i = np.where(np.arange(4, 20, 2) == n)[0][0] #get b_theta nbr
        
        PSTH_FR_list = np.load(cluster_folder + '/plot_MC_FR_dynamics_nonmerged.npy')[i] 
        PSTH_FR_list = PSTH_FR_list / win_size
        
        unique_thetas = np.load(cluster_folder + '/unique_thetas.npy') *  180 / np.pi
        unique_bthetas = np.load(cluster_folder + '/unique_bthetas.npy') *  180 / np.pi
        
        ys = np.linspace(.85, .13, len(PSTH_FR_list))
        colors = plt.cm.viridis(np.linspace(0, .8, len(PSTH_FR_list)))
        
        means = [np.mean(theta, axis = 0) for theta in PSTH_FR_list]
        min_mean = np.min(means)
        max_mean = np.max(means)
    
        fig, ax  = plt.subplots(len(PSTH_FR_list), 2, sharex = 'col', figsize = (12, 9))
    
        for it_0, theta in enumerate(PSTH_FR_list):
            for trial in theta :
                ax[it_0][0].plot(np.linspace(beg_PST, end_PST, len(trial)),
                             trial, color = colors[it_0], linewidth = .3)
                
            ax[it_0][1].plot(np.linspace(beg_PST, end_PST, len(trial)),
                             np.mean(theta, axis = 0),
                             color = colors[it_0])
            
            plt.text(0.02, ys[it_0], r'$\theta$' + '=%.1f°' % unique_thetas[it_0], fontsize = 9, transform = plt.gcf().transFigure, 
                     c = colors[it_0])
            ax[it_0][0].set_ylim(0, np.max(theta))
            ax[it_0][1].set_ylim(min_mean,
                             max_mean)
            
            if it_0 == len(PSTH_FR_list) - 1 :
                ax[it_0][0].set_xlabel('PST (s)')
                ax[it_0][0].set_ylabel('Mean FR\n(sp/s)')
                
                ax[it_0][1].set_xlabel('PST (s)')
                ax[it_0][1].set_ylabel('Mean FR\n(sp/s)')
            
        plt.suptitle(r'$B_\theta$' + ' = %.1f°' % unique_bthetas[i] + '\nFiring rate dynamics around PST', 
                     y = .95, fontsize = 15, )
        
        #plt.show()
        fig.savefig(cluster_folder + '/tmp%s.pdf' % n, bbox_inches = 'tight')
        plt.close(fig) # We don't want display
       
        
    # ------------
    # PSTH
    # ------------
    elif plot_type == 'PSTH' :
        i = np.where(np.arange(4, 12, 1) == n)[0][0] #get b_theta nbr

        PSTH_list = np.load(cluster_folder + '/plot_MC_PSTH_nonmerged.npy', allow_pickle = True)[i]
        
        unique_thetas = np.load(cluster_folder + '/unique_thetas.npy') *  180 / np.pi
        unique_bthetas = np.load(cluster_folder + '/unique_bthetas.npy') *  180 / np.pi
        
        n_bin = (end_PST) - (beg_PST) 
        n_bin*=1000
        n_bin/= binsize
        
        hists = [np.histogram(np.concatenate(theta), int(n_bin))[0] for theta in PSTH_list]
        min_hist = np.min(hists)
        max_hist = np.max(hists)
     
        ys = np.linspace(.85, .13, len(PSTH_list))
        colors = plt.cm.viridis(np.linspace(0, .8, len(PSTH_list)))
        
        fig, ax = plt.subplots(len(PSTH_list), 2, sharex = 'col', figsize = (12, 9))
    
        for it_0, theta in enumerate(PSTH_list) : 
            for it_1, trial in enumerate(theta) :
                ax[it_0][0].scatter(trial, np.full_like(trial, it_1), s =  .3,
                                    color = colors[it_0])
            
            
            ax[it_0][1].hist(np.concatenate(theta), int(n_bin), color = colors[it_0])
            
            plt.text(0.02, ys[it_0], r'$\theta$' + '=%.1f°' % unique_thetas[it_0], fontsize = 9, transform = plt.gcf().transFigure, 
                     c = colors[it_0])
            
            ax[it_0][0].set_xlim(beg_PST, end_PST)
            ax[it_0][1].set_xlim(beg_PST, end_PST)
            ax[it_0][1].set_ylim(min_hist, max_hist+1)
            
            if it_0 == len(PSTH_list)-1 :
                    ax[it_0][0].set_xlabel('PST (s)')
                    ax[it_0][0].set_ylabel('Trial')
                    ax[it_0][1].set_xlabel('PST (s)')
                    ax[it_0][1].set_ylabel('sp/bin')
            
        plt.suptitle(r'$B_\theta$' + ' = %.1f°' % unique_bthetas[i] + '\nHistogram with %sms bin size' % binsize,
                     y = .95, fontsize = 15, )
        
        fig.savefig(cluster_folder + '/tmp%s.pdf' % n, bbox_inches = 'tight')
        plt.close(fig) # We don't want display
       
   
# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def make_pg20(cluster_folder, end_TC, fs):
    '''
    Creates the final page, with merged and non merged tuning curve, as well
    as the neurometric curve
    '''

    unique_thetas = np.load(cluster_folder + '/unique_thetas.npy') *  180 / np.pi
    unique_thetas = np.round(unique_thetas, 1)
    
    unique_bthetas = np.load(cluster_folder + '/unique_bthetas.npy') *  180 / np.pi
        
    fig = plt.figure(figsize = (11,17))
    fig.tight_layout()
    
    gs = gridspec.GridSpec(12,6)
    
    axs1 = plt.subplot(gs[0:2, 0:2]) # merged TC
    axs2 = plt.subplot(gs[0:2, 2:-1]) # neurometric
    
    axs3 = plt.subplot(gs[3:5, :2]) # b theta 0 to
    axs4 = plt.subplot(gs[5:7, :2])
    axs5 = plt.subplot(gs[7:9, :2])
    axs6 = plt.subplot(gs[9:11, :2]) # btheta 4
    
    axs7 = plt.subplot(gs[3:5, 3:-1]) # b theta 4 to
    axs8 = plt.subplot(gs[5:7, 3:-1])
    axs9 = plt.subplot(gs[7:9, 3:-1])
    axs10 = plt.subplot(gs[9:11, 3:-1]) # btheta 8
    TC_nonmerged_axs = [axs3, axs4, axs5, axs6,
                        axs7, axs8, axs9, axs10]
    colors = plt.cm.magma(np.linspace(.8, 0, len(TC_nonmerged_axs)))

    # Merged TC plot
    mean_FR_per_theta = np.load(cluster_folder + '/plot_MC_TC_merged_means.npy')
    stds_FR_per_theta = np.load(cluster_folder + '/plot_MC_TC_merged_stds.npy')
    r_squared = np.load(cluster_folder + '/plot_neurometric_fit_reports.npy')
    
    fitted_merge_curve = np.load(cluster_folder + '/plot_neurometric_merged_fitted_TC.npy')
    btheta_merge_curve = np.load(cluster_folder + '/plot_neurometric_merged_Btheta_fits.npy')
    r_squared_merge_curve = np.load(cluster_folder + '/plot_neurometric_merged_fit_reports.npy')

    # Non merged TC
    mean_FR_per_btheta = np.load(cluster_folder + '/plot_MC_TC_nonmerged_means.npy')
    stds_FR_per_btheta = np.load(cluster_folder + '/plot_MC_TC_nonmerged_stds.npy')
    fitted_TC = np.load(cluster_folder + '/plot_neurometric_fitted_TC.npy')

    max_FR = np.max(mean_FR_per_btheta)*1.1
    min_FR = np.min(mean_FR_per_btheta)*.9

    
    plt.text(0.38, .72, 'Spikes on [0;%.1f]s interval'% end_TC, fontsize = 12, transform = plt.gcf().transFigure)

    axs1.plot(unique_thetas, mean_FR_per_theta, '.k')
    axs1.plot(unique_thetas, fitted_merge_curve[0])
#    axs1.errorbar(unique_thetas, mean_FR_per_theta, stds_FR_per_theta, fmt = 'none',
#                  capsize = 2,c = 'gray')
    axs1.set_xlabel(r'$\theta$' + '°')
    axs1.set_ylabel('FR (sp/s)')
    axs1.set_title('Tuning curve, averaged over all ' + r'$B_\theta$stim' +'\n' + r'$B_\theta$fit = %.2f' % btheta_merge_curve[0] + '    r² = %.2f' % r_squared_merge_curve[0],
     fontsize = 10)
    axs1.set_ylim(min_FR, max_FR)
    
    # Neurometric TC plot
    bthetas_fit = np.load(cluster_folder + '/plot_neurometric_Btheta_fits.npy')
    axs2.plot(unique_bthetas, bthetas_fit, 'k')
    axs2.yaxis.tick_right()
    axs2.yaxis.set_label_position('right')
    axs2.set_xlabel(r'$B_\theta$' + ' stim')
    axs2.set_ylabel(r'$B_\theta$' + ' fit')
    axs2.set_title('TC opening for each ' + r'$B_\theta$' + ' stim', fontsize = 10)
    
    
    
    
    ys = np.linspace(.62, .25, 4)
    for i, ax in enumerate(TC_nonmerged_axs) :
        ax.plot(unique_thetas, mean_FR_per_btheta[i], '.k')
#        ax.errorbar(unique_thetas, mean_FR_per_btheta[i], stds_FR_per_btheta[i], fmt = 'none',
#                  capsize = 2,c = 'gray')
        ax.plot(unique_thetas, fitted_TC[i], c = colors[i])
        ax.set_ylim(min_FR, max_FR)
        
        if i == 0 or i == 4:
            ax.set_title('Tuning curve for one '+r'$B_\theta$', fontsize = 10)
        
        if i <= 3 : 
            plt.text(0.38, ys[i]+.015, r'$B_\theta$ stim' + '=%.1f°' % unique_bthetas[i], fontsize = 12, transform = plt.gcf().transFigure)
            plt.text(0.38, ys[i]-.02, r'$B_\theta$ fit' + '=%.1f°' % bthetas_fit[i], fontsize = 12, transform = plt.gcf().transFigure)
            plt.text(0.38, ys[i]-.035, 'r² = %.2f' % r_squared[i], fontsize = 12, transform = plt.gcf().transFigure)
        else : 
            plt.text(0.78, ys[i-4]+.015, r'$B_\theta$ stim' + '=%.1f°' % unique_bthetas[i], fontsize = 12, transform = plt.gcf().transFigure)
            plt.text(0.78, ys[i-4]-.02, r'$B_\theta$ fit' + '=%.1f°' % bthetas_fit[i], fontsize = 12, transform = plt.gcf().transFigure)
            plt.text(0.78, ys[i-4]-.035, 'r² = %.2f' % r_squared[i], fontsize = 12, transform = plt.gcf().transFigure)
            
        if i == 3 or i == 7 :
            ax.set_xlabel(r'$\theta$' + '°')
            ax.set_ylabel('FR (sp/s)')
            
        else :
            ax.set_xticks([])
            #ax.set_yticks([])

    fig.savefig(cluster_folder + '/tmp2.pdf', bbox_inches = 'tight')
    plt.close(fig) # We don't want display
  
# --------------------------------------------------------------
# 
# --------------------------------------------------------------
    
def get_var_from_file(filename):
    f = open(filename)
    cluster_info = imp.load_source('cluster_info', filename)
    f.close()
    
    return cluster_info


#create_ID_card(['A005_a17'], verbose = True, 
#               step_size = .002, win_size = .2,
#                   beg_PST = -.5, end_PST = 1.5,
#                   fs = 30000.0, binsize = 5)
    