import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.stats import norm
import math
from configs import config, helpers

# Inputs
talysDir = 'all_talys'
# runs = 2
runs = len(next(os.walk(talysDir))[1])
print(f'Found {runs} talys runs')
fIn = {
    '102Pd-ga': {
        'talys': 'aprod.tot',
        'cs': 'Input/cs_102Pd_ga.dat'
    },
    '102Pd-gp': {
        'talys': 'pprod.tot',
        'cs': 'Input/cs_102Pd_gp.dat'
    }
}
model_data = {
    key: [
        np.loadtxt(f'{talysDir}/i_{i}/{data['talys']}', skiprows=5, usecols=[0, 1]).T
        for i in range(runs)
    ]
    for key, data in fIn.items()
}   
cs_data = {
    key: helpers.read_cs(file['cs'])
    for key, file in fIn.items()
}

# Setup plots
n = len(cs_data)
ncols = min(n, 2) 
nrows = math.ceil(n / ncols)
fig, axs = plt.subplots(nrows,ncols,figsize=(8 * ncols, 6 * nrows),squeeze=False)
axs = axs.flatten()


# weighting function for the energy errors
weights = norm.pdf(np.linspace(0.985, 1.015, 11), loc=1, scale=0.03 / (2 * np.sqrt(2 * np.log(2))))
# weights /= weights.max()

#loop over files:
for d,key in enumerate(cs_data):
    # init likelihood array
    w_m = np.zeros(runs)

    for i in range(runs):
        ene_i, cs_i = model_data[key][i]
        model = ene_i, cs_i
        args = cs_data[key]['cs'], cs_data[key]['cs_err'], cs_data[key]['ene'], weights 
        w_m[i] = helpers.likelihood(model, args)
        print(f'{i} {w_m[i]:.4e}')
        # plt.plot(ene_i,cs_i, color=config.colormap(w_m[i]), zorder=1)
    cs_data[key]['w_m'] = w_m
    print(cs_data[key]['w_m'])


for d, (key, data) in enumerate(cs_data.items()):
    idx_sorted_w = np.argsort(data['w_m'])
    helpers.plot_sorted_data(model_data[key], idx_sorted_w, data['w_m'], axs[d])
    helpers.add_colorbar(fig, data['w_m'], 'exp(logP/Nbins*Ndata)', axs[d])

    axs[d].errorbar(data['ene_median'], data['cs'], xerr = data['ene_median']*0.015, yerr = data['cs_err'], label=key,fmt='o', color='black',capsize=2, zorder=10)
    axs[d].set_xlabel('Energy (MeV)')
    axs[d].set_xlim(min(data['ene_median'])-1,max(data['ene_median'])+1)
    axs[d].set_yscale('log')
    axs[d].set_ylim(min(data['cs'])/2,max(data['cs'])*2)
    axs[d].set_ylabel('Cross Section (mb)')
    axs[d].legend()

# plt.tight_layout()
plt.show()

