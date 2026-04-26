# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Agent Smith Invariant Validator for Quantum-Adaptive Lattice Footwear (QALF)
Checks:
  Φ-1: lattice must be genus-0 (betti0=1, betti1=0)
  Φ-2: total entropy increase ≤ 1.5% of initial entropy
  Φ-3: actuation latency Δt ≥ d/c (causal bound)
"""

import numpy as np
import gudhi as gd   # Gudhi library for persistent homology

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def compute_betti_numbers(simplex_tree):
    """Return betti_0, betti_1 from a Gudhi simplex tree."""
    betti = simplex_tree.betti_numbers()
    # Ensure we have at least two dimensions
    b0 = betti[0] if len(betti) > 0 else 0
    b1 = betti[1] if len(betti) > 1 else 0
    return b0, b1

def shannon_entropy(probabilities):
    """Shannon entropy (base 2) for a discrete distribution."""
    p = np.asarray(probabilities, dtype=float)
    p = p[p > 0]  # avoid log2(0)
    return -np.sum(p * np.log2(p))

def entropy_increase_percent(initial_entropy, final_entropy):
    """Percent increase relative to initial."""
    if initial_entropy == 0:
        return np.inf
    return 100.0 * (final_entropy - initial_entropy) / initial_entropy

def causal_latency_ok(max_path_length, distance, c=299792458.0):
    """
    Verify Δt >= d/c.
    max_path_length: longest directed path length in the consensus graph (in seconds)
    distance: spatial separation that the signal must cover (meters)
    """
    return max_path_length >= distance / c

# ----------------------------------------------------------------------
# Mock data representing a runtime snapshot
# ----------------------------------------------------------------------
# 1. Simplicial complex of the lattice (example: a triangulated disc)
#    Vertices: 0..5, Triangles fill a disc shape -> genus 0
simplices = [
    [0,1,2], [0,2,3], [0,3,4], [0,4,5],   # fan triangles
    [1,2,3], [2,3,4], [3,4,5]             # interior fill
]
st = gd.SimplexTree()
for s in simplices:
    st.insert(s)
st.compute_persistence()

b0, b1 = compute_betti_numbers(st)

# 2. Entropy bookkeeping
#    Initial defect distribution (uniform over 6 sites)
initial_defects = np.ones(6) / 6.0
initial_entropy = shannon_entropy(initial_defects)

#    After a time step, defects have slightly shifted (non‑uniform)
final_defects = np.array([0.2, 0.15, 0.2, 0.15, 0.15, 0.15])
final_entropy = shannon_entropy(final_defects)

entropy_pct_inc = entropy_increase_percent(initial_entropy, final_entropy)

# 3. Causal latency
#    Consensus graph: longest directed path measured as 3.2e-9 s (3.2 ns)
#    Maximum separation across the sole: 0.12 m (12 cm)
max_path_length = 3.2e-9   # seconds
sole_diameter   = 0.12     # meters
causal_ok = causal_latency_ok(max_path_length, sole_diameter)

# ----------------------------------------------------------------------
# Invariant evaluation
# ----------------------------------------------------------------------
print("=== Smith Audit Invariant Check ===")
print(f"Φ-1 (Genus-0): b0={b0}, b1={b1}  -> {'PASS' if (b0==1 and b1==0) else 'FAIL'}")
print(f"Φ-2 (Entropy increase): {entropy_pct_inc:.3f}%  -> {'PASS' if entropy_pct_inc <= 1.5 else 'FAIL'}")
print(f"Φ-3 (Causal latency): Δt={max_path_length:.2e}s, d/c={sole_diameter/299792458:.2e}s  -> {'PASS' if causal_ok else 'FAIL'}")

overall_pass = (b0==1 and b1==0) and (entropy_pct_inc <= 1.5) and causal_ok
print("\nOVERALL:", "PASS" if overall_pass else "FAIL")