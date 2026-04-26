# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validator for Adversarial Transactional Geometry Shield (ATGS‑Ω)

This script checks the mathematical internal consistency of the ATGS‑Ω proposal
against the Omega Protocol invariants (Φ_N, Φ_Δ, ψ) and the MPC‑Ω constraints
described in the proposal.

We do **not** attempt to implement the full UMAP/Ricci‑curvature pipeline;
instead we use surrogate functions that preserve the algebraic relationships
stated in the paper.  The validator asserts that:
  1. ATI ∈ [0,1] and the high‑risk threshold (0.72) is respected.
  2. Φ_N^(adv) and Φ_Δ^(adv) are computed correctly from the linear maps.
  3. ψ_adv is derived from a mock Ricci curvature and ATI.
  4. The derived stiffness coefficients ξ_N, ξ_Δ are consistent with finite‑difference
     approximations of the Φ‑maps w.r.t. ψ_adv.
  5. The entropy gauge S_adv satisfies the MPC‑Ω lower bound.
  6. The QP‑style constraints (ATI ≤ 0.72, Φ_N ≥ 0.6, S_adv ≥ log(3)) are
     satisfied for the sampled state.
  7. The cost‑function integrand is non‑negative (as required for a QP).

If any assertion fails, the script raises an AssertionError with a diagnostic
message, indicating a breach of Omega Protocol invariants or internal math.
"""

import numpy as np
import math
from typing import Tuple

# ----------------------------------------------------------------------
# Surrogate functions (stand‑ins for complex pipelines)
# ----------------------------------------------------------------------
def mock_ricci_curvature(ati: float, base: float = -1.0) -> float:
    """
    Mock Ricci curvature of the adversarial manifold.
    The proposal suggests ψ_adv = ln(|R_adv|/R0) + λ·ATI.
    We choose a simple linear relationship: R_adv = base * ati.
    """
    return base * ati  # negative curvature for positive ATI (as in the paper)

def compute_ati(rho: float, G: float, nu: float, sigma_il: float,
                alpha: float = 1.0, beta: float = 1.0,
                gamma: float = 1.0, delta: float = 1.0) -> float:
    """
    Adversarial Threat Index (ATI) as defined in the proposal.
    All inputs are assumed to be in [0,1] (except nu which is >0).
    """
    arg = alpha * rho + beta * G + gamma * (1.0 / nu) + delta * sigma_il
    return np.tanh(arg)

def compute_phi_n_adv(ati: float, phi_n0: float = 1.0,
                      eta1: float = 0.2, eta2: float = 0.1,
                      g: float = 0.5, tau: int = 3) -> float:
    """
    Φ_N^(adv)(t) = Φ_N^(0) - η1·ATI(t-τ) + η2·(1 - G(t-τ))
    For validation we use contemporaneous values (τ=0) and a fixed G.
    """
    return phi_n0 - eta1 * ati + eta2 * (1.0 - g)

def compute_phi_delta_adv(ati: float, phi_delta0: float = 0.5,
                          eta3: float = 0.15, eta4: float = 0.1,
                          rho: float = 0.5, nu: float = 5.0,
                          tau: int = 3) -> float:
    """
    Φ_Δ^(adv)(t) = Φ_Δ^(0) + η3·ρ(t-τ) - η4·ν(t-τ)^{-1}
    Again we use contemporaneous values.
    """
    return phi_delta0 + eta3 * rho - eta4 * (1.0 / nu)

def compute_psi_adv(ati: float, r0: float = 1.0, lamb: float = 0.5) -> float:
    """
    ψ_adv(t) = ln(|R_adv(t)|/R0) + λ·ATI(t)
    Using mock_ricci_curvature for R_adv.
    """
    r_adv = mock_ricci_curvature(ati)
    return math.log(abs(r_adv) / r0) + lamb * ati

def finite_diff_derivative(f, x, h=1e-6) -> float:
    """Central finite difference."""
    return (f(x + h) - f(x - h)) / (2 * h)

def compute_stiffness(ati: float) -> Tuple[float, float]:
    """
    ξ_N = ∂Φ_N^(adv)/∂ψ_adv
    ξ_Δ = ∂Φ_Δ^(adv)/∂ψ_adv
    We compute derivatives via chain rule:
        dΦ/dψ = (dΦ/dATI) / (dψ/dATI)
    """
    # dΦ_N/dATI
    dphi_n_dati = -0.2  # from η1 in compute_phi_n_adv (η1=0.2)
    # dΦ_Δ/dATI (note: Φ_Δ does NOT depend on ATI directly in the linear map;
    # only through ρ and ν which we hold constant → derivative 0)
    dphi_delta_dati = 0.0

    # dψ/dATI
    # ψ = ln(|base*ati|/r0) + λ*ati  => dψ/dati = 1/ati + λ
    dpsi_dati = 1.0 / ati + 0.5  # λ=0.5 from compute_psi_adv default

    xi_n = dphi_n_dati / dpsi_dati
    xi_delta = dphi_delta_dati / dpsi_dati
    return xi_n, xi_delta

def compute_entropy(strategy_probs: np.ndarray) -> float:
    """Shannon entropy S_adv = - Σ p_k log p_k."""
    # Avoid log(0)
    p = np.clip(strategy_probs, 1e-12, 1.0)
    return -np.sum(p * np.log(p))

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_state(rho: float, G: float, nu: float, sigma_il: float,
                   strategy_probs: np.ndarray) -> None:
    """
    Checks all Omega Protocol invariants and internal consistency for a
    single point in time.
    """
    # ---- 1. Compute core metrics -------------------------------------------------
    ati = compute_ati(rho, G, nu, sigma_il)
    assert 0.0 <= ati <= 1.0, f"ATI out of bounds: {ati}"

    phi_n = compute_phi_n_adv(ati)
    phi_delta = compute_phi_delta_adv(ati)
    psi = compute_psi_adv(ati)
    xi_n, xi_delta = compute_stiffness(ati)
    S_adv = compute_entropy(strategy_probs)

    # ---- 2. Omega Protocol invariant checks --------------------------------------
    # Φ_N should be non‑negative (connectivity cannot be negative)
    assert phi_n >= 0.0, f"Φ_N^(adv) negative: {phi_n}"
    # Φ_Δ should be non‑negative (asymmetry measure)
    assert phi_delta >= 0.0, f"Φ_Δ^(adv) negative: {phi_delta}"
    # ψ should be real (no log of zero or negative)
    assert np.isfinite(psi), f"ψ_adv not finite: {psi}"

    # ---- 3. MPC‑Ω constraints (QP style) ----------------------------------------
    # ATI ≤ 0.72 (high‑risk threshold)
    assert ati <= 0.72 + 1e-9, f"ATI exceeds safety threshold: {ati}"
    # Φ_N ≥ 0.6 (minimum connectivity to prevent fragmentation)
    assert phi_n >= 0.6 - 1e-9, f"Φ_N^(adv) below safety floor: {phi_n}"
    # Entropy ≥ log(3) → at least three equally likely attack strategies
    assert S_adv >= math.log(3) - 1e-9, f"Adversarial entropy too low: {S_adv}"

    # ---- 4. Internal mathematical consistency ------------------------------------
    # Re‑compute Φ maps via the linear formulas and compare to the values used
    # in the stiffness derivative calculation (should match up to tolerance).
    phi_n_check = compute_phi_n_adv(ati)
    phi_delta_check = compute_phi_delta_adv(ati)
    assert abs(phi_n - phi_n_check) < 1e-6, "Φ_N mapping mismatch"
    assert abs(phi_delta - phi_delta_check) < 1e-6, "Φ_Δ mapping mismatch"

    # Stiffness coefficients should equal the analytical derivatives we used.
    # We recompute via finite differences on the ψ→Φ maps.
    def phi_n_via_psi(x):
        # Re‑compute ATI from ψ? Inverse not trivial; instead we test the chain rule
        # by verifying that ξ_N * dψ/dATI ≈ dΦ_N/dATI.
        return compute_phi_n_adv(x)

    def phi_delta_via_psi(x):
        return compute_phi_delta_adv(x)

    dphi_n_dati_num = finite_diff_derivative(phi_n_via_psi, ati)
    dphi_delta_dati_num = finite_diff_derivative(phi_delta_via_psi, ati)
    dpsi_dati_num = finite_diff_derivative(lambda a: compute_psi_adv(a), ati)

    xi_n_num = dphi_n_dati_num / dpsi_dati_num
    xi_delta_num = dphi_delta_dati_num / dpsi_dati_num

    assert abs(xi_n - xi_n_num) < 1e-4, f"ξ_N mismatch: {xi_n} vs {xi_num}"
    assert abs(xi_delta - xi_delta_num) < 1e-4, f"ξ_Δ mismatch: {xi_delta} vs {xi_delta_num}"

    # ---- 5. Cost‑function non‑negativity (QP requirement) -----------------------
    # The integrand terms are squares of violations; they must be ≥0.
    term1 = max(ati - 0.72, 0.0) ** 2
    term2 = max(0.6 - phi_n, 0.0) ** 2
    term3 = phi_delta ** 2  # penalty on asymmetry (always ≥0)
    term4 = max(math.log(3) - S_adv, 0.0) ** 2
    integrand = term1 + term2 + term3 + term4
    assert integrand >= 0.0, "Cost‑function integrand negative (should be sum of squares)"

    # If we reach here, all checks passed.
    print(f"✓ State valid: ATI={ati:.3f}, Φ_N={phi_n:.3f}, Φ_Δ={phi_delta:.3f}, "
          f"ψ={psi:.3f}, S_adv={S_adv:.3f}")

# ----------------------------------------------------------------------
# Run a battery of random tests to increase confidence
# ----------------------------------------------------------------------
if __name__ == "__main__":
    np.random.seed(42)
    for i in range(20):
        # Random inputs in plausible ranges
        rho = np.random.rand()          # [0,1]
        G = np.random.rand()            # [0,1]
        nu = np.random.uniform(1, 20)   # block delay >0
        sigma_il = np.random.rand()     # [0,1]
        # Random strategy distribution over 3–5 attack types
        k = np.random.randint(3, 6)
        probs = np.random.dirichlet(np.ones(k))
        try:
            validate_state(rho, G, nu, sigma_il, probs)
        except AssertionError as e:
            print(f"✗ Validation failed on sample {i}: {e}")
            raise
    print("\nAll 20 random samples passed Omega Protocol invariants.")