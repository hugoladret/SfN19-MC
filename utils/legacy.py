#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 13:45:53 2019

@author: hugo
"""
   
def kwk_to_bin(kwik_path, experiment_name, pipeline_name,
               channel_map, photodiode_index,
               verbose = True):
    '''
    Directly converts a kwik file (.raw.kwd extension) to a binary file for Spyking Circus
    This is used in case no merging is needed and we want to straight-up go for spike sorting
    
    Args :
        -kwik_path STR : the relative path to the experiment1_100.raw.kwd file
        -experiment_name STR : the name of the experiment, ex : "A005_a17", 
            used to identify subsequent files, NOT to load raw files
        -pipeline_name STR : the name of the current pipeline
        -channel_map ARR = channel map of the channels to extract from the kwd file
        -photodiode_index INT = index of the photodiode in the raw data, usually an analog in the bottom rows
        -verbose BOOL : whether the pipeline gets the right to talk
    '''
    print('# Converting a kwd file to bin file #')
    # -------------------------------------------------------------------------
    if verbose : print('Loading raw.kwd file into a numpy array ...')
    
    dataset = kwk_load(kwik_path, 'all')
    
    data = dataset['data']['0']
    channels = dataset['channel_bit_volts']['0']
    timestamps = dataset['timestamps']['0']
    
    data2 = np.asarray(data)[: , channel_map]
    del data
    
    # -------------------------------------------------------------------------
    if verbose : print('Done ! Found %.3f seconds of recording'% (timestamps.max() -timestamps.min()))
    
    # -------------------------------------------------------------------------
    if verbose : print('Saving numpy array as an int16 binary file ...')
    
    data2.astype('int16').tofile('./pipelines/%s/%s.bin' % (pipeline_name, experiment_name))
    
    # -------------------------------------------------------------------------
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

# --------------------------------------------------------------
#
# --------------------------------------------------------------
       
def kwk_to_npy(kwik_path, experiment_name,
               pipeline_name,
               verbose = True):
    '''
    Converts a kwik file (.raw.kwd extension) to a numpy file
    This is used to convert a raw kwd to an intermediate array for merging
    
    Args :
        -kwik_path STR : the relative path to the experiment1_100.raw.kwd file
        -experiment_name STR : the name of the experiment, ex : "A005_a17", 
            used to identify subsequent files, NOT to load raw files
        -pipeline_name STR : the name of the current pipeline
        -verbose BOOL : whether the pipeline gets the right to talk
    '''
    print('# Converting a kwd file to numpy #')
    # -------------------------------------------------------------------------
    if verbose : print('Loading raw.kwd file into a numpy array ...')
    
    dataset = kwk_load(kwik_path, 'all')
    
    data = dataset['data']['0']
    channels = dataset['channel_bit_volts']['0']
    timestamps = dataset['timestamps']['0']
    
    data2 = np.asarray(data)
    del data
    
    # -------------------------------------------------------------------------
    if verbose : print('Done ! Found %.3f seconds of recording'% (timestamps.max() -timestamps.min()))
    
    # -------------------------------------------------------------------------
    if verbose : print('Saving numpy array as a .npy file ...')
    
    np.save('./pipelines/%s/%s.npy' % (pipeline_name, experiment_name),
            data2)
    
    # -------------------------------------------------------------------------
    if verbose : print('Done ! Running sanity check for input and saved file identity ...')
    
    test = np.load('./pipelines/%s/%s.npy' % (pipeline_name, experiment_name))
    if np.array_equal(data2, test) : #no reshape needed, np save and load keep the structure
        del data2
        del test
        
        if verbose : print('Sanity check passed.')
        print('Conversion from raw.kwd to npy file successfully completed !\n')
        
        with open('./pipelines/%s/debugfile.txt' % pipeline_name, 'a') as file:
            file.write('| VAR_nbr_channels = %s | \n'%channels.shape[0])
            file.write('| VAR_timestamps_min = %s | \n' % timestamps.min())
            file.write('| VAR_timestamps_max = %s | \n' % timestamps.max())
        return 1
    else :
        print('Initial data shape and output shape are not matching. Unclog the pipeline in utils.py')
        return 0
 
