# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
SLBA-Ω Mathematical Soundness Validator
---------------------------------------
Checks that the SLBA-Ω formulation respects the Omega Protocol invariants:
    - Phi_N  : connectedness  (>=0, bounded by Phi_N0)
    - Phi_Delta: asymmetry    (>=0)
    - xi_N, xi_Delta: correlation lengths (>0)
    - R_D    : robustness score (0..1)
    - Weights: non‑negative, sum to 1
"""

import math
from typing import Tuple, List

def validate_slba(
    # ----- Input document metrics -----
    C: float,          # coverage [0,1]
    kappa: float,      # consistency [0,1]
    delta_t: float,    # days since last update (>=0)
    sigma: float,      # specificity (raw count, >=0)
    # ----- Model parameters -----
    w: List[float],    # weights [w1,w2,w3,w4]
    alpha_C: float,    # >0
    beta_kappa: float, # >=0
    lam: float,        # decay constant >0
    sigma_max: float,  # normalisation factor for specificity (>0)
    R_crit: float,     # collapse threshold in (0,1)
    Phi_N0: float = 1.0,   # nominal connectedness
    Phi_Delta0: float = 0.0 # nominal asymmetry (often zero)
) -> Tuple[bool, List[str]]:
    """
    Returns (is_compliant, list_of_violation_messages)
    """
    violations = []

    # ---- 1. Weight checks ----
    if len(w) != 4:
        violations.append("Weight vector must have exactly 4 elements.")
    else:
        if any(wi < 0 for wi in w):
            violations.append("Weights must be non‑negative.")
        if not math.isclose(sum(w), 1.0, rel_tol=1e-9, abs_tol=1e-12):
            violations.append(f"Weights must sum to 1 (got {sum(w)}).")

    # ---- 2. Input metric bounds ----
    if not (0.0 <= C <= 1.0):
        violations.append(f"Coverage C must be in [0,1] (got {C}).")
    if not (0.0 <= kappa <= 1.0):
        violations.append(f"Consistency kappa must be in [0,1] (got {kappa}).")
    if delta_t < 0:
        violations.append(f"Delta_t (days since update) must be >=0 (got {delta_t}).")
    if sigma < 0:
        violations.append(f"Specificity sigma must be >=0 (got {sigma}).")
    if sigma_max <= 0:
        violations.append(f"sigma_max must be >0 (got {sigma_max}).")
    if lam <= 0:
        violations.append(f"Decay constant lambda must be >0 (got {lam}).")
    if alpha_C <= 0:
        violations.append(f"alpha_C must be >0 (got {alpha_C}).")
    if beta_kappa < 0:
        violations.append(f"beta_kappa must be >=0 (got {beta_kappa}).")
    if not (0.0 < R_crit < 1.0):
        violations.append(f"R_crit must be in (0,1) (got {R_crit}).")
    if Phi_N0 <= 0:
        violations.append(f"Phi_N0 must be >0 (got {Phi_N0}).")
    if Phi_Delta0 < 0:
        violations.append(f"Phi_Delta0 must be >=0 (got {Phi_Delta0}).")

    # If any basic check fails, we can stop early
    if violations:
        return False, violations

    # ---- 3. Normalise specificity to [0,1] ----
    sigma_norm = sigma / sigma_max
    if not (0.0 <= sigma_norm <= 1.0):
        # This can happen if sigma > sigma_max; we treat it as a violation
        violations.append(f"Normalised specificity sigma/sigma_max must be in [0,1] (got {sigma_norm}).")

    # ---- 4. Compute freshness ----
    phi = math.exp(-lam * delta_t)   # in (0,1]
    if not (0.0 < phi <= 1.0):
        violations.append(f"Freshness phi must be in (0,1] (got {phi}).")

    # ---- 5. Aggregate robustness score ----
    R = w[0]*C + w[1]*kappa + w[2]*phi + w[3]*sigma_norm
    if not (0.0 <= R <= 1.0):
        violations.append(f"Robustness score R_D must be in [0,1] (got {R}).")

    # ---- 6. Map to Omega invariants ----
    Phi_N_doc = Phi_N0 * math.tanh(alpha_C * C)
    if not (0.0 <= Phi_N_doc <= Phi_N0):
        violations.append(f"Phi_N^(doc) out of bounds [0,{Phi_N0}] (got {Phi_N_doc}).")

    Phi_Delta_doc = Phi_Delta0 + beta_kappa * (1.0 - kappa)
    if Phi_Delta_doc < 0:
        violations.append(f"Phi_Delta^(doc) must be >=0 (got {Phi_Delta_doc}).")

    # Correlation lengths (proportionality constants set to 1 for simplicity)
    if sigma_norm == 0.0:
        violations.append("Specificity sigma_norm cannot be zero (would make xi_N infinite).")
    else:
        xi_N = 1.0 / sigma_norm   # proportional to 1/sigma
        if xi_N <= 0:
            violations.append(f"xi_N must be >0 (got {xi_N}).")

    if phi == 0.0:
        violations.append("Freshness phi cannot be zero (would make xi_Delta infinite).")
    else:
        xi_Delta = 1.0 / phi      # proportional to 1/phi
        if xi_Delta <= 0:
            violations.append(f"xi_Delta must be >0 (got {xi_Delta}).")

    # ---- 7. Collapse precursor check (informational) ----
    # Not a violation, just flag if R < R_crit
    if R < R_crit:
        # This is an expected condition; we note it but do not treat as invalid.
        pass

    compliant = len(violations) == 0
    return compliant, violations


# ----------------- Example usage -----------------
if __name__ == "__main__":
    # Example parameter set (feel free to edit)
    w_example = [0.25, 0.25, 0.25, 0.25]   # equal weights
    alpha_example = 2.0
    beta_example = 0.5
    lam_example = 0.01   # per day
    sigma_max_example = 10.0   # assume max 10 constraints per mechanism
    R_crit_example = 0.6

    # Example document set
    C_example = 0.8
    kappa_example = 0.9
    delta_t_example = 30.0   # 30 days since last update
    sigma_example = 4.0      # 4 quantitative constraints found

    ok, msgs = validate_slba(
        C=C_example,
        kappa=kappa_example,
        delta_t=delta_t_example,
        sigma=sigma_example,
        w=w_example,
        alpha_C=alpha_example,
        beta_kappa=beta_example,
        lam=lam_example,
        sigma_max=sigma_max_example,
        R_crit=R_crit_example,
        Phi_N0=1.0,
        Phi_Delta0=0.0
    )

    print("SLBA-Ω validation result:")
    if ok:
        print("  ✅ All mathematical and invariant checks passed.")
    else:
        print("  ❌ Violations detected:")
        for m in msgs:
            print(f"    - {m}")