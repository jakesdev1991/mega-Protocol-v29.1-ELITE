# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the Byzantine-Resilient Omega Computation (BROC-Ω) proposal.
Checks mathematical consistency and adherence to the Omega Protocol invariants:
    • Φ_N ≥ 0.6   (strategic connectivity lower bound)
    • Φ_Δ ≤ 0.7   (information asymmetry upper bound)
    • κ = t/m ∈ [0, 0.5]   (maximum tolerable corrupt fraction)
    • overhead ≥ 0
    • κ ≥ κ_min, overhead ≤ overhead_max
    • Cost function terms are non‑negative
    • Encoding overhead relation: n' = n + 2t  (for tolerance t)
"""

import numpy as np

def validate_broc(
    m: int,               # total number of worker nodes
    t: int,               # number of Byzantine workers we aim to tolerate
    n: int,               # original data dimension (rows of X)
    Phi_N0: float,        # baseline strategic connectivity
    Phi_Delta0: float,    # baseline information asymmetry
    kappa0: float,        # nominal tolerable corrupt fraction (design target)
    eta1: float, eta2: float, eta3: float, eta4: float,
    overhead: float,      # normalized extra communication/computation cost
    kappa_min: float,     # minimum allowed κ from MPC‑Ω constraints
    overhead_max: float,  # maximum allowed overhead from MPC‑Ω constraints
    lambda1: float, lambda2: float   # weights in the MPC‑Ω cost function
) -> bool:
    """
    Returns True if all checks pass, raises AssertionError with a descriptive
    message otherwise.
    """
    # ------------------------------------------------------------------
    # 1. Basic feasibility of the Byzantine tolerance claim
    # ------------------------------------------------------------------
    assert 0 <= t <= m, f"t ({t}) must be between 0 and m ({m})"
    max_t_theory = (m - 1) // 2          # floor((m-1)/2) from the paper
    assert t <= max_t_theory, (
        f"t={t} exceeds the information‑theoretic bound "
        f"⌊(m-1)/2⌋ = {max_t_theory} for m={m}"
    )
    # κ definition
    kappa = t / m
    assert 0.0 <= kappa <= 0.5, f"κ = t/m = {kappa} must lie in [0, 0.5]"
    # ------------------------------------------------------------------
    # 2. Encoding dimension check (n' = n + 2t)
    # ------------------------------------------------------------------
    n_prime = n + 2 * t
    assert n_prime >= n, f"Encoded dimension n'={n_prime} must be ≥ original n={n}"
    # ------------------------------------------------------------------
    # 3. Overhead non‑negativity and MPC‑Ω bounds
    # ------------------------------------------------------------------
    assert overhead >= 0.0, f"Overhead must be non‑negative, got {overhead}"
    assert kappa >= kappa_min, f"κ={kappa} < κ_min={kappa_min}"
    assert overhead <= overhead_max, f"Overhead={overhead} > overhead_max={overhead_max}"
    # ------------------------------------------------------------------
    # 4. BROC‑Ω mapping to Φ_N and Φ_Δ
    # ------------------------------------------------------------------
    Phi_N_broc = Phi_N0 - eta1 * (kappa0 - kappa) + eta2 * overhead
    Phi_Delta_broc = Phi_Delta0 + eta3 * (kappa0 - kappa) - eta4 * overhead
    # Omega Protocol invariants
    assert Phi_N_broc >= 0.6, (
        f"Φ_N^(broc) = {Phi_N_broc:.4f} violates lower bound 0.6"
    )
    assert Phi_Delta_broc <= 0.7, (
        f"Φ_Δ^(broc) = {Phi_Delta_broc:.4f} violates upper bound 0.7"
    )
    # ------------------------------------------------------------------
    # 5. Cost function terms (should be non‑negative)
    # ------------------------------------------------------------------
    term_kappa = lambda1 * (kappa0 - kappa) ** 2
    term_overhead = lambda2 * overhead ** 2
    assert term_kappa >= 0.0, f"κ‑term negative: {term_kappa}"
    assert term_overhead >= 0.0, f"overhead‑term negative: {term_overhead}"
    # Optional: total cost non‑negative (trivially true if weights ≥0)
    assert lambda1 >= 0.0 and lambda2 >= 0.0, "λ₁, λ₂ must be non‑negative"
    # ------------------------------------------------------------------
    # 6. Internal consistency: if overhead = 0 and κ = κ0 → Φ unchanged
    # ------------------------------------------------------------------
    if np.isclose(overhead, 0.0) and np.isclose(kappa, kappa0):
        assert np.isclose(Phi_N_broc, Phi_N0), (
            f"With zero overhead and κ=κ0, Φ_N should stay {Phi_N0}, got {Phi_N_broc}"
        )
        assert np.isclose(Phi_Delta_broc, Phi_Delta0), (
            f"With zero overhead and κ=κ0, Φ_Δ should stay {Phi_Delta0}, got {Phi_Delta_broc}"
        )
    # ------------------------------------------------------------------
    # All checks passed
    # ------------------------------------------------------------------
    return True


# ----------------------------------------------------------------------
# Example usage with plausible numbers (feel free to modify)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # System parameters
    m = 9                     # total workers
    t = 3                     # we aim to tolerate up to 3 Byzantine workers
    n = 1000                  # original data rows (e.g., time points)

    # Baseline Omega variables
    Phi_N0 = 0.68
    Phi_Delta0 = 0.55

    # Design targets
    kappa0 = 1/3              # nominal tolerable fraction (≈0.333)
    eta1, eta2, eta3, eta4 = 0.1, 0.05, 0.12, 0.07

    # Overhead from encoding (for t=m/3 we expect constant overhead → small)
    overhead = 0.04           # 4% extra cost

    # MPC‑Ω constraints
    kappa_min = 0.2
    overhead_max = 0.15

    # Cost‑function weights
    lambda1, lambda2 = 1.0, 0.5

    try:
        ok = validate_broc(
            m, t, n, Phi_N0, Phi_Delta0, kappa0,
            eta1, eta2, eta3, eta4, overhead,
            kappa_min, overhead_max, lambda1, lambda2
        )
        if ok:
            print("✅ BROC-Ω mathematical formulation passes all Omega‑Protocol checks.")
    except AssertionError as e:
        print("❌ Validation failed:")
        print(e)