# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the Biological Topology Shield (BTS-Ω) proposal.
Checks compliance with the Ω‑Physics Rubric v26.0 invariants:

1. Covariant modes Φ_N and Φ_Δ are direct square‑roots of Hessian eigenvalues.
2. BTFI = Φ_N · Φ_Δ · C(t)  (C(t) is a coupling factor, assumed =1 for validation).
3. Shannon conditional entropy S_bts = Σ_s p(s)[ -Σ_k p(k|s) log p(k|s) ].
4. Invariant ψ_bts = ln( Φ_N / Φ_N0 ).
5. Boundary conditions:
      Shredding Event: ψ_bts → +∞  ⇔  Φ_N → ∞  AND  S_bts → S_max
      Informational Freeze: ψ_bts → -∞ ⇔  Φ_N → 0   AND  S_bts → 0
6. QP‑style constraints (as given in the repaired proposal):
      BTFI ≤ 0.7
      Φ_N ≥ 0.6
      S_low ≤ S_bts ≤ S_high
7. Dimensional consistency: characteristic scales τ₀≈1 month, ℓ₀≈1 render the
   action dimensionless – we only check that the combination
   (|χ_schema|/V) and (Δ_constraint / d_norm) are dimensionless.

The script is deliberately lightweight: it receives a dictionary of
measured/computed quantities and returns a boolean compliance flag together
with a list of violated rules (if any).
"""

import math
from typing import Dict, List, Tuple

def validate_bts_omega(
    data: Dict,
    *,
    kappa: Tuple[float, float, float, float] = (1.0, 0.1, 1.0, 0.1),
    Phi_N0: float = 0.6,
    S_low: float = 0.0,
    S_high: float = 1.0,
    eps: float = 1e-9
) -> Tuple[bool, List[str]]:
    """
    Parameters
    ----------
    data : dict
        Must contain the following keys (all scalars for simplicity):
        - V               : number of tables (vertices)   >0
        - chi_schema      : Euler characteristic (can be negative)
        - Delta_constraint: constraint satisfaction gap ∈[0,1]
        - d_norm          : normalization depth (BCNF level) ≥1
        - p_s             : dict {subsystem_type: probability}   Σ p_s =1
        - p_k_given_s     : dict {subsystem_type: {bin_idx: prob}}   Σ_k p =1 for each s
        - C_t             : coupling factor (default 1.0 if omitted)
        - S_bts           : pre‑computed conditional entropy (optional)
        - Phi_N           : pre‑computed Φ_N (optional)
        - Phi_Delta       : pre‑computed Φ_Δ (optional)
        - psi_bts         : pre‑computed ψ_bts (optional)
        - S_max           : maximal possible entropy for the system (optional)
    kappa : tuple (κ1, κ2, κ3, κ4) scaling constants for the Hessian eigenvalues.
    Phi_N0: reference Φ_N for a robust network.
    S_low, S_high: allowed entropy band.
    eps   : tolerance for floating‑point comparisons.

    Returns
    -------
    (compliant, violations) where compliant is True iff all checks pass.
    """
    violations = []

    # ------------------------------------------------------------------
    # 1. Basic sanity checks
    # ------------------------------------------------------------------
    V = data.get("V")
    if V is None or V <= 0:
        violations.append("V (number of tables) must be >0")
    chi = data.get("chi_schema")
    if chi is None:
        violations.append("chi_schema (Euler characteristic) missing")
    Delta = data.get("Delta_constraint")
    if Delta is None or not (0.0 - eps <= Delta <= 1.0 + eps):
        violations.append("Delta_constraint must be in [0,1]")
    d_norm = data.get("d_norm")
    if d_norm is None or d_norm < 1:
        violations.append("d_norm (normalization depth) must be ≥1")

    # ------------------------------------------------------------------
    # 2. Covariant modes from Hessian eigenvalues
    # ------------------------------------------------------------------
    # ω_N^2 = κ1 * |χ|/V + κ2
    # ω_Δ^2 = κ3 * Δ * (1/d_norm) + κ4
    kappa1, kappa2, kappa3, kappa4 = kappa
    if V is not None and chi is not None:
        omega_N_sq = kappa1 * abs(chi) / V + kappa2
        if omega_N_sq < 0:
            violations.append("ω_N^2 negative (non‑physical)")
        Phi_N_calc = math.sqrt(omega_N_sq)
    else:
        Phi_N_calc = None

    if Delta is not None and d_norm is not None:
        omega_Delta_sq = kappa3 * Delta * (1.0 / d_norm) + kappa4
        if omega_Delta_sq < 0:
            violations.append("ω_Δ^2 negative (non‑physical)")
        Phi_Delta_calc = math.sqrt(omega_Delta_sq)
    else:
        Phi_Delta_calc = None

    # Compare with supplied values (if any)
    Phi_N = data.get("Phi_N")
    if Phi_N is not None and Phi_N_calc is not None:
        if abs(Phi_N - Phi_N_calc) > eps:
            violations.append(f"Phi_N mismatch: supplied {Phi_N}, calculated {Phi_N_calc}")

    Phi_Delta = data.get("Phi_Delta")
    if Phi_Delta is not None and Phi_Delta_calc is not None:
        if abs(Phi_Delta - Phi_Delta_calc) > eps:
            violations.append(f"Phi_Delta mismatch: supplied {Phi_Delta}, calculated {Phi_Delta_calc}")

    # ------------------------------------------------------------------
    # 3. BTFI definition
    # ------------------------------------------------------------------
    C_t = data.get("C_t", 1.0)
    if Phi_N_calc is not None and Phi_Delta_calc is not None:
        BTFI_calc = Phi_N_calc * Phi_Delta_calc * C_t
        BTFI = data.get("BTFI")
        if BTFI is not None:
            if abs(BTFI - BTFI_calc) > eps:
                violations.append(f"BTFI mismatch: supplied {BTFI}, calculated {BTFI_calc}")
    else:
        BTFI_calc = None

    # ------------------------------------------------------------------
    # 4. Conditional entropy S_bts
    # ------------------------------------------------------------------
    p_s = data.get("p_s")
    p_k_given_s = data.get("p_k_given_s")
    S_bts_calc = None
    if p_s is not None and p_k_given_s is not None:
        # normalise p_s just in case
        total_p_s = sum(p_s.values())
        if abs(total_p_s - 1.0) > eps:
            violations.append("p_s probabilities do not sum to 1")
        else:
            ent = 0.0
            for s, prob_s in p_s.items():
                if s not in p_k_given_s:
                    violations.append(f"Missing p(k|s) for subsystem {s}")
                    continue
                cond = p_k_given_s[s]
                # normalise conditional distribution
                total_cond = sum(cond.values())
                if abs(total_cond - 1.0) > eps:
                    violations.append(f"p(k|{s}) does not sum to 1")
                inner = -sum(pk * math.log(pk + 1e-15) for pk in cond.values())  # avoid log(0)
                ent += prob_s * inner
            S_bts_calc = ent
    S_bts = data.get("S_bts")
    if S_bts is not None and S_bts_calc is not None:
        if abs(S_bts - S_bts_calc) > eps:
            violations.append(f"S_bts mismatch: supplied {S_bts}, calculated {S_bts_calc}")

    # ------------------------------------------------------------------
    # 5. Invariant ψ_bts = ln(Φ_N / Φ_N0)
    # ------------------------------------------------------------------
    if Phi_N_calc is not None:
        psi_calc = math.log(Phi_N_calc / Phi_N0) if Phi_N_calc > 0 else float('-inf')
        psi = data.get("psi_bts")
        if psi is not None:
            if abs(psi - psi_calc) > eps:
                violations.append(f"psi_bts mismatch: supplied {psi}, calculated {psi_calc}")

    # ------------------------------------------------------------------
    # 6. Boundary conditions (Shredding Event & Informational Freeze)
    # ------------------------------------------------------------------
    # We only check logical consistency: if the extremes are claimed,
    # the corresponding Φ_N and S_bts must be at the limits.
    S_max = data.get("S_max")
    if S_max is None:
        # If not supplied, infer from S_bts_calc (max possible given distribution)
        S_max = math.log(len(p_s)) if p_s is not None else 1.0  # rough upper bound

    # Shredding: ψ → +∞  <=>  Φ_N → ∞  AND  S_bts → S_max
    # We approximate "→∞" by a large number; here we just check that
    # if Phi_N is huge ( > 1e3 ) and S_bts is near S_max, the condition holds.
    if data.get("shredding_event", False):
        if Phi_N_calc is not None and Phi_N_calc < 1e3:
            violations.append("Shredding event flagged but Phi_N not large enough")
        if S_bts_calc is not None and abs(S_bts_calc - S_max) > eps:
            violations.append("Shredding event flagged but S_bts not at S_max")

    # Informational Freeze: ψ → -∞  <=>  Φ_N → 0  AND  S_bts → 0
    if data.get("informational_freeze", False):
        if Phi_N_calc is not None and Phi_N_calc > eps:
            violations.append("Freeze event flagged but Phi_N not near zero")
        if S_bts_calc is not None and S_bts_calc > eps:
            violations.append("Freeze event flagged but S_bts not near zero")

    # ------------------------------------------------------------------
    # 7. QP‑style constraints
    # ------------------------------------------------------------------
    if BTFI_calc is not None and BTFI_calc > 0.7 + eps:
        violations.append(f"BTFI constraint violated: {BTFI_calc} > 0.7")
    if Phi_N_calc is not None and Phi_N_calc < 0.6 - eps:
        violations.append(f"Phi_N constraint violated: {Phi_N_calc} < 0.6")
    if S_bts_calc is not None:
        if S_bts_calc < S_low - eps or S_bts_calc > S_high + eps:
            violations.append(f"S_bts outside allowed band [{S_low},{S_high}]: {S_bts_calc}")

    # ------------------------------------------------------------------
    # 8. Dimensional consistency (quick check)
    # ------------------------------------------------------------------
    # |χ|/V is dimensionless (both counts). Δ/d_norm is also dimensionless.
    # No further action needed; we just note that the scaling constants κ_i
    # must carry dimensions of (frequency)^2 to make ω^2 have correct units.
    # This is assumed by the model; we cannot verify without units.

    compliant = len(violations) == 0
    return compliant, violations


# ----------------------------------------------------------------------
# Example usage (self‑test)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Mock data representing a moderately fragile system
    mock_data = {
        "V": 12,
        "chi_schema": -3,               # V - E + F = -3
        "Delta_constraint": 0.45,
        "d_norm": 2,
        "p_s": {"genomic": 0.5, "proteomic": 0.3, "clinical": 0.2},
        "p_k_given_s": {
            "genomic":   {0: 0.7, 1: 0.3},
            "proteomic": {0: 0.4, 1: 0.6},
            "clinical":  {0: 0.5, 1: 0.5}
        },
        "C_t": 1.0,
        # Let the script compute the rest
    }

    compliant, msgs = validate_bts_omega(mock_data)
    print(f"Compliant: {compliant}")
    if not compliant:
        print("Violations:")
        for m in msgs:
            print(" -", m)
    else:
        print("All Ω‑Physics Rubric v26.0 checks passed.")