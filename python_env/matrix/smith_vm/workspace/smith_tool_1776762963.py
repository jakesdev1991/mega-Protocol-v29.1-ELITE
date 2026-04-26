# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ω‑Protocol validation for the Metabolic Capital Index (MCI-Ω) proposal.
Checks mathematical soundness of MCI, Φ‑invariants, Lagrangian stationarity,
and MPC‑Ω constraints on a toy metabolic network.
"""

import numpy as np
from scipy.stats import entropy
from numpy.linalg import pinv, norm

# -------------------------- Helper functions --------------------------

def js_divergence(p, q):
    """Jensen-Shannon divergence between two discrete distributions."""
    p = np.asarray(p)
    q = np.asarray(q)
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)
    return 0.5 * (entropy(p, m) + entropy(q, m))

def correlation_length(corr_mat):
    """
    Approximate correlation length ξ from the correlation matrix.
    We use ξ = 1 / (1 - λ_max_offdiag), where λ_max_offdiag is the
    largest off‑diagonal eigenvalue of the correlation matrix.
    This yields ξ ≥ 1; ξ → ∞ as correlations become uniform.
    """
    # Zero out diagonal to focus on off‑diagonal correlations
    C = corr_mat.copy()
    np.fill_diagonal(C, 0.0)
    eigvals = np.linalg.eigvalsh(C)  # real symmetric
    lambda_max = np.max(np.abs(eigvals))
    if lambda_max >= 1.0:  # avoid division by zero / negative
        lambda_max = 0.999
    return 1.0 / (1.0 - lambda_max)

def compute_mci(S, v, dG, ATP_idx, redox_idxs):
    """
    Metabolic Capital Index:
        MCI = ( Σ_i |v_i * ΔG_i| ) / sqrt( Σ_j (∂v_j/∂c_ATP)^2 ) *
              (1 - σ_redox / μ_redox)
    For the toy model we approximate ∂v_j/∂c_ATP by a simple sensitivity:
        ∂v_j/∂c_ATP ≈ v_j / (c_ATP + ε)   (linear scaling)
    """
    # Numerator: total capital turnover (absolute flux-weighted free energy)
    num = np.sum(np.abs(v * dG))
    # Denominator: sensitivity to ATP concentration
    c_ATP = 1.0  # placeholder intracellular ATP level (mM)
    eps = 1e-9
    sens = np.sum((v / (c_ATP + eps)) ** 2)
    den = np.sqrt(sens)
    # Redox term: variance/mean of redox cofactors (NADH/NADPH pool)
    red_vals = v[redox_idxs]  # use flux through redox reactions as proxy
    mu_redox = np.mean(np.abs(red_vals))
    sigma_redox = np.std(np.abs(red_vals))
    redox_term = 1.0 - (sigma_redox / (mu_redox + eps))
    mci = (num / (den + eps)) * redox_term
    return mci

def compute_phi_N(conc):
    """Average pairwise Pearson correlation of metabolite concentrations."""
    if conc.shape[0] < 2:
        return 0.0
    corr = np.corrcoef(conc, rowvar=False)  # metabolites as columns
    # Exclude diagonal
    mask = ~np.eye(corr.shape[0], dtype=bool)
    phi_n = np.mean(np.abs(corr[mask]))
    return phi_n

def compute_phi_delta(intra, extra):
    """Jensen-Shannon divergence between intra‑ and extracellular metabolite pools."""
    return js_divergence(intra, extra)

def compute_psi(xi, xi0=1.0):
    """ψ = ln(ξ/ξ₀)."""
    return np.log(xi / xi0)

# -------------------------- Synthetic test data --------------------------

# Toy network: 3 metabolites (A, B, C), 2 reactions
#   R1: A -> B
#   R2: B + C -> A
S = np.array([
    [-1,  1],   # A
    [ 1, -1],   # B
    [ 0, -1]    # C
])  # shape (metabolites, reactions)

# Feasible steady‑state flux vector (mol/(gDW·h))
v = np.array([0.8, 0.8])   # both forward, satisfies Sv ≈ 0

# Exchange vector b (external fluxes): assume no net exchange for simplicity
b = np.zeros(S.shape[0])

# Standard Gibbs free energies (kJ/mol) – random but consistent direction
dG = np.array([-20.0, -15.0])   # both exergonic

# Indices for sensitivity and redox terms
ATP_idx = 0          # treat metabolite A as ATP proxy
redox_idxs = np.array([1])   # metabolite B as redox carrier proxy

# Intracellular concentration snapshot (mM) – arbitrary but positive
conc_intra = np.array([1.0, 0.5, 0.2])   # [A, B, C]

# Extracellular concentration snapshot (mM)
conc_extra = np.array([0.1, 0.05, 0.01])

# -------------------------- Compute quantities --------------------------

mci = compute_mci(S, v, dG, ATP_idx, redox_idxs)
phi_N = compute_phi_N(conc_intra)
phi_Delta = compute_phi_delta(conc_intra, conc_extra)
xi = correlation_length(np.corrcoef(conc_intra, rowvar=False))
psi = compute_psi(xi, xi0=1.0)

# Numerical derivatives for stiffness coefficients (central difference)
eps = 1e-6
def phi_N_of_psi(psi_val):
    # Reconstruct correlation length from ψ: ξ = ξ0 * exp(ψ)
    xi_test = np.exp(psi_val)  # ξ0 = 1
    # Build a test correlation matrix with uniform off‑diag = 1 - 1/ξ
    offdiag = 1.0 - 1.0/xi_test if xi_test > 1 else 0.0
    C_test = np.full((3,3), offdiag)
    np.fill_diagonal(C_test, 1.0)
    return compute_phi_N(np.random.multivariate_normal(np.zeros(3), C_test, size=50))

# Approximate derivatives
psi_plus = psi + eps
psi_minus = psi - eps
xi_N = (phi_N_of_psi(psi_plus) - phi_N_of_psi(psi_minus)) / (2*eps)
xi_D = (compute_phi_delta(conc_intra + eps, conc_extra) -
        compute_phi_delta(conc_intra - eps, conc_extra)) / (2*eps)

# Shadow‑price vector λ from Sv = b (minimum‑norm solution)
lam = pinv(S) @ b   # yields λ such that Sᵀλ is orthogonal to nullspace of S

# Lagrange multiplier for Φ_N constraint (choose μ_Ω to satisfy stationarity)
# We solve ∂L/∂v = 0 for μ_Ω:
#   ∇U + Sᵀλ + μ_Ω ∂Φ_N/∂v = 0  => μ_Ω = -(∇U + Sᵀλ)·(∂Φ_N/∂v) / ||∂Φ_N/∂v||²
# For simplicity we take U(v) = biomass yield = cᵀv with c = [1,1,0] (arbitrary)
c = np.array([1.0, 1.0, 0.0])
grad_U = c  # ∂U/∂v = c
# Approximate ∂Φ_N/∂v via finite difference on concentrations (conc ≈ Sv? we use linear map)
# Assume concentrations proportional to flux: conc ≈ Sv (steady state)
def phi_N_from_v(v_test):
    conc_test = S @ v_test   # rough proxy
    return compute_phi_N(conc_test)

grad_phi_N = (phi_N_from_v(v + eps*np.ones_like(v)) -
              phi_N_from_v(v - eps*np.ones_like(v))) / (2*eps)
mu_Omega = -np.dot(grad_U + S.T @ lam, grad_phi_N) / (np.dot(grad_phi_N, grad_phi_N) + 1e-12)

# Stationarity residual
stationarity_resid = grad_U + S.T @ lam + mu_Omega * grad_phi_N

# -------------------------- Ω‑Protocol invariant checks --------------------------

# Invariants from the proposal (thresholds are illustrative)
assert mci >= 2.0, f"MCI too low: {mci:.3f} (must be ≥ 2.0)"
assert phi_N >= 0.6, f"Φ_N too low: {phi_N:.3f} (must be ≥ 0.6)"
assert phi_Delta <= 0.7, f"Φ_Δ too high: {phi_Delta:.3f} (must be ≤ 0.7)"
# λ_ATP is the shadow price associated with metabolite A (ATP proxy)
lam_ATP = lam[ATP_idx]
lam_max = 5.0  # arbitrary upper bound from proposal
assert lam_ATP <= lam_max, f"λ_ATP too high: {lam_ATP:.3f} (must be ≤ {lam_max})"

# Lagrangian stationarity tolerance
tol = 1e-4
assert norm(stationarity_resid) < tol, (
    f"Lagrangian stationarity violated: residual norm = {norm(stationarity_resid):.2e}"
)

# -------------------------- Output summary --------------------------

print("Ω‑Protocol validation passed.")
print(f"MCI                = {mci:.3f}")
print(f"Φ_N (connectivity) = {phi_N:.3f}")
print(f"Φ_Δ (asymmetry)    = {phi_Delta:.3f}")
print(f"ψ                  = {psi:.3f}")
print(f"ξ_N                = {xi_N:.3f}")
print(f"ξ_Δ                = {xi_D:.3f}")
print(f"Shadow prices λ    = {lam}")
print(f"μ_Ω                = {mu_Omega:.3f}")
print(f"Stationarity residual norm = {norm(stationarity_resid):.2e}")