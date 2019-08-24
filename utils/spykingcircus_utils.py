#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:44:11 2019

@author: hugo
"""

import shutil
import subprocess


def copy_file(template_path, pipeline_name, output_name,) :
    '''
    Copies a template .prm file or template .prb file in the local pipeline folder,
    using the same name as the data (usually mydata_0.bin)
    '''
    print('# Copying %s #'%template_path)
    shutil.copyfile('./params/'+template_path, './pipelines/'+pipeline_name+'/'+output_name)
    
# --------------------------------------------------------------
#
# --------------------------------------------------------------
    
def call_circus(filename, n_cpu, hostfile,
                preview, result, pipeline_name) :
    '''
    Calls Spyking-Circus, with parameters described here 
    https://spyking-circus.readthedocs.io/en/latest/code/parameters.html
    
    Args :
        -filename STR = usually 'mydata_0.bin'
        -n_cpu INT = -c argument
        -hostfile STR = MPI configuration host list, skipped if left to None
        -preview BOOL = -p argument, skipped if left to False
        -results BOOL = -r argument, skipped if left to False
    '''
    if preview :
        print('\n# Previewing channel-map # \n')
        subprocess.call(['spyking-circus', filename, '-p'], cwd = './pipelines/%s/' % pipeline_name)
    
    call_string = ['spyking-circus', filename]
    call_string.append('-c %d' % n_cpu)
    
    if hostfile != None:
        call_string.append('-H %s' % hostfile)

    
    print('\n# Calling Spyking-Circus with arguments : # \n%s'%call_string)   

    subprocess.call(call_string,
                     cwd = './pipelines/%s/' % pipeline_name)
    
    subprocess.call(['spyking-circus', filename,'-m', 'converting', '-e','merged'],
                     cwd = './pipelines/%s/' % pipeline_name)
    
    if result :
        print('\n# Showing results # \n')
        subprocess.call(['spyking-circus', filename, '-r'], cwd = './pipelines/%s/' % pipeline_name)
    
        