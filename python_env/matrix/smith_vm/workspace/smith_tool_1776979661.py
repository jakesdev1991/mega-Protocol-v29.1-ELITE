# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Invariant Validator for the Bureaucratic Decision Manifold spec.

This script translates the key mathematical definitions from the supplied C++ 
specification into Python and runs a battery of sanity‑checks to verify:
  * All quantities remain dimensionless and lie in their declared ranges.
  * The exponential damping term is dimensionless.
  * Goal‑integrity (Ψ_id) and COD thresholds are respected after smoothing.
  * The “Procedural Black Hole” condition is detected correctly.
  * Φ‑density accounting never yields a negative net value when the system
    is considered stable (i.e., when invariants hold).

If any assertion fails, an AssertionError is raised with a helpful message.
"""

import math
import random
from typing import List, Tuple

# ----------------------------------------------------------------------
# Constants taken directly from the spec (all dimensionless)
# ----------------------------------------------------------------------
PSI_ID_THRESHOLD = 0.95          # Goal Integrity lower bound
COD_THRESHOLD    = 0.80          # Minimum acceptable COD
H_TOP_LIMIT      = 0.85          # Max allowed Topological Impedance
XI_BOUND_DEFAULT = 1.5
XI_BOUND_MAX     = 3.0
XI_BOUND_MIN     = 0.5
LAMBDA_COUPLING  = 1.0           # dimensionless coupling for exp(-Λ*H_top)

# ----------------------------------------------------------------------
# Helper data structures
# ----------------------------------------------------------------------
class DecisionNode:
    __slots__ = ("approval_cost", "risk_variance", "node_id")
    def __init__(self, approval_cost: float, risk_variance: float, node_id: str):
        self.approval_cost   = max(0.0, min(1.0, approval_cost))
        self.risk_variance   = max(0.0, min(1.0, risk_variance))
        self.node_id         = node_id

# ----------------------------------------------------------------------
# Core mathematical functions (mirroring the C++ implementation)
# ----------------------------------------------------------------------
def calculate_topological_impedance(path: List[DecisionNode]) -> float:
    """
    H_top = Σ(cost_i * var_i) / Σ(cost_i)   clamped to [0,1]
    """
    total_impedance = 0.0
    total_length    = 0.0
    for node in path:
        total_impedance += node.approval_cost * node.risk_variance
        total_length    += node.approval_cost
    if total_length == 0.0:
        return 0.0
    raw = total_impedance / total_length
    return min(1.0, max(0.0, raw))

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Returns cosine similarity in [-1, 1]; assumes same length."""
    dot = sum(ai * bi for ai, bi in zip(a, b))
    mag_a = math.sqrt(sum(ai * ai for ai in a))
    mag_b = math.sqrt(sum(bi * bi for bi in b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot / (mag_a * mag_b)

def calculate_cod_decision(intent: List[float],
                           outcome: List[float],
                           H_top: float) -> float:
    """
    COD = Fidelity * exp(-Λ * H_top)
    Fidelity = |<Intent|Outcome>|  (cosine similarity, taken as absolute value)
    """
    fidelity = abs(cosine_similarity(intent, outcome))  # enforce non‑negative
    damping  = math.exp(-LAMBDA_COUPLING * H_top)       # Λ and H_top are dimensionless
    return fidelity * damping

def check_procedural_black_hole(H_top: float, Xi_bound: float) -> bool:
    """
    Returns True if the system is in a Procedural Black Hole state.
    Condition: H_top > H_TOP_LIMIT AND Xi_bound > 0.9 * XI_BOUND_MAX
    """
    return (H_top > H_TOP_LIMIT) and (Xi_bound > 0.9 * XI_BOUND_MAX)

def geodesic_smoothing_operator(path: List[DecisionNode],
                                intent: List[float],
                                outcome: List[float],
                                Xi_bound: float) -> Tuple[List[DecisionNode],
                                                          List[float],
                                                          float]:
    """
    Implements the smoothing gate described in the spec.
    Returns the (possibly) pruned path, the (possibly) adjusted outcome,
    and the updated Xi_bound.
    """
    # ----- Phase 1: diagnostic -----
    H_top   = calculate_topological_impedance(path)
    COD     = calculate_cod_decision(intent, outcome, H_top)

    # If already stable, do nothing
    if COD >= COD_THRESHOLD and not check_procedural_black_hole(H_top, Xi_bound):
        return path, outcome, Xi_bound

    # ----- Phase 2: curvature reduction (node pruning) -----
    # Work on a copy so we can rollback if identity breaks
    cur_path   = list(path)
    cur_outcome= list(outcome)
    cur_H_top  = H_top

    # Identify high‑curvature nodes (cost*var > 0.5)
    high_curv_idx = [i for i, n in enumerate(cur_path)
                     if (n.approval_cost * n.risk_variance) > 0.5]
    # Sort descending by curvature contribution
    high_curv_idx.sort(key=lambda i: (cur_path[i].approval_cost *
                                      cur_path[i].risk_variance),
                       reverse=True)

    for idx in high_curv_idx:
        if cur_H_top <= 0.9 * H_TOP_LIMIT:   # safety buffer
            break

        # Simulate removal: outcome shifts by -0.05 per dimension (as in spec)
        shifted_outcome = [v - 0.05 for v in cur_outcome]
        # Re‑compute COD with the shifted outcome (using current H_top * 0.8 as
        # an optimistic estimate of impedance after removal)
        temp_COD = calculate_cod_decision(intent, shifted_outcome,
                                          cur_H_top * 0.8)

        if temp_COD < PSI_ID_THRESHOLD:   # identity risk -> stop pruning
            break

        # Actually prune the node
        cur_path.pop(idx)
        cur_H_top = calculate_topological_impedance(cur_path)
        cur_outcome = shifted_outcome   # keep the shifted version

    # ----- Phase 3: stiffness modulation -----
    if cur_H_top < 0.5 * H_TOP_LIMIT:
        Xi_bound = min(XI_BOUND_MAX, Xi_bound * 1.1)

    # ----- Phase 4: entropy accounting (just a warning in spec) -----
    # We compute risk entropy but do not alter flow; we only assert it stays
    # within a reasonable bound for the test harness.
    risk_entropy = sum(node.risk_variance for node in cur_path)
    # The spec warns if risk_entropy > 0.8 * H_TOP_LIMIT; we record it.
    # (No automatic rollback here – the validator will flag violations.)
    _ = risk_entropy  # placeholder to avoid unused‑variable warnings

    return cur_path, cur_outcome, Xi_bound

def monitor_phi_density(throughput: float,
                        impedance_cost: float,
                        risk_leak: float) -> float:
    """
    Φ_Net = Throughput - Impedance_Cost - Risk_Leak
    Returns the net Φ‑density.
    """
    return throughput - impedance_cost - risk_leak

# ----------------------------------------------------------------------
# Validation harness
# ----------------------------------------------------------------------
def run_validation(trials: int = 1000) -> None:
    random.seed(42)  # deterministic for CI

    for t in range(trials):
        # ---- Randomly generate a decision path ----
        path_len = random.randint(1, 8)
        path = [DecisionNode(random.random(), random.random(),
                             f"N{i}") for i in range(path_len)]

        # ---- Random intent/outcome vectors (same length) ----
        vec_len = random.randint(2, 6)
        intent = [random.uniform(-1, 1) for _ in range(vec_len)]
        outcome = [random.uniform(-1, 1) for _ in range(vec_len)]

        # ---- Random system stiffness ----
        Xi_bound = random.uniform(XI_BOUND_MIN, XI_BOUND_MAX)

        # ---- 1. Basic range checks on core metrics ----
        H_top = calculate_topological_impedance(path)
        assert 0.0 <= H_top <= 1.0, f"H_top out of bounds: {H_top}"

        COD = calculate_cod_decision(intent, outcome, H_top)
        assert 0.0 <= COD <= 1.0, f"COD out of bounds: {COD} (intent={intent}, outcome={outcome}, H_top={H_top})"

        # Exponential damping argument must be dimensionless – already satisfied by construction
        # (Lambda is dimensionless, H_top is dimensionless)

        # ---- 2. Procedural Black Hole detection logic ----
        in_black_hole = check_procedural_black_hole(H_top, Xi_bound)
        # The condition should match the definition:
        expected = (H_top > H_TOP_LIMIT) and (Xi_bound > 0.9 * XI_BOUND_MAX)
        assert in_black_hole == expected, (
            f"Black hole detection mismatch: H_top={H_top}, Xi_bound={Xi_bound}"
        )

        # ---- 3. Geodesic smoothing preserves Goal Integrity (Ψ_id) ----
        new_path, new_outcome, new_Xi = geodesic_smoothing_operator(
            path, intent, outcome, Xi_bound
        )
        # After smoothing, COD must be at least the threshold (or we are in a black hole)
        new_H_top = calculate_topological_impedance(new_path)
        new_COD   = calculate_cod_decision(intent, new_outcome, new_H_top)
        if not check_procedural_black_hole(new_H_top, new_Xi):
            assert new_COD >= COD_THRESHOLD, (
                f"Post‑smoothing COD below threshold: {new_COD} "
                f"(H_top={new_H_top}, Xi={new_Xi})"
            )
        # Goal integrity (Ψ_id) is represented by PSI_ID_THRESHOLD; the spec
        # requires that we never drop below this when we prune.
        # We already enforced this inside the operator, but double‑check:
        assert new_COD >= PSI_ID_THRESHOLD or check_procedural_black_hole(new_H_top, new_Xi), (
            f"Goal integrity violated: COD={new_COD} < {PSI_ID_THRESHOLD}"
        )

        # ---- 4. Φ‑density accounting ----
        # For a "stable" configuration we expect non‑negative net Φ.
        # We define a simple proxy:
        #   throughput  = 1.0 / (1.0 + new_H_top)   (higher impedance → lower throughput)
        #   impedance_cost = new_H_top               (cost proportional to impedance)
        #   risk_leak    = sum(risk_variance) / len(new_path)   (average risk per node)
        throughput  = 1.0 / (1.0 + new_H_top)
        impedance_cost = new_H_top
        risk_leak = (sum(n.risk_variance for n in new_path) /
                     max(1, len(new_path)))
        phi_net = monitor_phi_density(throughput, impedance_cost, risk_leak)
        # If the system is NOT in a black hole, we demand phi_net >= 0.
        if not check_procedural_black_hole(new_H_top, new_Xi):
            assert phi_net >= -1e-9, (
                f"Negative Φ‑density in stable state: {phi_net} "
                f"(throughput={throughput}, cost={impedance_cost}, leak={risk_leak})"
            )

    print(f"All {trials} validation trials passed. The spec respects Omega Protocol invariants.")

# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    run_validation()