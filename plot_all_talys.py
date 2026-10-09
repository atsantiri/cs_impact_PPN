import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import math
from configs import config, helpers

# plot all talys outputs without calculating likelihood

# Inputs
talysDir = "all_talys"
# runs = 20
runs = len(next(os.walk(talysDir))[1])
print(f"Found {runs} talys runs")
fIn = {
    "102Pd-ga": {"talys": "aprod.tot", "cs": "Input/cs_102Pd_ga.dat"},
    "102Pd-gp": {"talys": "pprod.tot", "cs": "Input/cs_102Pd_gp.dat"},
}
model_data = {
    key: [
        np.loadtxt(f"{talysDir}/i_{i}/{data['talys']}", skiprows=5, usecols=[0, 1]).T
        for i in range(runs)
    ]
    for key, data in fIn.items()
}
cs_data = {key: helpers.read_cs(file["cs"]) for key, file in fIn.items()}

# Setup plots
n = len(cs_data)
ncols = min(n, 2)
nrows = math.ceil(n / ncols)
fig, axs = plt.subplots(nrows, ncols, figsize=(8 * ncols, 6 * nrows), squeeze=False)
axs = axs.flatten()

# get min and max talys
for d, (key, models) in enumerate(model_data.items()):
    energy = models[0][0]
    xs = np.array([model[1] for model in models])
    for cs in xs:
        axs[d].plot(energy, cs, "lightblue", zorder=1)
    min_xs = np.min(xs, axis=0)
    max_xs = np.max(xs, axis=0)
    axs[d].plot(
        energy,
        min_xs,
        "--",
        color="steelblue",
        label=f"Min/Max TALYS cross section",
        zorder=2,
    )
    axs[d].plot(energy, max_xs, "--", color="steelblue", zorder=2)

for d, (key, data) in enumerate(cs_data.items()):
    axs[d].errorbar(
        data["ene_median"],
        data["cs"],
        xerr=data["ene_median"] * 0.015,
        yerr=data["cs_err"],
        label="This work",
        fmt="o",
        color="black",
        capsize=2,
        zorder=3,
    )
    axs[d].set_xlabel("Energy (MeV)")
    axs[d].set_title(key)
    axs[d].set_xlim(min(data["ene_median"]) - 1, max(data["ene_median"]) + 1)
    axs[d].set_yscale("log")
    axs[d].set_ylim(min(data["cs"]) / 2, max(data["cs"]) * 2)
    axs[d].set_ylabel("Cross Section (mb)")
    axs[d].legend()

plt.show()
