# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validator for Quantum-Adaptive Lattice Footwear (QALF) proposal.

This script checks the mathematical soundness of the informational‑first
claims made in the Engine's pleading (the revised QALF proposal) and
verifies compliance with the Omega Protocol invariants:

    Φ_L = 1 - S_defects / S_max                     (lattice informational mode)
    Φ_E = Δt_quantum / Δt_classical                (terrain‑energy informational mode)
    ξ_E ≤ 0.015                                      (entropy‑cap invariant)
    Φ = Φ_L + Φ_E - ξ_E                              (total Φ‑density)

Additionally, the protocol requires **dimensional homogeneity**:
    Φ must be used consistently either as a *bounded density* [0,1]
    *or* as an *additive entropy‑like quantity*.  Mixing the two
    interpretations is a violation.

The script flags any invariant breach or dimensional inconsistency.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Tuple


@dataclass
class QALFParameters:
    """Input parameters needed to evaluate the QALF informational model."""
    S_defects: float          # Shannon entropy of lattice defects (bits)
    S_max: float              # Maximum possible defect entropy (bits)
    dt_quantum: float         # Actuation latency achieved by quantum protocol (s)
    dt_classical: float       # Light‑travel‑time bound d/c (s)
    xi_E: float               # Entropy‑cap invariant (fraction of S_max)


def compute_modes(p: QALFParameters) -> Tuple[float, float, float]:
    """
    Returns (Φ_L, Φ_E, Φ) according to the Omega‑Protocol formulas.
    """
    if p.S_max <= 0:
        raise ValueError("S_max must be > 0")
    if p.dt_classical <= 0:
        raise ValueError("dt_classical (d/c) must be > 0")

    Φ_L = 1.0 - p.S_defects / p.S_max
    Φ_E = p.dt_quantum / p.dt_classical
    Φ = Φ_L + Φ_E - p.xi_E
    return Φ_L, Φ_E, Φ


def validate_invariants(p: QALFParameters) -> Tuple[bool, list[str]]:
    """
    Checks all Omega Protocol invariants and dimensional consistency.
    Returns (is_compliant, list_of_violation_messages).
    """
    violations = []

    # --- Invariant Φ_L bounds (informational mode must be a probability) ---
    Φ_L, Φ_E, Φ = compute_modes(p)
    if not (0.0 <= Φ_L <= 1.0 + 1e-12):   # tiny tolerance for floating‑point
        violations.append(
            f"Φ_L = {Φ_L:.6f} outside [0,1] (S_defects={p.S_defects}, S_max={p.S_max})"
        )

    # --- Invariant Φ_E must respect causality (Δt_quantum ≥ Δt_classical) ---
    if Φ_E < 1.0 - 1e-12:
        violations.append(
            f"Φ_E = {Φ_E:.6f} < 1 implies Δt_quantum < Δt_classical "
            f"(dt_quantum={p.dt_quantum}, dt_classical={p.dt_classical})"
        )

    # --- Entropy‑cap invariant ---
    if p.xi_E > 0.015 + 1e-12:
        violations.append(
            f"ξ_E = {p.xi_E:.6f} exceeds allowed 0.015 (1.5%)"
        )

    # --- Dimensional homogeneity check ---
    # The proposal treats Φ both as a bounded density (0.89) and as an additive
    # term (+4.8Φ).  We detect this by seeing if the instantaneous Φ (computed
    # from the model) is claimed to be a density *and* if an additive gain is
    # reported that would push the total far above 1.
    instantaneous_phi_claim = 0.89   # from the proposal's "Φ‑density = 0.89"
    additive_gain_claim = 4.8        # from "+4.8Φ"
    net_phi_claim = instantaneous_phi_claim + additive_gain_claim  # 5.69

    # If the model yields a Φ that is clearly a density (≈0.9) but the paper
    # also adds a large additive constant, we flag a dimensional mismatch.
    if abs(Φ - instantaneous_phi_claim) < 0.05:   # model matches the claimed density
        if additive_gain_claim > 0.1:             # any non‑trivial additive term
            violations.append(
                f"Dimensional inconsistency: Φ treated as density ({instantaneous_phi_claim}) "
                f"yet an additive gain of {additive_gain_claim}Φ is added, yielding net {net_phi_claim}Φ. "
                "Φ must be used consistently as either a bounded density [0,1] or an additive entropy‑like quantity."
            )
    else:
        # If the model does NOT match the claimed instantaneous density, that's also a problem.
        violations.append(
            f"Model Φ ({Φ:.6f}) does not match the claimed instantaneous Φ‑density "
            f"({instantaneous_phi_claim}). Check the definition of Φ_L, Φ_E, ξ_E."
        )

    # --- Plausibility sanity checks (optional but useful) ---
    # Bekenstein bound: maximum entropy in a sphere of radius R is S_max ≤ 2π k_B R E / (ħ c ln2)
    # We cannot verify without R and E, but we can warn if S_defects > S_max (already caught).
    # Decoherence: T2 > 1 ms at 300 K is claimed; we cannot verify without temperature model.

    compliant = len(violations) == 0
    return compliant, violations


def demo():
    """
    Example run using numbers that *could* satisfy the invariants.
    Adjust the parameters to see where the proposal fails.
    """
    # Example set that tries to meet the claims:
    #   S_defects = 0.1 * S_max  → Φ_L = 0.9
    #   dt_quantum = dt_classical → Φ_E = 1.0 (minimal causal compliance)
    #   ξ_E = 0.01                → within 1.5%
    S_max = 1.0          # normalize to 1 bit for simplicity
    S_defects = 0.1 * S_max
    dt_classical = 1e-9  # 1 ns light‑travel time (example)
    dt_quantum = dt_classical  # saturates the bound
    xi_E = 0.01

    params = QALFParameters(
        S_defects=S_defects,
        S_max=S_max,
        dt_quantum=dt_quantum,
        dt_classical=dt_classical,
        xi_E=xi_E,
    )

    compliant, msgs = validate_invariants(params)
    Φ_L, Φ_E, Φ = compute_modes(params)

    print("=== QALF Omega‑Protocol Validation ===")
    print(f"Input: S_defects={S_defects:.3f}, S_max={S_max:.3f}")
    print(f"       dt_quantum={dt_quantum:.3e}s, dt_classical={dt_classical:.3e}s")
    print(f"       ξ_E={xi_E:.3f}")
    print()
    print(f"Computed modes: Φ_L={Φ_L:.6f}, Φ_E={Φ_E:.6f}, Φ={Φ:.6f}")
    print()
    if compliant:
        print("✅ All Omega Protocol invariants satisfied (dimensional homogeneity OK).")
    else:
        print("❌ Invariant violations detected:")
        for m in msgs:
            print("   -", m)
    print()
    # Show the instantaneous vs additive claim mismatch if present
    instantaneous_phi_claim = 0.89
    additive_gain_claim = 4.8
    net_phi_claim = instantaneous_phi_claim + additive_gain_claim
    print(f"Claimed instantaneous Φ‑density : {instantaneous_phi_claim}")
    print(f"Claimed additive gain            : +{additive_gain_claim}Φ")
    print(f"Claimed net Φ‑density            : {net_phi_claim}Φ")
    print(f"Model‑derived Φ (instantaneous)  : {Φ:.6f}")
    if abs(Φ - instantaneous_phi_claim) < 0.05 and additive_gain_claim > 0.1:
        print("⚠️  Dimensional inconsistency flagged (see violations above).")


if __name__ == "__main__":
    demo()