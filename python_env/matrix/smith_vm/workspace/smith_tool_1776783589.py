# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KSSM‑Ω mathematical validation.
Generates synthetic finance data, computes kinetic metrics,
and verifies Omega Protocol invariant compliance.
"""

import numpy as np
from scipy.signal import savgol_filter

# ------------------- Synthetic data generation -------------------
np.random.seed(42)
T = 5000               # time steps (e.g., minutes)
N = 20                 # number of assets
# Base correlation structure (some persistent factors)
F = 3                  # latent factors
factor_loadings = np.random.randn(N, F)
factor_loadings /= np.linalg.norm(factor_loadings, axis=0, keepdims=True)
# Time‑varying factor volatility to induce kinetic stress
factor_vol = 0.2 + 0.5 * np.sin(np.linspace(0, 4*np.pi, T))[:, None]  # (T,1)
# Generate returns
returns = np.random.randn(T, N) * 0.01  # idiosyncratic noise
returns += (factor_vol[:, None] * factor_loadings[None, :, :]) @ np.random.randn(T, F, 1)  # factor part
returns = returns.squeeze(-1)  # shape (T, N)

# ------------------- Rolling correlation -------------------
window = 30   # ~30 min look‑back
corr_mats = np.empty((T - window + 1, N, N))
for t in range(window - 1, T):
    window_data = returns[t - window + 1: t + 1, :]
    corr = np.corrcoef(window_data, rowvar=False)
    # enforce positive‑definiteness (numerical)
    corr = (corr + corr.T) / 2
    eigvals, eigvecs = np.linalg.eigh(corr)
    eigvals = np.clip(eigvals, 1e-12, None)  # avoid zeros
    corr = eigvecs @ np.diag(eigvals) @ eigvecs.T
    corr_mats[t - window + 1] = corr

# ------------------- Eigenvalues & eigenvectors over time -------------------
lam = np.linalg.eigvalsh(corr_mats)          # shape (T-w+1, N), sorted asc
vec = np.linalg.eigh(corr_mats)[1]          # eigenvectors columns

# ------------------- Spectral flow & acceleration -------------------
# Savitzky‑Golay parameters: window length 5, polynomial order 2
sg_window = 5
sg_order = 2
lam_smooth = savgol_filter(lam, window_length=sg_window, polyorder=sg_order, axis=0, mode='interp')
lam_dot = savgol_filter(lam, window_length=sg_window, polyorder=sg_order, deriv=1, axis=0, mode='interp')
lam_ddot = savgol_filter(lam, window_length=sg_window, polyorder=sg_order, deriv=2, axis=0, mode='interp')

# ------------------- Kinetic Fragility Index -------------------
KFI = np.linalg.norm(lam_dot, axis=1)               # ||dot λ||_2
KFI_mu, KFI_sigma = KFI.mean(), KFI.std()
KFI_norm = (KFI - KFI_mu) / KFI_sigma

# ------------------- Kinetic invariant ψ -------------------
eps = 1e-12
psi = np.log((np.linalg.norm(lam_ddot, axis=1) + eps) / (KFI + eps))

# ------------------- Mapping to Omega variables -------------------
# Base invariants (chosen arbitrarily but within [0,1])
Phi_N0, Phi_Delta0 = 0.8, 0.2
eta1, eta2 = 0.15, 0.05
tau1, tau2 = 3, 4   # minutes offset (index shift)
# Shift arrays to respect lead times
def shift(arr, k):
    if k >= 0:
        return np.concatenate([np.full(k, np.nan), arr[:-k]]) if k>0 else arr
    else:
        return np.concatenate([arr[-k:], np.full(-k, np.nan)]) if k<0 else arr

Phi_N_kin = Phi_N0 - eta1 * np.tanh(shift(KFI_norm, tau1))
Phi_Delta_kin = Phi_Delta0 + eta2 * np.var(lam_dot, axis=1, ddof=1)  # variance across assets at each t
Phi_Delta_kin = shift(Phi_Delta_kin, tau2)

# ------------------- Stiffness coefficients (∂Φ/∂ψ) -------------------
# Approximate derivative via central difference
def derivative(x, dx=1.0):
    return np.gradient(x, dx, edge_order=2)

xi_N = derivative(Phi_N_kin) / derivative(psi)   # element‑wise, guard divide‑by‑zero
xi_Delta = derivative(Phi_Delta_kin) / derivative(psi)
# Replace infinities/nans with zeros for reporting
xi_N = np.nan_to_num(xi_N, nan=0.0, posinf=0.0, neginf=0.0)
xi_Delta = np.nan_to_num(xi_Delta, nan=0.0, posinf=0.0, neginf=0.0)

# ------------------- Entropy gauge from eigenvector rotation -------------------
dt = 1.0   # assume unit time step between samples
# angle between successive dominant eigenvectors (largest eigenvalue -> last column)
v1 = vec[:, :, -1]                     # shape (time, N)
dot_prod = np.sum(v1 * np.roll(v1, 1, axis=0), axis=1)
dot_prod[0] = 1.0                      # first step self‑overlap
angle = np.arccos(np.clip(dot_prod, -1, 1))
omega = angle / dt
# Discretize omega into bins for Shannon entropy
hist, _ = np.histogram(omega, bins=10, density=True)
hist = hist[hist > 0]
S_omega = -np.sum(hist * np.log(hist))

# ------------------- Protocol compliance checks -------------------
# Bounds from MPC‑Ω proposal
KFI_norm_bound = 2.5
psi_bound = 1.5
Phi_N_min = 0.6

# Evaluate only where data is not NaN (due to shifts)
valid = ~(np.isnan(KFI_norm) | np.isnan(psi) | np.isnan(Phi_N_kin))

violations = []
if np.any(KFI_norm[valid] > KFI_norm_bound):
    violations.append("KFI_norm exceeds 2.5")
if np.any(psi[valid] > psi_bound):
    violations.append("psi exceeds 1.5")
if np.any(Phi_N_kin[valid] < Phi_N_min):
    violations.append("Phi_N_kin drops below 0.6")

# Also ensure invariants stay in [0,1] (reasonable range)
if np.any(Phi_N_kin[valid] < 0) or np.any(Phi_N_kin[valid] > 1):
    violations.append("Phi_N_kin outside [0,1]")
if np.any(Phi_Delta_kin[valid] < 0) or np.any(Phi_Delta_kin[valid] > 1):
    violations.append("Phi_Delta_kin outside [0,1]")

# ------------------- Reporting -------------------
print("=== KSSM‑Ω Validation Report ===")
print(f"Time steps evaluated: {valid.sum()} / {T-window+1}")
print(f"KFI_norm  : mean={KFI_norm[valid].mean():.3f}, max={KFI_norm[valid].max():.3f}")
print(f"psi       : mean={psi[valid].mean():.3f}, max={psi[valid].max():.3f}")
print(f"Phi_N_kin : mean={Phi_N_kin[valid].mean():.3f}, min={Phi_N_kin[valid].min():.3f}")
print(f"Phi_Delta_kin: mean={Phi_Delta_kin[valid].mean():.3f}")
print(f"Entropy gauge S_omega: {S_omega:.3f}")
print(f"Stiffness coeffs: xi_N mean={xi_N[valid].mean():.3f}, xi_Delta mean={xi_Delta[valid].mean():.3f}")

if violations:
    print("\n⚠️  PROTOCOL VIOLATIONS DETECTED:")
    for v in violations:
        print(" -", v)
    raise AssertionError("Omega Protocol invariants breached.")
else:
    print("\n✅ All Omega Protocol invariant checks passed.")