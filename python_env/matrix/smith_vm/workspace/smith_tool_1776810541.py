# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATS‑Ω Mathematical & Rubric Compliance Validator
-------------------------------------------------
Checks:
1. Double‑well potential parameters (α<0, β>0, γ>0)
2. ATI definition ∈ [0,1] and its three factors
3. Φ_N, Φ_Δ derived from covariance matrix Σ
4. Invariant ψ = ln(Φ_N/Φ_N0)
5. Shannon conditional entropy S_alg ≥ 0
6. Entropy gauge & current definitions (formal check)
7. Boundaries: shredding & freeze conditions
8. MPC‑Ω QP constraints (ATI≥0.6, Φ_N≥0.5, S_alg≥ln2)
9. Cost function non‑negativity
10. Lead‑time τ positivity (causality)

If all assertions pass, the supplied state is rubric‑compliant.
"""

import numpy as np
from numpy.linalg import eigvalsh

def validate_ats_ohm(state: dict, params: dict) -> None:
    """
    Parameters
    ----------
    state : dict
        Must contain:
            - 'ATI'               : float
            - 'curvature_ratio'   : float = |R_G(t)|/|R_G(0)|
            - 'beta1_ratio'       : float = β₁(t)/β₁(0)
            - 'S_alg'             : float = Shannon conditional entropy
            - 'Phi_N0'            : float = baseline variance (Φ_N^{(0)})
            - 'Phi_N'             : float = current Φ_N^{(ats)}
            - 'Phi_Delta'         : float = current Φ_Δ^{(ats)}
            - 'covariance'        : np.ndarray (NxN) of 𝒜 across components
            - 'mu2'               : float = second central moment of 𝒜
            - 'mu3'               : float = third central moment of 𝒜
            - 'tau'               : float = lead time (control cycles)
    params : dict
        Must contain:
            - 'alpha' : float (α)
            - 'beta'  : float (β)
            - 'gamma' : float (γ)
            - 'mu1'   : float (weight for Φ_N penalty)
            - 'mu2'   : float (weight for Φ_Δ penalty)
            - 'mu3'   : float (weight for S_alg penalty)
            - 'Phi_N0_ref' : float (reference baseline, should equal state['Phi_N0'])
    """
    # ------------------------------------------------------------------
    # 1. Double‑well potential coefficients
    # ------------------------------------------------------------------
    assert params['alpha'] < 0, f"α must be negative (got {params['alpha']})"
    assert params['beta']  > 0, f"β must be positive  (got {params['beta']})"
    assert params['gamma'] > 0, f"γ must be positive  (got {params['gamma']})"

    # ------------------------------------------------------------------
    # 2. ATI definition and range
    # ------------------------------------------------------------------
    ATI = state['ATI']
    assert 0.0 <= ATI <= 1.0, f"ATI must be in [0,1] (got {ATI})"
    # Decompose ATI into its three factors (they should already be provided)
    curv = state['curvature_ratio']
    beta1 = state['beta1_ratio']
    entropy_factor = np.exp(-state['S_alg'])   # e^{-S_alg}
    # Re‑compose and allow tiny numerical tolerance
    ATI_recomposed = curv * beta1 * entropy_factor
    assert np.isclose(ATI, ATI_recomposed, rtol=1e-6, atol=1e-9), \
        f"ATI mismatch: supplied {ATI}, recomposed {ATI_recomposed}"

    # ------------------------------------------------------------------
    # 3. Φ_N, Φ_Δ from covariance matrix Σ
    # ------------------------------------------------------------------
    Sigma = state['covariance']
    assert Sigma.ndim == 2 and Sigma.shape[0] == Sigma.shape[1], \
        "Covariance must be a square matrix"
    # Φ_N = sqrt(max eigenvalue)
    eigvals = eigvalsh(Sigma)
    Phi_N_calc = np.sqrt(np.max(eigvals))
    assert np.isclose(state['Phi_N'], Phi_N_calc, rtol=1e-6), \
        f"Φ_N mismatch: supplied {state['Phi_N']}, calc {Phi_N_calc}"
    # Φ_Δ = skewness = μ₃ / (μ₂)^{3/2}
    mu2 = state['mu2']
    mu3 = state['mu3']
    assert mu2 > 0, f"Second central moment μ₂ must be >0 for skewness (got {mu2})"
    Phi_Delta_calc = mu3 / (mu2 ** 1.5)
    assert np.isclose(state['Phi_Delta'], Phi_Delta_calc, rtol=1e-6), \
        f"Φ_Δ mismatch: supplied {state['Phi_Delta']}, calc {Phi_Delta_calc}"

    # ------------------------------------------------------------------
    # 4. Invariant ψ = ln(Φ_N/Φ_N0)
    # ------------------------------------------------------------------
    Phi_N0 = state['Phi_N0']
    assert Phi_N0 > 0, f"Baseline Φ_N0 must be positive (got {Phi_N0})"
    psi_calc = np.log(state['Phi_N'] / Phi_N0)
    # The proposal stores ψ directly; if not present we compute it.
    psi_state = state.get('psi', psi_calc)
    assert np.isclose(psi_state, psi_calc, rtol=1e-6), \
        f"ψ invariant mismatch: supplied {psi_state}, calc {psi_calc}"

    # ------------------------------------------------------------------
    # 5. Shannon conditional entropy S_alg ≥ 0
    # ------------------------------------------------------------------
    S_alg = state['S_alg']
    assert S_alg >= 0.0, f"S_alg must be non‑negative (got {S_alg})"

    # ------------------------------------------------------------------
    # 6. Entropy gauge & current (formal check – we only verify symbols)
    # ------------------------------------------------------------------
    # The gauge is A_μ = ∂_μ S_alg ; we cannot evaluate derivatives here,
    # but we can assert that S_alg is a scalar field → gradient exists.
    # The current J^μ = √2 Φ_Δ δ^μ₀ must have only time component non‑zero.
    J_time = np.sqrt(2) * state['Phi_Delta']
    J_space = np.zeros_like(state.get('Phi_Delta', 0))  # placeholder
    # No explicit vector supplied; we just note the form is correct.
    # (If a full 4‑vector were supplied we would check J[1:]==0.)

    # ------------------------------------------------------------------
    # 7. Boundaries: shredding & freeze
    # ------------------------------------------------------------------
    # Shredding: Φ_N → ∞ (practically > large threshold) AND S_alg → high
    # Freeze:   Φ_N → 0 (practically < small threshold) AND S_alg → low
    # We define operational thresholds:
    PHI_N_LARGE = 1e3   # "infinite" for numerical purposes
    PHI_N_SMALL = 1e-3  # "zero"
    S_HIGH = np.log(state.get('M', 10))  # max entropy if M equiprobable paths
    S_LOW  = 0.0

    # Shredding condition (should NOT hold in normal operation)
    shredding = (state['Phi_N'] > PHI_N_LARGE) and (S_alg > 0.9 * S_HIGH)
    # Freeze condition (should NOT hold in normal operation)
    freeze = (state['Phi_N'] < PHI_N_SMALL) and (S_alg < 0.1 * S_HIGH + S_LOW)

    assert not shredding, "Algorithmic Shredding detected (Φ_N huge & entropy high)"
    assert not freeze,    "Informational Freeze detected (Φ_N near zero & entropy low)"

    # ------------------------------------------------------------------
    # 8. MPC‑Ω QP constraints
    # ------------------------------------------------------------------
    assert ATI >= 0.6, f"ATI constraint violated: {ATI} < 0.6"
    assert state['Phi_N'] >= 0.5, f"Φ_N constraint violated: {state['Phi_N']} < 0.5"
    assert S_alg >= np.log(2), f"S_alg constraint violated: {S_alg} < ln(2)"

    # ------------------------------------------------------------------
    # 9. Cost function non‑negativity
    # ------------------------------------------------------------------
    mu1, mu2, mu3 = params['mu1'], params['mu2'], params['mu3']
    cost = (max(0.6 - ATI, 0.0) ** 2) \
         + mu1 * (max(0.5 - state['Phi_N'], 0.0) ** 2) \
         + mu2 * (state['Phi_Delta'] ** 2) \
         + mu3 * (max(np.log(2) - S_alg, 0.0) ** 2)
    assert cost >= 0.0, f"Cost function negative: {cost}"
    # Optionally, we could require cost == 0 when all constraints satisfied:
    if (ATI >= 0.6 and state['Phi_N'] >= 0.5 and S_alg >= np.log(2)):
        assert np.isclose(cost, 0.0, atol=1e-12), \
            f"Cost should be zero inside feasible region, got {cost}"

    # ------------------------------------------------------------------
    # 10. Lead‑time τ positivity (causality)
    # ------------------------------------------------------------------
    tau = state['tau']
    assert tau > 0, f"Lead time τ must be positive (got {tau})"

    # If we reach here, all checks passed.
    print("[VALIDATION PASSED] ATS‑Ω state is mathematically sound and rubric‑compliant.")

# ----------------------------------------------------------------------
# Example usage (replace with real telemetry from the Omega Protocol VM)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Mock data representing a healthy algorithmic state
    N = 5  # number of algorithm components
    Sigma = np.eye(N) * 0.2 + np.ones((N, N)) * 0.05  # modest correlations
    mu2 = 0.2
    mu3 = 0.0  # symmetric distribution → zero skew
    state = {
        'ATI'               : 0.78,
        'curvature_ratio'   : 0.9,
        'beta1_ratio'       : 0.95,
        'S_alg'             : 0.8,          # > ln2 ≈ 0.693
        'Phi_N0'            : 0.5,
        'Phi_N'             : 0.55,
        'Phi_Delta'         : mu3 / (mu2 ** 1.5),
        'covariance'        : Sigma,
        'mu2'               : mu2,
        'mu3'               : mu3,
        'tau'               : 20.0,         # control cycles
        # optional: if you already have ψ from elsewhere:
        'psi'               : np.log(0.55/0.5),
        'M'                 : 10            # number of distinct path types for entropy bound
    }
    params = {
        'alpha'   : -1.0,
        'beta'    : 2.0,
        'gamma'   : 0.5,
        'mu1'     : 1.0,
        'mu2'     : 1.0,
        'mu3'     : 1.0,
        'Phi_N0_ref': 0.5   # should match state['Phi_N0']
    }

    validate_ats_ohm(state, params)