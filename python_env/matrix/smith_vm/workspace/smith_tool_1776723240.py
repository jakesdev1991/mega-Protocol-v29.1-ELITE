# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation of the refined CLEM‑Ω proposal.
Checks mathematical soundness and Omega‑Protocol invariant compliance.
"""

import numpy as np
import scipy.stats as stats

# --------------------------
# Helper functions
# --------------------------
def zscore(x):
    """Return z‑scored version of x (zero mean, unit std)."""
    return (x - np.mean(x)) / (np.std(x) + 1e-12)

def compute_CLE(R, S, E, M, weights):
    """
    Linear CLE definition with pre‑zscored features.
    R, S, E, M: 1‑D arrays (z‑scored) for a business unit.
    weights: array [α,β,γ,δ] (should sum to 1 for interpretability).
    """
    assert len(weights) == 4, "Four weights required"
    CLE = np.dot(weights, np.array([np.mean(R), np.std(S), np.mean(E), np.mean(M)]))
    return CLE

def invariants(CLE_series, feature_matrix):
    """
    Compute the Omega‑Rubric invariants from a time series of CLE
    and the underlying feature matrix (features × time).
    feature_matrix shape: (n_features, n_time)
    """
    CLE0 = np.median(CLE_series)               # reference baseline
    psi = np.log(CLE_series / CLE0)            # scalar invariant

    # Radial correlation length: gradient across business units.
    # Here we approximate gradient across features as a proxy.
    grad = np.gradient(feature_matrix, axis=1)  # shape (n_feat, n_time)
    norm_grad_sq = np.sum(grad**2, axis=0)      # sum over features
    xi_N = np.power(np.mean(norm_grad_sq, axis=0) + 1e-12, -0.5)

    # Poloidal correlation length: ratio of max/min variance across features
    var_f = np.var(feature_matrix, axis=1)      # variance per feature
    xi_Delta = np.max(var_f) / (np.min(var_f) + 1e-12)

    # Credential‑risk entropy (Shannon)
    # weight per credential: w = R * (1 - S) * E
    w = feature_matrix[0] * (1 - feature_matrix[1]) * feature_matrix[2]  # R,S,E rows
    w = np.maximum(w, 0)                       # avoid negatives
    p = w / (np.sum(w) + 1e-12)
    S_h = -np.sum(p * np.log(p + 1e-12))

    return psi, xi_N, xi_Delta, S_h

def map_to_Omega(psi, xi_Delta, eta1=0.3, eta2=0.2, PhiN0=0.9, PhiD0=0.4):
    """Linear mapping to Omega variables (with lag omitted for simplicity)."""
    PhiN = PhiN0 - eta1 * psi
    PhiD = PhiD0 + eta2 * xi_Delta
    return PhiN, PhiD

def gpd_exceedance_score(data, threshold=None):
    """
    Fit a Generalized Pareto Distribution to exceedances over threshold.
    Returns the survival probability (tail probability) for the latest point.
    """
    if threshold is None:
        threshold = np.percentile(data, 90)   # default 90th percentile
    exceed = data[data > threshold] - threshold
    if len(exceed) < 5:
        raise ValueError("Too few exceedances for GPD fit.")
    # MLE for GPD shape (c) and scale (scipy uses shape=c, loc=0, scale=scale)
    c, loc, scale = stats.genpareto.fit(exceed, floc=0)
    # Survival function for the latest observation
    latest = data[-1]
    if latest <= threshold:
        return 1.0   # not an exceedance → low anomaly
    z = latest - threshold
    sf = stats.genpareto.sf(z, c, loc, scale)   # P(X > z)
    return sf

# --------------------------
# Synthetic data generation (for illustration)
# --------------------------
np.random.seed(42)
n_time = 100
# Simulate four z‑scored features (already unit variance)
R = zscore(np.random.randn(n_time) + 0.2*np.sin(np.linspace(0, 4*np.pi, n_time)))
S = zscore(np.random.randn(n_time) - 0.1*np.cos(np.linspace(0, 3*np.pi, n_time)))
E = zscore(np.random.randn(n_time) + 0.05*np.linspace(0, 1, n_time))
M = zscore(np.random.randn(n_time) - 0.15*np.sin(np.linspace(0, 5*np.pi, n_time)))

# Feature matrix: rows = [R, S, E, M]
feat_mat = np.vstack([R, S, E, M])

# Learned weights (example, should sum to 1)
weights = np.array([0.4, 0.3, 0.2, 0.1])   # α,β,γ,δ

# --------------------------
# Core computations
# --------------------------
CLE_series = np.array([compute_CLE(R[:t+1], S[:t+1], E[:t+1], M[:t+1], weights)
                       for t in range(n_time)])

psi, xi_N, xi_Delta, S_h = invariants(CLE_series, feat_mat)

PhiN, PhiD = map_to_Omega(psi, xi_Delta)

# Anomaly score via GPD
try:
    a_CLE = gpd_exceedance_score(CLE_series)
except ValueError as e:
    a_CLE = np.nan
    print("GPD fitting issue:", e)

# Dual condition for alert
alert = (a_CLE < 0.01) and (PhiD[-1] > 0.5)

# --------------------------
# Constraint checking (MPC‑Ω)
# --------------------------
constraints = {
    "CLE <= 2.0": np.all(CLE_series <= 2.0 + 1e-9),
    "Phi_N >= 0.75": np.all(PhiN >= 0.75 - 1e-9),
    "psi_CLE <= 0 (CLE <= baseline)": np.all(psi <= 1e-9)
}

# --------------------------
# Output summary
# --------------------------
print("=== CLEM‑Ω Validation Summary ===")
print(f"Final CLE value: {CLE_series[-1]:.4f}")
print(f"Scalar invariant ψ_CLE: {psi[-1]:.4f}")
print(f"Radial correlation length ξ_N: {xi_N[-1]:.4f}")
print(f"Poloidal correlation length ξ_Δ: {xi_Delta[-1]:.4f}")
print(f"Credential‑risk entropy S_h: {S_h:.4f}")
print(f"Mapped Φ_N: {PhiN[-1]:.4f}")
print(f"Mapped Φ_Δ: {PhiD[-1]:.4f}")
print(f"GPD anomaly score (tail prob.): {a_CLE:.4f}")
print(f"Operational‑risk alert triggered? {alert}")
print("\nConstraint satisfaction:")
for name, satisfied in constraints.items():
    print(f"  {name}: {'OK' if satisfied else 'VIOLATION'}")

# --------------------------
# Optional: raise exception if any constraint violated (for automated testing)
# --------------------------
if not all(constraints.values()):
    raise AssertionError("One or more Omega‑Protocol constraints violated.")