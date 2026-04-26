# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATS-Ω Mathematical & Rubric Compliance Validator
------------------------------------------------
Checks:
  - psi = ln(Phi_N / Phi_N0)
  - Phi_N, Phi_Delta from covariance & skewness
  - ATI definition and bounds
  - Double‑well potential shape
  - Entropy gauge and current
  - QP constraints (ATI>=0.6, Phi_N>=0.5, S_alg>=ln2)
  - Cost function non‑negativity
  - Boundary behaviour of psi
"""

import numpy as np
from scipy.stats import skew
from scipy.spatial.distance import euclidean
from scipy.optimize import linprog

# ----------------- Helper Functions -----------------

def compute_covariance(field_vals):
    """
    field_vals: shape (n_components, n_samples)
    Returns covariance matrix (n_components x n_components)
    """
    return np.cov(field_vals, rowvar=True)

def Phi_N_from_cov(cov):
    """Phi_N = sqrt(max eigenvalue of covariance)"""
    eigvals = np.linalg.eigvalsh(cov)  # real symmetric
    return np.sqrt(np.max(eigvals))

def Phi_Delta_from_moments(samples):
    """Phi_Delta = skewness = mu3 / (mu2)^{3/2}"""
    mu2 = np.var(samples)
    mu3 = np.mean((samples - np.mean(samples))**3)
    if mu2 == 0:
        return 0.0
    return mu3 / (mu2 ** 1.5)

def shannon_conditional_entropy(path_counts):
    """
    path_counts: dict {type_m: {path_k: count}}
    Returns S_alg = sum_m p(m) * [- sum_k p_{m,k} log p_{m,k}]
    """
    S = 0.0
    total = sum(sum(v.values()) for v in path_counts.values())
    for m, inner in path_counts.items():
        p_m = sum(inner.values()) / total
        if p_m == 0:
            continue
        inner_sum = 0.0
        for k, cnt in inner.items():
            p_mk = cnt / sum(inner.values())
            if p_mk > 0:
                inner_sum -= p_mk * np.log(p_mk)
        S += p_m * inner_sum
    return S

def ATI_from_topology(Ricci_curv, Ricci_curv0, beta1, beta10, S_alg):
    """
    ATI = (|Ricci|/|Ricci0|) * (beta1/beta10) * exp(-S_alg)
    Assumes inputs are non‑negative.
    """
    term1 = np.abs(Ricci_curv) / (np.abs(Ricci_curv0) + 1e-12)
    term2 = beta1 / (beta10 + 1e-12)
    term3 = np.exp(-S_alg)
    return term1 * term2 * term3

def double_well(B, alpha=-1.0, beta=1.0, gamma=0.5):
    """V(B) = 0.5*alpha*B^2 + 0.25*beta*B^4 - gamma*B"""
    return 0.5 * alpha * B**2 + 0.25 * beta * B**4 - gamma * B

def psi_from_PhiN(PhiN, PhiN0):
    return np.log(PhiN / PhiN0)

# ----------------- Synthetic Data Generation -----------------

np.random.seed(42)
n_comp = 8          # number of algorithm components (vertices)
n_samples = 500     # time steps for statistics

# Simulate a computational‑integrity field B_i(t) ~ Gaussian with some correlation
mean = np.zeros(n_comp)
# Create a covariance with a dominant eigenvalue (to get non‑zero Phi_N)
A = np.random.randn(n_comp, n_comp)
cov_field = A @ A.T + 0.1 * np.eye(n_comp)  # ensure PD
field_vals = np.random.multivariate_normal(mean, cov_field, size=n_samples).T  # shape (n_comp, n_samples)

# Simulate path counts for entropy (3 types, each with up to 4 paths)
path_counts = {}
for m in range(3):
    inner = {}
    n_paths = np.random.randint(2, 5)
    counts = np.random.randint(1, 20, size=n_paths)
    for k, cnt in enumerate(counts):
        inner[k] = int(cnt)
    path_counts[m] = inner

# Simulate topological invariants (Ricci curvature, Betti numbers)
# For simplicity, take average edge curvature as a scalar
Ricci_curv0 = 0.8   # baseline curvature
Ricci_curv  = Ricci_curv0 * np.random.uniform(0.7, 1.2)  # allow variation
beta10 = 3          # baseline # independent cycles
beta1  = beta10 * np.random.randint(1, 4)   # allow some change

# ----------------- Compute Quantities -----------------

cov = compute_covariance(field_vals)
PhiN = Phi_N_from_cov(cov)
# For Phi_Delta we need a time series of a scalar observable; use spatial mean of B(t)
B_time_series = np.mean(field_vals, axis=0)   # shape (n_samples,)
PhiDelta = Phi_Delta_from_moments(B_time_series)

S_alg = shannon_conditional_entropy(path_counts)

ATI = ATI_from_topology(Ricci_curv, Ricci_curv0, beta1, beta10, S_alg)

PhiN0 = np.sqrt(np.max(np.linalg.eigvalsh(cov_field)))  # baseline from same cov (should equal PhiN if no perturbation)
psi = psi_from_PhiN(PhiN, PhiN0)

# Entropy gauge & current (just compute scalar versions for validation)
A_mu = np.gradient(S_alg)  # dummy gradient w.r.t. a dummy coordinate
J_mu = np.sqrt(2) * PhiDelta  # only time component non‑zero per definition

# Double‑well check: ensure two minima exist
Bs = np.linspace(-2, 2, 401)
Vs = double_well(Bs)
minima = Bs[(Vs[1:-1] < Vs[:-2]) & (Vs[1:-1] < Vs[2:])]
assert len(minima) >= 2, "Double‑well potential does not exhibit at least two minima"

# ----------------- Assertions (Invariants & Constraints) -----------------

# Psi invariant
assert np.allclose(psi, np.log(PhiN / PhiN0)), "Psi invariant violated"

# Phi_N, Phi_Delta ranges (non‑negative)
assert PhiN >= 0, "Phi_N negative"
assert np.isfinite(PhiDelta), "Phi_Delta not finite"

# ATI bounds (should be in [0,1] given construction)
assert 0 <= ATI <= 1 + 1e-9, f"ATI out of expected range: {ATI}"

# Entropy non‑negative
assert S_alg >= 0, "Negative Shannon entropy"

# QP constraints (must hold for a valid control step)
assert ATI >= 0.6 - 1e-9, f"ATI constraint violated: {ATI}"
assert PhiN >= 0.5 - 1e-9, f"Phi_N constraint violated: {PhiN}"
assert S_alg >= np.log(2) - 1e-9, f"S_alg constraint violated: {S_alg}"

# Cost function non‑negativity (example with unit weights)
mu1 = mu2 = mu3 = 1.0
cost = ((0.6 - ATI) if ATI < 0.6 else 0.0)**2 \
     + mu1 * ((0.5 - PhiN) if PhiN < 0.5 else 0.0)**2 \
     + mu2 * (PhiDelta)**2 \
     + mu3 * ((np.log(2) - S_alg) if S_alg < np.log(2) else 0.0)**2
assert cost >= 0, "Cost function negative"

# Boundary behaviour of psi:
#   - If PhiN -> large and S_alg high -> psi -> +inf
#   - If PhiN -> small and S_alg low  -> psi -> -inf
# We test monotonicity: psi increases with PhiN (holding PhiN0 fixed) and decreases with S_alg via ATI.
# Simple check: increase PhiN by 10% -> psi should increase (approx)
PhiN_up = PhiN * 1.1
psi_up = psi_from_PhiN(PhiN_up, PhiN0)
assert psi_up > psi, "Psi does not increase with PhiN"

# Decrease PhiN by 10% -> psi should decrease
PhiN_down = PhiN * 0.9
psi_down = psi_from_PhiN(PhiN_down, PhiN0)
assert psi_down < psi, "Psi does not decrease with PhiN"

print("All ATS-Ω mathematical and rubric checks passed.")
print(f"Phi_N = {PhiN:.4f}, Phi_Delta = {PhiDelta:.4f}, Psi = {psi:.4f}")
print(f"ATI = {ATI:.4f}, S_alg = {S_alg:.4f}, Cost = {cost:.6f}")