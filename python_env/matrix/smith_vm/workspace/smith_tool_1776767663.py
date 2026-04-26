# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validate the Informational Jerk stability analysis for a Linux HSA node
as described in the Agent Smith thought.

The script:
  1. Generates a synthetic mutual‑information trace I(t).
  2. Applies a Savitzky‑Golay filter (cubic, window=5) to reduce noise.
  3. Computes first, second and third derivatives via central differences.
  4. Estimates Newtonian (ξ_N) and Archive (ξ_Δ) stiffness from the
     jerk‑stiffness relation using least‑squares.
  5. Checks the Omega Protocol invariants:
        ξ_N > ξ_crit
        ξ_Δ < ξ_max
        |J(t)| < J_max   (for all t)
  6. Prints a concise stability report.

Assumptions:
  - Uniform sampling with Δt = 1 ms.
  - Noise η(t) ~ N(0, σ²) added to I(t).
  - The jerk‑stiffness model is linear in Ẋ and Ẍ.
"""

import numpy as np
from scipy.signal import savgol_filter

# ----------------------------------------------------------------------
# Parameters (matching the thought)
# ----------------------------------------------------------------------
dt = 1e-3                     # sampling interval [s]
T  = 1.0                      # total duration [s]
t  = np.arange(0, T, dt)      # time vector
N  = len(t)

I0   = 5.0                    # baseline mutual information [bits]
eps  = 0.2                    # oscillation amplitude
wc   = 2 * np.pi * 50.0       # 50 Hz coherent oscillation
tau  = 2.0                    # slow decay time constant [s]
sigma = 0.1                   # measurement noise std-dev [bits]

# Synthetic I(t): damped cosine + Gaussian noise
I_raw = I0 * (1 + eps * np.cos(wc * t)) * np.exp(-t / tau) + \
        np.random.normal(0.0, sigma, size=N)

# ----------------------------------------------------------------------
# Pre‑filter to suppress high‑frequency noise before differentiation
# ----------------------------------------------------------------------
window_length = 5          # must be odd and >= polynomial order+2
polyorder     = 3
I = savgol_filter(I_raw, window_length, polyorder, mode='interp')

# ----------------------------------------------------------------------
# Finite‑difference derivatives (central, O(dt²))
# ----------------------------------------------------------------------
def central_diff(f, dt):
    """First derivative using central difference."""
    df = np.empty_like(f)
    df[0]        = (f[1] - f[0])   / dt          # forward at left edge
    df[-1]       = (f[-1] - f[-2]) / dt          # backward at right edge
    df[1:-1]     = (f[2:] - f[:-2]) / (2 * dt)
    return df

def second_central_diff(f, dt):
    """Second derivative using central difference."""
    d2f = np.empty_like(f)
    d2f[0]    = (f[2] - 2*f[1] + f[0])   / (dt**2)   # forward stencil
    d2f[-1]   = (f[-1] - 2*f[-2] + f[-3])/ (dt**2)   # backward stencil
    d2f[1:-1] = (f[2:] - 2*f[1:-1] + f[:-2]) / (dt**2)
    return d2f

def third_central_diff(f, dt):
    """Third derivative using central difference (5‑point stencil)."""
    d3f = np.empty_like(f)
    # interior points: 5‑point stencil
    d3f[2:-2] = (f[4:] - 2*f[3:-1] + 2*f[1:-3] - f[:-4]) / (2 * dt**3)
    # edges – fall back to lower‑order (less accurate) but sufficient for demo
    d3f[0]    = (-f[3] + 3*f[2] - 3*f[1] + f[0]) / (dt**3)
    d3f[1]    = (-f[4] + 3*f[3] - 3*f[2] + f[1]) / (dt**3)
    d3f[-2]   = ( f[-1] - 3*f[-2] + 3*f[-3] - f[-4]) / (dt**3)
    d3f[-1]   = ( f[-1] - 3*f[-2] + 3*f[-3] - f[-4]) / (dt**3)
    return d3f

Idot  = central_diff(I, dt)
Iddot = second_central_diff(I, dt)
J     = third_central_diff(I, dt)   # informational jerk [bits/s³]

# ----------------------------------------------------------------------
# Estimate stiffness invariants from jerk‑stiffness relation:
#   J = -ξ_N^{-2} * Idot - ξ_Δ^{-2} * Iddot + noise
# Solve for a = ξ_N^{-2}, b = ξ_Δ^{-2} via linear least squares.
# ----------------------------------------------------------------------
A = np.column_stack((-Idot, -Iddot))   # shape (N,2)
# Use only interior points where derivatives are reliable (avoid edge stencils)
mask = np.ones(N, dtype=bool)
mask[:2] = mask[-2:] = False
A_fit = A[mask]
J_fit = J[mask]

# Solve A * [a, b]^T ≈ J
params, residuals, rank, s = np.linalg.lstsq(A_fit, J_fit, rcond=None)
a_est, b_est = params          # a = ξ_N^{-2}, b = ξ_Δ^{-2}
# Guard against negative estimates (non‑physical)
a_est = max(a_est, 0.0)
b_est = max(b_est, 0.0)

xi_N_est = 1.0 / np.sqrt(a_est) if a_est > 0 else np.inf
xi_Delta_est = 1.0 / np.sqrt(b_est) if b_est > 0 else np.inf

# ----------------------------------------------------------------------
# Omega Protocol thresholds (from the thought)
# ----------------------------------------------------------------------
xi_crit   = 10e-3   # 10 ms
xi_max    = 100e-3  # 100 ms
J_max     = 1e6     # bits/s³

# ----------------------------------------------------------------------
# Stability checks
# ----------------------------------------------------------------------
stable_N   = xi_N_est > xi_crit
stable_D   = xi_Delta_est < xi_max
stable_J   = np.all(np.abs(J) < J_max)

# ----------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------
print("=== Informational Jerk Stability Validation ===")
print(f"Sampled points: {N}  (dt = {dt*1e3:.3f} ms, T = {T:.3f} s)")
print(f"Estimated ξ_N  : {xi_N_est*1e3:.3f} ms  (crit > {xi_crit*1e3:.0f} ms)  -> {'PASS' if stable_N else 'FAIL'}")
print(f"Estimated ξ_Δ  : {xi_Delta_est*1e3:.3f} ms  (max < {xi_max*1e3:.0f} ms)  -> {'PASS' if stable_D else 'FAIL'}")
print(f"max|J|         : {np.max(np.abs(J)):.3e} bits/s³  (limit {J_max:.0e})  -> {'PASS' if stable_J else 'FAIL'}")
overall = stable_N and stable_D and stable_J
print(f"Overall stability: {'STABLE' if overall else 'UNSTABLE'}")
print("-" * 55)
# Optional: show time series of jerk for visual inspection (first 200 ms)
if N > 200:
    print("Jerk preview (first 200 ms):")
    print(J[:200])