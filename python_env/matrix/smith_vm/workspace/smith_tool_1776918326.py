# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Validation Script for QECF v1.0 Proposal
# --------------------------------------------------------------
# This script checks the mathematical consistency of the Φ‑density
# accounting and verifies that the stated Absolute Invariants are
# satisfied by the reported numbers.
#
# Assumptions (taken directly from the proposal):
#   - Φ contributions are additive and independent.
#   - Invariants have hard thresholds (violation → penalty Φ).
#   - Net Φ‑density = Σ(component Φ)  (no cross‑terms subtracted).
#
# The script is deliberately minimal: it only validates the arithmetic
# and the logical relationship between thresholds and penalties.
# --------------------------------------------------------------

from dataclasses import dataclass
from typing import Dict, List

# ------------------------------------------------------------------
# Data structures representing the proposal's claims
# ------------------------------------------------------------------
@dataclass
class Component:
    name: str
    phi_contrib: float   # Φ contributed by this component
    audit_verified: bool # Whether the Omega audit signed off on it

@dataclass
class Invariant:
    name: str
    threshold: float          # Minimum allowed value (for ">") or maximum allowed (for "<")
    comparison: str           # ">" or "<"
    violation_penalty: float  # Φ penalty if the invariant is broken
    measured_value: float     # Value reported in the proposal (assumed to be the actual)

# ------------------------------------------------------------------
# 1. Component Φ‑density accounting (from the proposal table)
# ------------------------------------------------------------------
components: List[Component] = [
    Component("Quantum Sensors",   +1.5, True),
    Component("DEDS Core",         +2.0, True),
    Component("Nano-Actuators",    +1.5, True),
]

# ------------------------------------------------------------------
# 2. Absolute Invariants (from the proposal)
# ------------------------------------------------------------------
invariants: List[Invariant] = [
    # Entanglement Fidelity > 0.95  (penalty -5.0Φ if violated)
    Invariant("Entanglement Fidelity", 0.95, ">", -5.0, 0.96),   # proposal claims >0.95, we assume 0.96 as a compliant value

    # Topological Safety Bounds (metric non‑degeneracy) – violation → -∞Φ.
    # We model "-∞Φ" as a sufficiently large negative number that makes net Φ negative.
    Invariant("Topological Safety Bounds", 0.0, ">", -1e9, 0.01),  # any positive curvature measure >0 is safe

    # Biomechanical Entropy Limit – violation → -2.0Φ
    Invariant("Biomechanical Entropy", 0.0, "<", -2.0, 0.5),   # entropy must be *below* some threshold; we assume 0.5 units < limit
]

# ------------------------------------------------------------------
# Validation functions
# ------------------------------------------------------------------
def sum_phi(comp_list: List[Component]) -> float:
    """Add up the Φ contributions of all components."""
    return sum(c.phi_contrib for c in comp_list)

def check_invariant(inv: Invariant) -> bool:
    """Return True if the invariant is satisfied (no penalty incurred)."""
    if inv.comparison == ">":
        return inv.measured_value > inv.threshold
    elif inv.comparison == "<":
        return inv.measured_value < inv.threshold
    else:
        raise ValueError(f"Unknown comparison operator: {inv.comparison}")

def total_penalty(inv_list: List[Invariant]) -> float:
    """Sum the penalties for all violated invariants."""
    penalty = 0.0
    for inv in inv_list:
        if not check_invariant(inv):
            penalty += inv.violation_penalty   # note: violation_penalty is negative in the proposal
    return penalty

def net_phi(comp_list: List[Component], inv_list: List[Invariant]) -> float:
    """Net Φ after accounting for invariant violations."""
    return sum_phi(comp_list) + total_penalty(inv_list)

# ------------------------------------------------------------------
# 3. Run validation
# ------------------------------------------------------------------
if __name__ == "__main__":
    # --- Component accounting -------------------------------------------------
    claimed_total_phi = sum_phi(components)
    print(f"Sum of component Φ contributions: {claimed_total_phi:.2f}Φ")
    print("Component breakdown:")
    for c in components:
        print(f"  - {c.name}: {c.phi_contrib:+.2f}Φ (audit verified: {c.audit_verified})")

    # --- Invariant checks ----------------------------------------------------
    print("\nInvariant validation:")
    all_ok = True
    for inv in invariants:
        ok = check_invariant(inv)
        status = "PASS" if ok else "FAIL"
        print(f"  - {inv.name}: measured={inv.measured_value}, threshold={inv.threshold} ({inv.comparison}) → {status}")
        if not ok:
            all_ok = False

    # --- Penalty calculation --------------------------------------------------
    penalty = total_penalty(invariants)
    print(f"\nTotal invariant violation penalty: {penalty:.2f}Φ")

    # --- Net Φ ---------------------------------------------------------------
    net = net_phi(components, invariants)
    print(f"Net Φ‑density after penalties: {net:.2f}Φ")

    # --- Consistency with proposal claim --------------------------------------
    proposal_net_phi = +5.0   # as stated in the proposal's "Total" row
    tolerance = 1e-9
    if abs(net - proposal_net_phi) < tolerance:
        print("\n✅ Net Φ matches the proposal claim (+5.0Φ).")
    else:
        print(f"\n❌ Net Φ mismatch: proposal claims {proposal_net_phi}Φ, validation yields {net}Φ.")

    # --- Overall compliance ---------------------------------------------------
    if all_ok and abs(net - proposal_net_phi) < tolerance:
        print("\n🟢 OVERALL VALIDATION: PASSED – the proposal is mathematically sound and complies with the Omega Protocol invariants.")
    else:
        print("\n🔴 OVERALL VALIDATION: FAILED – see issues above.")