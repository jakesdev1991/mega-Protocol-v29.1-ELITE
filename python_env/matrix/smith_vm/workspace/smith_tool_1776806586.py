# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for TTM-Ω and TCPM-Ω
------------------------------------------------------
Inputs (per time step t):
    - ttci          : Trading Topology Coherence Index (raw, may be >1)
    - xi_ij         : dict {(i,j): correlation length}  (must be >0)
    - delta_regime  : scalar regime energy gap Δ_regime(t)
    - delta_0       : reference gap Δ₀
    - xi_0          : reference correlation length ξ₀
    - J_mat         : coupling matrix (numpy 2D array) → J* = spectral norm
    - T             : ensemble temperature (TCPM‑Ω)
    - Tc            : critical temperature (normalized)
    - PhiN_therm    : Φ_N^{(therm)}(t)  (optional, if using TCPM‑Ω)
    - PhiDelta_therm: Φ_Δ^{(therm)}(t)  (optional)
    - S_thermal     : thermodynamic entropy (optional)
    - w_critical    : list of agents with T_i > Tc (optional)

All optional fields are ignored if not present; the validator still
checks the core Ω‑invariants Φ_N, Φ_Δ, J*.

Ω‑Invariants (as per rubric v26.0):
    Φ_N ≥ 0
    Φ_Δ ≥ 0
    J*  ≥ 0
    ψ = ln Φ_N  must be real → Φ_N > 0
    (Additional protocol‑specific bounds are enforced as soft constraints:
        TTCI ∈ [0,1]   → Φ_N = 1‑TTCI ∈ [0,1]
        T ≤ 0.8·Tc     (cooling bound)
        Φ_N_therm ≥ 0.6   (if TCPM‑Ω active)
        S_thermal ≥ ln(3) (if TCPM‑Ω active)
"""

import numpy as np
from typing import Dict, Any, Tuple, List

def validate_omega_step(step: Dict[str, Any],
                        xi0: float = 1.0,
                        delta0: float = 1.0,
                        Tc: float = 1.0,
                        J_max: float = 10.0) -> Tuple[bool, List[str]]:
    """
    Validate a single time‑step against Omega Protocol invariants.
    Returns (pass, violations).
    """
    violations = []

    # ----- 1. Extract core quantities -------------------------------------------------
    ttci_raw = step.get("ttci")
    if ttci_raw is None:
        violations.append("Missing 'ttci'")
        ttci = None
    else:
        ttci = float(ttci_raw)

    xi_ij = step.get("xi_ij", {})
    if not isinstance(xi_ij, dict) or len(xi_ij) == 0:
        violations.append("'xi_ij' must be a non‑empty dict")
        xi_vals = np.array([])
    else:
        # ensure all lengths are positive
        xi_vals = np.array([float(v) for v in xi_ij.values() if v is not None])
        if np.any(xi_vals <= 0):
            violations.append("All ξ_ij must be > 0 for log")
            xi_vals = np.array([])

    delta_regime = step.get("delta_regime")
    if delta_regime is None:
        violations.append("Missing 'delta_regime'")
        delta_regime = None
    else:
        delta_regime = float(delta_regime)

    J_mat = step.get("J_mat")
    if J_mat is None:
        violations.append("Missing coupling matrix 'J_mat'")
        J_mat = np.array([[0.0]])
    else:
        J_mat = np.asarray(J_mat, dtype=float)

    # ----- 2. Compute Ω‑covariant modes ------------------------------------------------
    # Φ_N = 1 - TTCI (clip TTCI to [0,1] to keep Φ_N in [0,1])
    if ttci is not None:
        ttci_clipped = np.clip(ttci, 0.0, 1.0)
        Phi_N = 1.0 - ttci_clipped
    else:
        Phi_N = np.nan

    # Φ_Δ = Var[log(ξ/ξ₀)]
    if xi_vals.size > 0:
        log_ratios = np.log(xi_vals / xi0)
        Phi_Delta = float(np.var(log_ratios))
    else:
        Phi_Delta = np.nan

    # J* = spectral norm of J (largest singular value)
    try:
        J_star = float(np.linalg.norm(J_mat, ord=2))
    except np.linalg.LinAlgError:
        J_star = np.nan
        violations.append("Failed to compute spectral norm of J_mat")

    # ----- 3. Core invariant checks ----------------------------------------------------
    if not (np.isfinite(Phi_N) and Phi_N >= 0.0):
        violations.append(f"Φ_N = {Phi_N} must be ≥ 0")
    if not (np.isfinite(Phi_Delta) and Phi_Delta >= 0.0):
        violations.append(f"Φ_Δ = {Phi_Delta} must be ≥ 0")
    if not (np.isfinite(J_star) and J_star >= 0.0):
        violations.append(f"J* = {J_star} must be ≥ 0")
    # ψ = ln Φ_N must be real → Φ_N > 0
    if np.isfinite(Phi_N) and Phi_N <= 0.0:
        violations.append(f"Φ_N = {Phi_N} must be > 0 for ψ = ln Φ_N")

    # ----- 4. Protocol‑specific soft constraints (optional but recommended) -----------
    # TTCI range (already clipped, but we warn if original was out of bounds)
    if ttci is not None and (ttci < 0.0 or ttci > 1.0):
        violations.append(f"Raw TTCI = {ttci} outside [0,1]; clipped for safety")

    # Temperature bound (TCPM‑Ω)
    T = step.get("T")
    if T is not None:
        T = float(T)
        if T > 0.8 * Tc:
            violations.append(f"Temperature T={T} exceeds 0.8·Tc={0.8*Tc}")

    # Φ_N_therm lower bound (if TCPM‑Ω active)
    PhiN_therm = step.get("PhiN_therm")
    if PhiN_therm is not None:
        PhiN_therm = float(PhiN_therm)
        if PhiN_therm < 0.6:
            violations.append(f"Φ_N_therm = {PhiN_therm} < 0.6 (cooling required)")

    # Entropy bound (TCPM‑Ω)
    S_thermal = step.get("S_thermal")
    if S_thermal is not None:
        S_thermal = float(S_thermal)
        if S_thermal < np.log(3.0):
            violations.append(f"Entropy S_thermal={S_thermal} < ln(3)")

    # Optional: critical agent list length (just informational)
    w_crit = step.get("w_critical", [])
    if isinstance(w_crit, list) and len(w_crit) > 0:
        # no violation, just note
        pass

    # ----- 5. Return result -----------------------------------------------------------
    passed = len(violations) == 0
    return passed, violations


# ------------------- Example usage -------------------------------------------------
if __name__ == "__main__":
    # Synthetic data for one time step (feel free to replace with real stream)
    example_step = {
        "ttci": 0.55,                     # → Φ_N = 0.45
        "xi_ij": {(0,1): 1.2, (1,2): 0.9, (0,2): 1.0},
        "delta_regime": 1.3,
        "J_mat": [[0.5, 0.1], [0.1, 0.4]],
        "T": 0.7,                         # below 0.8·Tc (Tc=1.0)
        "PhiN_therm": 0.65,
        "S_thermal": 1.2,                 # > ln(3)≈1.099
        "w_critical": []
    }

    ok, msgs = validate_omega_step(example_step)
    print(f"Omega‑step PASS? {ok}")
    if not ok:
        print("Violations:")
        for m in msgs:
            print(" -", m)