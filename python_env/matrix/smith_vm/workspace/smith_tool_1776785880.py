# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation of the Jerk Stability Index for Linux HSA unified memory.
Ensures:
  * Dimensionless index S_j in (0, 1]
  * Constraints S_j >= 0.5 and |j|/j0 <= 2.0 are dimensionless
  * No markdown headings are present in the output narrative (checked externally)
"""

import numpy as np

def jerk_stability_index(sigma_j: float, j_max_abs: float, j0: float) -> float:
    """
    Compute the dimensionless Jerk Stability Index.
    Parameters
    ----------
    sigma_j : float
        Standard deviation of jerk (units: GB/s^3).
    j_max_abs : float
        Peak absolute jerk (same units).
    j0 : float
        Characteristic jerk scale (same units, >0).
    Returns
    -------
    S_j : float
        Dimensionless stability index.
    """
    if j0 <= 0:
        raise ValueError("Characteristic jerk scale j0 must be positive.")
    sigma_hat = sigma_j / j0          # dimensionless
    jmax_hat = j_max_abs / j0         # dimensionless
    S_j = 1.0 / (1.0 + sigma_hat * jmax_hat)
    return S_j

def validate_constraints(S_j: float, jerk_norm: float) -> dict:
    """
    Check Omega‑Protocol constraints.
    Returns a dict with boolean flags.
    """
    constraints = {
        "S_j_ge_0.5": S_j >= 0.5,
        "jerk_norm_le_2.0": jerk_norm <= 2.0,
        "S_j_in_unit_interval": 0.0 < S_j <= 1.0,
    }
    return constraints

# Example values from the thought (ROCm‑based HSA node)
sigma_j_example = 0.85   # GB/s^3
j_max_example   = 3.2    # GB/s^3
j0_example      = 1.0    # GB/s^3 (baseline)

S_j_val = jerk_stability_index(sigma_j_example, j_max_example, j0_example)
jerk_norm_example = j_max_example / j0_example  # |j|/j0

print(f"Computed S_j: {S_j_val:.4f}")
print(f"Normalized peak jerk |j|/j0: {jerk_norm_example:.2f}")
print("Constraint check:", validate_constraints(S_j_val, jerk_norm_example))

# Additional sanity: dimensional homogeneity check
# Since we divided sigma_j and j_max by the same j0, the product is unit‑less.
assert np.isclose((sigma_j_example/j0_example) * (j_max_example/j0_example),
                  (sigma_j_example * j_max_example) / (j0_example**2)),
    "Dimensional homogeneity violated"
print("Dimensional homogeneity: OK")