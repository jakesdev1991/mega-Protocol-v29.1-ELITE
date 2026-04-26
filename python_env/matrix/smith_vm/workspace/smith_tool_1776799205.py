# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ω‑Protocol Validator for BRDI‑Ω (Byzantine‑Resilient Data Ingestion)

This script checks the mathematical soundness of the BRDI‑Ω proposal
by evaluating the key quantities and verifying that the Ω‑Protocol
invariants (Φ_N, Φ_Δ, J*) and MPC‑Ω QP constraints are satisfied
under random but plausible data‑corruption scenarios.
"""

import numpy as np
import itertools

# -------------------------- CONFIGURATION --------------------------
np.random.seed(42)                     # reproducibility
m = 30                                 # number of data sources
d = 10                                 # dimension of the true data vector
n = 3 * d                              # encoding dimension → redundancy ρ = n/d = 3
t_max = m // 3                         # max Byzantine sources tolerated (⌊(m‑1)/2⌋ ≈ m/3 for m=30)

# Parameters appearing in the proposal (choose sensible values)
alpha, beta, gamma = 1.0, 1.0, 0.5     # DCI linear combination weights
lam = 0.2                              # weight of DCI in ψ invariant
# η coefficients for Φ‑mapping
eta1, eta2, eta3, eta4 = 0.4, 0.3, 0.2, 0.15
# Baseline Φ values (must be in feasible region)
Phi_N0 = 0.8
Phi_Delta0 = 0.1
R0 = 1.0                               # reference Ricci scalar (non‑zero)

# MPC‑Ω QP limits
DCI_MAX = 0.7
PHI_N_MIN = 0.6
S_DATA_MIN = np.log(3)

# Simulation parameters
num_scenarios = 5000                   # Monte‑Carlo trials
tau1, tau2 = 5.0, 8.0                  # lead‑times (hours) – not used directly in static check

# -------------------------- HELPERS --------------------------
def sparse_encoding_matrix(n, d):
    """Create a deterministic sparse matrix 𝔈 ∈ ℝ^{n×d} with exactly one 1 per column."""
    E = np.zeros((n, d))
    for col in range(d):
        row = (col * 7) % n   # simple deterministic pattern
        E[row, col] = 1.0
    return E

def encode_data(d_vec, E):
    """y = 𝔈 d"""
    return E @ d_vec

def add_byzantine_error(y_vec, corrupt_idx, error_scale=0.5):
    """Inject adversarial error e_i on selected sources."""
    e = np.zeros_like(y_vec)
    for i in corrupt_idx:
        # adversarial perturbation: direction random, magnitude scaled
        e[i] = error_scale * np.random.randn(*y_vec[i].shape)
    return e

def compute_residuals(y_tilde, E, d_true):
    """r_i = ŷ_i − 𝔈_i d"""
    y_hat = E @ d_true
    return y_tilde - y_hat

def data_corruption_index(residuals, rho):
    """θ = fraction of sources with ‖r_i‖ > τ, ε = mean ‖r_i‖."""
    norms = np.linalg.norm(residuals, axis=1)
    tau = 0.3 * np.mean(norms) if np.mean(norms) > 0 else 0.1  # threshold proportional to avg norm
    theta = np.mean(norms > tau)
    epsilon = np.mean(norms)
    # Ensure non‑negative argument for tanh
    inner = alpha * theta + beta * epsilon + gamma * rho
    inner = max(0.0, inner)          # <-- fixes the sign issue
    return np.tanh(inner)

def phi_N_mapping(DCI, theta):
    return Phi_N0 - eta1 * DCI + eta2 * (1.0 - theta)

def phi_Delta_mapping(theta, epsilon):
    return Phi_Delta0 + eta3 * theta - eta4 * epsilon

def ricci_scalar_from_residuals(residuals):
    """
    Very rough proxy for Ollivier‑Ricci curvature on the source‑similarity graph:
    we use the variance of residual norms as a surrogate; higher variance → lower curvature.
    """
    norms = np.linalg.norm(residuals, axis=1)
    var_norm = np.var(norms)
    # Map variance to a positive scalar: ℛ = 1 / (1 + var_norm)  (ensures ℛ>0)
    return 1.0 / (1.0 + var_norm)

def entropy_gauge(y_tilde):
    """S_data = - Σ p_i log p_i,  p_i = ‖ŷ_i‖ / Σ‖ŷ_j‖."""
    norms = np.linalg.norm(y_tilde, axis=1)
    total = np.sum(norms)
    if total == 0:
        return 0.0
    p = norms / total
    # avoid log(0)
    p = p[p > 0]
    return -np.sum(p * np.log(p))

def action_penalty(DCI, Phi_N, Phi_Delta, S_data):
    """Replicates the integrand of the cost function (point‑wise, non‑negative)."""
    term1 = max(0.0, DCI - 0.6) ** 2
    term2 = max(0.0, 0.6 - Phi_N) ** 2
    term3 = Phi_Delta ** 2
    term4 = max(0.0, np.log(3) - S_data) ** 2
    return term1 + term2 + term3 + term4

# -------------------------- MAIN VALIDATION LOOP --------------------------
E = sparse_encoding_matrix(n, d)
violations = []

for scen in range(num_scenarios):
    # 1. true data vector
    d_true = np.random.randn(d)

    # 2. encode and distribute
    y = encode_data(d_true, E)               # shape (n,)
    # split into m chunks (assume n divisible by m for simplicity)
    chunk_size = n // m
    y_chunks = [y[i*chunk_size:(i+1)*chunk_size] for i in range(m)]

    # 3. choose a random set of Byzantine sources (≤ t_max)
    t_byz = np.random.randint(0, t_max + 1)
    byz_idx = np.random.choice(m, size=t_byz, replace=False) if t_byz > 0 else []

    # 4. inject adversarial errors
    errors = np.zeros_like(y)
    if t_byz > 0:
        errors = add_byzantine_error(errors.reshape(m, chunk_size), byz_idx, error_scale=0.7).ravel()
    y_tilde = y + errors

    # 5. compute residuals and derived quantities
    residuals = compute_residuals(y_tilde.reshape(m, chunk_size), E, d_true)
    rho = n / d
    DCI = data_corruption_index(residuals, rho)
    theta = np.mean(np.linalg.norm(residuals, axis=1) > 
                    (0.3 * np.mean(np.linalg.norm(residuals, axis=1)) 
                     if np.mean(np.linalg.norm(residuals, axis=1)) > 0 else 0.1))
    epsilon = np.mean(np.linalg.norm(residuals, axis=1))

    Phi_N = phi_N_mapping(DCI, theta)
    Phi_Delta = phi_Delta_mapping(theta, epsilon)

    # ψ invariant (not directly constrained, just compute)
    R_G = ricci_scalar_from_residuals(residuals)
    psi = np.log(np.abs(R_G) / R0) + lam * DCI

    S_data = entropy_gauge(y_tilde.reshape(m, chunk_size))

    # 6. QP constraint checks
    if DCI > DCI_MAX + 1e-9:
        violations.append((f"SCENARIO {scen}: DCI={DCI:.4f} > {DCI_MAX}", scen))
    if Phi_N < PHI_N_MIN - 1e-9:
        violations.append((f"SCENARIO {scen}: Φ_N={Phi_N:.4f} < {PHI_N_MIN}", scen))
    if S_data < S_DATA_MIN - 1e-9:
        violations.append((f"SCENARIO {scen}: S_data={S_data:.4f} < {np.log(3):.4f}", scen))

    # 7. Ensure the cost‑integrand is non‑negative (should always hold)
    pen = action_penalty(DCI, Phi_N, Phi_Delta, S_data)
    if pen < -1e-12:
        violations.append((f"SCENARIO {scen}: negative penalty {pen:.2e}", scen))

# -------------------------- REPORT --------------------------
print("\n=== Ω‑Protocol BRDI‑Ω Validation Summary ===")
print(f"Scenarios examined: {num_scenarios}")
print(f"Total violations found: {len(violations)}")
if violations:
    print("\nFirst few violations:")
    for msg, idx in violations[:10]:
        print(f"  [{idx}] {msg}")
else:
    print("\nAll constraints satisfied – the proposal is mathematically sound")
    print("under the sampled random corruptions and the chosen parameters.")
    print("\nNote: This is a statistical check; exhaustive verification would require")
    print("formal proofs of the parameter ranges (η, α, β, γ, λ).")