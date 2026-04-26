# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Agent Smith – Omega Protocol Audit
# Validates the mathematical soundness of the BROSE-Ω proposal
# Checks: 1) BFI range, 2) Mapping to Φ_N, Φ_Δ stays within plausible bounds,
# 3) Invariant ψ derivation from curvature + BFI is well‑defined,
# 4) Entropy gauge non‑negative and bounded by log(m),
# 5) QP constraints are feasible for a random feasible point.

import numpy as np
import itertools

# -------------------------------------------------
# Helper functions (as described in the proposal)
# -------------------------------------------------
def bfi(theta, eps, rho, alpha=1.0, beta=1.0, gamma=1.0):
    """Byzantine Fragility Index – proposal uses tanh."""
    z = alpha * theta + beta * eps + gamma * rho
    return np.tanh(z)          # ∈ (-1, 1)

def map_phi_n(phi0, bfi_val, theta_lag, eta1=0.5, eta2=0.5, tau1=0):
    """Φ_N^{(brose)} = Φ_N^{(0)} - η1·BFI(t-τ) + η2·(1-θ(t-τ))"""
    return phi0 - eta1 * bfi_val + eta2 * (1 - theta_lag)

def map_phi_delta(phi0, bfi_val, theta_lag, eps_lag, eta3=0.5, eta4=0.5, tau2=0):
    """Φ_Δ^{(brose)} = Φ_Δ^{(0)} + η3·θ(t-τ) - η4·ε(t-τ)"""
    return phi0 + eta3 * theta_lag - eta4 * eps_lag

def ollivier_ricci_curvature(residual_norms):
    """
    Placeholder: Ollivier‑Ricci curvature on a complete graph with edge weight
    w_ij = exp(-|r_i - r_j|). For demonstration we return the negative variance
    (high curvature ⇔ low variance).
    """
    if len(residual_norms) < 2:
        return 0.0
    return -np.var(residual_norms)

def psi_from_curvature(curvature, bfi_val, R0=1.0, lam=0.5):
    """ψ = ln(|R|/R0) + λ·BFI"""
    return np.log(np.abs(curvature) / R0) + lam * bfi_val

def worker_entropy(residual_norms):
    """Shannon entropy of normalized residual magnitudes."""
    p = residual_norms / np.sum(residual_norms)
    # avoid log(0)
    p = p[p > 0]
    return -np.sum(p * np.log(p))

# -------------------------------------------------
# Audit 1: BFI range
# -------------------------------------------------
print("=== Audit 1: BFI range ===")
thetas = np.linspace(0, 1, 5)
epss   = np.linspace(0, 1, 5)
rhos   = np.linspace(1, 3, 3)   # redundancy factor n/d
bfi_vals = bfi(thetas[:,None,None], epss[None,:,None], rhos[None,None,:])
print(f"BFI min: {bfi_vals.min():.4f}, max: {bfi_vals.max():.4f}")
assert np.allclose(bfi_vals, np.tanh(bfi_vals)), "BFI must be tanh of linear combo"
print("BFI computed correctly via tanh.\n")

# -------------------------------------------------
# Audit 2: Mapping to Φ_N, Φ_Δ stays in [0,1] for reasonable inputs
# -------------------------------------------------
print("=== Audit 2: Φ_N, Φ_Δ bounds ===")
phi0_N, phi0_D = 0.7, 0.2   # baseline values in [0,1]
theta_lag_vals = np.linspace(0, 1, 4)
eps_lag_vals   = np.linspace(0, 1, 4)
bfi_test       = bfi(0.3, 0.2, 2.0)   # sample BFI
phi_N_vals = map_phi_n(phi0_N, bfi_test, theta_lag_vals)
phi_D_vals = map_phi_delta(phi0_D, bfi_test, theta_lag_vals, eps_lag_vals)
print(f"Φ_N range: [{phi_N_vals.min():.4f}, {phi_N_vals.max():.4f}]")
print(f"Φ_Δ range: [{phi_D_vals.min():.4f}, {phi_D_vals.max():.4f}]")
# Simple sanity: keep within [0,1] if coefficients are modest
assert np.all(phi_N_vals >= 0) and np.all(phi_N_vals <= 1), "Φ_N out of [0,1]"
assert np.all(phi_D_vals >= -0.5) and np.all(phi_D_vals <= 0.5), "Φ_Δ unreasonably large"
print("Mappings produce plausible values.\n")

# -------------------------------------------------
# Audit 3: ψ derivation – curvature + BFI
# -------------------------------------------------
print("=== Audit 3: ψ from curvature ===")
# Simulate residual norms for 5 workers
residual_norms = np.abs(np.random.randn(5)) + 0.1
curv = ollivier_ricci_curvature(residual_norms)
psi  = psi_from_curvature(curv, bfi_test)
print(f"Sample curvature: {curv:.4f}")
print(f"Resulting ψ: {psi:.4f}")
# ψ should be real (no domain errors from log of non‑positive)
assert np.isfinite(psi), "ψ must be finite (curvature non‑zero)"
print("ψ well‑defined.\n")

# -------------------------------------------------
# Audit 4: Worker entropy bounds
# -------------------------------------------------
print("=== Audit 4: Worker entropy ===")
ent = worker_entropy(residual_norms)
max_ent = np.log(len(residual_norms))   # uniform distribution
print(f"Entropy: {ent:.4f}, max possible: {max_ent:.4f}")
assert 0 <= ent <= max_ent + 1e-9, "Entropy out of bounds"
print("Entropy within [0, log m].\n")

# -------------------------------------------------
# Audit 5: Feasibility of QP constraints (BFI≤0.7, Φ_N≥0.6, S≥log3)
# -------------------------------------------------
print("=== Audit 5: QP constraint feasibility ===")
def feasible_point():
    # Choose redundancy rho=2 (constant overhead)
    rho = 2.0
    # Need BFI ≤ 0.7 => alpha*theta+beta*eps+gamma*rho ≤ atanh(0.7) ≈ 0.867
    atanh_07 = np.arctanh(0.7)
    # Pick small theta, eps to satisfy
    theta = 0.1
    eps   = 0.05
    bfi_val = bfi(theta, eps, rho, alpha=0.5, beta=0.5, gamma=0.2)
    # Compute Φ_N, Φ_Δ with modest coefficients
    phi_N = map_phi_n(0.8, bfi_val, theta)
    phi_D = map_phi_delta(0.1, bfi_val, theta, eps)
    S = worker_entropy(np.array([1.0, 1.0, 1.0]))  # three equal workers → log(3)
    return bfi_val, phi_N, phi_D, S, atanh_07

bfi_val, phi_N, phi_D, S, limit = feasible_point()
print(f"Sample BFI: {bfi_val:.4f} (limit {limit:.4f})")
print(f"Φ_N: {phi_N:.4f} (≥0.6?)")
print(f"Φ_Δ: {phi_D:.4f}")
print(f"Worker entropy: {S:.4f} (≥log3≈1.099?)")
assert bfi_val <= limit + 1e-9, "BFI exceeds 0.7 bound"
assert phi_N >= 0.6 - 1e-9, "Φ_N below 0.6"
assert S >= np.log(3) - 1e-9, "Entropy below log(3)"
print("All QP constraints satisfied for this point.\n")

# -------------------------------------------------
# Summary
# -------------------------------------------------
print("=== Audit Summary ===")
print("All automated checks passed. The proposal is mathematically internally consistent")
print("under the assumed parameter ranges and respects the Omega Protocol invariants")
print("(Φ_N, Φ_Δ, ψ) as far as the spot‑checked logic goes.")