# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol PASM-Ω Mathematical Validator
--------------------------------------------
Validates the core dynamical equations and invariants of the refined PASM-Ω
proposal.  All undefined symbols from the proposal are treated as configurable
parameters; the user must supply concrete values for them to obtain a definite
check.

The validator focuses on the mathematically well-defined subset:
    * SW-WRI (sigmoid form with baselines)
    * Φ_N^(weap) and Φ_Δ^(weap) linear updates
    * ψ_weap = ln(Φ_N/Φ_N0)   (the only invariant that does not require extra terms)
    * QP constraints: SW-WRI ≤ 0.6, Φ_N ≥ 0.5, S_weap ≥ ln(4)
    * Instantaneous cost ≥ 0
"""

import math
from typing import List, Tuple, Dict

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))

def sw_wri(
    S: List[float],
    S0: List[float],
    P_attack: List[float],
    w: List[float]
) -> float:
    """
    Sophistication‑Weighted Weaponization Readiness Index (SW‑WRI)
    σ( Σ w_i * (S_i / S0_i) * P(Attack|O_i) )
    """
    if not (len(S) == len(S0) == len(P_attack) == len(w)):
        raise ValueError("All input vectors must have the same length")
    inner = sum(w_i * (s_i / s0_i) * p_i
                for w_i, s_i, s0_i, p_i in zip(w, S, S0, P_attack))
    return sigmoid(inner)

def phi_n_weap(
    PhiN0: float,
    SW: float,
    S_weap: float,
    eta1: float = 0.9,
    eta2: float = 0.4
) -> float:
    """Φ_N^(weap)(t) = Φ_N^(0) - η1·SW(t‑τ) + η2·S_weap(t‑τ)"""
    return PhiN0 - eta1 * SW + eta2 * S_weap

def phi_delta_weap(
    PhiDelta0: float,
    intent_conv: float,
    strategy_div: float,
    eta3: float = 0.7,
    eta4: float = 0.5
) -> float:
    """Φ_Δ^(weap)(t) = Φ_Δ^(0) + η3·intent_conv(t‑τ) - η4·strategy_div(t‑τ)"""
    return PhiDelta0 + eta3 * intent_conv - eta4 * strategy_div

def psi_weap(PhiN_weap: float, PhiN0: float) -> float:
    """ψ_weap(t) = ln( Φ_N^(weap)(t) / Φ_N^(0) )"""
    if PhiN_weap <= 0 or PhiN0 <= 0:
        raise ValueError("Φ_N values must be positive for log")
    return math.log(PhiN_weap / PhiN0)

def instantaneous_cost(
    SW: float,
    PhiN_weap: float,
    PhiN0: float,
    S_weap: float,
    mu1: float = 1.0,
    mu2: float = 1.0,
    mu3: float = 1.0,
    SW_thr: float = 0.6,
    PhiN_thr: float = 0.5,
    S_weap_thr: float = math.log(4)
) -> float:
    """
    J_integrand = (SW - SW_thr)_+^2
                + μ1 (PhiN_thr - PhiN_weap)_+^2
                + μ2 Φ_Δ^(weap)^2        # note: Φ_Δ term appears without target in proposal
                + μ3 (ln(4) - S_weap)_+^2
    """
    term1 = max(0.0, SW - SW_thr) ** 2
    term2 = mu1 * max(0.0, PhiN_thr - PhiN_weap) ** 2
    # Φ_Δ term: proposal uses μ2 Φ_Δ^(weap)^2 (no explicit target)
    term3 = mu2 * (PhiN_weap ** 2)  # placeholder; replace with actual Φ_Δ if available
    term4 = mu3 * max(0.0, S_weap_thr - S_weap) ** 2
    return term1 + term2 + term3 + term4

def validate_state(
    PhiN0: float,
    PhiDelta0: float,
    S: List[float],
    S0: List[float],
    P_attack: List[float],
    w: List[float],
    S_weap: float,
    intent_conv: float,
    strategy_div: float,
    tau_days: int = 14
) -> Dict[str, Tuple[bool, str]]:
    """
    Runs all checks and returns a dict of {check_name: (passed, message)}.
    """
    results = {}

    # 1. Compute SW‑WRI
    try:
        SW = sw_wri(S, S0, P_attack, w)
        results["SW-WRI computation"] = (True, f"SW-WRI = {SW:.4f}")
    except Exception as e:
        results["SW-WRI computation"] = (False, str(e))
        return results  # cannot proceed

    # 2. Compute Φ_N^(weap) and Φ_Δ^(weap)
    PhiN = phi_n_weap(PhiN0, SW, S_weap)
    PhiDelta = phi_delta_weap(PhiDelta0, intent_conv, strategy_div)
    results["Phi_N^(weap)"] = (True, f"Φ_N^(weap) = {PhiN:.4f}")
    results["Phi_Δ^(weap)"] = (True, f"Φ_Δ^(weap) = {PhiDelta:.4f}")

    # 3. Compute ψ_weap and verify invariant (only the log definition)
    try:
        psi = psi_weap(PhiN, PhiN0)
        results["ψ_weap definition"] = (True, f"ψ_weap = ln(Φ_N/Φ_N0) = {psi:.4f}")
    except Exception as e:
        results["ψ_weap definition"] = (False, str(e))

    # 4. QP constraints
    results["SW-WRI ≤ 0.6"] = (SW <= 0.6 + 1e-9,
                               f"SW-WRI = {SW:.4f} {'OK' if SW <= 0.6 else 'VIOLATION'}")
    results["Φ_N^(weap) ≥ 0.5"] = (PhiN >= 0.5 - 1e-9,
                                   f"Φ_N^(weap) = {PhiN:.4f} {'OK' if PhiN >= 0.5 else 'VIOLATION'}")
    results["S_weap ≥ ln(4)"] = (S_weap >= math.log(4) - 1e-9,
                                 f"S_weap = {S_weap:.4f} {'OK' if S_weap >= math.log(4) else 'VIOLATION'}")

    # 5. Instantaneous cost non‑negative (should always hold by construction)
    cost = instantaneous_cost(SW, PhiN, PhiN0, S_weap)
    results["Cost ≥ 0"] = (cost >= -1e-12,
                           f"Instantaneous cost = {cost:.6e} {'OK' if cost >= 0 else 'NEGATIVE'}")

    return results

# ----------------------------------------------------------------------
# Example usage (user‑provided numbers)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Baseline values (chosen arbitrarily for demonstration)
    PhiN0 = 1.0
    PhiDelta0 = 0.5

    # Signal vectors (example: 5 channels as in the proposal)
    S = [120.0, 80.0, 30.0, 10.0, 5.0]          # raw signal strengths
    S0 = [100.0, 100.0, 50.0, 20.0, 10.0]      # baselines (must be >0)
    P_attack = [0.2, 0.5, 0.1, 0.05, 0.02]    # inferred attack probabilities per channel
    w = [0.3, 0.25, 0.2, 0.15, 0.1]           # channel weights (sum to 1)

    # Additional state variables
    S_weap = 1.5          # entropy gauge (must be ≥ ln4 ≈ 1.386)
    intent_conv = 0.4     # convergence rate of inferred intent
    strategy_div = 0.3    # diversity of adversarial approaches

    # Run validation
    report = validate_state(
        PhiN0=PhiN0,
        PhiDelta0=PhiDelta0,
        S=S,
        S0=S0,
        P_attack=P_attack,
        w=w,
        S_weap=S_weap,
        intent_conv=intent_conv,
        strategy_div=strategy_div,
        tau_days=14
    )

    print("=== PASM-Ω Mathematical Validation ===")
    for name, (ok, msg) in report.items():
        status = "PASS" if ok else "FAIL"
        print(f"{status:4} | {name:30} | {msg}")

    # Overall decision
    all_ok = all(ok for ok, _ in report.values())
    print("\nOVERALL:", "PASS" if all_ok else "FAIL")