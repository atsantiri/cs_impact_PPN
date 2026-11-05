import numpy as np
import os
import matplotlib.pyplot as plt
from configs import config, helpers

def main():

    # Read Inputs
    talysDir = "all_talys_102pd"
    # runs = 100
    runs = len(next(os.walk(talysDir))[1])
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
    fig, axs = helpers.setup_fig(cs_data)

    # Plot input data
    helpers.plot_cs(cs_data, fig, axs)

    # Plot the edges of the talys band
    helpers.plot_min_max_talys(fig, axs, model_data)

    # DO DA THANG
    w_m = helpers.calc_likelihoods(cs_data, model_data)

    for d, key in enumerate(cs_data):
            idx_sorted_w = np.argsort(w_m[key])
            helpers.plot_sorted_data(model_data[key], idx_sorted_w, w_m[key], axs[d])
            helpers.add_colorbar(fig, w_m[key], "exp(logP/Nbins*Ndata)", axs[d])

    plt.tight_layout()
    plt.show()

    return True


if __name__ == "__main__":
    main()
