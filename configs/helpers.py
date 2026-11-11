import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.stats import norm
from scipy.special import logsumexp
from configs import config

# helper functions


# likelihood adapted from Practical Bayes example of 2023 FRIB TA Summer school,
# https://github.com/ascsn/2023-FRIB-TA-Summer-School/blob/main/practical-bayes/Practical%20example.ipynb
# for data with uncertainty on the x axis
def likelihood(model, args):
    cs, cs_err, ene, weights = args
    ene_i, cs_i = model
    likelihood_log_val = 0

    f_mi_lookup = {e: val for e, val in zip(ene_i, cs_i)}  # parse the model data
    for i in range(len(cs)):
        log_terms = [] 
        for j in range(len(ene[i])):
            # find the talys cs for specific energy
            f_mi = f_mi_lookup.get(ene[i, j], None)
            # if energy doesn't exist in talys, interpolate
            if f_mi is None:
                f_mi = interp_cs(ene[i, j], ene_i, cs_i)
                # print(f"something is off here {f_mi} for ene {ene[j,i]}")
                # break

            # Calculate P(y_mi)
            p_ymi = -1 / 2 * ((cs[i] - f_mi) / cs_err[i]) ** 2
            likelihood_log_val += weights[j] * p_ymi    

    # return likelihood_log_val
    return np.exp(likelihood_log_val)


# instead of the likelihood function to throw an error if the energy of the cs data doesn't exist in the energies that talys was run, it'll interpolate the talys cs. Now it will throw error when it can't interpolate (I'm not adding extrapolations).
def interp_cs(e, ene_i, cs_i):
    if e < ene_i[0] or e > ene_i[-1]:
        raise ValueError(
            f"Energy {e} is outside the model range [{ene_i[0]}, {ene_i[-1]}]"
        )
    k = np.searchsorted(ene_i, e)  # ene_i[k-1] < e <= ene_i[k]
    k = np.clip(k, 1, len(ene_i) - 1)
    e0, e1 = ene_i[k - 1], ene_i[k]
    c0, c1 = cs_i[k - 1], cs_i[k]
    return c0 + (c1 - c0) * (e - e0) / (e1 - e0)


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
    ene = np.round(ene_median[:, None] * np.linspace(0.985, 1.015, 11), 3)
    return {
        "file": file,
        "ene_median": ene_median,
        "ene": ene,
        "cs": cs,
        "cs_err": cs_err,
    }


def setup_fig(cs_data):
    # Setup plots
    n = len(cs_data)
    ncols = min(n, 2)
    nrows = math.ceil(n / ncols)
    fig, axs = plt.subplots(nrows, ncols, figsize=(8 * ncols, 6 * nrows), squeeze=False)
    axs = axs.flatten()

    return fig, axs


def plot_cs(cs_data, fig, axs):
    for d, (key, data) in enumerate(cs_data.items()):
        axs[d].errorbar(
            data["ene_median"],
            data["cs"],
            xerr=data["ene_median"] * 0.015,
            yerr=data["cs_err"],
            label=key,
            fmt="o",
            color="black",
            capsize=2,
            zorder=10,
        )
        axs[d].set_xlabel("Energy (MeV)")
        axs[d].set_xlim(min(data["ene_median"]) - 1, max(data["ene_median"]) + 1)
        axs[d].set_yscale("log")
        axs[d].set_ylim(min(data["cs"]) / 2, max(data["cs"]) * 2)
        axs[d].set_ylabel("Cross Section (mb)")
        axs[d].legend(loc="lower right")


def plot_min_max_talys(fig, axs, model_data):
    for ax, models in zip(axs, model_data.values()):
        energy = models[0][0]
        xs = np.array([model[1] for model in models])
        min_xs = xs.min(axis=0)
        max_xs = xs.max(axis=0)
        ax.plot(
            energy, min_xs, "--", color="steelblue", label="Min/Max TALYS", zorder=10
        )
        ax.plot(energy, max_xs, "--", color="steelblue", zorder=10)


def make_weights_for_energy_errors(n=11, half_width=0.015, fwhm=0.03):
    sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
    w = norm.pdf(np.linspace(1 - half_width, 1 + half_width, n), loc=1, scale=sigma)
    return w / w.sum()


def calc_likelihoods(cs_data, model_data, weights=None):

    if weights is None:
        weights = make_weights_for_energy_errors()

    likelihoods = {}
    for key, data in cs_data.items():
        args = (data["cs"], data["cs_err"], data["ene"], weights)
        likelihoods[key] = np.array(
            [likelihood(model, args) for model in model_data[key]]
        )
    return likelihoods
