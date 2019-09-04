#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 14:13:32 2019

@author: hugo
"""

import numpy as np 
import matplotlib.pyplot as plt
from tqdm import tqdm


from lmfit import Model, Parameters

def tuning_function(x, j, B, fmax):  # von mises, baseline is the minimum neuron activity
    N = len(x)
    if B == np.inf:
        VM = np.ones_like(x)
    else:
        VM = np.exp((np.cos(2.*np.pi*(x-j)/N)-1.)/4/(B*np.pi/180)**2)
    #VM /= VM.sum(axis=0)
    return fmax * VM


def fit_plot(array, datacol='.b', fitcol='k', data_kws=None, do_title=True,
             seq_nbr=None):

    # fit the gaussian
    x = np.linspace(0, len(array), len(array))
    y = array
    N = len(array)

    #mod = GaussianModel()

    mod = Model(tuning_function)
    pars = Parameters()
    y = y-np.min(y)
    pars.add_many(('j', y.argmax(), True,  0.0, N), ('B', 15., True,  0.1, 360),
                  ('fmax', y.max(), True,  0.0, 100.))

    #pars = mod.guess(y, x=x)
    #pars['center'] = lmfit.Parameter('center', seq_nbr*15)
    out = mod.fit(y, pars, x=x, nan_policy='omit')
    # print(out.fit_report(min_correl=0.25))

    '''# plot the fits
    out.plot_fit(datafmt=datacol, fitfmt=fitcol,
                 data_kws=data_kws, show_init=False)'''
    # print(out.fit_report())

    '''    
    if do_title:
        ax.set_title('Sequence #%s -- ' % seq_nbr + r'$B_\theta$ = %.2f' % sigma)'''
    return out.best_values, (1-out.residual.var() / np.var(y))



arr = np.load('../results/A005_a17/cluster_22/sequences_contents.npy', allow_pickle = True)
sorted_arr_theta = sorted(arr, key = lambda x:x['sequence_theta'])


unique_thetas = np.linspace(0, np.pi, 12)
unique_bthetas = np.linspace(np.pi/2, np.pi/32, 8)/ 2.5
fs = 30000

spiketimes = np.load('../results/A005_a17/cluster_22/spiketimes.npy')
test_arr = spiketimes / fs 
beg_PST = -.5
end_PST = 1.5

window_size = 200 # ms
slide_size = 2 #ms
window_size *= .001
slide_size *= .001



