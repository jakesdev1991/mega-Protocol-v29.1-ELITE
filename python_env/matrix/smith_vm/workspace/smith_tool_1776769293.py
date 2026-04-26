# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ------------------------------
# Parameters (SI units)
# ------------------------------
S0      = 2.0          # bits (dimensionless)
eps     = 0.3
fc      = 50.0         # Hz
tau     = 2.0          # s
sigma_n = 0.1          # bits noise std
dt      = 0.001        # 1 ms sampling
T       = 1.0          # total simulation time (s)
t       = np.arange(0, T, dt)
N       = len(t)

# ------------------------------
# Synthetic entropy S(t)
# ------------------------------
np.random.seed(42)
noise   = sigma_n * np.random.randn(N)
S       = S0 * (1 + eps * np.cos(2*np.pi*fc*t)) * np.exp(-t/tau) + noise

# ------------------------------
# Finite‑difference derivatives
# ------------------------------
# First derivative (central)
dS   = np.gradient(S, dt, edge_order=2)
# Second derivative
d2S  = np.gradient(dS, dt, edge_order=2)
# Third derivative (informational jerk) using the 5‑point stencil from the text
J    = (np.roll(S, -2) - 2*np.roll(S, -1) + 2*np.roll(S, 1) - np.roll(S, 2)) / (2*dt**3)
# Handle edges (set to NaN then ignore later)
J[[0,1,-2,-1]] = np.nan

# ------------------------------
# Estimate stiffness invariants from jerk‑stiffness relation:
#   J = -a * dS - b * d2S   where a = ξ_N^{-2}, b = ξ_Δ^{-2}
# ------------------------------
# Build design matrix (ignore NaNs)
valid = ~np.isnan(J)
A     = np.column_stack([-dS[valid], -d2S[valid]])
b_vec = J[valid]
# Least‑squares solution
x, *_ = np.linalg.lstsq(A, b_vec, rcond=None)
a_est, b_est = x
# Guard against non‑positive estimates (would give imaginary ξ)
if a_est <= 0 or b_est <= 0:
    raise ValueError("Regression gave non‑positive stiffness coefficients.")
xi_N_est = 1.0 / np.sqrt(a_est)   # seconds
xi_D_est = 1.0 / np.sqrt(b_est)   # seconds

# ------------------------------
# Stability thresholds from the Omega Protocol
# ------------------------------
xi_crit = 0.01   # 10 ms  → prevents shredding (ξ_N must be > this)
xi_max  = 0.10   # 100 ms → prevents informational freeze (ξ_Δ must be < this)

# ------------------------------
# Validation checks
# ------------------------------
tol = 1e-2   # tolerance for dimensionless quantities (relative)

# 1. Dimensional sanity: S dimensionless → derivatives have correct units
#    (We trust the code because we used seconds for dt.)
assert np.allclose(np.diff(t), dt), "Time step not uniform"
# 2. Jerk‑stiffness relation residual
J_pred = -a_est * dS[valid] - b_est * d2S[valid]
rel_err = np.sqrt(np.mean(((J[valid] - J_pred) / (np.abs(J[valid]) + 1e-12))**2))
assert rel_err < tol, f"Jerk‑stiffness relation failed (rel_err={rel_err:.3e})"

# 3. Stability criteria
stable_N = xi_N_est > xi_crit
stable_D = xi_D_est < xi_max

# ------------------------------
# Report
# ------------------------------
print("=== Omega Protocol Audit ===")
print(f"Estimated ξ_N  = {xi_N_est*1e3:.2f} ms  (crit > {xi_crit*1e3:.0f} ms)  -> {'PASS' if stable_N else 'FAIL'}")
print(f"Estimated ξ_Δ  = {xi_D_est*1e3:.2f} ms  (max  < {xi_max*1e3:.0f} ms)  -> {'PASS' if stable_D else 'FAIL'}")
print(f"Jerk‑stiffness relative error = {rel_err:.3e}  -> {'PASS' if rel_err < tol else 'FAIL'}")
print("\nOverall compliance:", "PASS" if (stable_N and stable_D and rel_err < tol) else "FAIL")