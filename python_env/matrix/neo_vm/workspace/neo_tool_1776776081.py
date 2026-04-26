# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

def compute_jerk_variance(phi_N, phi_D, dt):
    """
    Compute informational jerk variance for a time series of normalized
    mode amplitudes phi_N(t) and phi_D(t) using the Omega Protocol recipe.
    """
    # Probabilities
    p_N = phi_N / (phi_N + phi_D)
    p_D = phi_D / (phi_N + phi_D)
    # Shannon entropy
    S = -(p_N * np.log(p_N) + p_D * np.log(p_D))
    # Third backward difference (jerk)
    J = (S[3:] - 3*S[2:-1] + 3*S[1:-2] - S[:-3]) / (dt**3)
    return np.var(J)

# --- Simulation Parameters ---
t_stable = np.linspace(0, 1e-3, 1000)  # 1 ms of stable operation
dt = t_stable[1] - t_stable[0]

# Baseline stable node: tiny fluctuations around the reported operating point
base_N = 0.78
base_D = 0.35
noise_level = 1e-6  # essentially negligible

phi_N_stable = base_N + noise_level * np.random.randn(len(t_stable))
phi_D_stable = base_D + noise_level * np.random.randn(len(t_stable))

# --- Case 1: “Standard” sampling ---
var_stable = compute_jerk_variance(phi_N_stable, phi_D_stable, dt)
print(f"Stable node jerk variance (Δt={dt:.2e} s): {var_stable:.3e}")

# --- Case 2: Aggressive oversampling (smaller Δt) ---
t_oversample = np.linspace(0, 1e-3, 10000)  # 10× more points
dt_oversample = t_oversample[1] - t_oversample[0]
phi_N_os = base_N + noise_level * np.random.randn(len(t_oversample))
phi_D_os = base_D + noise_level * np.random.randn(len(t_oversample))

var_oversample = compute_jerk_variance(phi_N_os, phi_D_os, dt_oversample)
print(f"Same node, 10× oversampling (Δt={dt_oversample:.2e} s): {var_oversample:.3e}")

# --- Case 3: Add a microscopic high‑frequency ripple (hardware PLL jitter) ---
ripple = 1e-5 * np.sin(2*np.pi * 1e6 * t_stable)  # 1 MHz, amplitude 10⁻⁵
phi_N_ripple = base_N + ripple + noise_level * np.random.randn(len(t_stable))
phi_D_ripple = base_D + ripple + noise_level * np.random.randn(len(t_stable))

var_ripple = compute_jerk_variance(phi_N_ripple, phi_D_ripple, dt)
print(f"Stable node + 1 MHz ripple: {var_ripple:.3e}")

# --- Demonstrate that the “instability” flag is arbitrary ---
threshold = 1.0  # the proclaimed stability limit
for label, var in [("Standard", var_stable),
                   ("Oversampled", var_oversample),
                   ("Ripple", var_ripple)]:
    flag = "UNSTABLE" if var > threshold else "stable"
    print(f"{label:12s} → variance {var:.3e} ({flag})")