# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Validation script for the Engine's repaired solution on Linux HSA node data.
Checks:
1. Jerk (third derivative of memory bandwidth) is computed correctly.
2. The Jerk Stability Index S_j' is dimensionless.
3. MPC‑Ω constraints S_j' >= 0.5 and |j|/j_0 <= 2.0 are satisfied for a stable baseline.
4. No structural markup (headings, bold, lists) is present in the narrative (assumed satisfied by output format).

The script uses synthetic bandwidth data to demonstrate the math; replace the data
section with real measurements from `rocm-smi`/`rocprof` for production validation.
"""

import numpy as np
from scipy.signal import savgol_filter

def validate_jerk_stability(bandwidth, dt, window_length=11, polyorder=3,
                            baseline_frac=0.2):
    """
    Parameters
    ----------
    bandwidth : np.ndarray
        Memory bandwidth time series (GB/s).
    dt : float
        Sampling interval (s).
    window_length, polyorder : int
        Parameters for Savitzky–Golay filter (must be odd window_length > polyorder).
    baseline_frac : float
        Fraction of the start of the signal used to compute the characteristic jerk j0.

    Returns
    -------
    dict
        Contains computed quantities and a boolean indicating compliance.
    """
    # 1. Compute jerk = d^3B/dt^3 using Savitzky–Golay (returns derivatives in original units per dt^order)
    # The filter returns the derivative scaled by 1/dt^order, so we multiply by dt^-3.
    jerk = savgol_filter(bandwidth, window_length, polyorder, deriv=3, delta=dt)
    # jerk now has units GB/s^3

    # 2. Statistics of jerk
    sigma_j = np.std(jerk)                     # GB/s^3
    j_abs = np.abs(jerk)
    j_max = np.max(j_abs)                      # GB/s^3
    # Characteristic jerk scale from baseline period
    n_baseline = int(len(jerk) * baseline_frac)
    j0 = np.mean(j_abs[:n_baseline]) if n_baseline > 0 else np.mean(j_abs)  # GB/s^3

    # 3. Dimensionless stability index
    # Ensure we avoid division by zero
    if j0 == 0:
        raise ValueError("Characteristic jerk j0 is zero; check data.")
    S_j_prime = 1.0 / (1.0 + (sigma_j / j0) * (j_max / j0))

    # 4. MPC‑Ω constraints (dimensionless)
    constraint_S = S_j_prime >= 0.5
    constraint_J = (j_max / j0) <= 2.0

    compliant = constraint_S and constraint_J

    result = {
        "jerk_mean": np.mean(jerk),
        "jerk_std": sigma_j,
        "jerk_max_abs": j_max,
        "j0": j0,
        "S_j_prime": S_j_prime,
        "sigma_j_over_j0": sigma_j / j0,
        "j_max_over_j0": j_max / j0,
        "constraint_S_j_ge_0_5": constraint_S,
        "constraint_j_max_le_2": constraint_J,
        "overall_compliant": compliant,
    }
    return result

if __name__ == "__main__":
    # --- Synthetic data generation for demonstration ---
    np.random.seed(42)
    t = np.linspace(0, 10, 1000)          # 10 seconds, 100 Hz sampling
    dt = t[1] - t[0]
    # Baseline bandwidth ~ 10 GB/s with small fluctuations
    B_base = 10.0 + 0.5 * np.sin(2 * np.pi * 0.5 * t)  # slow oscillation
    # Add occasional bandwidth spikes to mimic page‑migration thrashing
    spikes = np.zeros_like(t)
    spike_times = [2.0, 5.5, 8.0]
    for st in spike_times:
        idx = np.argmin(np.abs(t - st))
        spikes[idx:idx+20] += 3.0 * np.exp(-np.arange(20)/5.0)  # decaying spike
    bandwidth = B_base + spikes + 0.2 * np.random.randn(len(t))  # measurement noise

    # --- Run validation ---
    try:
        out = validate_jerk_stability(bandwidth, dt,
                                      window_length=15, polyorder=4,
                                      baseline_frac=0.15)
        print("Validation Results:")
        for k, v in out.items():
            if isinstance(v, float):
                print(f"{k:>25}: {v:.6f}")
            else:
                print(f"{k:>25}: {v}")
    except Exception as e:
        print(f"Validation failed: {e}")