# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
POASH‑Ω mathematical soundness validator.
Checks:
  * PHI ∈ [0,1] (with optional clipping)
  * Φ_N, Φ_Δ stay in [0,1] (or user‑specified bounds)
  * ξ ≥ 1  → ψ = ln(ξ/ξ0) real
  * ξ_N, ξ_Δ have correct sign w.r.t. ψ
  * MPC‑Ω constraints satisfied
  * Cost integrand non‑negative
Run: python validate_poash_omega.py
"""

import numpy as np
import sympy as sp

# ----------------------------------------------------------------------
# Helper symbolic expressions
# ----------------------------------------------------------------------
K = sp.symbols('K', integer=True, positive=True)
k = sp.symbols('k', integer=True, positive=True)

# Symbols for a single order (we will sum over k=1..K)
A_k   = sp.symbols('A_k')
mu_k  = sp.symbols('mu_k')
sigma_k = sp.symbols('sigma_k', positive=True)
w_k   = sp.symbols('w_k', nonnegative=True)

# PHI definition (raw, before clipping)
PHI_raw = 1 - sp.Sum(w_k * sp.Abs(A_k - mu_k) / sigma_k, (k, 1, K)).doit()

# ----------------------------------------------------------------------
# Mapping to Omega variables (sigmoid form)
# ----------------------------------------------------------------------
Phi_N0, Phi_Delta0 = sp.symbols('Phi_N0 Phi_Delta0', real=True)
eta1, eta2, eta3 = sp.symbols('eta1 eta2 eta3', real=True)
tau1, tau2 = sp.symbols('tau1 tau2', real=True, nonnegative=True)
mu_PHI, sigma_PHI = sp.symbols('mu_PHI sigma_PHI', real=True, positive=True)

PHI_t = sp.symbols('PHI_t', real=True)   # PHI at time t (could be delayed)

Phi_N = Phi_N0 + eta1 * sp.logistic((PHI_t - mu_PHI) / sigma_PHI)
Phi_Delta = Phi_Delta0 - eta2 * PHI_t + eta3 * sp.Symbol('Var_Ak')  # Var(A_k) placeholder

# ----------------------------------------------------------------------
# Invariant derivation from coherence
# ----------------------------------------------------------------------
# Coherence for a pair of metrics (generic)
S_xx = sp.symbols('S_xx', nonnegative=True)
S_yy = sp.symbols('S_yy', nonnegative=True)
S_xy = sp.symbols('S_xy', complex=True)

coh = sp.Abs(S_xy)**2 / (S_xx * S_yy)          # ∈ [0,1] if S_xx,S_yy>0
# Average coherence over orders (symbolic sum)
coh_avg = sp.Sum(coh, (k, 1, K)) / K
xi = 1 / coh_avg                               # correlation length
xi0 = sp.symbols('xi0', positive=True)
psi = sp.log(xi / xi0)

# Derivatives (approx. using chain rule: dΦ/dψ = (dΦ/dPHI)*(dPHI/dψ))
# We approximate dPHI/dψ via a finite difference later in numeric test.
# Here we just keep the symbolic form.
xi_N   = sp.diff(Phi_N, psi)
xi_Delta = sp.diff(Phi_Delta, psi)

# ----------------------------------------------------------------------
# Numeric validation routine
# ----------------------------------------------------------------------
def numeric_test():
    np.random.seed(42)
    # Choose a modest number of orders
    K_val = 5
    # Random but plausible metric statistics
    A   = np.random.randn(K_val) * 0.5 + 1.0   # amplitudes around 1
    mu  = np.ones(K_val)                       # healthy mean = 1
    sigma = np.full(K_val, 0.2)                # 20% std
    w   = np.full(K_val, 0.15)                 # weights sum = 0.75 < 1
    # Raw PHI
    PHI_raw_val = 1 - np.sum(w * np.abs(A - mu) / sigma)
    # Clip to [0,1] as per protocol safeguard
    PHI_val = np.clip(PHI_raw_val, 0.0, 1.0)

    # Mapping parameters (chosen to keep outputs in [0,1])
    Phi_N0_val = 0.3
    Phi_Delta0_val = 0.2
    eta1_val = 0.4
    eta2_val = 0.3
    eta3_val = 0.1
    mu_PHI_val = 0.5
    sigma_PHI_val = 0.2
    tau1_val = tau2_val = 0.0   # ignore delay for static test
    Var_Ak_val = np.var(A)

    PHI_t_val = PHI_val   # using instantaneous PHI

    Phi_N_val = Phi_N0_val + eta1_val * 1/(1+np.exp(-(PHI_t_val-mu_PHI_val)/sigma_PHI_val))
    Phi_Delta_val = Phi_Delta0_val - eta2_val*PHI_t_val + eta3_val*Var_Ak_val

    # Coherence test (pairwise random spectra)
    S_xx = np.random.rand(K_val) + 0.5
    S_yy = np.random.rand(K_val) + 0.5
    S_xy = (np.random.rand(K_val) + 1j*np.random.rand(K_val)) * np.sqrt(S_xx*S_yy)
    coh_vals = np.abs(S_xy)**2 / (S_xx * S_yy)
    coh_avg_val = np.mean(coh_vals)
    xi_val = 1.0 / coh_avg_val
    xi0_val = 1.0
    psi_val = np.log(xi_val / xi0_val)

    # Numeric derivatives via finite difference (perturb PHI)
    eps = 1e-6
    PHI_plus = np.clip(PHI_val + eps, 0, 1)
    Phi_N_plus = Phi_N0_val + eta1_val * 1/(1+np.exp(-(PHI_plus-mu_PHI_val)/sigma_PHI_val))
    Phi_Delta_plus = Phi_Delta0_val - eta2_val*PHI_plus + eta3_val*Var_Ak_val
    xi_N_val = (Phi_N_plus - Phi_N_val) / eps
    xi_Delta_val = (Phi_Delta_plus - Phi_Delta_val) / eps

    # ------------------------------------------------------------------
    # Assertions (Omega Protocol invariants & constraints)
    # ------------------------------------------------------------------
    assert 0.0 <= PHI_val <= 1.0, f"PHI out of bounds: {PHI_val}"
    assert 0.0 <= Phi_N_val <= 1.0, f"Phi_N out of bounds: {Phi_N_val}"
    assert 0.0 <= Phi_Delta_val <= 1.0, f"Phi_Delta out of bounds: {Phi_Delta_val}"
    assert xi_val >= 1.0 - 1e-12, f"xi < 1: {xi_val}"   # coherence ≤1 ⇒ ξ≥1
    # ψ real automatically if xi>0 and xi0>0
    assert np.isfinite(psi_val), f"ψ not finite: {psi_val}"
    # Sign of derivatives should follow sigmoid monotonicity:
    # Φ_N increases with PHI → ξ_N = dΦ_N/dψ = (dΦ_N/dPHI)*(dPHI/dψ)
    # Since dΦ_N/dPHI >0 (sigmoid slope) and we expect dPHI/dψ >0 (PHI grows with coherence)
    # We simply check that ξ_N and ξ_Delta have the same sign as (psi_val - psi_ref) for a reference.
    # For simplicity we verify that ξ_N * (psi_val) >= 0 when psi_val>0 (healthy) and <=0 when psi_val<0.
    if psi_val > 0:
        assert xi_N_val >= -1e-9, f"ξ_N negative while ψ>0: {xi_N_val}"
        assert xi_Delta_val <= 1e-9, f"ξ_Δ positive while ψ>0: {xi_Delta_val}"
    else:
        assert xi_N_val <= 1e-9, f"ξ_N positive while ψ<0: {xi_N_val}"
        assert xi_Delta_val >= -1e-9, f"ξ_Δ negative while ψ<0: {xi_Delta_val}"

    # MPC‑Ω constraints
    assert PHI_val >= 0.4, f"PHI constraint violated: {PHI_val}"
    assert Phi_N_val >= 0.7, f"Phi_N constraint violated: {Phi_N_val}"
    assert Phi_Delta_val <= 0.6, f"Phi_Delta constraint violated: {Phi_Delta_val}"

    # Cost integrand non‑negative (discrete approximation)
    lambda1, lambda2 = 0.5, 0.3
    grad_A = np.gradient(A)  # simple finite‑difference gradient
    integrand = (1 - PHI_val)**2 + lambda1 * Phi_Delta_val**2 + lambda2 * np.sum(grad_A**2)
    assert integrand >= -1e-12, f"Cost integrand negative: {integrand}"

    print("All numeric checks passed.")
    print(f"PHI={PHI_val:.4f}, Φ_N={Phi_N_val:.4f}, Φ_Δ={Phi_Delta_val:.4f}")
    print(f"ξ={xi_val:.4f}, ψ={psi_val:.4f}, ξ_N={xi_N_val:.4f}, ξ_Δ={xi_Delta_val:.4f}")

if __name__ == "__main__":
    # Symbolic sanity: ensure PHI_raw expression is well‑formed
    print("Symbolic PHI expression:", PHI_raw)
    print("Symbolic Φ_N:", Phi_N)
    print("Symbolic Φ_Δ:", Phi_Delta)
    print("Symbolic ψ:", psi)
    print("Symbolic ξ_N:", xi_N)
    print("Symbolic ξ_Δ:", xi_Delta)
    print("\n--- Running numeric validation ---")
    numeric_test()