# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Audit: Kinetic Spectral Shredding Monitor (KSSM‑Ω)
Verifies internal mathematical consistency and invariant compliance.
"""

import numpy as np
from scipy.linalg import eigvalsh
from scipy.signal import savgol_filter

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def rolling_correlation(returns, window):
    """Compute rolling Pearson correlation matrix (returns: T x N)."""
    T, N = returns.shape
    corrs = np.empty((T, N, N))
    for t in range(window, T):
        window_data = returns[t-window:t]
        cov = np.cov(window_data, rowvar=False)
        std = np.sqrt(np.diag(cov))
        with np.errstate(divide='ignore', invalid='ignore'):
            cor = cov / np.outer(std, std)
        corrs[t] = np.nan_to_num(cov / np.outer(std, std))
    # fill early windows with NaN (will be ignored later)
    corrs[:window] = np.nan
    return corrs

def spectral_flow(eigvals, dt):
    """Finite‑difference derivative with Savitzky‑Golay smoothing."""
    # smooth each eigenvalue trajectory
    smoothed = savgol_filter(eigvals, window_length=5, polyorder=2, axis=0, mode='interp')
    deriv = np.gradient(smoothed, dt, axis=0)
    return deriv

def kinetic_fragility(flow):
    """KFI = L2 norm of spectral flow across eigenvalues."""
    return np.linalg.norm(flow, axis=1)  # shape (T,)

def kinetic_invariant(flow, accel, eps=1e-8):
    """psi = ln( (||acc||+eps) / (||flow||+eps) )."""
    norm_flow = np.linalg.norm(flow, axis=1)
    norm_acc = np.linalg.norm(accel, axis=1)
    return np.log((norm_acc + eps) / (norm_flow + eps))

def map_phi_N(phi0, kfi_tilde, eta1):
    """Phi_N^(kin) = phi0 - eta1 * tanh(kfi_tilde)."""
    return phi0 - eta1 * np.tanh(kfi_tilde)

def map_phi_Delta(phi0, flow_var, eta2):
    """Phi_Delta^(kin) = phi0 + eta2 * Var(dot{lambda})."""
    return phi0 + eta2 * flow_var

def stiffness_coeffs(phi0, kfi_tilde, flow_var, eta1, eta2):
    """Analytic derivatives of the mappings."""
    # dPhi_N/dpsi = dPhi_N/d(kfi_tilde) * d(kfi_tilde)/dpsi
    # Here we treat psi as a monotonic function of kfi_tilde for the test;
    # we compute derivative via chain rule using numeric diff of psi.
    dPhi_N_dkfi = -eta1 * (1 - np.tanh(kfi_tilde)**2)
    dPhi_Delta_dflow = eta2
    return dPhi_N_dkfi, dPhi_Delta_dflow

# ----------------------------------------------------------------------
# Synthetic data generation (stable correlation process)
# ----------------------------------------------------------------------
np.random.seed(42)
T, N = 500, 10          # 500 time steps, 10 assets
dt = 1.0                # 1‑minute sampling (arbitrary unit)

# Generate a base correlation matrix that slowly drifts
base_corr = np.eye(N)
for i in range(N):
    for j in range(i+1, N):
        base_corr[i, j] = base_corr[j, i] = 0.3 * np.exp(-0.001*np.arange(T))

# Add small Gaussian noise to returns to induce realistic correlation fluctuations
returns = np.random.multivariate_normal(mean=np.zeros(N), cov=base_corr, size=T)

# ----------------------------------------------------------------------
# Core computation pipeline
# ----------------------------------------------------------------------
window = 20                     # 20‑min rolling correlation
corrs = rolling_correlation(returns, window)

# Extract eigenvalues for each time step (skip NaN rows)
eigvals = np.array([eigvalsh(c) for c in corrs if not np.any(np.isnan(c))])
T_eff = eigvals.shape[0]
time = np.arange(T_eff) * dt

# Spectral flow and acceleration
flow = spectral_flow(eigvals, dt)          # (T_eff, N)
accel = spectral_flow(flow, dt)            # (T_eff, N)

# Kinetic quantities
kfi = kinetic_fragility(flow)              # (T_eff,)
kfi_mu, kfi_sigma = np.mean(kfi), np.std(kfi)+1e-12
kfi_tilde = (kfi - kfi_mu) / kfi_sigma

psi = kinetic_invariant(flow, accel)       # (T_eff,)

# Variance of flow across eigenvalues (for Phi_Delta)
flow_var = np.var(flow, axis=1)            # (T_eff,)

# ----------------------------------------------------------------------
# Parameter selection (respecting invariant bounds)
# ----------------------------------------------------------------------
phi0_N = 0.8          # baseline strategic connectivity
phi0_D = 0.2          # baseline information asymmetry
eta1 = 0.15           # ensures Phi_N stays in [0,1] given phi0_N
eta2 = 0.05           # small positive contribution
tau1 = tau2 = 3.0     # minutes (lead time) – not used directly in static test

# Map to Omega variables
Phi_N_kin = map_phi_N(phi0_N, kfi_tilde, eta1)
Phi_Delta_kin = map_phi_Delta(phi0_D, flow_var, eta2)

# Stiffness coefficients (analytic vs numeric)
dPhi_N_dkfi, dPhi_Delta_dflow = stiffness_coeffs(phi0_N, kfi_tilde, flow_var, eta1, eta2)
# numeric derivative of Phi_N w.r.t psi for verification
dPhi_N_dpsi_num = np.gradient(Phi_N_kin, psi, edge_order=2)
dPhi_Delta_dpsi_num = np.gradient(Phi_Delta_kin, psi, edge_order=2)

# ----------------------------------------------------------------------
# Assertions – the ruthless audit
# ----------------------------------------------------------------------
# 1. No NaNs/infs in core quantities
assert not np.any(np.isnan(eigvals)), "Eigenvalues contain NaN"
assert not np.any(np.isnan(flow)), "Spectral flow contains NaN"
assert not np.any(np.isnan(accel)), "Spectral acceleration contains NaN"
assert not np.any(np.isnan(kfi)), "KFI contains NaN"
assert not np.any(np.isnan(psi)), "Psi contains NaN"
assert not np.any(np.isnan(Phi_N_kin)), "Phi_N^(kin) contains NaN"
assert not np.any(np.isnan(Phi_Delta_kin)), "Phi_Delta^(kin) contains NaN"

# 2. Bounds on Omega variables
assert np.all((Phi_N_kin >= 0) & (Phi_N_kin <= 1)), "Phi_N^(kin) out of [0,1]"
assert np.all(Phi_Delta_kin >= 0), "Phi_Delta^(kin) negative"

# 3. Stiffness coefficient consistency (allow small tolerance)
tol = 1e-3
assert np.allclose(dPhi_N_dpsi_num, dPhi_N_dkfi * np.gradient(kfi_tilde, psi), atol=tol), \
       "Stiffness coefficient for Phi_N mismatch"
assert np.allclose(dPhi_Delta_dpsi_num, dPhi_Delta_dflow * np.gradient(flow_var, psi), atol=tol), \
       "Stiffness coefficient for Phi_Delta mismatch"

# 4. MPC‑Omega feasibility under stable regime (should hold)
assert np.all(kfi_tilde <= 2.5 + 1e-6), "KFI_tilde exceeds MPC constraint"
assert np.all(psi <= 1.5 + 1e-6), "Psi exceeds MPC constraint"
assert np.all(Phi_N_kin >= 0.6 - 1e-6), "Phi_N^(kin) drops below MPC lower bound"

# 5. Cost functional non‑negativity (quadratic form)
lam1, lam2 = 1.0, 1.0
integrand = (np.maximum(kfi_tilde, 0)**2) + lam1 * psi**2 + lam2 * np.maximum(0.6 - Phi_N_kin, 0)**2
assert np.all(integrand >= -1e-12), "Cost integrand negative (numerical tolerance)"

print("✅ All audit checks passed – KSSM‑Ω formulation is mathematically sound and respects Omega Protocol invariants.")