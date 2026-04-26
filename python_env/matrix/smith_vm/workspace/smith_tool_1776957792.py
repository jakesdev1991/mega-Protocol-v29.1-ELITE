# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for the QULN proposal
--------------------------------------------------------
This script checks the three Absolute Invariants (Φ‑1, Φ‑2, Φ‑3) that the
Quantum‑Entangled Urban Logistics Nexus (QULN) must never violate.
It also verifies internal consistency of the claimed Φ‑density contributions.

Usage:
    >>> from omega_validator import check_invariants
    >>> result = check_invariants(
    ...     decision_latency=0.0,          # seconds (negative would imply retrocausality)
    ...     data_latency=0.1,              # seconds
    ...     entropy_initial=100.0,
    ...     entropy_final=103.0,           # must be ≤ entropy_initial * 1.05
    ...     topological_changes=0,         # 0 = no change in homotopy type (3‑sphere)
    ...     phi_claims=[3.0, 2.5, 2.7]     # claimed Φ‑density gains per mechanism
    ... )
    >>> print(result)
"""

from dataclasses import dataclass
from typing import List, Tuple

# ----------------------------------------------------------------------
# Omega Protocol constants (as defined by the proposal)
# ----------------------------------------------------------------------
PHI_1_PENALTY = float('-inf')   # Causal Fidelity violation
PHI_2_PENALTY = -2.0            # Informational Mass Conservation violation
PHI_3_PENALTY = -1.5            # Topological Integrity violation

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def causal_fidelity_ok(decision_latency: float, data_latency: float) -> bool:
    """
    Φ‑1: No decision shall propagate faster than the local speed of causal influence.
    In discrete‑time terms: decision cannot be made before the data that informs it
    arrives (i.e., decision_latency >= data_latency).  Equality is allowed
    (perfect causal alignment → Φ‑density = 1.0).
    """
    return decision_latency >= data_latency

def informational_mass_ok(entropy_initial: float, entropy_final: float) -> bool:
    """
    Φ‑2: Total informational entropy shall never exceed initial conditions + 5%.
    """
    return entropy_final <= entropy_initial * 1.05

def topological_integrity_ok(topological_changes: int) -> bool:
    """
    Φ‑3: The delivery mesh shall remain homotopy‑equivalent to a 3‑sphere.
    We encode any change that alters the homotopy class as a non‑zero integer.
    """
    return topological_changes == 0

def phi_density_consistency(claimed_gains: List[float]) -> Tuple[bool, float]:
    """
    Simple sanity check: the sum of claimed gains must be non‑negative
    and must not exceed a reasonable physical bound (here we use +10Φ as
    a conservative ceiling; any claim beyond this is flagged as numerology).
    """
    total = sum(claimed_gains)
    ok = 0.0 <= total <= 10.0   # arbitrary but sane upper bound for illustration
    return ok, total

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
@dataclass
class ValidationResult:
    phi1_ok: bool
    phi2_ok: bool
    phi3_ok: bool
    phi_density_ok: bool
    phi_density_total: float
    overall_pass: bool
    penalty: float

def check_invariants(
    decision_latency: float,
    data_latency: float,
    entropy_initial: float,
    entropy_final: float,
    topological_changes: int,
    phi_claims: List[float]
) -> ValidationResult:
    """
    Evaluate the QULN design against the Omega Protocol Absolute Invariants.
    Returns a ValidationResult detailing which checks passed and the net
    penalty (if any) according to the proposal's penalty scheme.
    """
    # Invariant checks
    phi1 = causal_fidelity_ok(decision_latency, data_latency)
    phi2 = informational_mass_ok(entropy_initial, entropy_final)
    phi3 = topological_integrity_ok(topological_changes)

    # Φ‑density sanity check
    phi_density_ok, total_phi = phi_density_consistency(phi_claims)

    # Compute penalty (only if invariant violated)
    penalty = 0.0
    if not phi1:
        penalty += PHI_1_PENALTY   # -∞ → overall system invalid
    if not phi2:
        penalty += PHI_2_PENALTY
    if not phi3:
        penalty += PHI_3_PENALTY

    overall_pass = phi1 and phi2 and phi3 and phi_density_ok

    return ValidationResult(
        phi1_ok=phi1,
        phi2_ok=phi2,
        phi3_ok=phi3,
        phi_density_ok=phi_density_ok,
        phi_density_total=total_phi,
        overall_pass=overall_pass,
        penalty=penalty
    )

# ----------------------------------------------------------------------
# Example usage (illustrates why the original QULN proposal fails)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example inputs that reflect the QULN claims:
    # - decision_latency < data_latency (superluminal/retrocausal claim)
    # - entropy increase claimed to be used as "free fuel" (no export)
    # - topological changes unspecified → assume possible non‑zero
    # - claimed Φ‑density gains as in the proposal
    example = check_invariants(
        decision_latency=-0.05,   # decision made 0.05 s before data arrives
        data_latency=0.10,
        entropy_initial=100.0,
        entropy_final=115.0,      # +15 % > allowed +5 %
        topological_changes=1,    # assume a handle/wormhole introduced
        phi_claims=[3.0, 2.5, 2.7]
    )

    print("=== Omega Protocol Invariant Validation ===")
    print(f"Φ‑1 (Causal Fidelity)      : {'PASS' if example.phi1_ok else 'FAIL'}")
    print(f"Φ‑2 (Informational Mass)   : {'PASS' if example.phi2_ok else 'FAIL'}")
    print(f"Φ‑3 (Topological Integrity): {'PASS' if example.phi3_ok else 'FAIL'}")
    print(f"Φ‑density sanity check     : {'PASS' if example.phi_density_ok else 'FAIL'} "
          f"(sum = {example.phi_density_total:.2f}Φ)")
    print(f"Overall compliance         : {'PASS' if example.overall_pass else 'FAIL'}")
    print(f"Net penalty (Φ)            : {example.penalty}")
    if not example.overall_pass:
        print("\nConclusion: The QULN proposal violates one or more Omega Protocol "
              "Absolute Invariants and must be revised before submission.")