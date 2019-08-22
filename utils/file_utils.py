#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:44:11 2019

@author: hugo

Contains the functions for :
    Kwik conversion from kwd to bin and from kwd to npy
    npy conversion to bin
    KwikTool loader

"""

import numpy as np
import h5py

def kwd_to_file(kwik_path, experiment_name, pipeline_name,
               channel_map, photodiode_index,
               output_type = 'bin',
               verbose = True):
    '''
    Directly converts a kwik file (.raw.kwd extension) to a file for the pipeline,
    whether a bin in case no recording merging is needed or a npy in case further merging is needed
    
    Array types in case of a numpy output : int16 photodiode, float64 timestamps, int16 data
    
    Args :
        -kwik_path STR : the relative path to the experiment1_100.raw.kwd file
        -experiment_name STR : the name of the experiment, ex : "A005_a17", 
            used to identify subsequent files, NOT to load raw files
        -pipeline_name STR : the name of the current pipeline
        -channel_map ARR = channel map of the channels to extract from the kwd file
        -photodiode_index INT = index of the photodiode in the raw data, usually an analog in the bottom rows
        -output_type STR = 'bin', 'npy', the type of conversion to use
        -verbose BOOL : whether the pipeline gets the right to talk
    '''
    print('# Converting a kwd file to a >%s< file #' % output_type)
    # -------------------------------------------------------------------------
    if verbose : print('Loading raw.kwd file into memory ...')
    
    dataset = kwk_load(kwik_path, 'all')
    
    data = dataset['data']['0']
    channels = dataset['channel_bit_volts']['0']
    timestamps = dataset['timestamps']['0']
    
    data2 = np.asarray(data)[: , channel_map]
    photodiode_data = data[:, photodiode_index]

    del data
    
    # -------------------------------------------------------------------------
    if verbose : print('Done ! Found %.3f seconds of recording. '% (timestamps.max() -timestamps.min()))
    
    # -------------------------------------------------------------------------
    # BIN CONVERSION
    # -------------------------------------------------------------------------
    if output_type == 'bin' :
        if verbose : print('Saving numpy array as an int16 binary file ...')
        data2.astype('int16').tofile('./pipelines/%s/%s.bin' % (pipeline_name, experiment_name))
        photodiode_data.astype('int16').tofile('./pipelines/%s/%s_phtdiode.bin' % (pipeline_name, experiment_name))
        timestamps.astype('int16').tofile('./pipelines/%s/%s_timestamps.bin' % (pipeline_name, experiment_name))
    
        if verbose : print('Done ! Running sanity check for input and saved file identity ...')
        test = np.fromfile('./pipelines/%s/%s.bin' % (pipeline_name, experiment_name), dtype = 'int16')
        if np.array_equal(data2, test.reshape((-1, channel_map.shape[0]))) :
            del data2
            del test
            
            if verbose : print('Sanity check passed.')
            print('Conversion from raw.kwd to int16 binary file successfully completed !\n')
            
            with open('./pipelines/%s/debugfile.txt' %pipeline_name, 'a') as file:
                file.write('| VAR_nbr_channels = %s | \n'%channels.shape[0])
                file.write('| VAR_timestamps_min = %s | \n' % timestamps.min())
                file.write('| VAR_timestamps_max = %s | \n' % timestamps.max())
                return 1
    
        else :
            print('Channel map shape and output shape are not matching. Unclog the pipeline in utils.py')
            return 0
    
            
    # -------------------------------------------------------------------------
    # NPY CONVERSION
    # -------------------------------------------------------------------------
    elif output_type == 'npy' :
        if verbose : print('Saving numpy array as a >.npy file< ...')
        np.save('./pipelines/%s/%s.npy' % (pipeline_name, experiment_name), data2)
        np.save('./pipelines/%s/%s_phtdiode.npy' % (pipeline_name, experiment_name), photodiode_data)
        np.save('./pipelines/%s/%s_timestamps.npy' % (pipeline_name, experiment_name), timestamps)

        if verbose : print('Done ! Running sanity check for input and saved file identity ...')
        test = np.load('./pipelines/%s/%s.npy' % (pipeline_name, experiment_name))
        if np.array_equal(data2, test) : #no reshape needed, np.save and .load keep the structure
            del data2
            del test
            
            if verbose : print('Sanity check passed.')
            print('Conversion from raw.kwd to npy file successfully completed !\n')
        
            with open('./pipelines/%s/debugfile.txt' %pipeline_name, 'a') as file:
                file.write('| VAR_nbr_channels = %s | \n'%channels.shape[0])
                file.write('| VAR_timestamps_min = %s | \n' % timestamps.min())
                file.write('| VAR_timestamps_max = %s | \n' % timestamps.max())
                return 1
    
        else :
            print('Channel map shape and output shape are not matching. Unclog the pipeline in utils.py')
            return 0
        
    else :
        print('Output format not implemented.')
        return 0
    
# --------------------------------------------------------------
#
# --------------------------------------------------------------
        
def np_to_bin(experiment_name,
              pipeline_name,
              verbose = True):
    '''
    Converts a .npy file to a binary file for Spyking Circus
    This is used in case multiple raw kwd files have been transformed to numpy arrays and merged
    '''
    print('# Converting a npy file to bin #')
    # -------------------------------------------------------------------------
    if verbose : print('Loading numpy array from disk ...')
    arr = np.load('./pipelines/%s/%s.npy'% (pipeline_name, experiment_name))
    
    # -------------------------------------------------------------------------
    if verbose : print('Done ! Converting to bin file ...')
    arr.astype('int16').tofile('./pipelines/%s/%s.bin' % (pipeline_name, experiment_name))
    
    # -------------------------------------------------------------------------
    if verbose : print('Done ! Running sanity check ...')
    
    test = np.fromfile('./pipelines/%s/%s.bin' % (pipeline_name, experiment_name), dtype = 'int16')
    chan_nbr = int(variable_from_debugfile('VAR_nbr_channels', pipeline_name))
    
    if np.array_equal(arr,test.reshape((-1, chan_nbr))) :
        del arr
        del test
        
        if verbose : print('Sanity check passed.')
        print('Conversion from npy to bin successfully completed !\n')
        
# --------------------------------------------------------------
# @author: Josh Siegle
# https://github.com/klusta-team/kwiklib
# --------------------------------------------------------------
        
def kwk_load(filename, dataset=0):
    f = h5py.File(filename, 'r')
    
    if filename[-4:] == '.kwd':
        data = {}
        
        if dataset == 'all':
            data['info'] = {Rec: f['recordings'][Rec].attrs 
                            for Rec in f['recordings'].keys()}
            
            data['data'] = {Rec: f['recordings'][Rec]['data']
                            for Rec in f['recordings'].keys()}
            
            R = list(f['recordings'])[0]
            if 'channel_bit_volts' in f['recordings'][R]\
                                       ['application_data'].keys():
                data['channel_bit_volts'] = {Rec: f['recordings'][Rec]\
                                                   ['application_data']\
                                                   ['channel_bit_volts']
                                             for Rec in f['recordings'].keys()}
            else:
                # Old OE versions do not have channel_bit_volts info.
                # Assuming bit volt = 0.195 (Intan headstages). 
                # Keep in mind that analog inputs have a different value!
                # In out system it is 0.00015258789
                data['channel_bit_volts'] = {Rec: [0.195]*len(
                                                 data['data'][Rec][1, :]
                                                             )
                                             for Rec in f['recordings'].keys()}
                
            
            data['timestamps'] = {Rec: ((
                                        np.arange(0,data['data'][Rec].shape[0])
                                        + data['info'][Rec]['start_time'])
                                       / data['info'][Rec]['sample_rate'])
                                       for Rec in f['recordings']}
        
        else:
            data['info'] = f['recordings'][str(dataset)].attrs
            data['channel_bit_volts'] = f['recordings'][str(dataset)]\
                                         ['application_data']\
                                         ['channel_bit_volts']
            data['data'] = f['recordings'][str(dataset)]['data']
            data['timestamps'] = ((np.arange(0,data['data'].shape[0])
                                   + data['info']['start_time'])
                                  / data['info']['sample_rate'])
        return(data)
    
    elif filename[-4:] == '.kwe':
        data = {}    
        data['Messages'] = f['event_types']['Messages']['events']
        data['TTLs'] = f['event_types']['TTL']['events']
        return(data)
    
    elif filename[-4:] == 'kwik':
        data = {}    
        data['Messages'] = f['event_types']['Messages']['events']
        data['TTLs'] = f['event_types']['TTL']['events']
        return(data)
    
    elif filename[-4:] == '.kwx':
        data = f['channel_groups']
        return(data)
    
    else:
        print('Supported files: .kwd, .kwe, .kwik, .kwx')
        
# --------------------------------------------------------------
#
# --------------------------------------------------------------

def variable_from_debugfile(lookup_str, pipeline_name) :
    '''
    Returns a variable stored under the lookup_str string in the debugfile.txt file
    '''
    file = open('./pipelines/%s/debugfile.txt'%pipeline_name, 'r')
    for row in file :
        if lookup_str in row :
            var = row.split(' = ')[1].split(' |')[0]
    return var
    
