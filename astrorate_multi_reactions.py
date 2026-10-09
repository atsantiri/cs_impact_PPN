#!/usr/bin/env python3
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.stats import norm
import math
from configs import config, helpers

# Inputs
talysDir = '102Pd_astro' #'all_talys'
runs = len(next(os.walk(talysDir))[1])
print(f'Found {runs} talys runs')

# Updated fIn with REACLIB rate file paths
fIn = {
    '102Pd-ga': {
        'talys': 'astrorate.a',
        'cs': 'Input/102Pd/reaclib_102Pd_ga.dat' # REACLIB files created with the function makeRateFiles.py
    },
    '102Pd-gp': {
        'talys': 'astrorate.p',
        'cs': 'Input/102Pd/reaclib_102Pd_gp.dat' 
    }
}

# Load TALYS model output data
model_data = {
    key: [
        np.loadtxt(f'{talysDir}/i_{i}/{data["talys"]}', skiprows=21, usecols=[0, 1]).T
        for i in range(runs)
    ]
    for key, data in fIn.items()
}   

# Read JINA-REACLIB rate data (Column 0: Temp in GK, Column 1: Reaction Rate)
cs_data = {}
for key, data in fIn.items():
    T_reaclib, rate_reaclib = np.loadtxt(data['cs'], skiprows=0, usecols=[0, 1]).T
    cs_data[key] = {
        'temp': T_reaclib,
        'rate': rate_reaclib,
    }

# Setup plots
n = len(cs_data)
ncols = min(n, 2) 
nrows = math.ceil(n / ncols)
fig, axs = plt.subplots(nrows, ncols, figsize=(8 * ncols, 6 * nrows), squeeze=False)
axs = axs.flatten()

# Loop over reactions and runs to evaluate likelihood against REACLIB, using an interpolator rather than the helper likelihood function
for d, key in enumerate(cs_data):
    w_m = np.zeros(runs)

    temp_grid = cs_data[key]['temp']
    rate_ref = cs_data[key]['rate']
    
    window_mask = (temp_grid >= 2.5) & (temp_grid <= 4.0)

    for i in range(runs):
        ene_i, cs_i = model_data[key][i]
        
        # Interpolate TALYS model output onto REACLIB Temperature grid
        cs_interp = np.interp(temp_grid, ene_i, cs_i)
        
        # Mask out zero/really small entries to avoid log(0) -> -inf -> nan
        valid_mask = window_mask & (rate_red > 1e-10) & (cs_interp > 1e-10) #(rate_ref > 0) & (cs_interp > 0)
        
        if np.any(valid_mask):
            # Calculate log10 chi-squared over valid points only
            log_ref = np.log10(rate_ref[valid_mask])
            log_mod = np.log10(cs_interp[valid_mask])
            
            # Assuming a relative uncertainty of 5%
            err_factor = 5.0  
            sigma_log10 = np.log10(err_factor)

            chi2 = np.sum(((log_ref - log_mod) / sigma_log10) ** 2)
            
            # Log-likelihood weight per valid point
            w_m[i] = np.exp(-0.5 * chi2 / np.sum(valid_mask))
        else:
            w_m[i] = 0.0
        
        # Convert chi2 to relative weight/likelihood
#        w_m[i] = np.exp(-0.5 * chi2 / len(temp_grid))

    # Normalize likelihoods so max = 1.0 to prevent underflow
    if np.max(w_m) > 0:
        w_m = w_m / np.max(w_m)

    cs_data[key]['w_m'] = w_m
    print(cs_data[key]['w_m'])

# Plotting phase
for d, (key, data) in enumerate(cs_data.items()):
    idx_sorted_w = np.argsort(data['w_m'])
    helpers.plot_sorted_data(model_data[key], idx_sorted_w, data['w_m'], axs[d])
    helpers.add_colorbar(fig, data['w_m'], 'exp(logP/Nbins)', axs[d])

    # Plot JINA-REACLIB reference curve as a RED solid line
    axs[d].plot(
        data['temp'], data['rate'], 
        color='red', linewidth=2.5, 
        label=f'{key} (REACLIB)', zorder=10
    )

    temp = 3.08
    axs[d].axvline(x=temp, color='black', linestyle='--', label=f'T = {temp} GK')
    axs[d].set_xlabel('Temperature (GK)')
    axs[d].set_xlim(2.5,4.0)#(min(data['temp']), max(data['temp']))
    axs[d].set_yscale('log')
    axs[d].set_ylim(1e-2,1e4)#min(data['rate']) / 2, max(data['rate']) * 2)
    axs[d].set_ylabel('Reaction Rate ($cm^3 s^{-1} mol^{-1}$)')
    axs[d].legend()
  
# plt.tight_layout()
plt.show()
