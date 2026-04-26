# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Ω‑Protocol compliance validator for the AMMHM‑Ω proposal.
Checks:
  - HFI ∈ [0,1]
  - Φ_N, Φ_Δ ∈ [0,1] (normalised Ω‑variables)
  - ψ_amm real (log argument > 0)
  - ξ_N, ξ_Δ real (finite‑difference derivatives)
  - S_amm ≥ 0 (entropy non‑negative)
  - MPC‑Ω QP constraints
  - Cost‑function terms non‑negative
"""

import math
import numpy as np

def validate_ammhm(params):
    """
    params: dict with the following keys (all scalars or 1‑D arrays):
        kappa          : manifold curvature scalar (can be + or -)
        sigma_IL       : impermanent‑loss dispersion (>=0)
        C              : reserve concentration HHI (in [0,1])
        s              : slippage skewness (real)
        alpha,beta,gamma,delta : HFI weights (>=0)
        PhiN0, PhiDelta0 : baseline Ω‑variables (in [0,1])
        eta1,eta2,eta3,eta4 : mapping coefficients (real)
        tau            : lead time (days, >=0)
        R_amm          : Ricci scalar of AMM manifold (real, !=0)
        R0             : reference curvature scale (>0)
        lam            : lambda coupling in ψ (real)
        # For stiffness we need ψ at t and t-Δt; we approximate with a small Δ
        delta_psi      : small perturbation to ψ for FD (default 1e-6)
        S_amm          : Shannon conditional entropy (real)
        # MPC‑Ω QP constraint tolerances
        eps            : numerical tolerance (default 1e-9)
    """
    eps = params.get('eps', 1e-9)

    # ---- 1. HFI -------------------------------------------------
    alpha = params['alpha']
    beta  = params['beta']
    gamma = params['gamma']
    delta = params['delta']
    for w in (alpha, beta, gamma, delta):
        assert w >= -eps, f"Weight {w} must be non‑negative"
    inner = alpha * abs(params['kappa']) + beta * params['sigma_IL'] \
            + gamma * params['C'] + delta * params['s']
    assert inner >= -eps, "Inner sum for HFI must be non‑negative"
    HFI = math.tanh(inner)
    assert 0 - eps <= HFI <= 1 + eps, f"HFI={HFI} not in [0,1]"
    # Clamp to [0,1] for downstream use
    HFI = max(0.0, min(1.0, HFI))

    # ---- 2. Φ_N, Φ_Δ mapping ------------------------------------
    PhiN0 = params['PhiN0']
    PhiD0 = params['PhiDelta0']
    assert 0 - eps <= PhiN0 <= 1 + eps and 0 - eps <= PhiD0 <= 1 + eps, \
        "Baseline Ω‑variables must be in [0,1]"
    eta1, eta2, eta3, eta4 = params['eta1'], params['eta2'], params['eta3'], params['eta4']
    tau = params['tau']
    assert tau >= -eps, "Lead time τ must be non‑negative"
    # Use HFI at (t‑τ); for simplicity we assume stationarity → same HFI
    PhiN = PhiN0 - eta1 * HFI + eta2 * (1.0 - params['C'])
    PhiD = PhiD0 + eta3 * params['s'] - eta4 * abs(params['kappa'])
    assert 0 - eps <= PhiN <= 1 + eps, f"Φ_N={PhiN} out of [0,1]"
    assert 0 - eps <= PhiD <= 1 + eps, f"Φ_Δ={PhiD} out of [0,1]"

    # ---- 3. Invariant ψ -----------------------------------------
    R_amm = params['R_amm']
    R0    = params['R0']
    assert R0 > eps, "Reference curvature R0 must be >0"
    assert abs(R_amm) > eps, "Ricci scalar R_amm must be non‑zero for log"
    lam = params['lam']
    psi = math.log(abs(R_amm) / R0) + lam * HFI
    # ψ is real by construction; just ensure no NaN
    assert not math.isnan(psi), "ψ resulted in NaN"

    # ---- 4. Stiffness coefficients (finite‑difference) -----------
    dpsi = params.get('delta_psi', 1e-6)
    # Φ_N(ψ±dψ) using same linear mapping (keeping other vars fixed)
    PhiN_plus  = PhiN0 - eta1 * math.tanh(inner) + eta2 * (1.0 - params['C'])  # HFI unchanged if inner unchanged
    PhiN_minus = PhiN_plus  # In this simple linearisation HFI does not depend on ψ directly;
                            # therefore derivative is zero – we keep the formula generic.
    # To have a non‑zero test we perturb inner via κ (which influences ψ via HFI)
    # We'll compute derivative numerically by perturbing κ slightly.
    kappa = params['kappa']
    kappa_p = kappa + dpsi
    kappa_m = kappa - dpsi
    inner_p = alpha * abs(kappa_p) + beta * params['sigma_IL'] \
              + gamma * params['C'] + delta * params['s']
    inner_m = alpha * abs(kappa_m) + beta * params['sigma_IL'] \
              + gamma * params['C'] + delta * params['s']
    HFI_p = math.tanh(inner_p)
    HFI_m = math.tanh(inner_m)
    PhiN_p = PhiN0 - eta1 * HFI_p + eta2 * (1.0 - params['C'])
    PhiN_m = PhiN0 - eta1 * HFI_m + eta2 * (1.0 - params['C'])
    xi_N = (PhiN_p - PhiN_m) / (2 * dpsi)
    assert not (math.isnan(xi_N) or math.isinf(xi_N)), "ξ_N not a real number"

    # Φ_Δ derivative (similar)
    PhiD_p = PhiD0 + eta3 * params['s'] - eta4 * abs(kappa_p)
    PhiD_m = PhiD0 + eta3 * params['s'] - eta4 * abs(kappa_m)
    xi_D = (PhiD_p - PhiD_m) / (2 * dpsi)
    assert not (math.isnan(xi_D) or math.isinf(xi_D)), "ξ_Δ not a real number"

    # ---- 5. Entropy gauge ----------------------------------------
    S_amm = params['S_amm']
    assert S_amm >= -eps, f"Entropy S_amm={S_amm} negative"
    # ---- 6. MPC‑Ω QP constraints ---------------------------------
    assert HFI <= 0.68 + eps, f"HFI={HFI} exceeds 0.68 bound"
    assert PhiN >= 0.6 - eps, f"Φ_N={PhiN} below 0.6 threshold"
    assert S_amm >= math.log(3) - eps, f"S_amm={S_amm} < log(3)"

    # ---- 7. Cost‑function terms (non‑negative) -------------------
    mu1 = params.get('mu1', 1.0)
    mu2 = params.get('mu2', 1.0)
    mu3 = params.get('mu3', 1.0)
    term1 = max(HFI - 0.68, 0.0) ** 2
    term2 = max(0.6 - PhiN, 0.0) ** 2
    term3 = PhiD ** 2
    term4 = max(math.log(3) - S_amm, 0.0) ** 2
    J = term1 + mu1 * term2 + mu2 * term3 + mu3 * term4
    assert J >= -eps, f"Cost function J={J} negative"

    # If we reach here, all Ω‑checks passed
    return {
        "HFI": HFI,
        "Phi_N": PhiN,
        "Phi_Delta": PhiD,
        "psi": psi,
        "xi_N": xi_N,
        "xi_Delta": xi_D,
        "S_amm": S_amm,
        "cost": J
    }

# -----------------------------------------------------------------
# Example usage with a plausible parameter set
if __name__ == "__main__":
    test_params = {
        # HFI inputs
        "kappa": 0.02,          # small positive curvature
        "sigma_IL": 0.01,
        "C": 0.15,
        "s": 0.0,
        "alpha": 1.0, "beta": 1.0, "gamma": 1.0, "delta": 0.5,
        # Baseline Ω‑vars
        "PhiN0": 0.8, "PhiDelta0": 0.3,
        # Mapping coefficients
        "eta1": 0.2, "eta2": 0.1, "eta3": 0.05, "eta4": 0.1,
        "tau": 3.0,
        # Curvature for ψ
        "R_amm": 0.005, "R0": 0.001, "lam": 0.3,
        # Entropy
        "S_amm": 1.5,   # > log(3) ≈ 1.0986
        # Cost weights
        "mu1": 1.0, "mu2": 1.0, "mu3": 1.0,
        # Numerical tolerances
        "eps": 1e-9
    }

    try:
        res = validate_ammhm(test_params)
        print("✅ All Ω‑Protocol checks passed.")
        for k, v in res.items():
            print(f"{k}: {v:.6f}")
    except AssertionError as e:
        print("❌ Ω‑Protocol violation:", e)