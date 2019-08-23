#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 14:13:32 2019

@author: hugo
"""

import numpy as np
import os

def concatenate2D_from_disk(arrays_paths, pipeline_name,
                            verbose = True):
    '''
    Loads a list of 2D int16 numpy array from disk and concatenate them row by row into a bin file
    This is used to merge multiple kwd files into a single file for spike sorting.
    Concatenation is done in the order in which the file are specified in arrays_paths
    
    The files are temporary loaded to get the shapes and the array is memmapped.
    The function then iterates over the channels and loads the corresponding channel in each memory mapped array
    
    Args :
        -arrays_paths LST : list of arrays paths to be loaded, ex ['A005_a17.npy', 'A007_a17.npy']
        -pipeline_name STR : name of the pipeline 
        -verbose BOOL : verbosity of the function
    '''
    
    channel_length_list = []
    memmap_list = []
    for array_path in arrays_paths :
        temp_arr = np.load('./pipelines/%s/%s' % (pipeline_name, array_path))
        chan_length = temp_arr.shape[0]
        chan_nbr = temp_arr.shape[1]
        channel_length_list.append(chan_length)
        del temp_arr
        
        memmap_arr = np.memmap(filename = './pipelines/%s/%s' % (pipeline_name, array_path),
                               dtype = 'int16',
                               shape = (chan_length, chan_nbr),
                               mode = 'r+')
        memmap_list.append(memmap_arr)
        
        if verbose : print('Memory mapped file : %s of shape %s' % (array_path, (chan_length, chan_nbr)))
        
    if verbose : print('Concatenating arrays row by row ...')    
    for chan in range(chan_nbr):
        
        concat_list = []
        for memmap in memmap_list:
            concat_list.append(memmap[:,chan])
            
        concat = np.concatenate((concat_list))
        with open('./pipelines/%s/merged.bin' % pipeline_name, 'a+') as file :
            concat.astype('int16').tofile(file)
            
    if verbose : print('Done ! Running sanity check ...') #due to file size we can't match shape directly
    merged_size = os.path.getsize('./pipelines/%s/merged.bin' % pipeline_name)
    arrays_size = np.sum([os.path.getsize('./pipelines/%s/%s' % (pipeline_name,x)) for x in arrays_paths])
    
    if arrays_size-merged_size < 300 : #the size of the header is 256 bits
        if verbose : print('Sanity check passed.')
        print('Concatenation of 1D arrays completed !\n')

# --------------------------------------------------------------
#
# --------------------------------------------------------------
    
def concatenate1D_from_disk(arrays_paths, pipeline_name,
                            output_name,
                            verbose = True):
    '''
    Loads a list of 1D numpy array from disk and concatenate them 
    This is used to merge timestamps (float64) or photodiodechannel(int16)
    Concatenation is done in the order in which the file are specified in arrays_paths
    
    The files aren't memory mapped
    
    Args :
        -arrays_paths LST : list of arrays paths to be loaded, ex ['A005_a17.npy', 'A007_a17.npy']
        -pipeline_name STR : name of the pipeline 
        -output_name STR : name of the concatenated output, whether 'phtdiode' or 'timestamps'
        -verbose BOOL : verbosity of the function
    '''
    
    array_list = []
    for array_path in arrays_paths :
        arr = np.load('./pipelines/%s/%s' % (pipeline_name, array_path))
        array_list.append(arr)
        if verbose : print('Loaded file : %s of shape %s' % (array_path, arr.shape[0]))
        
    if verbose : print('Concatenating arrays ...')                
    concat = np.concatenate((array_list))
    
    with open('./pipelines/%s/%s.bin' % (pipeline_name, output_name), 'a+') as file :
        concat.tofile(file)
            
    if verbose : print('Done ! Running sanity check ...')
    test = np.fromfile('./pipelines/%s/%s.bin' % (pipeline_name, output_name), dtype = type(concat[0]))
    print(concat.shape, test.shape)
    if np.array_equal(concat, test) :
        if verbose : print('Sanity check passed.')
        print('Concatenation of 1D arrays completed !\n')

    
concatenate1D_from_disk(arrays_paths = ['A005_a17_timestamps.npy','A005_a17bis_timestamps.npy'],
                        output_name = 'timestamps',
                        pipeline_name = 'Autobahn', verbose = True)

