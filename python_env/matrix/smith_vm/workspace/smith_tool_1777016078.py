# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QLMG Invariant Validator
------------------------
Validates the three Absolute Invariants (Φ-1, Φ-2, Φ-3) for a
snapshot of the Adaptive Logistics Mesh (ALM).

Dependencies:
    numpy, gudhi, scipy
Install via: pip install numpy gudhi scipy
"""

import numpy as np
from scipy.spatial.distance import pdist, squareform
import gudhi as gd

# ----------------------------------------------------------------------
# Constants (can be loaded from a config file or runtime telemetry)
# ----------------------------------------------------------------------
C = 299_792_458          # speed of light in m/s
ENTROPY_BOUND_FACTOR = 0.021   # 2.1% excess entropy allowed
TORUS_BETTI = np.array([1, 3, 3, 1])  # b0,b1,b2,b3 for T^3
# ----------------------------------------------------------------------


def check_causal_fidelity(events: np.ndarray) -> bool:
    """
    Φ-1: No adjustment faster than c.
    events: shape (N, 4) -> [t, x, y, z] timestamps and positions.
    Returns True if all pairwise adjustments respect causality.
    """
    # Sort by time to only consider forward-in-time adjustments
    events = events[np.argsort(events[:, 0])]
    dt = np.diff(events[:, 0])                     # time differences
    dxyz = np.diff(events[:, 1:], axis=0)          # spatial differences
    dist = np.linalg.norm(dxyz, axis=1)            # Euclidean distance
    # Causality condition: Δt >= distance / c
    return np.all(dt >= dist / C)


def compute_route_entropy(deviations: np.ndarray) -> float:
    """
    Φ-2: Shannon entropy of route deviation magnitudes.
    deviations: 1D array of scalar deviation values (e.g., metres off‑nominal).
    Returns entropy in bits.
    """
    # Bin deviations into a histogram (choose bin width via Freedman‑Diaconis)
    if len(deviations) == 0:
        return 0.0
    q75, q25 = np.percentile(deviations, [75, 25])
    bin_width = 2 * (q75 - q25) * len(deviations) ** (-1/3)
    bin_width = max(bin_width, 1e-9)
    bins = np.arange(min(deviations), max(deviations) + bin_width, bin_width)
    hist, _ = np.histogram(deviations, bins=bins, density=True)
    # Remove zero probabilities for log2
    hist = hist[hist > 0]
    return -np.sum(hist * np.log2(hist))


def check_entropy_bound(current_entropy: float, baseline_entropy: float) -> bool:
    """
    Φ-2: S <= S0 * (1 + 0.021)
    """
    return current_entropy <= baseline_entropy * (1 + ENTROPY_BOUND_FACTOR)


def check_topological_integrity(points: np.ndarray) -> bool:
    """
    Φ-3: Fleet lattice must be homotopy‑equivalent to a 3‑torus.
    Uses Vietoris‑Rips complex; computes Betti numbers up to dimension 3.
    """
    # Build Rips complex with a generous max edge length (tunable)
    max_edge = np.percentile(pdist(points), 90)  # 90th percentile of pairwise distances
    rips = gd.RipsComplex(points=points, max_edge_length=max_edge)
    simplex_tree = rips.create_simplex_tree(max_dimension=3)
    simplex_tree.compute_persistence()
    betti = simplex_tree.betti_numbers()
    # Ensure we have at least 4 dimensions; pad with zeros if needed
    betti = np.array(betti + [0] * (4 - len(betti)))
    return np.array_equal(betti, TORUS_BETTI)


# ----------------------------------------------------------------------
# Example usage (replace with real telemetry feeds in production)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # 1. Simulated route‑adjustment events: [t(s), x(m), y(m), z(m)]
    np.random.seed(42)
    n_events = 150
    times = np.sort(np.random.uniform(0, 3600, n_events))  # within an hour
    positions = np.random.normal(loc=0, scale=500, size=(n_events, 3))  # ±500m jitter
    events = np.column_stack([times, positions])

    # 2. Simulated deviation magnitudes (metres off the nominal geodesic)
    deviations = np.random.exponential(scale=2.0, size=n_events)  # mean 2m error

    # 3. Baseline entropy (pre‑deployment) – could be stored from a reference run
    baseline_entropy = compute_route_entropy(np.random.exponential(2.0, 1000))

    # 4. Current fleet node positions (for topology check)
    fleet_nodes = np.random.uniform(-1000, 1000, size=(200, 3))  # 200 vehicles in a 2km cube

    # ---- Run checks ----------------------------------------------------
    assert check_causal_fidelity(events), "Φ-1 VIOLATION: Superluminal route adjustment detected."
    print("✓ Φ-1 Causal Fidelity satisfied.")

    current_entropy = compute_route_entropy(deviations)
    assert check_entropy_bound(current_entropy, baseline_entropy), \
        f"Φ-2 VIOLATION: Entropy {current_entropy:.3f} > bound {baseline_entropy*(1+ENTROPY_BOUND_FACTOR):.3f}"
    print(f"✓ Φ-2 Entropy bound satisfied (S={current_entropy:.3f} bits).")

    assert check_topological_integrity(fleet_nodes), "Φ-3 VIOLATION: Fleet lattice not 3‑torus."
    print("✓ Φ-3 Topological Integrity satisfied (Betti numbers match T^3).")

    print("\nAll Omega Protocol invariants validated. QLMG snapshot is compliant.")