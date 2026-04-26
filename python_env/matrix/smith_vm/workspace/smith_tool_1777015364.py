# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Q-FAN Omega Protocol Invariant Validator
----------------------------------------
This script checks the three Absolute Invariants (Φ-1, Φ-2, Φ-3) for a single
control cycle of the Quantum Flux Adaptive Footwear Nexus (Q-FAN).

Assumptions:
- The shoe's adaptive lattice is represented as a set of nodes with 3‑D positions.
- Each node can only receive information from neighbours within its past light‑cone.
- Entropy is quantified as the Shannon entropy of the gait‑deviation distribution
  (provided as a float `entropy_current`; `entropy_initial` is the baseline).
- Topology is assessed via persistent homology; we require the Betti numbers
  of a 3‑sphere: β0=1, β1=0, β2=0, β3=1.
- The speed of light `c` is taken as 299_792_458 m/s (SI units).

If any invariant fails, an AssertionError is raised with a diagnostic message.
"""

from __future__ import annotations
import numpy as np
from typing import List, Tuple

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
C_LIGHT = 299_792_458  # m/s
ENTROPY_CAP_FACTOR = 1.021  # allowed increase = 2.1%
# Expected Betti numbers for a 3‑sphere (β0, β1, β2, β3)
EXPECTED_BETTI = np.array([1, 0, 0, 1], dtype=int)

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def light_cone_delay(pos_i: np.ndarray, pos_j: np.ndarray) -> float:
    """
    Minimum time for a signal to travel from node i to node j at speed c.
    """
    distance = np.linalg.norm(pos_i - pos_j)
    return distance / C_LIGHT

def check_causal_fidelity(
    nodes: List[np.ndarray],
    update_times: List[float],
    max_allowed_dt: float,
) -> None:
    """
    Φ-1: No update shall occur sooner than the light‑cone delay permits.
    `nodes[i]` is the position of node i.
    `update_times[i]` is the timestamp at which node i applied its latest
    topological adjustment (seconds since some epoch).
    `max_allowed_dt` is the maximum permissible Δt between successive
    control cycles (should be >= actual cycle time).
    """
    n = len(nodes)
    for i in range(n):
        for j in range(i + 1, n):
            # The earliest time node j could have influenced node i:
            min_dt_ij = light_cone_delay(nodes[i], nodes[j])
            # If node i updated *before* it could have received info from j,
            # we have a violation (unless the update was purely local and
            # independent of j – we conservatively treat any cross‑node
            # dependency as a potential violation).
            if update_times[i] < update_times[j] - min_dt_ij:
                raise AssertionError(
                    f"Φ-1 violation: node {i} updated at {update_times[i]:.3e}s "
                    f"before node {j}'s influence could arrive "
                    f"(min delay {min_dt_ij:.3e}s)."
                )
    # Optional: also ensure the global cycle time respects the cap
    if max_allowed_dt < 0:
        raise AssertionError("Control cycle time must be non‑negative.")
    # (No explicit upper bound needed; we just verify no superluminal
    #  influences as above.)

def check_entropy_conservation(
    entropy_initial: float,
    entropy_current: float,
) -> None:
    """
    Φ-2: Total entropy must not exceed initial entropy × 1.021 (2.1% increase).
    """
    if entropy_current > entropy_initial * ENTROPY_CAP_FACTOR:
        raise AssertionError(
            f"Φ-2 violation: entropy {entropy_current:.6f} > "
            f"allowed {entropy_initial * ENTROPY_CAP_FACTOR:.6f} "
            f"(initial {entropy_initial:.6f})."
        )

def check_topological_integrity(
    betti_numbers: np.ndarray,
) -> None:
    """
    Φ-3: The lattice mesh must be homotopy‑equivalent to a 3‑sphere.
    We enforce equality of Betti numbers (necessary condition).
    """
    if betti_numbers.shape != EXPECTED_BETTI.shape:
        raise AssertionError(
            f"Φ-3 shape mismatch: got {betti_numbers.shape}, expected {EXPECTED_BETTI.shape}"
        )
    if not np.array_equal(betti_numbers, EXPECTED_BETTI):
        raise AssertionError(
            f"Φ-3 violation: Betti numbers {betti_numbers} do not match S³ {EXPECTED_BETTI}"
        )

# ----------------------------------------------------------------------
# Example usage (simulated data)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Simulate a small lattice of 8 nodes arranged roughly in a sphere.
    np.random.seed(42)
    # Random points on a unit sphere, then scale to ~0.1 m (shoe size)
    raw = np.random.normal(size=(8, 3))
    nodes = [raw[i] / np.linalg.norm(raw[i]) * 0.1 for i in range(8)]

    # Simulated update times (seconds since start of cycle)
    # We enforce that each node's update time is at least the light‑cone
    # delay from its neighbours; for simplicity we set all to the same value.
    cycle_time = 0.001  # 1 ms control loop
    update_times = [cycle_time] * 8

    # Entropy values (Shannon entropy of gait deviation)
    entropy_initial = 0.015  # baseline
    entropy_current = 0.0152  # slight increase, still within 2.1%

    # Betti numbers from a persistent homology call (mocked as perfect S³)
    betti = np.array([1, 0, 0, 1], dtype=int)

    # Run checks
    try:
        check_causal_fidelity(nodes, update_times, max_allowed_dt=cycle_time)
        print("✓ Φ-1 (Causal Fidelity) PASSED")
    except AssertionError as e:
        print("✗ Φ-1 FAILED:", e)

    try:
        check_entropy_conservation(entropy_initial, entropy_current)
        print("✓ Φ-2 (Kinetic Energy Conservation) PASSED")
    except AssertionError as e:
        print("✗ Φ-2 FAILED:", e)

    try:
        check_topological_integrity(betti)
        print("✓ Φ-3 (Topological Integrity) PASSED")
    except AssertionError as e:
        print("✗ Φ-3 FAILED:", e)

    print("\nAll invariant checks completed.")