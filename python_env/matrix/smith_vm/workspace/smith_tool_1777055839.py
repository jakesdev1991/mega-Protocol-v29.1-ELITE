# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
FSG‑v57.1 Invariant Validator
-----------------------------
Checks the mathematical soundness of the core Omega‑Protocol invariants
as stated in the proposal:

1. COD = |⟨Ψ_fire|Ψ_sense⟩|²   ∈ [0, 1]
2. Φ_N = log₂(COD)                     (≤ 0)
3. ψ_bounded = tanh((Φ_N - Φ_min)/Φ_scale)   ∈ (-1, 1)
4. ψ_tanhPhi   = tanh(Φ_N)             ∈ (-1, 0]   (because Φ_N ≤ 0)
5. Invariant #2 from the Smith Audit:
      ψ_tanhPhi ≥ 0.95   (must hold for all admissible states)
6. Stiffness matching:
      Ξ_control ≤ Ξ_kinematic
7. Audit cost consistency:
      ΔS_audit = k_B·ln2·C_audit   (C_audit ≥ 0 integer)

If any check fails, the function returns False and a diagnostic message.
"""

import numpy as np

# Physical constants (Landauer)
K_B = 1.380649e-23   # J/K
LN2 = np.log(2.0)

def validate_fsg(
    fire_state: np.ndarray,
    sense_state: np.ndarray,
    Phi_min: float = 0.0,
    Phi_scale: float = 1.0,
    Xi_control: float = 0.0,
    Xi_kinematic: float = 0.0,
    C_audit: int = 0,
    tol: float = 1e-12
) -> tuple[bool, str]:
    """
    Returns (is_valid, message).
    """
    # ---- 1. COD definition & range ----
    # Normalise states (the proposal assumes they are already normalised,
    # but we enforce it to avoid spurious >1 values)
    fire_n = fire_state / (np.linalg.norm(fire_state) + tol)
    sense_n = sense_state / (np.linalg.norm(sense_state) + tol)
    cod = np.abs(np.vdot(fire_n, sense_n)) ** 2   # |⟨Ψ_fire|Ψ_sense⟩|²
    if not (0.0 - tol <= cod <= 1.0 + tol):
        return False, f"COD out of bounds: {cod}"
    
    # ---- 2. Φ_N ----
    # Avoid log2(0) → add tiny epsilon
    phi_N = np.log2(cod + 1e-15)
    if phi_N > 0.0 + tol:   # should never happen because COD ≤ 1
        return False, f"Φ_N > 0 (COD>1): phi_N={phi_N}"
    
    # ---- 3. ψ definitions ----
    # Bounded form from Concept §1.2
    psi_bounded = np.tanh((phi_N - Phi_min) / Phi_scale)
    # Tanh‑Φ_N form from Smith Audit invariant #2
    psi_tanhPhi = np.tanh(phi_N)
    
    # Consistency check: the two ψ must be identical if the proposal
    # claims they are the same invariant.
    if not np.allclose(psi_bounded, psi_tanhPhi, atol=tol):
        return False, (
            f"ψ definition mismatch: bounded={psi_bounded:.6f}, "
            f"tanh(Φ_N)={psi_tanhPhi:.6f}"
        )
    
    # ---- 4. Smith Audit Invariant #2 ----
    # ψ_tanhPhi ≥ 0.95 must hold for all admissible states.
    if psi_tanhPhi < 0.95 - tol:
        return False, (
            f"Invariant #2 violated: ψ=tanh(Φ_N)={psi_tanhPhi:.6f} < 0.95"
        )
    
    # ---- 5. Stiffness matching ----
    if Xi_control > Xi_kinematic + tol:
        return False, (
            f"Stiffness mismatch: Ξ_control={Xi_control} > Ξ_kinematic={Xi_kinematic}"
        )
    
    # ---- 6. Audit cost ----
    if C_audit < 0:
        return False, f"Negative audit count: C_audit={C_audit}"
    delta_S_audit = K_B * LN2 * C_audit   # Landauer bound per check
    # (no further constraint; just compute for completeness)
    
    # ---- All checks passed ----
    return True, (
        f"All invariants satisfied. "
        f"COD={cod:.6f}, Φ_N={phi_N:.6f}, ψ={psi_tanhPhi:.6f}, "
        f"ΔS_audit={delta_S_audit:.3e} J"
    )


# ----------------------------------------------------------------------
# Example usage – demonstrates the inevitable failure
if __name__ == "__main__":
    # Choose any normalised states; the worst case for ψ is COD=1 (phi_N=0)
    fire = np.array([1.0, 0.0, 0.0, 0.0])
    sense = np.array([1.0, 0.0, 0.0, 0.0])   # perfect alignment → COD=1
    
    ok, msg = validate_fsg(
        fire_state=fire,
        sense_state=sense,
        Phi_min=0.0,
        Phi_scale=1.0,
        Xi_control=0.5,
        Xi_kinematic=1.0,
        C_audit=10
    )
    print("VALID?" , ok)
    print("MESSAGE:", msg)