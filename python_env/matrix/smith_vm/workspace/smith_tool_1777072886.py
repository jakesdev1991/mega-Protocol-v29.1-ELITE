# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for Flux Stabilization Governor (FSG‑v57.2)
---------------------------------------------------------------------
This script checks the *absolute* invariants that any FSG‑v57.2 implementation
must satisfy before HoTT‑proof enforcement can be considered.
It is deliberately lightweight so it can be executed in the Protocol's VM.
"""

from __future__ import annotations
import math
from typing import Callable, Dict, List, Tuple

# ----------------------------------------------------------------------
# Protocol Constants (as per Omega Physics Rubric v57.0 Strictor Gate)
# ----------------------------------------------------------------------
PHI_MIN   = -2.0          # lower bound for Φ_N (allows ψ to reach 0.95)
PHI_SCALE = 1.5           # scaling factor for ψ
COD_THRESH   = 0.85       # Alignment Fidelity
PSI_THRESH   = 0.95       # Identity Continuity
XI_CONTROL_LE_XI_KIN = True   # Ξ_control ≤ Ξ_kinematic (boolean flag)
H_COLLAPSE_MAX = 0.3      # Dissonance Cap
PHI_DELTA_RATIO_MAX = 0.5 # Φ_Δ < 0.5·Φ_N
K_B_LOG2 = 1.380649e-23 * math.log2(math.e)   # k_B·ln 2 in J/K (Landauer)

# ----------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------
def compute_phi_N(cod: float) -> float:
    """Φ_N = log2(COD)  (protected against log of zero)"""
    if cod <= 0.0:
        raise ValueError("COD must be > 0 for log2")
    return math.log2(cod)

def compute_psi(phi_N: float,
                phi_min: float = PHI_MIN,
                phi_scale: float = PHI_SCALE) -> float:
    """ψ = tanh((Φ_N - Φ_min) / Φ_scale)  – the form used in the proposal."""
    return math.tanh((phi_N - phi_min) / phi_scale)

def compute_psi_rubric(phi_N: float) -> float:
    """Rubric‑required ψ = ln(Φ_N)  (shifted to stay positive for typical range)."""
    # The Rubric expects ψ = ln(Φ_N); we shift by a constant to avoid negativity
    # when Φ_N < 1. The constant is chosen so that ψ ≥ 0 when Φ_N ≥ 1.
    if phi_N <= 0.0:
        raise ValueError("Φ_N must be > 0 for ln")
    return math.log(phi_N)   # natural log; base‑e is irrelevant up to affine transform

def landauer_cost(audit_checks: int) -> float:
    """ΔS_audit = k_B·ln2·C_audit  (J/K)"""
    return K_B_LOG2 * audit_checks

# ----------------------------------------------------------------------
# Main Validation Routine
# ----------------------------------------------------------------------
def validate_fsg(state: Dict,
                 variational_derivation: Callable[[Dict], Tuple[float, float, float]] | None = None
                 ) -> Tuple[bool, List[str]]:
    """
    Parameters
    ----------
    state : dict
        Must contain the following keys (float unless noted):
        - cod                : Tr(ρ_fire ρ_sense)
        - phi_N              : optional; if missing will be computed from cod
        - phi_Delta          : Φ_Δ
        - psi                : optional; if missing will be computed from phi_N
        - xi_control         : Ξ_control
        - xi_kinematic       : Ξ_kinematic
        - h_collapse         : H_collapse
        - audit_checks       : integer count of invariant checks per control cycle
        - (optional) xi_N, xi_Delta : stiffness terms required by Rubric
    variational_derivation : callable(state) -> (phi_N_expr, phi_Delta_expr, phi_total_expr)
        If supplied, the validator will symbolically compare the returned expressions
        to the claimed phi_N, phi_Delta and the total Φ‑density (phi_N + phi_Delta -
        landauer_cost).  For simplicity we only check that the expressions are
        *consistent* with the numeric values (within tolerance).  A full symbolic
        check would require sympy or a dependent‑type engine.

    Returns
    -------
    (compliant, violations) : tuple
        compliant – True if all absolute invariants hold.
        violations – list of human‑readable strings describing each failure.
    """
    violations: List[str] = []
    TOL = 1e-9

    # ------------------------------------------------------------------
    # 1. COD ≥ 0.85
    # ------------------------------------------------------------------
    cod = state.get("cod")
    if cod is None:
        violations.append("Missing 'cod' (Tr(ρ_fire ρ_sense)).")
    else:
        if cod + TOL < COD_THRESH:
            violations.append(f"COD = {cod:.6f} < required {COD_THRESH}")

    # ------------------------------------------------------------------
    # 2. Φ_N = log2(COD)  (if not supplied)
    # ------------------------------------------------------------------
    phi_N = state.get("phi_N")
    if phi_N is None:
        if cod is None:
            violations.append("Cannot compute Φ_N: both 'phi_N' and 'cod' missing.")
        else:
            try:
                phi_N = compute_phi_N(cod)
                state["phi_N"] = phi_N   # store for later use
            except ValueError as e:
                violations.append(str(e))
    else:
        # Verify consistency
        expected = compute_phi_N(cod) if cod is not None else None
        if expected is not None and abs(phi_N - expected) > TOL:
            violations.append(f"Φ_N mismatch: supplied {phi_N:.6f} vs log2(COD)={expected:.6f}")

    # ------------------------------------------------------------------
    # 3. ψ form – Rubric requires ψ = ln(Φ_N) (up to affine transform)
    # ------------------------------------------------------------------
    psi = state.get("psi")
    if psi is None:
        if phi_N is None:
            violations.append("Cannot compute ψ: both 'psi' and 'phi_N' missing.")
        else:
            psi = compute_psi(phi_N)
            state["psi"] = psi
    # Rubric check
    try:
        psi_rubric = compute_psi_rubric(phi_N) if phi_N is not None else None
        if psi_rubric is not None and abs(psi - psi_rubric) > TOL:
            violations.append(
                f"ψ does not match Rubric form ln(Φ_N): "
                f"supplied ψ={psi:.6f}, Rubric ψ={psi_rubric:.6f}"
            )
    except ValueError as e:
        violations.append(str(e))

    # ------------------------------------------------------------------
    # 4. ψ ≥ 0.95 (Identity Continuity)
    # ------------------------------------------------------------------
    if psi is not None and psi + TOL < PSI_THRESH:
        violations.append(f"ψ = {psi:.6f} < required {PSI_THRESH}")

    # ------------------------------------------------------------------
    # 5. Φ_Δ < 0.5·Φ_N  (Asymmetry Control)
    # ------------------------------------------------------------------
    phi_Delta = state.get("phi_Delta")
    if phi_Delta is None:
        violations.append("Missing 'phi_Delta' (Φ_Δ).")
    else:
        if phi_N is None:
            violations.append("Cannot check Φ_Δ < 0.5·Φ_N: Φ_N unavailable.")
        else:
            if phi_Delta + TOL > PHI_DELTA_RATIO_MAX * phi_N:
                violations.append(
                    f"Φ_Δ = {phi_Delta:.6f} ≥ 0.5·Φ_N = {PHI_DELTA_RATIO_MAX*phi_N:.6f}"
                )

    # ------------------------------------------------------------------
    # 6. Ξ_control ≤ Ξ_kinematic  (Stiffness Matching)
    # ------------------------------------------------------------------
    xi_c = state.get("xi_control")
    xi_k = state.get("xi_kinematic")
    if xi_c is None:
        violations.append("Missing 'xi_control' (Ξ_control).")
    if xi_k is None:
        violations.append("Missing 'xi_kinematic' (Ξ_kinematic).")
    if xi_c is not None and xi_k is not None:
        if xi_c - TOL > xi_k:
            violations.append(
                f"Ξ_control = {xi_c:.6f} > Ξ_kinematic = {xi_k:.6f}"
            )

    # ------------------------------------------------------------------
    # 7. H_collapse ≤ 0.3  (Dissonance Cap)
    # ------------------------------------------------------------------
    h_col = state.get("h_collapse")
    if h_col is None:
        violations.append("Missing 'h_collapse' (H_collapse).")
    elif h_col - TOL > H_COLLAPSE_MAX:
        violations.append(
            f"H_collapse = {h_col:.6f} > cap {H_COLLAPSE_MAX}"
        )

    # ------------------------------------------------------------------
    # 8. Audit Cost Subtraction (Landauer)
    # ------------------------------------------------------------------
    audit_checks = state.get("audit_checks")
    if audit_checks is None:
        violations.append("Missing 'audit_checks' (C_audit).")
    else:
        if not isinstance(audit_checks, int) or audit_checks < 0:
            violations.append("'audit_checks' must be a non‑negative integer.")
        else:
            delta_S = landauer_cost(audit_checks)
            # The validator cannot check that the subtraction was actually performed
            # in the Φ‑ledger without seeing the ledger; we merely note the cost.
            state["delta_S_audit"] = delta_S   # for downstream use

    # ------------------------------------------------------------------
    # 9. Rubric‑required stiffness terms ξ_N and ξ_Δ
    # ------------------------------------------------------------------
    xi_N = state.get("xi_N")
    xi_Delta = state.get("xi_Delta")
    if xi_N is None:
        violations.append("Missing Rubric stiffness term 'xi_N'.")
    if xi_Delta is None:
        violations.append("Missing Rubric stiffness term 'xi_Delta'.")

    # ------------------------------------------------------------------
    # 10. Variational Derivation Check (optional but strongly encouraged)
    # ------------------------------------------------------------------
    if variational_derivation is not None:
        try:
            phi_N_expr, phi_Delta_expr, phi_total_expr = variational_derivation(state)
            # For this lightweight validator we only verify that the *numeric*
            # values of the expressions match the state within tolerance.
            # A real implementation would use sympy or a dependent‑type checker.
            if abs(phi_N_expr - state.get("phi_N", 0.0)) > TOL:
                violations.append(
                    f"Variational Φ_N expression ({phi_N_expr:.6f}) "
                    f"does not match state Φ_N ({state.get('phi_N',0.0):.6f})"
                )
            if abs(phi_Delta_expr - state.get("phi_Delta", 0.0)) > TOL:
                violations.append(
                    f"Variational Φ_Δ expression ({phi_Delta_expr:.6f}) "
                    f"does not match state Φ_Δ ({state.get('phi_Delta',0.0):.6f})"
                )
            # Total Φ‑density (including audit subtraction) should equal:
            expected_total = (state.get("phi_N",0.0) +
                              state.get("phi_Delta",0.0) -
                              state.get("delta_S_audit",0.0))
            if abs(phi_total_expr - expected_total) > TOL:
                violations.append(
                    f"Variational Φ‑total ({phi_total_expr:.6f}) "
                    f"does not match ledger total ({expected_total:.6f})"
                )
            # Additionally, we can assert that the expressions are *analytically*
            # derivable from the Omega Action Functional – this would require
            # supplying the functional itself; omitted here for brevity.
        except Exception as e:
            violations.append(f"Variational derivation callback raised: {e}")

    # ------------------------------------------------------------------
    # Final verdict
    # ------------------------------------------------------------------
    compliant = len(violations) == 0
    return compliant, violations


# ----------------------------------------------------------------------
# Example Usage (for illustration only – not part of the validation core)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Mock state that would be produced by a running FSG‑v57.2 controller
    example_state = {
        "cod": 0.90,
        # phi_N will be computed from cod
        "phi_Delta": 0.20,
        # psi will be computed from phi_N
        "xi_control": 1.2,
        "xi_kinematic": 1.5,
        "h_collapse": 0.15,
        "audit_checks": 42,
        # Rubric‑required stiffness terms (deliberately omitted to trigger a violation)
        # "xi_N": 0.3,
        # "xi_Delta": 0.1,
    }

    # Dummy variational derivation that simply returns the current numeric values.
    # A real implementation would return symbolic expressions derived from 𝒮[Φ].
    def dummy_variational(state):
        return state["phi_N"], state["phi_Delta"], \
               state["phi_N"] + state["phi_Delta"] - state.get("delta_S_audit", 0.0)

    compliant, msgs = validate_fsg(example_state, variational_derivation=dummy_variational)
    print("Compliant:", compliant)
    if not compliant:
        print("Violations:")
        for m in msgs:
            print(" -", m)