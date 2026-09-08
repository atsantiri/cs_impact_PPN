import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from configs import config

def likelihood(model, args):
    cs, cs_err, ene, weights = args
    ene_i, cs_i = model 
    likelihood_val = 0
    f_mi_lookup = {ene: val for ene, val in zip(ene_i, cs_i)}

    for i, e in enumerate(ene):
        # f_mi = cs_i[e_eff[i] == ene_i]
        f_mi = f_mi_lookup.get(e, None)
        if f_mi is None:
            print(f'something is off here {f_mi}')
            break
        p_ymi = - 1/2*((cs[i]-f_mi)/cs_err[i])**2
        likelihood_val += weights[i] * p_ymi
    return np.exp(likelihood_val)


# Talys inputs
talysDir = 'all_talys'
runs = len(next(os.walk(talysDir))[1])
print(f'Found {runs} talys runs')
talysFile = 'rp046102.tot'

# Cross section Data 
csDataFile = 'Input/cs.dat'
ene, cs, cs_err = np.loadtxt(csDataFile,skiprows=1).T
# For now all data points are equal. This will change when we adopt x errors
weights = np.ones(len(cs))

# init likelihood array
w_m = np.zeros(runs)

for i in range(runs):
    ene_i, cs_i = np.loadtxt(f'{talysDir}/i_{i}/{talysFile}',skiprows=5,usecols=[0,1]).T
    model = ene_i, cs_i
    args = cs, cs_err, ene, weights
    w_m[i] = likelihood(model, args)
    print(f'{i} {w_m[i]:.3e}')
    plt.plot(ene_i,cs_i, color=config.colormap(w_m[i]), zorder=1)


# norm = colors.LogNorm(min(w_m),max(w_m))
norm = plt.Normalize(min(w_m),max(w_m))
sm = plt.cm.ScalarMappable(cmap=config.colormap, norm=norm)
plt.colorbar(sm,label = r'P($\sigma_{exp}$|m)')

plt.errorbar(ene, cs,  yerr = cs_err, fmt='o', color='black',capsize=2, zorder=10)
plt.xlabel('Energy (MeV)')
plt.xlim(2.5,4.)
plt.yscale('log')
plt.ylim(1e-2,0.5)
plt.ylabel('Cross Section (b)')
# plt.legend() 

plt.tight_layout()
plt.show()

