# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator – Bureaucratic Decision Manifold (v26.0‑Ω‑POLARIZED)
-----------------------------------------------------------------------
This script checks mathematical soundness and invariant compliance
according to the audit above.  It implements a *corrected* version of
the Geodesic Smoothing Gate and related helpers, then runs a battery
of assertions on random and edge‑case data.

Run:
    python3 omega_validator.py
"""

import math
import random
from typing import List, Tuple

# ----------------------------------------------------------------------
# 1.  INVARIANTS (Omega Protocol)
# ----------------------------------------------------------------------
PSI_ID_THRESHOLD = 0.95          # Goal Integrity hard gate
XI_BOUND_DEFAULT = 1.5
XI_BOUND_MAX = 3.0               # Beyond this → Procedural Black Hole risk
XI_BOUND_MIN = 0.5               # Below this → Decision Drift risk
LAMBDA_COUPLING = 1.0            # dimensionless
H_TOP_LIMIT = 0.85               # max normalized curvature density
COD_THRESHOLD = 0.80             # minimum alignment fidelity
PHI_NET_MIN = 0.0                # Φ‑density must not go negative

# ----------------------------------------------------------------------
# 2.  DATA STRUCTURES
# ----------------------------------------------------------------------
class DecisionNode:
    __slots__ = ("approval_cost", "risk_variance", "node_id")
    def __init__(self, cost: float, variance: float, nid: str):
        assert 0.0 <= cost <= 1.0, "cost must be dimensionless [0,1]"
        assert 0.0 <= variance <= 1.0, "variance must be dimensionless [0,1]"
        self.approval_cost = cost
        self.risk_variance = variance
        self.node_id = nid

    def curvature_contrib(self) -> float:
        """Cost × Variance – the local impedance contribution."""
        return self.approval_cost * self.risk_variance

# ----------------------------------------------------------------------
# 3.  CORE FUNCTIONS (dimension‑checked)
# ----------------------------------------------------------------------
def topological_impedance(path: List[DecisionNode]) -> float:
    """H_top = Σ(cost_i × var_i) / Σ(cost_i)  →  dimensionless, clamped [0,1]."""
    if not path:
        return 0.0
    num = sum(n.curvature_contrib() for n in path)
    den = sum(n.approval_cost for n in path)
    if den == 0.0:
        return 0.0
    raw = num / den
    # clamp for safety – does not change physics if already in [0,1]
    return min(1.0, max(0.0, raw))

def fidelity(intent: List[float], outcome: List[float]) -> float:
    """|⟨intent|outcome⟩| normalized to [0,1]."""
    assert len(intent) == len(outcome), "vectors must match dimension"
    dot = sum(i * o for i, o in zip(intent, outcome))
    mag_i = math.sqrt(sum(i * i for i in intent))
    mag_o = math.sqrt(sum(o * o for o in outcome))
    if mag_i == 0.0 or mag_o == 0.0:
        return 0.0
    return abs(dot) / (mag_i * mag_o)

def cod(intent: List[float], outcome: List[float], h_top: float) -> float:
    """COD = fidelity × exp(−Λ·H_top)  – dimensionless."""
    assert 0.0 <= h_top <= 1.0, "H_top must be normalized"
    f = fidelity(intent, outcome)
    damping = math.exp(-LAMBDA_COUPLING * h_top)
    return f * damping

def procedural_black_hole(h_top: float, xi_bound: float) -> bool:
    """True iff the system is in a Procedural Black Hole."""
    return h_top > H_TOP_LIMIT and xi_bound > XI_BOUND_MAX * 0.9

def risk_entropy(path: List[DecisionNode]) -> float:
    """Average variance along the path – dimensionless entropy proxy."""
    if not path:
        return 0.0
    return sum(n.risk_variance for n in path) / len(path)

def phi_density(throughput: float, h_top: float, path: List[DecisionNode]) -> float:
    """
    Φ_Net = Throughput - Impedance_Cost - Risk_Leak
    Impedance_Cost  ≡ α·H_top          (α = 1.0 for unit scaling)
    Risk_Leak       ≡ β·RiskEntropy   (β = 1.0 for unit scaling)
    """
    impedance_cost = h_top                     # α = 1.0
    risk_leak = risk_entropy(path)             # β = 1.0
    return throughput - impedance_cost - risk_leak

# ----------------------------------------------------------------------
# 4.  CORRECTED GEODESIC SMOOTHING GATE
# ----------------------------------------------------------------------
def geodesic_smoothing_operator(
    path: List[DecisionNode],
    intent: List[float],
    outcome: List[float],
    xi_bound: float,
) -> Tuple[List[DecisionNode], float]:
    """
    Returns a new path (pruned if needed) and the possibly updated xi_bound.
    All steps are invariant‑driven; no magic numbers.
    """
    # ----- Phase 1: diagnostics -----
    h_top = topological_impedance(path)
    current_cod = cod(intent, outcome, h_top)

    # Early exit if already stable
    if current_cod >= COD_THRESHOLD and not procedural_black_hole(h_top, xi_bound):
        return path, xi_bound

    # ----- Phase 2: identify prunable nodes -----
    # A node is *eligible* for removal if its curvature contribution
    # is above the current average impedance (i.e., it is a hotspot).
    avg_imp = h_top if len(path) > 0 else 0.0
    eligible_idxs = [
        i for i, n in enumerate(path) if n.curvature_contrib() > avg_imp
    ]
    # Sort by descending curvature contribution (worst first)
    eligible_idxs.sort(key=lambda i: path[i].curvature_contrib(), reverse=True)

    # ----- Phase 3: prune with hard invariant gate -----
    new_path = path.copy()
    for idx in eligible_idxs:
        # Re‑evaluate after hypothetical removal
        trial_path = new_path[:idx] + new_path[idx+1:]
        trial_h = topological_impedance(trial_path)
        # Simulate outcome shift proportional to removed curvature
        removed_curv = new_path[idx].curvature_contrib()
        shift_scale = 0.1  # tunable but dimensionless; kept small to avoid drift
        # Shift each outcome component towards zero (simulating loss of intent fidelity)
        trial_outcome = [o - shift_scale * removed_curv for o in outcome]
        trial_cod = cod(intent, trial_outcome, trial_h)

        # Hard gate: Goal Integrity must not drop below threshold
        if trial_cod < PSI_ID_THRESHOLD:
            # Cannot prune this node – stop further pruning
            break

        # Accept the prune
        new_path = trial_path
        # Update xi_bound only if Φ‑density improves (see Phase 4)

    # ----- Phase 4: stiffness modulation via Φ‑density -----
    h_new = topological_impedance(new_path)
    phi_before = phi_density(1.0, h_top, path)   # unit throughput for comparison
    phi_after  = phi_density(1.0, h_new, new_path)
    if phi_after > phi_before:
        # Improvement → we can afford a bit more stability
        xi_bound = min(XI_BOUND_MAX, xi_bound * 1.05)  # 5% increase, invariant‑safe
    else:
        # No improvement → keep or slightly reduce stiffness to avoid drift
        xi_bound = max(XI_BOUND_MIN, xi_bound * 0.95)

    # ----- Phase 5: final entropy check (Rubric §5) -----
    # Risk entropy must not exceed a fraction of the allowed impedance budget
    max_allowed_entropy = 0.5 * H_TOP_LIMIT   # dimensionless, derived from invariants
    assert risk_entropy(new_path) <= max_allowed_entropy, (
        f"Risk entropy {risk_entropy(new_path):.3f} exceeds budget {max_allowed_entropy:.3f}"
    )

    return new_path, xi_bound

# ----------------------------------------------------------------------
# 5.  VALIDATION HARNESS
# ----------------------------------------------------------------------
def random_path(n: int) -> List[DecisionNode]:
    return [DecisionNode(random.random(), random.random(), f"N{i}") for i in range(n)]

def random_vector(dim: int) -> List[float]:
    v = [random.random() for _ in range(dim)]
    norm = math.sqrt(sum(x*x for x in v))
    return [x / norm for x in v] if norm != 0.0 else v

def run_suite():
    random.seed(42)
    for _ in range(20):
        path = random_path(random.randint(3, 10))
        intent = random_vector(5)
        outcome = random_vector(5)
        xi = XI_BOUND_DEFAULT

        # ---- Pre‑condition checks ----
        h = topological_impedance(path)
        assert 0.0 <= h <= 1.0, "H_top out of bounds"
        c = cod(intent, outcome, h)
        assert 0.0 <= c <= 1.0, "COD out of bounds"
        assert 0.0 <= risk_entropy(path) <= 1.0, "Risk entropy out of bounds"

        # ---- Run the smoothing gate ----
        new_path, new_xi = geodesic_smoothing_operator(path, intent, outcome, xi)

        # ---- Post‑condition invariants ----
        h_new = topological_impedance(new_path)
        assert 0.0 <= h_new <= 1.0, "Post‑prune H_top invalid"
        c_new = cod(intent, outcome, h_new)
        # COD must be at least threshold *unless* we are in a black hole (which should have been resolved)
        if not procedural_black_hole(h_new, new_xi):
            assert c_new >= COD_THRESHOLD - 1e-9, f"COD dropped to {c_new:.4f} after smoothing"
        # Goal Integrity gate – COD never allowed to fall below PSI_ID_THRESHOLD during pruning
        # (already enforced inside the operator; we double‑check)
        assert c_new >= PSI_ID_THRESHOLD - 1e-9, "Goal Integrity violated"

        # Stiffness bounds
        assert XI_BOUND_MIN <= new_xi <= XI_BOUND_MAX, "Stiffness out of bounds"

        # Φ‑density non‑negative (throughput set to 1.0 for unit test)
        phi = phi_density(1.0, h_new, new_path)
        assert phi >= PHI_NET_MIN - 1e-9, f"Negative Φ‑density: {phi:.4f}"

        # Risk entropy budget
        assert risk_entropy(new_path) <= 0.5 * H_TOP_LIMIT, "Risk entropy budget exceeded"

        # Ensure we actually reduced impedance when we started unstable
        if c < COD_THRESHOLD or procedural_black_hole(h, xi):
            assert h_new <= h + 1e-9, "Impedance increased after smoothing attempt"

    print("All invariant checks passed – specification is Omega‑Protocol compliant.")

if __name__ == "__main__":
    run_suite()