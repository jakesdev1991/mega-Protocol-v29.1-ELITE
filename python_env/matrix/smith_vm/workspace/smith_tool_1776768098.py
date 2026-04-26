# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol v26.0 Compliance Validator for NCSM‑Ω–style proposals.
"""

import math
from typing import Dict, Any, Tuple

# ----------------------------------------------------------------------
# Helper: dimensional analysis (very lightweight, for illustration)
# ----------------------------------------------------------------------
class Dim:
    """Base dimensions: M (mass), L (length), T (time)."""
    def __init__(self, M: int = 0, L: int = 0, T: int = 0):
        self.M, self.L, self.T = M, L, T

    def __mul__(self, other):
        return Dim(self.M + other.M, self.L + other.L, self.T + other.T)

    def __truediv__(self, other):
        return Dim(self.M - other.M, self.L - other.L, self.T - other.T)

    def __pow__(self, p):
        return Dim(self.M * p, self.L * p, self.T * p)

    def __eq__(self, other):
        return (self.M, self.L, self.T) == (other.M, other.L, other.T)

    def __repr__(self):
        return f"Dim(M={self.M}, L={self.L}, T={self.T})"

# Reference dimensions (natural units: ħ = c = 1 → action dimensionless)
DIM_ACTION   = Dim()                     # dimensionless
DIM_FIELD    = Dim()                     # φ dimensionless (normalized embeddings)
DIM_LENGTH   = Dim(L=1)
DIM_TIME     = Dim(T=1)
DIM_CURV     = Dim(L=-2)                 # R ~ 1/L²
DIM_INV_TIME = Dim(T=-1)                 # 1/time

# ----------------------------------------------------------------------
# Core validation routine
# ----------------------------------------------------------------------
def validate_ncsm_omega(props: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Parameters
    ----------
    props : dict
        Expected keys (examples, can be numeric or symbolic):
        - 'action'          : expression for S[φ] (should be dimensionless)
        - 'phi'             : field φ (dimensionless)
        - 'R'               : scalar curvature ⟨R⟩
        - 'lambda_eff'      : λ_eff
        - 'I0'              : I0 (healthy equilibrium)
        - 'PhiN'            : Φ_N
        - 'PhiDelta'        : Φ_Δ
        - 'xiN'             : ξ_N
        - 'xiDelta'         : ξ_Δ
        - 'psi'             : ψ
        - 'NCI'             : narrative coherence index
        - 'entropy_obs'     : entropy‑based observable (must be Shannon form)
        - 'Phi_density_impact' : net Φ‑density change over 24 months (float)
        - 'R_c'             : critical curvature for NCI
        - 'xi0'             : reference length ξ₀
    Returns
    -------
    (bool, str) : (True if compliant, message)
    """
    msgs = []

    # 1. Dimensional consistency of the action
    action_dim = props.get('action_dim', DIM_ACTION)  # caller may pre‑compute
    if action_dim != DIM_ACTION:
        msgs.append(f"Action dimension mismatch: got {action_dim}, expected {DIM_ACTION}")

    # 2. Covariant mode definitions (symbolic check – we only verify dimensions here)
    #    Φ_N = δI/√2  → same dimension as I (dimensionless)
    #    Φ_Δ = (1/√2) ∫ √g (φ·δφ_⊥)/|φ|  → also dimensionless
    for name, val in [('PhiN', props.get('PhiN')), ('PhiDelta', props.get('PhiDelta'))]:
        if val is None:
            msgs.append(f"Missing {name}")
        else:
            # Assume dimensionless; if a Dim object is supplied, check it.
            if isinstance(val, Dim) and val != Dim():
                msgs.append(f"{name} should be dimensionless, got {val}")

    # 3. Invariant relations from Hessian
    lam = props.get('lambda_eff')
    I0  = props.get('I0')
    Ravg = props.get('R')
    xiN  = props.get('xiN')
    xiD  = props.get('xiDelta')
    if None not in (lam, I0, Ravg, xiN, xiD):
        # ξ_N^{-2} = λ_eff (3 I0² + ⟨R⟩)
        lhs_N = 1.0 / (xiN * xiN) if xiN != 0 else float('inf')
        rhs_N = lam * (3.0 * I0 * I0 + Ravg)
        if not math.isclose(lhs_N, rhs_N, rel_tol=1e-6, abs_tol=1e-8):
            msgs.append(f"ξ_N invariant violation: lhs={lhs_N}, rhs={rhs_N}")

        # ξ_Δ^{-2} = λ_eff (I0² + 3⟨R⟩)
        lhs_D = 1.0 / (xiD * xiD) if xiD != 0 else float('inf')
        rhs_D = lam * (I0 * I0 + 3.0 * Ravg)
        if not math.isclose(lhs_D, rhs_D, rel_tol=1e-6, abs_tol=1e-8):
            msgs.append(f"ξ_Δ invariant violation: lhs={lhs_D}, rhs={rhs_D}")

    # 4. ψ = ln(ξ/ξ₀) with ξ = sqrt(ξ_N ξ_Δ)
    xi0 = props.get('xi0')
    psi = props.get('psi')
    if None not in (xiN, xiD, xi0, psi):
        xi = math.sqrt(xiN * xiD)
        if xi0 == 0:
            msgs.append("Reference length ξ₀ must be non‑zero")
        else:
            expected_psi = math.log(xi / xi0)
            if not math.isclose(psi, expected_psi, rel_tol=1e-6, abs_tol=1e-8):
                msgs.append(f"ψ invariant violation: got {psi}, expected {expected_psi}")

    # 5. Entropy‑based observable (must be Shannon entropy)
    entropy_obs = props.get('entropy_obs')
    if entropy_obs is None:
        msgs.append("Missing entropy‑based observable (required by Rubric)")
    else:
        # Very light check: entropy should be a real number ≥0 and
        # should be expressed as -∑ p log p (we accept a numeric proxy)
        if isinstance(entropy_obs, (int, float)):
            if entropy_obs < -1e-12:   # allow tiny negative due to rounding
                msgs.append(f"Entropy observable negative: {entropy_obs}")
        else:
            msgs.append("Entropy observable not a scalar; expected Shannon entropy value")

    # 6. Boundary conditions (qualitative – we just check that NCI and ξ are in range)
    NCI = props.get('NCI')
    xiN = props.get('xiN')
    xiD = props.get('xiDelta')
    if NCI is not None:
        if not (0.0 <= NCI <= 1.0 + 1e-9):
            msgs.append(f"NCI out of physical range [0,1]: {NCI}")
    if xiN is not None and xiN < 0:
        msgs.append(f"ξ_N must be non‑negative: {xiN}")
    if xiD is not None and xiD < 0:
        msgs.append(f"ξ_Δ must be non‑negative: {xiD}")

    # 7. Φ‑density impact – net gain over 24 months must be positive
    net_impact = props.get('Phi_density_impact')
    if net_impact is None:
        msgs.append("Missing Φ‑density impact assessment")
    elif not (isinstance(net_impact, (int, float)) and net_impact > 0):
        msgs.append(f"Φ‑density impact must be positive net gain, got {net_impact}")

    # ------------------------------------------------------------------
    # Final verdict
    # ------------------------------------------------------------------
    if msgs:
        return False, " | ".join(msgs)
    return True, "All Omega Protocol v26.0 checks passed."

# ----------------------------------------------------------------------
# Example usage (mock data mimicking the Engine's output)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # These values are illustrative; in a real run they'd be extracted from the proposal.
    mock_props = {
        # dimensional placeholders (we treat everything as dimensionless for brevity)
        'action_dim': Dim(),
        'PhiN': Dim(),
        'PhiDelta': Dim(),
        'lambda_eff': 0.5,
        'I0': 1.0,
        'R': 0.2,                     # ⟨R⟩
        'xiN': 1.0,
        'xiDelta': 1.0,
        'xi0': 1.0,
        'psi': 0.0,                   # ln(1/1)=0
        'NCI': 0.7,
        'entropy_obs': None,          # <-- missing entropy gauge → will fail
        'Phi_density_impact': 0.26,   # +26 % over 24 months
        'R_c': 1.0,
    }

    compliant, message = validate_ncsm_omega(mock_props)
    print("Compliant?" , compliant)
    print("Message:", message)