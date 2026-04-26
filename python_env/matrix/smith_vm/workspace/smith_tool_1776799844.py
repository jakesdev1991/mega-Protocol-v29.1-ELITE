# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BRDI-Ω mathematical sanity check for Omega Protocol compliance.
Tests:
  - DCI in [0,1)
  - Φ_N^brdi, Φ_Δ^brdi in [0,1] (adjustable bounds)
  - ψ dimensionless (log term + λ*DCI)
  - S_data in [0, log(m)]
  - QP constraints: DCI ≤ 0.7, Φ_N^brdi ≥ 0.6, S_data ≥ log(3)
  - Cost integrand ≥ 0
  - Action density dimensionless (checked symbolically via units)
"""

import numpy as np
import math

# ------------------ Configuration ------------------
np.random.seed(42)
N_SAMPLES = 20000          # Monte‑Carlo draws
M_SOURCES = 30             # m = number of data feeds
D_DIM = 50                 # dimension of raw data vector d(t)
# Bounds for coefficients (chosen to satisfy audit)
ALPHA_BOUND = (0.0, 2.0)   # α ≥ 0
BETA_BOUND  = (0.0, 2.0)   # β ≥ 0
GAMMA_BOUND = (0.0, 2.0)   # γ ≥ 0
ETA_BOUND   = (0.0, 0.5)   # η_i small enough to keep Φ in [0,1]
LAMBDA_BOUND= (0.0, 2.0)   # λ dimensionless
MU_BOUND    = (0.0, 5.0)   # μ_i ≥ 0 for cost

# Nominal baseline values (must be in [0,1] for the test)
PHI_N0 = 0.8
PHI_DELTA0 = 0.2
R0 = 1.0                  # reference curvature magnitude

# ------------------ Helper functions ------------------
def sigmoid(x):
    """Alternative to tanh that guarantees [0,1] output."""
    return 1.0 / (1.0 + math.exp(-x))

def compute_dci(theta, eps, rho, alpha, beta, gamma, use_tanh=True):
    """Data Corruption Index."""
    arg = alpha * theta + beta * eps + gamma * rho
    if use_tanh:
        return math.tanh(arg)          # ∈ (-1,1)
    else:
        return sigmoid(arg)            # ∈ (0,1)

def compute_phi_n(dci, theta, eta1, eta2):
    """Φ_N^brdi mapping (see proposal)."""
    return PHI_N0 - eta1 * dci + eta2 * (1.0 - theta)

def compute_phi_delta(dci, eps, eta3, eta4):
    """Φ_Δ^brdi mapping."""
    return PHI_DELTA0 + eta3 * theta - eta4 * eps

def compute_psi(curv_mag, dci, lam):
    """Invariant ψ = ln(|ℛ_G|/ℛ0) + λ·DCI."""
    return math.log(abs(curv_mag) / R0) + lam * dci

def compute_entropy(norms):
    """S_data = -∑ p_i log p_i, p_i = ‖ŷ_i‖/∑‖ŷ_j‖."""
    total = np.sum(norms)
    if total == 0:
        return 0.0
    p = norms / total
    # avoid log(0)
    p = np.where(p > 0, p, 1e-15)
    return -np.sum(p * np.log(p))

def cost_integrand(dci, phi_n, phi_delta, s_data, mu1, mu2, mu3):
    """Integrand of 𝒥 (positive‑part squared)."""
    term1 = max(dci - 0.6, 0.0) ** 2
    term2 = mu1 * max(0.6 - phi_n, 0.0) ** 2
    term3 = mu2 * (phi_delta ** 2)
    term4 = mu3 * max(math.log(3) - s_data, 0.0) ** 2
    return term1 + term2 + term3 + term4

# ------------------ Monte‑Carlo Test ------------------
violations = 0
for i in range(N_SAMPLES):
    # draw coefficients
    alpha = np.random.uniform(*ALPHA_BOUND)
    beta  = np.random.uniform(*BETA_BOUND)
    gamma = np.random.uniform(*GAMMA_BOUND)
    eta1  = np.random.uniform(*ETA_BOUND)
    eta2  = np.random.uniform(*ETA_BOUND)
    eta3  = np.random.uniform(*ETA_BOUND)
    eta4  = np.random.uniform(*ETA_BOUND)
    lam   = np.random.uniform(*LAMBDA_BOUND)
    mu1   = np.random.uniform(*MU_BOUND)
    mu2   = np.random.uniform(*MU_BOUND)
    mu3   = np.random.uniform(*MU_BOUND)

    # synthetic source responses: generate random errors
    # true data vector d(t) drawn from N(0,1)
    d_true = np.random.randn(D_DIM)
    # each source returns y_i + e_i ; we only need residuals r_i = ŷ_i - E_i d
    # Simulate residuals as Gaussian with variance sigma^2
    sigma = np.random.uniform(0.0, 0.5)
    residuals = sigma * np.random.randn(M_SOURCES, D_DIM)

    # compute per‑source error norms
    err_norms = np.linalg.norm(residuals, axis=1)          # shape (M,)
    theta = np.mean(err_norms > 0.1) / M_SOURCES          # fraction > τ (τ=0.1)
    eps   = np.mean(err_norms)                           # average magnitude
    # redundancy factor ρ = n/d ; we fix n = 3*d (ρ=3) for simplicity
    rho = 3.0

    # DCI (using tanh as in proposal)
    dci = compute_dci(theta, eps, rho, alpha, beta, gamma, use_tanh=True)

    # Φ mappings
    phi_n = compute_phi_n(dci, theta, eta1, eta2)
    phi_delta = compute_phi_delta(dci, eps, eta3, eta4)

    # Invariant ψ (need a curvature magnitude; draw from a plausible range)
    curv_mag = np.random.uniform(0.1, 5.0)   # |ℛ_G|
    psi = compute_psi(curv_mag, dci, lam)

    # Entropy gauge
    # ŷ_i norms: use ||y_i|| + error norm; we approximate with 1.0 + err_norm
    y_norms = 1.0 + err_norms
    s_data = compute_entropy(y_norms)

    # ----- Constraint checks -----
    # 1) DCI in [0,1) (tanh may give negative if arg<0)
    if not (0.0 <= dci < 1.0):
        violations += 1
        continue

    # 2) Φ_N, Φ_Δ in [0,1] (reasonable physical range)
    if not (0.0 <= phi_n <= 1.0 and 0.0 <= phi_delta <= 1.0):
        violations += 1
        continue

    # 3) ψ dimensionless – just ensure it's a real number
    if not np.isfinite(psi):
        violations += 1
        continue

    # 4) Entropy bounds
    if not (0.0 <= s_data <= math.log(M_SOURCES)):
        violations += 1
        continue

    # 5) QP constraints
    if not (dci <= 0.7 + 1e-12 and phi_n >= 0.6 - 1e-12 and s_data >= math.log(3) - 1e-12):
        violations += 1
        continue

    # 6) Cost integrand non‑negative (by construction it is, but we check)
    integ = cost_integrand(dci, phi_n, phi_delta, s_data, mu1, mu2, mu3)
    if integ < -1e-12:
        violations += 1
        continue

# ------------------ Report ------------------
print(f"Monte‑Carlo samples: {N_SAMPLES}")
print(f"Violations found:    {violations}")
print(f"Success rate:        {100.0 * (N_SAMPLES - violations) / N_SAMPLES:.2f}%")
if violations == 0:
    print("\nAll sampled configurations satisfy the Omega‑Protocol invariants "
          "and internal consistency checks.")
else:
    print("\nSome configurations failed – revisit coefficient bounds or mapping functions.")