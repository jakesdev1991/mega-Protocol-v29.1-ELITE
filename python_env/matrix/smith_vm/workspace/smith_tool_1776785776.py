# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for Byzantine-Resilient Omega Computation (BROC-Ω)
Checks mathematical soundness and compliance with Omega Protocol invariants:
    • Φ_N ∈ [0,1] (strategic connectivity)
    • Φ_Δ ∈ [0,1] (information asymmetry)
    • Protocol constraints: Φ_N ≥ 0.6, Φ_Δ ≤ 0.7
    • Resilience invariant κ = t/m ∈ [0, 0.5] (max tolerable corrupt fraction)
    • Overhead ≥ 0 and ≤ overhead_max
    • Cost‑function terms are non‑negative
"""

import numpy as np

def broc_phi_n(phi_n0: float, eta1: float, eta2: float,
               kappa0: float, kappa: float, overhead: float) -> float:
    """
    Φ_N^{(broc)} = Φ_N^{(0)} - η1·(κ0 - κ) + η2·overhead
    """
    return phi_n0 - eta1 * (kappa0 - kappa) + eta2 * overhead

def broc_phi_delta(phi_d0: float, eta3: float, eta4: float,
                   kappa0: float, kappa: float, overhead: float) -> float:
    """
    Φ_Δ^{(broc)} = Φ_Δ^{(0)} + η3·(κ0 - κ) - η4·overhead
    """
    return phi_d0 + eta3 * (kappa0 - kappa) - eta4 * overhead

def validate_broc_params(params: dict) -> bool:
    """
    Enforce Omega Protocol invariants and BROC‑Ω consistency rules.
    Returns True if all checks pass, raises AssertionError with details otherwise.
    """
    # ---- Unpack -------------------------------------------------
    phi_n0   = params.get('phi_n0', 0.7)   # baseline strategic connectivity
    phi_d0   = params.get('phi_d0', 0.4)   # baseline information asymmetry
    eta1     = params.get('eta1', 0.1)
    eta2     = params.get('eta2', 0.05)
    eta3     = params.get('eta3', 0.1)
    eta4     = params.get('eta4', 0.05)
    kappa0   = params.get('kappa0', 1/3)   # nominal tolerable corrupt fraction
    kappa    = params.get('kappa', 0.3)    # actual tolerable fraction
    overhead = params.get('overhead', 0.2) # normalized extra cost
    kappa_min= params.get('kappa_min', 0.0)
    overhead_max = params.get('overhead_max', 0.5)

    # ---- Basic domain checks ------------------------------------
    assert 0.0 <= phi_n0   <= 1.0, f"Baseline Φ_N out of [0,1]: {phi_n0}"
    assert 0.0 <= phi_d0   <= 1.0, f"Baseline Φ_Δ out of [0,1]: {phi_d0}"
    assert 0.0 <= kappa0   <= 0.5, f"Nominal κ0 must be ≤0.5 (Byzantine bound): {kappa0}"
    assert kappa_min <= kappa <= 0.5, f"Actual κ must be in [κ_min,0.5]: {kappa}"
    assert 0.0 <= overhead <= overhead_max, f"Overhead must be in [0,overhead_max]: {overhead}"
    assert eta1 >= 0 and eta2 >= 0 and eta3 >= 0 and eta4 >= 0, "Eta coefficients must be non‑negative"

    # ---- Compute BROC‑Ω variables -------------------------------
    phi_n_broc = broc_phi_n(phi_n0, eta1, eta2, kappa0, kappa, overhead)
    phi_d_broc = broc_phi_delta(phi_d0, eta3, eta4, kappa0, kappa, overhead)

    # ---- Omega Protocol invariant constraints -------------------
    assert 0.0 <= phi_n_broc <= 1.0, f"Computed Φ_N^{(broc)} out of [0,1]: {phi_n_broc}"
    assert 0.0 <= phi_d_broc <= 1.0, f"Computed Φ_Δ^{(broc)} out of [0,1]: {phi_d_broc}"
    assert phi_n_broc >= 0.6, f"Φ_N^{(broc)} violates Ω constraint Φ_N ≥ 0.6: {phi_n_broc}"
    assert phi_d_broc <= 0.7, f"Φ_Δ^{(broc)} violates Ω constraint Φ_Δ ≤ 0.7: {phi_d_broc}"

    # ---- Cost‑function non‑negativity ---------------------------
    # J = (1-Φ_N)^2 + Φ_Δ^2 + λ1·(κ0-κ)^2 + λ2·overhead^2
    lam1 = params.get('lambda1', 1.0)
    lam2 = params.get('lambda2', 1.0)
    J = (1 - phi_n_broc)**2 + phi_d_broc**2 \
        + lam1 * (kappa0 - kappa)**2 + lam2 * overhead**2
    assert J >= 0, f"Cost function J must be non‑negative: {J}"

    # ---- Monotonicity sanity (optional but insightful) ---------
    # Increasing κ (more tolerance) should not decrease Φ_N when η1,η2≥0
    # (because -η1·(κ0-κ) grows with κ)
    phi_n_plus = broc_phi_n(phi_n0, eta1, eta2, kappa0, min(kappa+0.05,0.5), overhead)
    assert phi_n_plus >= phi_n_broc - 1e-9, \
        f"Φ_N should not decrease with higher κ: {phi_n_broc} → {phi_n_plus}"

    # Increasing overhead should increase Φ_N and decrease Φ_Δ (by construction)
    phi_n_over = broc_phi_n(phi_n0, eta1, eta2, kappa0, kappa, min(overhead+0.05, overhead_max))
    phi_d_over = broc_phi_delta(phi_d0, eta3, eta4, kappa0, kappa, min(overhead+0.05, overhead_max))
    assert phi_n_over >= phi_n_broc - 1e-9, \
        f"Φ_N should not decrease with higher overhead: {phi_n_broc} → {phi_n_over}"
    assert phi_d_over <= phi_d_broc + 1e-9, \
        f"Φ_Δ should not increase with higher overhead: {phi_d_broc} → {phi_d_over}"

    # All checks passed
    return True

# -----------------------------------------------------------------
# Example usage – feel free to tweak parameters to stress‑test the model
if __name__ == "__main__":
    test_cases = [
        # nominal case
        dict(phi_n0=0.7, phi_d0=0.4, eta1=0.1, eta2=0.05,
             eta3=0.1, eta4=0.05, kappa0=1/3, kappa=0.3,
             overhead=0.2, kappa_min=0.0, overhead_max=0.5,
             lambda1=1.0, lambda2=1.0),
        # high threat (lower κ)
        dict(phi_n0=0.65, phi_d0=0.45, eta1=0.2, eta2=0.07,
             eta3=0.2, eta4=0.07, kappa0=0.4, kappa=0.15,
             overhead=0.3, kappa_min=0.0, overhead_max=0.6,
             lambda1=2.0, lambda2=0.5),
        # low overhead, high tolerance
        dict(phi_n0=0.8, phi_d0=0.3, eta1=0.05, eta2=0.02,
             eta3=0.05, eta4=0.02, kappa0=0.33, kappa=0.4,
             overhead=0.05, kappa_min=0.1, overhead_max=0.4,
             lambda1=0.5, lambda2=2.0),
    ]

    for i, tc in enumerate(test_cases, 1):
        try:
            if validate_broc_params(tc):
                print(f"Test case {i}: ✅ PASSED")
        except AssertionError as e:
            print(f"Test case {i}: ❌ FAILED – {e}")