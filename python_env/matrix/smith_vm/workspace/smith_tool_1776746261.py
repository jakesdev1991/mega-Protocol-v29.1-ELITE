# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation of the Informational Jerk stability analysis for a Linux HSA node
as presented in the Agent's thought.

We:
1. Synthesize I(t) as described.
2. Compute first, second and third derivatives using the finite‑difference
   formulas given (with Savitzky‑Golay smoothing approximated by a simple
   moving‑average of window 5 before differentiation).
3. Estimate the stiffness invariants ξ_N and ξ_Δ from the jerk‑stiffness
   relation.
4. Check the Omega Protocol stability criteria:
      ξ_N > ξ_crit   (prevents Shredding)
      ξ_Δ < ξ_max    (prevents Informational Freeze)
      |J|_max < J_max
5. Print the results and assert compliance (or raise an AssertionError).

Note: This script is self‑contained and uses only NumPy (no SciPy required).
"""

import numpy as np

# ----------------------------------------------------------------------
# 1. Synthetic I(t) generation (matching the description)
# ----------------------------------------------------------------------
def synthetic_I(t, I0=5.0, eps=0.2, fc=50.0, tau=2.0, noise_std=0.1):
    """
    I(t) = I0 * [1 + eps * cos(2π fc t)] * exp(-t/tau) + η(t)
    η ~ N(0, noise_std^2)
    """
    deterministic = I0 * (1.0 + eps * np.cos(2 * np.pi * fc * t)) * np.exp(-t / tau)
    noise = np.random.normal(loc=0.0, scale=noise_std, size=t.shape)
    return deterministic + noise

# Simulation parameters
dt = 1e-3                     # 1 ms sampling
T  = 1.0                      # 1 second total
t  = np.arange(0, T, dt)      # time vector
N  = len(t)

# Fix seed for reproducibility
np.random.seed(42)
I = synthetic_I(t)

# ----------------------------------------------------------------------
# 2. Savitzky‑Golay smoothing (cubic polynomial, window=5)
#    Implemented via least‑squares fit of a 3rd‑order polynomial to each
#    window; equivalent to convolution with pre‑computed coefficients.
# ----------------------------------------------------------------------
def savitzky_golay(y, window=5, order=3):
    """Return smoothed y using Savitzky‑Golay filter."""
    if window % 2 != 1 or window < order + 2:
        raise ValueError("window must be odd and >= order+2")
    half = window // 2
    # Precompute coefficients for the central point
    x = np.arange(-half, half + 1)
    A = np.vander(x, order + 1)
    coeff = np.linalg.lstsq(A, np.eye(window), rcond=None)[0]
    # Central row gives the smoothing coefficients
    c = coeff[0, :]
    # Pad signal symmetrically
    y_pad = np.r_[y[half:0:-1], y, y[-2:-half-2:-1]]
    y_smooth = np.convolve(y_pad, c, mode='valid')
    return y_smooth

I_smooth = savitzky_golay(I, window=5, order=3)

# ----------------------------------------------------------------------
# 3. Derivatives via the finite‑difference formulas given in the thought
# ----------------------------------------------------------------------
def central_first_derivative(y, dt):
    """First derivative using central difference (same as formula)."""
    dydt = np.empty_like(y)
    dydt[1:-1] = (y[2:] - y[:-2]) / (2 * dt)
    # Forward/backward at edges
    dydt[0]    = (y[1] - y[0]) / dt
    dydt[-1]   = (y[-1] - y[-2]) / dt
    return dydt

def central_second_derivative(y, dt):
    """Second derivative using central difference."""
    d2ydt2 = np.empty_like(y)
    d2ydt2[1:-1] = (y[2:] - 2*y[1:-1] + y[:-2]) / (dt**2)
    d2ydt2[0]    = (y[0] - 2*y[1] + y[2]) / (dt**2)
    d2ydt2[-1]   = (y[-3] - 2*y[-2] + y[-1]) / (dt**2)
    return d2ydt2

def third_derivative_formula(y, dt):
    """
    Third derivative as given:
    J ≈ (y[t+2δt] - 2y[t+δt] + 2y[t-δt] - y[t-2δt]) / (2 δt^3)
    """
    d3ydt3 = np.empty_like(y)
    # valid indices: 2 .. N-3
    d3ydt3[2:-2] = (y[4:] - 2*y[3:-1] + 2*y[1:-3] - y[:-4]) / (2 * dt**3)
    # edges: fallback to lower‑order forward/backward schemes
    d3ydt3[0]    = (y[3] - 3*y[2] + 3*y[1] - y[0]) / (dt**3)   # forward 3rd
    d3ydt3[1]    = (y[4] - 3*y[3] + 3*y[2] - y[1]) / (dt**3)
    d3ydt3[-2]   = (y[-1] - 3*y[-2] + 3*y[-3] - y[-4]) / (dt**3) # backward
    d3ydt3[-1]   = (y[-1] - 3*y[-2] + 3*y[-3] - y[-4]) / (dt**3)
    return d3ydt3

dI   = central_first_derivative(I_smooth, dt)
d2I  = central_second_derivative(I_smooth, dt)
J    = third_derivative_formula(I_smooth, dt)   # Informational Jerk

# ----------------------------------------------------------------------
# 4. Estimate stiffness invariants from the jerk‑stiffness relation
#    J = -ξ_N^{-2} * dI - ξ_Δ^{-2} * d2I + noise
#    Solve via linear least squares for the coefficients a = ξ_N^{-2},
#    b = ξ_Δ^{-2} (note the minus sign is absorbed).
# ----------------------------------------------------------------------
A = np.vstack([-dI, -d2I]).T   # shape (N,2)
# Solve A * [a, b]^T ≈ J
coeff, residuals, rank, s = np.linalg.lstsq(A, J, rcond=None)
a_est, b_est = coeff   # a_est ≈ ξ_N^{-2}, b_est ≈ ξ_Δ^{-2}

# Guard against negative estimates (non‑physical)
a_est = max(a_est, 1e-12)
b_est = max(b_est, 1e-12)

xi_N_est = 1.0 / np.sqrt(a_est)   # seconds
xi_D_est = 1.0 / np.sqrt(b_est)   # seconds

# ----------------------------------------------------------------------
# 5. Stability criteria (values taken from the thought)
# ----------------------------------------------------------------------
xi_crit = 10e-3   # 10 ms
xi_max  = 100e-3  # 100 ms
J_max   = 1e6     # bits / s^3

J_max_abs = np.max(np.abs(J))

stable = (xi_N_est > xi_crit) and (xi_D_est < xi_max) and (J_max_abs < J_max)

# ----------------------------------------------------------------------
# 6. Output results
# ----------------------------------------------------------------------
print("=== Informational Jerk Stability Validation ===")
print(f"Sampling dt          : {dt*1e3:.3f} ms")
print(f"Duration             : {T:.3f} s")
print(f"Estimated ξ_N        : {xi_N_est*1e3:.3f} ms")
print(f"Estimated ξ_Δ        : {xi_D_est*1e3:.3f} ms")
print(f"Max |J|              : {J_max_abs:.3e} bits/s^3")
print()
print("Omega Protocol thresholds:")
print(f"  ξ_N > ξ_crit ({xi_crit*1e3:.1f} ms)  ? {'PASS' if xi_N_est > xi_crit else 'FAIL'}")
print(f"  ξ_Δ < ξ_max  ({xi_max*1e3:.1f} ms)  ? {'PASS' if xi_D_est < xi_max else 'FAIL'}")
print(f"  |J|_max < J_max ({J_max:.1e})       ? {'PASS' if J_max_abs < J_max else 'FAIL'}")
print()
print(f"Overall stability assessment : {'STABLE' if stable else 'UNSTABLE'}")

# Assert for automated checking; will raise if any condition fails
assert xi_N_est > xi_crit, f"ξ_N ({xi_N_est*1e3:.3f} ms) not > crit ({xi_crit*1e3:.1f} ms)"
assert xi_D_est < xi_max, f"ξ_Δ ({xi_D_est*1e3:.3f} ms) not < max ({xi_max*1e3:.1f} ms)"
assert J_max_abs < J_max, f"|J|_max ({J_max_abs:.3e}) not < J_max ({J_max:.1e})"
print("\nAll checks passed – the analysis is mathematically consistent with the stated Omega invariants.")