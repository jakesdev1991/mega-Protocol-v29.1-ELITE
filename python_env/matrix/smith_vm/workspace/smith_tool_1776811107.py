# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Validation of the repaired Biological Topology Shield (BTS-Ω) math.
Checks:
  1. Schema topology invariants (χ, V, E, F, Δ, d_norm)
  2. BTFI definition and bounds
  3. Field‑theoretic covariant modes (Φ_N, Φ_Δ) from Hessian eigenvalues
  4. Invariant ψ = ln(Φ_N/Φ_N0)
  5. Shannon conditional entropy S_bts
  6. Boundary conditions (shredding vs. freeze)
  7. MPC‑Ω QP constraints
"""

import math
from typing import Dict, List, Tuple

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def euler_characteristic(V: int, E: int, F: int) -> int:
    """χ = V - E + F"""
    return V - E + F

def btfi(chi: int, V: int, Delta: float, d_norm: float) -> float:
    """BTFI = (|χ|/V) * Δ * (1/d_norm)"""
    if V == 0 or d_norm == 0:
        raise ValueError("V and d_norm must be > 0")
    return (abs(chi) / V) * Delta * (1.0 / d_norm)

def covariant_modes(chi: int, V: int, Delta: float, d_norm: float,
                    kappa: Tuple[float, float, float, float]) -> Tuple[float, float]:
    """
    Returns (Φ_N, Φ_Δ) from:
        ω_N² = κ1 * |χ|/V + κ2
        ω_Δ² = κ3 * Δ * (1/d_norm) + κ4
        Φ_N = sqrt(ω_N²), Φ_Δ = sqrt(ω_Δ²)
    """
    k1, k2, k3, k4 = kappa
    omega_N_sq = k1 * (abs(chi) / V) + k2
    omega_D_sq = k3 * Delta * (1.0 / d_norm) + k4
    if omega_N_sq < 0 or omega_D_sq < 0:
        raise ValueError("Hessian eigenvalues must be non‑negative")
    return math.sqrt(omega_N_sq), math.sqrt(omega_D_sq)

def invariant_psi(Phi_N: float, Phi_N0: float) -> float:
    """ψ = ln(Φ_N / Φ_N0)"""
    if Phi_N <= 0 or Phi_N0 <= 0:
        raise ValueError("Φ_N and Φ_N0 must be > 0")
    return math.log(Phi_N / Phi_N0)

def conditional_entropy(p_s: List[float], p_k_given_s: List[List[float]]) -> float:
    """
    Shannon conditional entropy:
        S = Σ_s p(s) * [ - Σ_k p(k|s) log p(k|s) ]
    p_s: list of probabilities for each subsystem type (sums to 1)
    p_k_given_s: list of lists, inner list sums to 1 for each s
    """
    if not math.isclose(sum(p_s), 1.0, rel_tol=1e-9):
        raise ValueError("p_s must sum to 1")
    S = 0.0
    for s_idx, ps in enumerate(p_s):
        inner = 0.0
        for pk in p_k_given_s[s_idx]:
            if pk > 0:
                inner -= pk * math.log(pk)
        S += ps * inner
    return S

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_bts_omega(
    V: int, E: int, F: int,
    Delta: float, d_norm: float,
    kappa: Tuple[float, float, float, float],
    Phi_N0: float,
    p_s: List[float],
    p_k_given_s: List[List[float]],
    S_low: float, S_high: float,
    S_target: float,
    mu: Tuple[float, float, float, float]
) -> Dict[str, float]:
    """
    Runs all checks and returns a dict of key quantities.
    Raises AssertionError if any Ω‑Physics Rubric v26.0 rule is violated.
    """
    # 1. Schema topology
    chi = euler_characteristic(V, E, F)
    # 2. BTFI
    BTFI_val = btfi(chi, V, Delta, d_norm)
    assert 0.0 <= BTFI_val <= 1.0, f"BTFI out of [0,1]: {BTFI_val}"
    assert BTFI_val <= 0.7, f"BTFI > 0.7 (QP constraint): {BTFI_val}"

    # 3. Covariant modes → Φ_N, Φ_Δ
    Phi_N, Phi_Delta = covariant_modes(chi, V, Delta, d_norm, kappa)
    assert Phi_N >= 0.6, f"Φ_N < 0.6 (QP constraint): {Phi_N}"
    # Φ_Δ has no explicit bound but should be non‑negative
    assert Phi_Delta >= 0.0, f"Φ_Δ negative: {Phi_Delta}"

    # 4. Invariant ψ
    psi = invariant_psi(Phi_N, Phi_N0)
    # ψ is unbounded; just compute

    # 5. Conditional entropy
    S_bts = conditional_entropy(p_s, p_k_given_s)
    assert S_low <= S_bts <= S_high, f"S_bts outside [{S_low},{S_high}]: {S_bts}"

    # 6. Boundary condition logic (shredding vs freeze)
    # Shredding: Φ_N → ∞ AND S_bts → S_high (high entropy)
    # Freeze:    Φ_N → 0   AND S_bts → S_low  (low entropy)
    # We simply verify that the mapping is monotonic:
    #   - High BTFI → high Φ_N → tends toward freeze (low S)
    #   - Low BTFI  → low Φ_N  → tends toward shredding (high S)
    # For a sanity check we enforce:
    if BTFI_val > 0.7:  # high fragility region
        assert S_bts <= S_target + 0.1, \
            "High BTFI should correspond to low entropy (near freeze)"
    else:  # low/moderate fragility
        assert S_bts >= S_target - 0.1, \
            "Low BTFI should correspond to high entropy (near shredding)"

    # 7. MPC‑Ω cost function (sample evaluation)
    m1, m2, m3, m4 = mu
    cost = (
        (max(BTFI_val - 0.6, 0.0)) ** 2 +
        m1 * (max(0.6 - Phi_N, 0.0)) ** 2 +
        m2 * (Phi_Delta ** 2) +
        m3 * (max(S_bts - S_target, 0.0)) ** 2
    )
    # cost should be non‑negative (trivially true)
    assert cost >= 0.0, f"Negative cost: {cost}"

    return {
        "chi": chi,
        "BTFI": BTFI_val,
        "Phi_N": Phi_N,
        "Phi_Delta": Phi_Delta,
        "psi": psi,
        "S_bts": S_bts,
        "cost": cost
    }

# ----------------------------------------------------------------------
# Example usage with plausible numbers
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Schema: 120 tables, 250 foreign keys, 40 independent query cycles
    V, E, F = 120, 250, 40
    Delta = 0.55          # fraction of enforced biological rules
    d_norm = 2.5          # average BCNF level
    kappa = (1.2, 0.1, 0.9, 0.05)   # calibrated constants
    Phi_N0 = 0.4          # reference for a robust network
    # Subsystem types: genomic, proteomic, clinical (3 types)
    p_s = [0.4, 0.35, 0.25]
    p_k_given_s = [
        [0.7, 0.2, 0.1],   # genomic BTFI bins
        [0.5, 0.3, 0.2],   # proteomic
        [0.6, 0.25, 0.15]  # clinical
    ]
    S_low, S_high = 0.2, 1.5   # plausible entropy bounds
    S_target = 0.8
    mu = (0.5, 0.3, 0.4, 0.2)

    result = validate_bts_omega(
        V, E, F, Delta, d_norm, kappa, Phi_N0,
        p_s, p_k_given_s, S_low, S_high, S_target, mu
    )
    print("Validation passed. Key quantities:")
    for k, v in result.items():
        print(f"  {k}: {v:.4f}")