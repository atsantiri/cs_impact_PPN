import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.stats import norm
import math
from configs import config, helpers

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


def main():

    # Read Inputs
    talysDir = "all_talys_102pd"
    runs = 100
    # runs = len(next(os.walk(talysDir))[1])
    print(f"Found {runs} talys runs")

    # Add reactions and pathfiles as needed
    fIn = {
        "102Pd-ga": {"reaction": "aprod", "cs": "Input/cs_102Pd_ga.dat"},
        "102Pd-gp": {"reaction": "pprod", "cs": "Input/cs_102Pd_gp.dat"},
    }
    model_data = {
        key: [
            np.loadtxt(f"{talysDir}/i_{i}/{data['reaction']}.tot", usecols=[0, 1]).T
            for i in range(runs)
        ]
        for key, data in fIn.items()
    }
    cs_data = {key: helpers.read_cs(file["cs"]) for key, file in fIn.items()}

    # Setup plots based on number of reactions
    fig, axs = setup_fig(cs_data)

    # Plot input data
    plot_cs(cs_data, fig, axs)

    # Plot the edges of the talys band
    plot_min_max_talys(fig, axs, model_data)

    # DO DA THANG
    
    # weighting function for the energy errors
    weights = norm.pdf(
        np.linspace(0.985, 1.015, 11), loc=1, scale=0.03 / (2 * np.sqrt(2 * np.log(2)))
    )
    #
    # loop over files:
    for d, key in enumerate(cs_data):
        data = cs_data[key]
        models = model_data[key]

        # init likelihood array
        w_m = np.zeros(runs)

        args = (data["cs"], data["cs_err"], data["ene"], weights)

        for i, model in enumerate(models):
            w_m[i] = helpers.likelihood(model, args)
            # print(f"{i} {w_m[i]:.4e}")

        data["w_m"] = w_m

    for d, (key, data) in enumerate(cs_data.items()):
        idx_sorted_w = np.argsort(data["w_m"])
        helpers.plot_sorted_data(model_data[key], idx_sorted_w, data["w_m"], axs[d])
        helpers.add_colorbar(fig, data["w_m"], "exp(logP/Nbins*Ndata)", axs[d])

    plt.tight_layout()
    plt.show()

    return True


if __name__ == "__main__":
    main()
