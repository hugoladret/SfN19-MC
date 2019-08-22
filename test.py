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
    This is used to merge multiple kwd files into a single file for spike sorting
    
    The files are temporary loaded to get the shapes and the array is memmapped.
    The function then iterates over the channels and loads the corresponding channel in each memory mapped array
    
    Args :
        -arrays_paths LST : list of arrays paths to be loaded, ex ['A005_a17.npy', 'A007_a17.npy']
        -pipeline_name STR : name of the pipeline 
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
    print(merged_size)
    print(arrays_size)
    print(arrays_size-merged_size)

    

concatenate2D_from_disk(arrays_paths = ['A005_a17.npy', 'A005_a17bis.npy'],
                        pipeline_name = 'Autobahn', verbose = True)
#temp_arr_0 = np.load('./pipelines/Autobahn/A005_a17.npy')
#chan_length_0 = temp_arr_0.shape[0]
#del temp_arr_0
#
#temp_arr_1 = np.load('./pipelines/Autobahn/A005_a17bis.npy')
#chan_length_1 = temp_arr_1.shape[0]
#del temp_arr_1
#
#arr1 = np.memmap(filename = './pipelines/Autobahn/A005_a17.npy',
#                 dtype = 'int16',
#                 shape = (chan_length_0, 32),
#                 mode = 'r+')
#arr2 = np.memmap(filename = './pipelines/Autobahn/A005_a17bis.npy',
#                 dtype = 'int16',
#                 shape = (chan_length_1, 32),
#                 mode = 'r+')
#
#print(arr1.shape)
#print(arr2.shape)
#
#for chan in range(32):
#    concat = np.concatenate((arr1[:,chan], arr2[:, chan]))
#    print(arr1[:,chan].shape)
#    print(arr2[:,chan].shape)
#    print(concat.shape)
#    print('\n')
#    
#    #concat.astype('int16').tofile('./pipelines/concated.bin')
#    
#    with open('./pipelines/concat.bin', 'a+') as file :
#        concat.astype('int16').tofile(file)
#    
