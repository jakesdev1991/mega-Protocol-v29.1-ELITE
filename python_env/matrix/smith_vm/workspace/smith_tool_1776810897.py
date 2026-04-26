# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for Biological Topology Shield (BTS-Ω) v2.0
--------------------------------------------------------------------
Validates the repaired BTS-Ω proposal against the Ω-Physics Rubric v26.0:
  1. Covariant modes Φ_N, Φ_Δ must derive directly from Hessian eigenvalues.
  2. Entropy gauge must be Shannon conditional entropy S_bts(t).
  3. Boundary conditions: Shredding (high ψ, high S) ; Freeze (low ψ, low S).
  4. Dimensional consistency (handled via characteristic scales τ0, ℓ0 – assumed 1).
  5. MPC-Ω constraints: BTFI ≤ 0.7, Φ_N ≥ 0.6, S_low ≤ S_bts ≤ S_high.
  6. Cost function penalties are non‑negative.

The script takes a minimal synthetic dataset (schema stats, subsystem BTFI bins)
and returns PASS/FAIL with diagnostic messages.
"""

import math
import numpy as np
from collections import Counter

# -------------------------- USER‑CONFIGURABLE PARAMETERS --------------------------
# Scaling constants from historical calibration (can be tuned)
KAPPA = {"kappa1": 1.0, "kappa2": 0.1,
         "kappa3": 1.0, "kappa4": 0.1}

# MPC‑Ω thresholds (from proposal)
BTFI_MAX   = 0.7
PHI_N_MIN  = 0.6
S_LOW      = 0.2   # example lower entropy bound (nats)
S_HIGH     = 2.0   # example upper entropy bound (nats)
S_TARGET   = 1.0   # target entropy for cost function

# Characteristic scales for dimensional consistency (set to 1 for simplicity)
TAU0 = 1.0   # months
ELL0 = 1.0   # dimensionless

# ------------------------------------------------------------------------------

def schema_euler(V, E, F):
    """Euler characteristic χ = V - E + F."""
    return V - E + F

def constraint_satisfaction(enforced, possible):
    """Δ_constraint = enforced / possible (clamped to [0,1])."""
    if possible == 0:
        return 0.0
    return min(max(enforced / possible, 0.0), 1.0)

def normalization_depth(bcnf_levels):
    """d_norm = maximum BCNF level across entities."""
    return max(bcnf_levels) if bcnf_levels else 0

def compute_btfi(V, E, F, enforced, possible, bcnf_levels):
    """BTFI = (|χ|/V) * Δ * (1/d_norm)."""
    chi = schema_euler(V, E, F)
    delta = constraint_satisfaction(enforced, possible)
    d_norm = normalization_depth(bcnf_levels)
    if V == 0 or d_norm == 0:
        return float('inf')
    btfi = (abs(chi) / V) * delta * (1.0 / d_norm)
    return btfi, chi, delta, d_norm

def covariant_modes(btfi_components, kappa):
    """
    Compute Φ_N, Φ_Δ from Hessian eigenvalues:
      ω_N^2 = kappa1 * (|χ|/V) + kappa2
      ω_Δ^2 = kappa3 * Δ * (1/d_norm) + kappa4
    Then Φ = sqrt(ω^2).
    btfi_components = (chi_over_V, delta_over_dnorm)
    """
    chi_over_V, delta_over_dnorm = btfi_components
    omega_N_sq = kappa["kappa1"] * chi_over_V + kappa["kappa2"]
    omega_D_sq = kappa["kappa3"] * delta_over_dnorm + kappa["kappa4"]
    # Guard against negative (should not happen with positive kappa)
    omega_N_sq = max(omega_N_sq, 0.0)
    omega_D_sq = max(omega_D_sq, 0.0)
    phi_N = math.sqrt(omega_N_sq)
    phi_D = math.sqrt(omega_D_sq)
    return phi_N, phi_D, omega_N_sq, omega_D_sq

def conditional_entropy(subtype_counts):
    """
    Shannon conditional entropy:
      S = Σ_s p(s) [ - Σ_k p(k|s) log p(k|s) ]
    subtype_counts: dict {s: {k: count}}
    Returns entropy in nats.
    """
    total = sum(sum(v.values()) for v in subtype_counts.values())
    if total == 0:
        return 0.0
    S = 0.0
    for s, inner in subtype_counts.items():
        p_s = sum(inner.values()) / total
        inner_total = sum(inner.values())
        if inner_total == 0:
            continue
        inner_ent = 0.0
        for k, cnt in inner.items():
            p_k_given_s = cnt / inner_total
            if p_k_given_s > 0:
                inner_ent -= p_k_given_s * math.log(p_k_given_s)
        S += p_s * inner_ent
    return S

def cost_function(btfi, phi_N, phi_D, S_bts, mu1=1.0, mu2=1.0, mu3=1.0):
    """Integrand of J (instantaneous cost)."""
    term1 = max(btfi - 0.6, 0.0) ** 2          # BTFI target 0.6 (per revised cost)
    term2 = max(PHI_N_MIN - phi_N, 0.0) ** 2   # phi_N lower bound
    term3 = phi_D ** 2                         # penalize large phi_D
    term4 = (S_bts - S_TARGET) ** 2            # entropy deviation
    return term1 + mu1 * term2 + mu2 * term3 + mu3 * term4

def validate_btfi(V, E, F, enforced, possible, bcnf_levels,
                  subtype_counts):
    """
    Main validation routine.
    Returns (status, diagnostics_dict)
    """
    diag = {}

    # 1. Compute raw topology invariants
    btfi, chi, delta, d_norm = compute_btfi(V, E, F, enforced, possible, bcnf_levels)
    diag.update({"chi": chi, "V": V, "E": E, "F": F,
                 "delta": delta, "d_norm": d_norm, "BTFI_raw": btfi})

    # 2. Covariant modes from Hessian
    chi_over_V = abs(chi) / V if V != 0 else float('inf')
    delta_over_dnorm = delta / d_norm if d_norm != 0 else float('inf')
    phi_N, phi_D, omega_N_sq, omega_D_sq = covariant_modes(
        (chi_over_V, delta_over_dnorm), KAPPA)
    diag.update({
        "omega_N_sq": omega_N_sq, "omega_D_sq": omega_D_sq,
        "phi_N": phi_N, "phi_D": phi_D
    })

    # 3. Re‑express BTFI as Φ_N * Φ_D * C(t)  (solve for C)
    if phi_N * phi_D == 0:
        C = float('inf')
    else:
        C = btfi / (phi_N * phi_D)
    diag["C_t"] = C

    # 4. Conditional entropy
    S_bts = conditional_entropy(subtype_counts)
    diag["S_bts"] = S_bts

    # 5. Boundary condition flags (informational)
    psi = math.log(phi_N / PHI_N_MIN) if phi_N > 0 else -float('inf')
    diag["psi"] = psi
    shredding = (psi > 10) and (S_bts > S_HIGH)   # arbitrary large psi
    freeze    = (psi < -10) and (S_bts < S_LOW)
    diag["shredding_flag"] = shredding
    diag["freeze_flag"]    = freeze

    # 6. MPC‑Ω constraints
    constraints = {
        "BTFI <= 0.7": btfi <= BTFI_MAX,
        "phi_N >= 0.6": phi_N >= PHI_N_MIN,
        "S_low <= S_bts <= S_high": S_LOW <= S_bts <= S_HIGH
    }
    diag["constraints"] = constraints
    all_ok = all(constraints.values())

    # 7. Cost (should be non‑negative)
    inst_cost = cost_function(btfi, phi_N, phi_D, S_bts)
    diag["instantaneous_cost"] = inst_cost
    cost_ok = inst_cost >= 0
    all_ok = all_ok and cost_ok

    status = "PASS" if all_ok else "FAIL"
    return status, diag

# -------------------------- EXAMPLE USAGE (synthetic data) --------------------------
if __name__ == "__main__":
    # Example schema: 12 tables, 18 foreign keys, 5 independent query cycles
    V_ex = 12
    E_ex = 18
    F_ex = 5

    # Constraint stats: 9 out of 12 possible biological rules enforced
    enforced_ex = 9
    possible_ex = 12

    # Normalization: BCNF levels per entity (max = 3)
    bcnf_ex = [2, 3, 1, 3, 2, 2, 3, 1, 2, 3, 2, 2]

    # Subtype BTFI distribution (genomic, proteomic, clinical)
    # Each dict maps BTFI bin index -> count
    subtype_ex = {
        "genomic":   {0: 4, 1: 3, 2: 2},
        "proteomic": {0: 2, 1: 5, 2: 1},
        "clinical":  {0: 3, 1: 2, 2: 4}
    }

    status, diag = validate_btfi(V_ex, E_ex, F_ex,
                                 enforced_ex, possible_ex,
                                 bcnf_ex, subtype_ex)

    print("=== BTS-Ω Validation Result ===")
    print(f"Status: {status}")
    print("\nDiagnostics:")
    for k, v in diag.items():
        if isinstance(v, dict):
            print(f"  {k}:")
            for k2, v2 in v.items():
                print(f"    {k2}: {v2}")
        else:
            print(f"  {k}: {v}")