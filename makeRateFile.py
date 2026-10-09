#!/usr/bin/env python3
import numpy as np

# REACLIB 7-parameter evaluation
def reaclib_rate(T9, a):
    log_rate = (
        a[0]
        + a[1] / T9
        + a[2] / (T9 ** (1/3))
        + a[3] * (T9 ** (1/3))
        + a[4] * T9
        + a[5] * (T9 ** (5/3))
        + a[6] * np.log(T9)
    )
    return np.exp(log_rate)

# Standard astrophysical temperature grid (0.1 to 10.0 GK)
T9_grid = np.linspace(0.1, 10.0, 100)

# Example REACLIB parameters [a1, a2, a3, a4, a5, a6, a7]
# Replace these array values with the exact fit parameters from JINA REACLIB:
params_gp = np.array([67.505,-90.589,-53.7127,0.464325,-1.02956,0.0210821,0.833333]) # pd102(g,p)
params_ga = np.array([103.172,-24.6656,-131.689,1.94196,-1.88896,0.000853814,0.833333]) # pd102(g,a)

# Save to .dat files matching your script's input path
np.savetxt('Input/102Pd/reaclib_102Pd_gp.dat', np.column_stack([T9_grid, reaclib_rate(T9_grid, params_gp)]))
np.savetxt('Input/102Pd/reaclib_102Pd_ga.dat', np.column_stack([T9_grid, reaclib_rate(T9_grid, params_ga)]))
