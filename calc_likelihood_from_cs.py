import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.stats import norm
from configs import config

#before x uncertainty
# def likelihood(model, args):
#     cs, cs_err, ene, weights = args
#     ene_i, cs_i = model 
#     likelihood_val = 0
#     f_mi_lookup = {ene: val for ene, val in zip(ene_i, cs_i)}

#     for i, e in enumerate(ene):
#         # f_mi = cs_i[e_eff[i] == ene_i]
#         f_mi = f_mi_lookup.get(e, None)
#         if f_mi is None:
#             print(f'something is off here {f_mi}')
#             break
#         p_ymi = - 1/2*((cs[i]-f_mi)/cs_err[i])**2 
#         likelihood_val += weights[i] * p_ymi
    # return np.exp(likelihood_val)

# after x uncertainty embedded in weights
def likelihood(model, args):
    cs, cs_err, ene, weights = args
    ene_i, cs_i = model 
    likelihood_val = 0
    
    # f_mi_lookup = {ene: val for ene, val in zip(ene_i, cs_i)}
    f_mi_lookup = {e: val for e, val in zip(ene_i, cs_i)}
    for i in range(len(cs)):
        for j in range(len(ene[i])):
            # f_mi = cs_i[e_eff[i] == ene_i]
            f_mi = f_mi_lookup.get(ene[i,j], None)
            if f_mi is None:
                print(f'something is off here {f_mi} for ene {ene[j,i]}')
                break
            p_ymi = - 1/2*((cs[i]-f_mi)/cs_err[i])**2 
            likelihood_val += (weights[j] * p_ymi)
    return np.exp(likelihood_val/len(weights)) # note that here I normalize on number of bins per energy

# If I plot each talys line on top of each other I can't see the scores. 
# This ensures that the lines are plotted in order of score, so the ones with highest score are top and visible.
def plot_sorted_data(index, param, axis):
    norm = plt.Normalize(min(param), max(param))
    for i in index:
        ene_i, cs_i = model_data[i]
        color = config.colormap(norm(param[i]))
        axis.plot(ene_i, cs_i, color=color)

def add_colorbar(param, label, axis):
    norm = plt.Normalize(min(param), max(param))
    sm = plt.cm.ScalarMappable(cmap=config.colormap, norm=norm)
    fig.colorbar(sm, ax=axis, label=label)


# Talys inputs
talysDir = 'all_talys'
runs = len(next(os.walk(talysDir))[1])
print(f'Found {runs} talys runs')
talysFile = 'pprod.tot'
model_data = [
    np.loadtxt(f'{talysDir}/i_{i}/{talysFile}', skiprows=5, usecols=[0, 1]).T
    for i in range(runs)
]

# Cross section Data 
csDataFile = 'Input/cs_102Pd_gp.dat'
ene_median, cs, cs_err = np.loadtxt(csDataFile,skiprows=1).T
## For now all data points are equal. This will change when we adopt x errors
# weights = np.ones(len(cs))

# Adopting gaussian x errors: 
# "The horizontal error bars represent the 3% FWHM energy spread of the gamma beam, as determined in previous experiments..."
ene = np.round(ene_median[:, None] * np.linspace(0.985, 1.015, 11),3)
# print(ene)
weights = norm.pdf(np.linspace(0.985, 1.015, 11), loc=1, scale=0.03 / (2 * np.sqrt(2 * np.log(2))))
weights /= weights.max()
# print(weights)

# init likelihood array
w_m = np.zeros(runs)

fig, axs = plt.subplots()

for i in range(runs):
    ene_i, cs_i = model_data[i]
    model = ene_i, cs_i
    args = cs, cs_err, ene, weights 
    w_m[i] = likelihood(model, args)
    print(f'{i} {w_m[i]:.3e}')
    # plt.plot(ene_i,cs_i, color=config.colormap(w_m[i]), zorder=1)

idx_sorted_w = np.argsort(w_m)
plot_sorted_data(idx_sorted_w, w_m, axs)
add_colorbar(w_m, 'exp(logP/Nbins)', axs)

plt.errorbar(ene_median, cs, xerr = ene_median*0.015, yerr = cs_err, fmt='o', color='black',capsize=2, zorder=10)
plt.xlabel('Energy (MeV)')
plt.xlim(7,25)
plt.yscale('log')
plt.ylim(1e-2,20)
plt.ylabel('Cross Section (mb)')

plt.tight_layout()
plt.show()

