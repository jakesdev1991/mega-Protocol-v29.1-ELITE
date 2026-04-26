# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for the Quantum Logistical Manifold Governor (QLMG)
------------------------------------------------------------------------------------
This script implements the three Absolute Invariants (Φ‑1, Φ‑2, Φ‑3) that any
Submission‑Grade design must satisfy.  It expects concrete, measurable inputs
derived from the system’s runtime logs or simulation outputs.  If any invariant
is violated, the validator raises an AssertionError with a diagnostic message.

The validator is deliberately *minimal*: it does **not** attempt to infer missing
data – the burden of providing the required quantities lies on the proposal.
If the proposal cannot supply them, the validation will fail, exposing the
missing Ω‑Protocol compliance.

Usage:
    >>> from omega_validator import validate_qlmg
    >>> validate_qlmg(route_adjustments, entropy_data, lattice_homology)
"""

from __future__ import annotations
import numpy as np
from typing import List, Tuple, Dict

# ----------------------------------------------------------------------
# Physical constants (adjust units to match your simulation/logging system)
# ----------------------------------------------------------------------
C_LIGHT = 299_792_458  # m/s – local causal speed limit


# ----------------------------------------------------------------------
# Helper utilities
# ----------------------------------------------------------------------
def _check_causal_fidelity(
    adjustments: List[Tuple[float, float, float]]
) -> None:
    """
    Φ‑1 (Causal Fidelity):
        No route adjustment shall propagate faster than local causal influence (c).

    Parameters
    ----------
    adjustments : list of (delta_t, distance, description)
        delta_t   – time elapsed between the decision and the effect (seconds)
        distance  – spatial separation of the affected nodes (metres)
        description – optional label for debugging
    """
    for dt, dist, desc in adjustments:
        if dt < 0:
            raise AssertionError(f"[{desc}] Negative time delta ({dt}s) violates causality.")
        max_allowed = dist / C_LIGHT
        if dt < max_allowed - 1e-12:  # tiny tolerance for floating‑point noise
            raise AssertionError(
                f"[{desc}] Superluminal adjustment: dt={dt:.3e}s < d/c={max_allowed:.3e}s "
                f"(distance={dist:.1f}m)."
            )


def _check_entropy_conservation(
    entropy_initial: float,
    entropy_final: float,
    tolerance: float = 0.021
) -> None:
    """
    Φ‑2 (Logistical Entropy Conservation):
        Total entropy ≤ initial + 2.1 %.

    Entropy is assumed to be a non‑negative scalar (e.g., Shannon entropy of route
    deviation distribution, or topological entropy of the fleet lattice).  A
    decrease is allowed; only an increase beyond the tolerance is prohibited.

    Parameters
    ----------
    entropy_initial : float
        Entropy at the start of the observation window.
    entropy_final : float
        Entropy at the end of the observation window.
    tolerance : float
        Allowed fractional increase (default 0.021 → 2.1 %).
    """
    if entropy_initial < 0 or entropy_final < 0:
        raise AssertionError("Entropy values must be non‑negative.")
    allowed_max = entropy_initial * (1.0 + tolerance)
    if entropy_final > allowed_max + 1e-12:
        raise AssertionError(
            f"Entropy increase exceeds Φ‑2 bound: "
            f"S₀={entropy_initial:.6f}, S={entropy_final:.6f}, "
            f"allowed ≤ {allowed_max:.6f} (increase {((entropy_final/entropy_initial)-1)*100:.2f}%)."
        )


def _check_topological_integrity(
    betti_numbers: Tuple[int, int, int, int]
) -> None:
    """
    Φ‑3 (Topological Integrity):
        Fleet lattice must be homotopy‑equivalent to a 3‑torus.

    For a 3‑torus T³ the Betti numbers are:
        b₀ = 1  (connected components)
        b₁ = 3  (independent 1‑cycles)
        b₂ = 3  (independent 2‑cycles)
        b₃ = 1  (independent 3‑cycle)

    Parameters
    ----------
    betti_numbers : tuple (b0, b1, b2, b3)
        Integer Betti numbers computed from the fleet lattice (e.g., via persistent
        homology or simplicial complex analysis).
    """
    expected = (1, 3, 3, 1)
    if betti_numbers != expected:
        raise AssertionError(
            f"Topological invariant Φ‑3 failed: "
            f"observed Betti numbers {betti_numbers} ≠ expected {expected} "
            f"(fleet lattice not homotopy‑equivalent to T³)."
        )


# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def validate_qlmg(
    route_adjustments: List[Tuple[float, float, str]],
    entropy_initial: float,
    entropy_final: float,
    lattice_betti: Tuple[int, int, int, int],
) -> None:
    """
    Run all three Omega Protocol invariant checks.

    Parameters
    ----------
    route_adjustments : list of (delta_t [s], distance [m], description)
        Each entry represents a discrete routing decision enacted by the QLMG.
    entropy_initial : float
        Entropy of the logistics informational substrate before the window.
    entropy_final : float
        Entropy after the window.
    lattice_betti : tuple of four ints
        Betti numbers (b0, b1, b2, b3) of the fleet lattice topology.

    Raises
    ------
    AssertionError
        If any invariant is violated, with a message identifying the offending
        invariant and the offending datum.
    """
    _check_causal_fidelity(route_adjustments)
    _check_entropy_conservation(entropy_initial, entropy_final)
    _check_topological_integrity(lattice_betti)

    # If we reach this point, all invariants hold.
    print("[Ω‑Validator] All Absolute Invariants (Φ‑1, Φ‑2, Φ‑3) satisfied.")


# ----------------------------------------------------------------------
# Example usage (illustrative only – replace with real telemetry)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Dummy data that *would* pass the validator:
    example_adjustments = [
        (0.005, 1_000_000, "City‑wide reroute after accident"),   # dt=5 ms, d=1000 km → d/c≈3.33 ms → violates! (intentionally bad)
        (0.010, 100_000, "Neighbourhood load‑balancing"),        # dt=10 ms, d=100 km → d/c≈0.33 ms → OK
    ]
    S0 = 12.4          # arbitrary entropy units
    S1 = 12.55         # ~1.2 % increase → within 2.1 %
    betti = (1, 3, 3, 1)   # perfect 3‑torus

    try:
        validate_qlmg(example_adjustments, S0, S1, betti)
    except AssertionError as e:
        print(f"[Ω‑Validator] INVARIANT VIOLATION: {e}")