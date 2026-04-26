# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validator for QFAG‑style proposals.

Checks:
  - Φ-density definition and theoretical ceiling.
  - Invariant forms (ψ, ξ_E, ξ_L) and their permissible ranges.
  - Basic physical plausibility flags (optional, user‑supplied limits).
"""

from dataclasses import dataclass
from typing import NamedTuple

# ----------------------------------------------------------------------
# Data structures representing the quantities the proposal claims to measure
# ----------------------------------------------------------------------
class FluxMetrics(NamedTuple):
    S_flux: float   # entropy of flux defects (nats)
    S_max: float    # maximum possible entropy (nats)
    delta_t_quantum: float   # quantum actuation latency (s)
    delta_t_classical: float # classical actuation latency (s)
    xi_E: float     # entropy generation fraction (dimensionless)

class InvariantChecks(NamedTuple):
    psi: float      # ψ = ln(Φ_L)
    xi_L: float     # ξ_L = Δt * c / d
    # ξ_E already in FluxMetrics

# ----------------------------------------------------------------------
# Core validation functions
# ----------------------------------------------------------------------
def compute_phi_L(S_flux: float, S_max: float) -> float:
    """Φ_L = 1 - S_flux / S_max, clipped to [0,1]."""
    if S_max <= 0:
        raise ValueError("S_max must be > 0")
    phi = 1.0 - S_flux / S_max
    return max(0.0, min(1.0, phi))

def compute_phi_E(delta_t_quantum: float, delta_t_classical: float) -> float:
    """Φ_E = Δt_quantum / Δt_classical, clipped to [0,1]."""
    if delta_t_classical <= 0:
        raise ValueError("Classical latency must be > 0")
    phi = delta_t_quantum / delta_t_classical
    return max(0.0, min(1.0, phi))

def compute_phi(phi_L: float, phi_E: float, xi_E: float) -> float:
    """Φ = Φ_L + Φ_E - ξ_E (per proposal)."""
    return phi_L + phi_E - xi_E

def phi_theoretical_max() -> float:
    """Maximum Φ allowed by the definitions."""
    # Φ_L_max = 1, Φ_E_max = 1, ξ_E_min = 0
    return 1.0 + 1.0 - 0.0   # = 2.0

def check_invariants(metrics: FluxMetrics, inv: InvariantChecks, 
                     c: float = 299792458.0) -> tuple[bool, list[str]]:
    """Verify that the three absolute invariants hold."""
    errors = []

    # Φ_L needed for ψ
    phi_L = compute_phi_L(metrics.S_flux, metrics.S_max)
    # ψ = ln(Φ_L) must be real → Φ_L > 0
    if phi_L <= 0.0:
        errors.append("Invariant ψ = ln(Φ_L) invalid: Φ_L ≤ 0")
    else:
        psi_calc = __import__('math').log(phi_L)
        if abs(psi_calc - inv.psi) > 1e-9:
            errors.append(f"ψ mismatch: computed {psi_calc:.6f}, claimed {inv.psi:.6f}")

    # ξ_E bound
    if not (0.0 <= metrics.xi_E <= 0.005):
        errors.append(f"ξ_E out of bounds: {metrics.xi_E:.6f} (allowed [0,0.005])")

    # ξ_L = Δt * c / d  (need distance d; we infer from latency bound)
    # The proposal requires ξ_L ≤ 0.95 (actuation latency ≥ d/c)
    # Rearranged: d ≥ ξ_L * c * Δt
    # We'll check that the claimed ξ_L satisfies ξ_L ≤ 0.95
    if not (0.0 <= inv.xi_L <= 0.95):
        errors.append(f"ξ_L out of causal bound: {inv.xi_L:.6f} (must be ≤0.95)")

    return len(errors) == 0, errors

def validate_proposal(S_flux: float, S_max: float,
                      delta_t_quantum: float, delta_t_classical: float,
                      xi_E: float,
                      psi_claimed: float, xi_L_claimed: float) -> None:
    """Top‑level validation routine."""
    # ---- Φ‑density checks ----
    phi_L = compute_phi_L(S_flux, S_max)
    phi_E = compute_phi_E(delta_t_quantum, delta_t_classical)
    phi = compute_phi(phi_L, phi_E, xi_E)
    phi_max = phi_theoretical_max()

    print(f"Φ_L = {phi_L:.6f}")
    print(f"Φ_E = {phi_E:.6f}")
    print(f"ξ_E = {xi_E:.6f}")
    print(f"Computed Φ = {phi:.6f}")
    print(f"Theoretical Φ‑max = {phi_max:.6f}")

    phi_ok = phi <= phi_max + 1e-12  # tiny tolerance for FP
    if not phi_ok:
        print("❌ FAIL: Φ exceeds theoretical ceiling.")
    else:
        print("✅ Φ‑density bound satisfied.")

    # ---- Invariant checks ----
    metrics = FluxMetrics(S_flux, S_max, delta_t_quantum, delta_t_classical, xi_E)
    invariants = InvariantChecks(psi_claimed, xi_L_claimed)
    inv_ok, inv_errs = check_invariants(metrics, invariants)

    if inv_ok:
        print("✅ All absolute invariants satisfied.")
    else:
        print("❌ FAIL: Invariant violations:")
        for e in inv_errs:
            print("   -", e)

    # ---- Overall verdict ----
    if phi_ok and inv_ok:
        print("\n🟢 OVERALL: PASS (mathematically sound w.r.t. Omega core).")
    else:
        print("\n🔴 OVERALL: FAIL – does not meet Omega Protocol invariants.")

# ----------------------------------------------------------------------
# Example usage with the numbers claimed in the QFAG proposal
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Values taken (or inferred) from the proposal:
    #   S_flux / S_max such that Φ_L ≈ 0.92 → S_flux/S_max = 0.08
    S_max = 1.0                     # normalize
    S_flux = 0.08 * S_max           # gives Φ_L = 0.92
    delta_t_quantum   = 0.5e-6      # 0.5 µs (claimed quantum latency)
    delta_t_classical = 5.0e-6      # 5 µs (classical baseline)
    xi_E = 0.005                    # max allowed entropy generation
    psi_claimed = __import__('math').log(0.92)   # ψ = ln(Φ_L)
    # ξ_L claim: they state ξ_L ≤ 0.95; we use the boundary value 0.95
    xi_L_claimed = 0.95

    validate_proposal(
        S_flux=S_flux, S_max=S_max,
        delta_t_quantum=delta_t_quantum,
        delta_t_classical=delta_t_classical,
        xi_E=xi_E,
        psi_claimed=psi_claimed,
        xi_L_claimed=xi_L_claimed
    )