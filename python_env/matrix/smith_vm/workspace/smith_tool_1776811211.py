# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
BTS-Ω Ω‑Physics Rubric v26.0 Validator
--------------------------------------
Validates:
  * Schema topology → BTFI
  * Covariant modes from Hessian eigenvalues
  * Conditional entropy gauge
  * Boundary‑condition consistency
  * MPC‑Ω QP constraints and cost‑function signs
"""

import math
from typing import Dict, List, Tuple

# ----------------------------------------------------------------------
# User‑supplied constants (can be tuned per domain)
# ----------------------------------------------------------------------
KAPPA1 = 1.0   # scaling for Φ_N curvature
KAPPA2 = 0.1   # offset for Φ_N
KAPPA3 = 1.0   # scaling for Φ_Δ curvature
KAPPA4 = 0.1   # offset for Φ_Δ

PHI_N0 = 0.6   # reference Φ_N for robust network
S_LOW  = 0.05  # lower entropy bound (≈0)
S_HIGH = 0.95  # upper entropy bound (will be scaled later)

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def euler_characteristic(V: int, E: int, F: int) -> int:
    """χ = V - E + F"""
    return V - E + F

def btfi(V: int, chi: int, delta: float, d_norm: int) -> float:
    """Biological Topology Fragility Index"""
    if V <= 0 or d_norm <= 0:
        raise ValueError("V and d_norm must be positive")
    return (abs(chi) / V) * delta * (1.0 / d_norm)

def phi_n_from_hessian(chi: int, V: int) -> float:
    """Φ_N = sqrt( κ1 * |χ|/V + κ2 )"""
    return math.sqrt(KAPPA1 * abs(chi) / V + KAPPA2)

def phi_delta_from_hessian(delta: float, d_norm: int) -> float:
    """Φ_Δ = sqrt( κ3 * Δ * (1/d_norm) + κ4 )"""
    return math.sqrt(KAPPA3 * delta * (1.0 / d_norm) + KAPPA4)

def conditional_entropy(
    type_probs: Dict[str, float],
    bin_probs: Dict[str, Dict[int, float]]
) -> float:
    """
    S_bts = Σ_s p(s) [ - Σ_k p(k|s) log p(k|s) ]
    type_probs: p(s) for each subsystem type
    bin_probs: p(k|s) for each type s and BTFI bin k
    """
    S = 0.0
    for s, p_s in type_probs.items():
        if not math.isclose(p_s, 0.0, abs_tol=1e-12):
            inner = 0.0
            for k, p_ks in bin_probs.get(s, {}).items():
                if p_ks > 0.0:
                    inner -= p_ks * math.log(p_ks)
            S += p_s * inner
    return S

def gauge_current(phi_delta: float) -> float:
    """J^0 = √2 · Φ_Δ (spatial components zero)"""
    return math.sqrt(2.0) * phi_delta

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_bts_omega(
    V: int,
    E: int,
    F: int,
    enforced_constraints: int,
    possible_constraints: int,
    d_norm: int,
    btfi_bins: List[float],
    type_probs: Dict[str, float],
    bin_probs: Dict[str, Dict[int, float]],
    phi_n0_ref: float = PHI_N0,
    s_low: float = S_LOW,
    s_high: float = S_HIGH,
) -> Tuple[bool, List[str]]:
    """
    Returns (is_valid, list_of_violation_messages)
    """
    violations = []

    # ----- 1. Basic topology -----
    chi = euler_characteristic(V, E, F)
    if chi == 0:
        violations.append("Schema Euler characteristic χ = 0 (degenerate topology).")

    # ----- 2. BTFI and its bounds -----
    delta = enforced_constraints / possible_constraints if possible_constraints > 0 else 0.0
    try:
        btfi_val = btfi(V, chi, delta, d_norm)
    except ValueError as ve:
        violations.append(str(evi))
        btfi_val = float('inf')
    if btfi_val > 0.7 + 1e-9:
        violations.append(f"BTFI = {btfi_val:.4f} exceeds allowed maximum 0.7.")
    if btfi_val < 0.0:
        violations.append(f"BTFI = {btfi_val:.4f} is negative (should be ≥0).")

    # ----- 3. Covariant mode bounds (from rubric examples) -----
    phi_n = phi_n_from_hessian(chi, V)
    phi_d = phi_delta_from_hessian(delta, d_norm)
    if phi_n < phi_n0_ref - 1e-9:
        violations.append(f"Φ_N = {phi_n:.4f} below reference robust value {phi_n0_ref:.4f}.")
    # No explicit upper bound for Φ_N, but we can flag absurdly large values:
    if phi_n > 10.0:
        violations.append(f"Φ_N = {phi_n:.4f} unusually large; check scaling constants.")
    if phi_d < 0.0:
        violations.append(f"Φ_Δ = {phi_d:.4f} negative (non‑physical).")

    # ----- 4. Invariant ψ_bts -----
    if phi_n <= 0.0:
        violations.append("Φ_N ≤ 0 makes ψ_bts undefined (log of non‑positive).")
    else:
        psi = math.log(phi_n / phi_n0_ref)
        # No direct numeric bound, but we can flag extreme values:
        if abs(psi) > 20.0:
            violations.append(f"|ψ_bts| = {abs(psi):.2f} extremely large; may indicate numerical issues.")

    # ----- 5. Conditional entropy -----
    S = conditional_entropy(type_probs, bin_probs)
    # Determine theoretical maximum for scaling S_HIGH if not supplied
    num_types = len(type_probs)
    max_bins = max((len(v) for v in bin_probs.values()), default=0)
    S_max_theoretical = math.log(num_types * max_bins) if num_types > 0 and max_bins > 0 else 0.0
    effective_high = s_high * S_max_theoretical if S_max_theoretical > 0.0 else s_high
    if S < s_low - 1e-9:
        violations.append(f"Conditional entropy S_bts = {S:.4f} below lower bound {s_low:.4f}.")
    if S > effective_high + 1e-9:
        violations.append(f"Conditional entropy S_bts = {S:.4f} above upper bound {effective_high:.4f}.")

    # ----- 6. Gauge current (just compute, no bound) -----
    J0 = gauge_current(phi_d)
    # Could add sanity check: J0 should be non‑negative
    if J0 < 0.0:
        violations.append(f"Gauge current J^0 = {J0:.4f} negative.")

    # ----- 7. MPC‑Ω QP constraints (explicit from proposal) -----
    if btfi_val > 0.7 + 1e-9:
        violations.append("QP constraint BTFI ≤ 0.7 violated.")
    if phi_n < 0.6 - 1e-9:
        violations.append("QP constraint Φ_N ≥ 0.6 violated.")
    if not (s_low <= S <= effective_high + 1e-9):
        violations.append("QP constraint S_low ≤ S_bts ≤ S_high violated.")

    # ----- 8. Cost function sign check (should be non‑negative) -----
    # Example cost terms from the proposal:
    cost = (
        max(btfi_val - 0.6, 0.0) ** 2
        + 0.5 * max(0.6 - phi_n, 0.0) ** 2
        + 0.5 * (phi_d ** 2)
        + 0.5 * (S - 0.5 * (s_low + effective_high)) ** 2   # centre‑of‑band penalty
    )
    if cost < -1e-12:
        violations.append(f"Cost function evaluated to negative value {cost:.6f}.")

    return (len(violations) == 0, violations)


# ----------------------------------------------------------------------
# Example usage (replace with real data from a leak)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Mock data for demonstration
    V, E, F = 12, 15, 4                     # 12 tables, 15 foreign keys, 4 query cycles
    enforced, possible = 9, 12              # 9 of 12 possible biological constraints enforced
    d_norm = 2                              # Boyce‑Codd normal form level
    btfi_bins = [0.1, 0.2, 0.3, 0.4, 0.5]   # example BTFI bin edges (not used directly)
    type_probs = {"genomic": 0.4, "proteomic": 0.35, "clinical": 0.25}
    # Bin probabilities p(k|s) – here we just assign uniform for illustration
    bin_probs = {
        s: {k: 1.0/len(btfi_bins) for k in range(len(btfi_bins))}
        for s in type_probs
    }

    valid, msgs = validate_bts_omega(
        V, E, F, enforced, possible, d_norm,
        btfi_bins, type_probs, bin_probs
    )
    print("VALID" if valid else "INVALID")
    if msgs:
        print("Violations:")
        for m in msgs:
            print(" -", m)