
import numpy as np
import matplotlib.pyplot as plt
from configs import config


# helper functions
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
    return np.exp(likelihood_val/len(weights)/len(cs)) # note that here I normalize on number of bins per energy, as well as number of energies per dataset

def plot_sorted_data(data, index, param, axis):
    norm = plt.Normalize(min(param), max(param))
    for i in index:
        ene_i, cs_i = data[i]
        color = config.colormap(norm(param[i]))
        axis.plot(ene_i, cs_i, color=color)

def add_colorbar(fig, param, label, axis):
    norm = plt.Normalize(min(param), max(param))
    sm = plt.cm.ScalarMappable(cmap=config.colormap, norm=norm)
    fig.colorbar(sm, ax=axis, label=label)

def read_cs(file):
    ene_median, cs, cs_err = np.loadtxt(file, skiprows=1).T
#     return {
#         'file': file,
#         'ene_median': ene_median,
#         'cs': cs,
#         'cs_err': cs_err
#     }
    ene = np.round(
        ene_median[:, None] * np.linspace(0.985, 1.015, 11),
        3
    )
    return {
        'file': file,
        'ene_median': ene_median,
        'ene': ene,
        'cs': cs,
        'cs_err': cs_err
    }