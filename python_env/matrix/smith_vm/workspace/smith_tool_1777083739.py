# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Invariant Validator for Flux Stabilization Governor v57.1
-----------------------------------------------------------------------
This script strictly enforces the mathematical and informational invariants
defined in the repaired FSG‑v57.1 proposal.  It can be used as a runtime
guard (Smith Audit) or as a design‑time verification tool.

All formulas are taken directly from the proposal; constants are chosen to
match the stated thresholds.  The validator raises a ValidationError if any
invariant is violated, guaranteeing that the system state remains on the
smooth, non‑singular informational manifold required by the Omega Protocol.
"""

import math
import numpy as np
from dataclasses import dataclass
from typing import Tuple


# ----------------------------------------------------------------------
# Constants (as per the proposal)
# ----------------------------------------------------------------------
K_B = 1.380649e-23          # Boltzmann constant (J/K) – kept for dimensionality
LN2 = math.log(2.0)         # natural log of 2
GAMMA = 0.01                # hr⁻¹, control‑stiffness integration rate
PHI_MIN = 0.0               # shift for bounded identity metric
PHI_SCALE = 1.0             # scale for bounded identity metric
R_MAX = 1.0                 # normalisation for stiffness mismatch (chosen unitless)
C_AUDIT = 1.0               # audit‑cost coefficient (one Landauer check per tick)

# Invariant thresholds (from Smith Invariant Enforcer)
COD_MIN = 0.85              # Alignment fidelity
PSI_MIN = 0.95              # Identity continuity (bounded tanh output)
H_COLLAPSE_MAX = 0.30       # Dissonance cap (binary entropy)
ASYMMETRY_FACTOR = 0.5      # Φ_Δ < 0.5·Φ_N


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def fidelity(psi: np.ndarray, phi: np.ndarray) -> float:
    """
    Quantum‑inspired fidelity between two (normalized) state vectors:
        COD = |⟨ψ|φ⟩|²
    Assumes inputs are already normalized; if not, we normalise internally.
    """
    psi_n = psi / np.linalg.norm(psi)
    phi_n = phi / np.linalg.norm(phi)
    overlap = np.vdot(psi_n, phi_n)          # ⟨ψ|φ⟩
    return np.abs(overlap) ** 2              # |⟨ψ|φ⟩|²


def binary_entropy(p: float) -> float:
    """
    Binary entropy H(p) = -p log₂ p - (1-p) log₂ (1-p).
    Defined to be 0 at p=0 or p=1 (limit taken).
    """
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p)


def control_stiffness(xi0: float, xi_kin: float, t: float) -> float:
    """
    Adiabatic stiffness evolution (Eq. in proposal):
        ξ_control(t) = ξ_control(0)·e^(−γt) + ξ_kin·(1−e^(−γt))
    t is in hours to match GAMMA units.
    """
    exp_term = math.exp(-GAMMA * t)
    return xi0 * exp_term + xi_kin * (1.0 - exp_term)


def bounded_identity(phi_N: float) -> float:
    """
    ψ = tanh((Φ_N − Φ_min)/Φ_scale)
    Guarantees ψ ∈ (−1,1) and C^∞ differentiability.
    """
    return math.tanh((phi_N - PHI_MIN) / PHI_SCALE)


# ----------------------------------------------------------------------
# Validation dataclass
# ----------------------------------------------------------------------
@dataclass
class ValidationError(Exception):
    """Raised when any Omega Protocol invariant is violated."""
    message: str


def validate_fsg_state(
    fire_state: np.ndarray,
    sense_state: np.ndarray,
    xi_control_0: float,
    xi_kinematic: float,
    t_hr: float,
    *,
    phi_min: float = PHI_MIN,
    phi_scale: float = PHI_SCALE,
    r_max: float = R_MAX,
    c_audit: float = C_AUDIT,
) -> Tuple[float, float, float, float, float, float]:
    """
    Core validation routine.
    Returns:
        (COD, phi_N, psi, phi_Delta, delta_S_audit, phi_net)
    Raises ValidationError if any invariant fails.
    """
    # ---- 1. Informational overlap (COD) ----
    cod = fidelity(fire_state, sense_state)
    if cod <= 0.0:
        raise ValidationError(f"COD must be > 0 (got {cod}) for log₂ definition.")
    # ---- 2. Phi_N (informational density) ----
    phi_N = math.log2(cod)                     # log₂(COD) as per proposal
    # ---- 3. Bounded identity continuity (psi) ----
    psi = bounded_identity(phi_N)              # ψ = tanh((Φ_N−Φ_min)/Φ_scale)
    # ---- 4. Control stiffness evolution ----
    xi_control = control_stiffness(xi_control_0, xi_kinematic, t_hr)
    # ---- 5. Stiffness mismatch term ----
    r_align = xi_kinematic - xi_control
    phi_Delta = psi * math.tanh(r_align / r_max)
    # ---- 6. Audit cost (Landauer) ----
    delta_S_audit = K_B * LN2 * c_audit        # J/K * dimensionless → J/K (kept symbolic)
    # ---- 7. Net Phi-density ----
    phi_net = phi_N + phi_Delta - delta_S_audit

    # ---- 8. Invariant checks (Smith Audit) ----
    if cod < COD_MIN:
        raise ValidationError(f"COD={cod:.4f} < required {COD_MIN}")
    if psi < PSI_MIN:
        raise ValidationError(f"ψ={psi:.4f} < required {PSI_MIN} (identity continuity)")
    if xi_control > xi_kinematic + 1e-12:      # allow tiny floating‑point slack
        raise ValidationError(
            f"ξ_control={xi_control:.4f} > ξ_kinematic={xi_kinematic:.4f}"
        )
    h_collapse = binary_entropy(cod)
    if h_collapse > H_COLLAPSE_MAX + 1e-12:
        raise ValidationError(
            f"Binary entropy H(COD)={h_collapse:.4f} > {H_COLLAPSE_MAX}"
        )
    if phi_Delta >= ASYMMETRY_FACTOR * phi_N - 1e-12:
        raise ValidationError(
            f"Φ_Δ={phi_Delta:.4f} ≥ 0.5·Φ_N={0.5*phi_N:.4f} (asymmetry control)"
        )
    # Optional: ensure psi stays in [-1,1] (theoretically guaranteed by tanh)
    if not (-1.0 <= psi <= 1.0):
        raise ValidationError(f"ψ={psi:.4f} outside bounded range [-1,1]")

    # All checks passed
    return cod, phi_N, psi, phi_Delta, delta_S_audit, phi_net


# ----------------------------------------------------------------------
# Example usage (self‑test)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example: reasonably aligned states
    fire = np.array([1.0, 0.0, 0.0])          # normalized
    sense = np.array([0.9, 0.1, 0.0])         # slightly off‑axis
    sense = sense / np.linalg.norm(sense)    # renormalise for safety

    xi0 = 0.2          # initial control stiffness
    xi_kin = 0.8       # kinematic capacity (target)
    t = 5.0            # hours into engagement

    try:
        results = validate_fsg_state(
            fire_state=fire,
            sense_state=sense,
            xi_control_0=xi0,
            xi_kinematic=xi_kin,
            t_hr=t,
        )
        cod, phi_N, psi, phi_Delta, delta_S, phi_net = results
        print("✅ Validation PASSED")
        print(f"  COD            = {cod:.4f}")
        print(f"  Φ_N (log₂COD)  = {phi_N:.4f}")
        print(f"  ψ (tanh)       = {psi:.4f}")
        print(f"  Φ_Δ            = {phi_Delta:.4f}")
        print(f"  ΔS_audit       = {delta_S:.4e}")
        print(f"  Φ_net          = {phi_net:.4f}")
    except ValidationError as e:
        print("❌ Validation FAILED:", e)