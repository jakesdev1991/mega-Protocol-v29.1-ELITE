# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
HVFI‑Ω invariant validator
--------------------------
This script implements the core equations from the HVFI‑Ω proposal
and asserts that the Omega Protocol invariants (Phi_N, Phi_Delta, J*)
remain within their prescribed bounds at every time step.
"""

import numpy as np
from scipy.special import softmax  # for stable log-sum-exp if needed

# ------------------ Hyper‑parameters (as suggested in the proposal) ------------------
L = 4                     # number of pyramid levels (tick, minute, hour, day)
B = 20                    # histogram bins for entropy / MI estimation
eps = 1e-6                # jitter to keep covariance PD
epsilon_cov = 1e-8        # small value added to Sigma_A before logdet
Phi_N0 = 0.5              # baseline strategic connectivity
Phi_Delta0 = 0.2          # baseline information asymmetry
eta1, eta2 = 0.3, 0.3     # scaling factors for Phi updates
alpha, beta = 1.0, 0.5    # entropy weighting in Phi_N
gamma, delta = 1.0, 0.5   # MI / Psi weighting in Phi_Delta
tau1, tau2, tau3 = 5, 10, 20   # ms lags (not used in synthetic demo)
S_min = 0.1
I_max = 2.0
Psi_min = -15.0           # corresponds to det ~ 3e-7 (still >0)
Phi_N_lower = 0.65
Phi_Delta_upper = 0.70
lambda1, lambda2, lambda3 = 1.0, 1.0, 1.0   # cost weights (not checked here)

# ------------------ Helper functions ------------------
def histogram_entropy(samples, bins=B):
    """Shannon entropy of 1‑D samples via histogram."""
    hist, _ = np.histogram(samples, bins=bins, density=True)
    # Avoid zeros in log
    hist = hist[hist > 0]
    return -np.sum(hist * np.log(hist))

def mutual_information_joint(x, y, bins=B):
    """Estimate I(X;Y) via 2‑D histogram."""
    hist2d, x_edges, y_edges = np.histogram2d(x, y, bins=bins, density=True)
    # Joint
    pxy = hist2d[hist2d > 0]
    # Marginals
    px = np.histogram(x, bins=bins, density=True)[0]
    py = np.histogram(y, bins=bins, density=True)[0]
    px = px[px > 0][:, None]
    py = py[py > 0][None, :]
    # Avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        log_term = np.log(pxy / (px * py))
        log_term[~np.isfinite(log_term)] = 0
    return np.sum(pxy * log_term)

def logdet_cov(matrices):
    """Log‑determinant of covariance of stacked activations + epsilon*I."""
    # matrices: shape (L, N) where N = feature length per level
    cov = np.cov(matrices)          # (L, L)
    cov += epsilon_cov * np.eye(L)  # ensure PD
    sign, logdet = np.slogdet(cov)
    # sign should be +1 because we added epsilon*I
    return logdet

def mahalanobis_score(residual, cov_residual):
    """sqrt(e^T Sigma^{-1} e)"""
    # Add jitter to avoid singular cov
    cov = cov_residual + epsilon_cov * np.eye(residual.shape[-1])
    inv_cov = np.linalg.inv(cov)
    return np.sqrt(np.einsum('...i,ij,...j->...', residual, inv_cov, residual))

# ------------------ Synthetic data generation ------------------
np.random.seed(42)
T = 100                     # number of time steps
# Simulate activation vectors per level: each level has a different feature dim
feat_dims = [64, 32, 16, 8]  # finer → coarser
activations = [np.random.randn(T, d) for d in feat_dims]   # list length L

# ------------------ Main validation loop ------------------
for t in range(T):
    # ----- 1. Per‑scale entropy -----
    S = np.array([histogram_entropy(activations[l][t]) for l in range(L)])
    assert np.all(S >= 0.0), f"Negative entropy at t={t}: {S}"

    # ----- 2. Cross‑scale mutual information -----
    I = np.zeros(L-1)
    for l in range(L-1):
        I[l] = mutual_information_joint(activations[l][t],
                                        activations[l+1][t])
    assert np.all(I >= 0.0), f"Negative mutual info at t={t}: {I}"

    # ----- 3. Pyramid curvature invariant -----
    # Stack level‑wise activation vectors (already 1‑D per level)
    A_stack = np.array([activations[l][t] for l in range(L)])  # shape (L,)
    # For covariance we need multiple samples; we use a short exponential window
    # Here we approximate using the last W samples (including current)
    W = 10
    start = max(0, t-W+1)
    A_window = np.array([activations[l][start:t+1] for l in range(L)])  # (L, W)
    # Covariance across levels (each level is a variable, we have W observations)
    Psi = logdet_cov(A_window)
    # No explicit bound on Psi, but we guard against -inf
    assert np.isfinite(Psi), f"Non‑finite Psi at t={t}: {Psi}"

    # ----- 4. Map to Omega variables -----
    mean_S = np.mean(S)
    std_S  = np.std(S)
    Phi_N = Phi_N0 + eta1 * np.tanh(alpha * mean_S - beta * std_S)
    # Enforce Phi_N in [0,1] (protocol invariant)
    assert 0.0 <= Phi_N <= 1.0, f"Phi_N out of bounds at t={t}: {Phi_N}"

    max_I = np.max(I) if L>1 else 0.0
    Phi_Delta = Phi_Delta0 + eta2 * (1.0 / (1.0 + np.exp(-(gamma * max_I - delta * Psi))))
    # Enforce Phi_Delta in [0,1]
    assert 0.0 <= Phi_Delta <= 1.0, f"Phi_Delta out of bounds at t={t}: {Phi_Delta}"

    # ----- 5. Anomaly score (optional, just compute) -----
    # Build feature vector z = [S, I, Psi]
    z = np.concatenate([S, I, [Psi]])
    # Simple baseline: rolling mean
    if t == 0:
        z_hat = z.copy()
        cov_err = np.eye(len(z))
    else:
        # update running mean/cov (omitted for brevity)
        z_hat = np.mean([z] + [z_prev for z_prev in [z]*0], axis=0)  # placeholder
        cov_err = np.eye(len(z))
    e = z - z_hat
    s_hvfi = mahalanobis_score(e, cov_err)
    assert s_hvfi >= 0.0, f"Negative Mahalanobis score at t={t}: {s_hvfi}"

    # ----- 6. MPC‑Ω constraint checks (invariants) -----
    assert np.all(S >= S_min), f"S_l < S_min at t={t}: {S}"
    assert np.all(I <= I_max), f"I_{l,l+1} > I_max at t={t}: {I}"
    assert Psi >= Psi_min, f"Psi < Psi_min at t={t}: {Psi}"
    assert Phi_N >= Phi_N_lower, f"Phi_N < {Phi_N_lower} at t={t}: {Phi_N}"
    assert Phi_Delta <= Phi_Delta_upper, f"Phi_Delta > {Phi_Delta_upper} at t={t}: {Phi_Delta}"

    # Store for next iteration (dummy)
    z_prev = z

print("All HVFI‑Ω invariants satisfied for the synthetic run.")