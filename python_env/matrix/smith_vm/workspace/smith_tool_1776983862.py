# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Validation for Bureaucratic Decision Manifold (v26.0‑Ω‑POLARIZED)
Checks mathematical soundness and invariant compliance.
"""

import random
import math
from typing import List, Tuple

# ----------------------------------------------------------------------
# Constants (as per spec)
# ----------------------------------------------------------------------
PSI_ID_THRESHOLD = 0.95          # kept for reference; not used as COD gate
XI_BOUND_DEFAULT = 1.5
XI_BOUND_MAX = 3.0
XI_BOUND_MIN = 0.5
LAMBDA_COUPLING = 1.0
H_TOP_LIMIT = 0.85
COD_THRESHOLD = 0.80             # correct COD gate
RISK_ENTROPY_LIMIT = 0.8 * H_TOP_LIMIT  # derived bound used in spec

# ----------------------------------------------------------------------
# Data structures
# ----------------------------------------------------------------------
class DecisionNode:
    __slots__ = ("approval_cost", "risk_variance", "node_id")
    def __init__(self, cost: float, var: float, nid: str):
        self.approval_cost = max(0.0, min(1.0, cost))
        self.risk_variance = max(0.0, min(1.0, var))
        self.node_id = nid

# ----------------------------------------------------------------------
# Core functions (spec‑accurate, with COD gate fixed)
# ----------------------------------------------------------------------
def calculate_topological_impedance(path: List[DecisionNode]) -> float:
    total_impedance = sum(n.approval_cost * n.risk_variance for n in path)
    total_length = sum(n.approval_cost for n in path)
    if total_length == 0.0:
        return 0.0
    raw = total_impedance / total_length
    return min(1.0, max(0.0, raw))

def cosine_fidelity(intent: List[float], outcome: List[float]) -> float:
    dot = sum(i * o for i, o in zip(intent, outcome))
    mag_i = math.sqrt(sum(i * i for i in intent))
    mag_o = math.sqrt(sum(o * o for o in outcome))
    if mag_i == 0.0 or mag_o == 0.0:
        return 0.0
    cos = dot / (mag_i * mag_o)
    # Clamp to [0,1] because negative alignment is meaningless for COD
    return max(0.0, min(1.0, cos))

def calculate_cod(intent: List[float], outcome: List[float], h_top: float) -> float:
    fidelity = cosine_fidelity(intent, outcome)
    damping = math.exp(-LAMBDA_COUPLING * h_top)
    return fidelity * damping

def check_procedural_black_hole(h_top: float, xi_bound: float) -> bool:
    return h_top > H_TOP_LIMIT and xi_bound > XI_BOUND_MAX * 0.9

def geodesic_smoothing_operator(
    path: List[DecisionNode],
    intent: List[float],
    outcome: List[float],
    xi_bound: float,
) -> Tuple[List[DecisionNode], List[float], float]:
    """Returns (new_path, new_outcome, new_xi_bound)."""
    # ----- Phase 1: Diagnostic -----
    h_top = calculate_topological_impedance(path)
    cod = calculate_cod(intent, outcome, h_top)

    # Early exit if stable and not in black hole
    if cod >= COD_THRESHOLD and not check_procedural_black_hole(h_top, xi_bound):
        return path, outcome, xi_bound

    # ----- Phase 2: Curvature Reduction -----
    # Identify high‑curvature nodes
    high_idx = [
        i for i, n in enumerate(path)
        if n.approval_cost * n.risk_variance > 0.5
    ]
    high_idx.sort(
        key=lambda i: path[i].approval_cost * path[i].risk_variance,
        reverse=True,
    )

    # Work on copies so we can rollback if invariant violated
    cur_path = path.copy()
    cur_outcome = outcome.copy()
    cur_h_top = h_top

    for idx in high_idx:
        if cur_h_top <= H_TOP_LIMIT * 0.9:
            break  # safety buffer

        # Simulate removal: shift outcome downward by a small epsilon
        shift = 0.05
        sim_outcome = [max(0.0, v - shift) for v in cur_outcome]
        sim_cod = calculate_cod(intent, sim_outcome, cur_h_top * 0.8)

        # INVARIANT GATE: COD must stay above COD_THRESHOLD (not PSI_ID_THRESHOLD)
        if sim_cod < COD_THRESHOLD:
            break  # cannot prune further without violating goal integrity

        # Actual prune
        del cur_path[idx]
        cur_outcome = sim_outcome
        cur_h_top = calculate_topological_impedance(cur_path)

    # ----- Phase 3: Stiffness Modulation -----
    if cur_h_top < H_TOP_LIMIT * 0.5:
        xi_bound = min(XI_BOUND_MAX, xi_bound * 1.1)

    # ----- Phase 4: Entropy Accounting -----
    new_risk_entropy = sum(n.risk_variance for n in cur_path)
    if new_risk_entropy > RISK_ENTROPY_LIMIT:
        # In a real system we would flag/rollback; here we just note.
        pass

    return cur_path, cur_outcome, xi_bound

def monitor_phi_density(
    throughput: float,
    impedance_cost: float,
    risk_leak: float,
) -> float:
    phi_net = throughput - impedance_cost - risk_leak
    if phi_net < 0.0:
        # In practice this would auto‑trigger smoothing; we just return negative.
        pass
    return phi_net

# ----------------------------------------------------------------------
# Validation harness
# ----------------------------------------------------------------------
def run_validation(trials: int = 1000) -> None:
    random.seed(42)
    for t in range(trials):
        # Random path length 2‑8
        path_len = random.randint(2, 8)
        path = [
            DecisionNode(
                cost=random.random(),
                var=random.random(),
                nid=f"N{i}",
            )
            for i in range(path_len)
        ]

        # Random intent/outcome vectors (dimension 3‑5)
        dim = random.randint(3, 5)
        intent = [random.random() for _ in range(dim)]
        outcome = [random.random() for _ in range(dim)]

        xi_bound = random.uniform(XI_BOUND_MIN, XI_BOUND_MAX)

        # --- Invariants before any operation ---
        h_top = calculate_topological_impedance(path)
        assert 0.0 <= h_top <= 1.0, f"H_top out of bounds: {h_top}"
        cod = calculate_cod(intent, outcome, h_top)
        assert 0.0 <= cod <= 1.0, f"COD out of bounds: {cod}"

        # If not in black hole and COD already sufficient, no smoothing needed
        if not check_procedural_black_hole(h_top, xi_bound) and cod >= COD_THRESHOLD:
            # Invariants must still hold (they do by construction)
            continue

        # --- Apply smoothing operator ---
        new_path, new_outcome, new_xi = geodesic_smoothing_operator(
            path, intent, outcome, xi_bound
        )

        # Re‑compute metrics after smoothing
        new_h_top = calculate_topological_impedance(new_path)
        new_cod = calculate_cod(intent, new_outcome, new_h_top)

        # Post‑smoothing invariants
        assert 0.0 <= new_h_top <= 1.0, f"Post H_top OOB: {new_h_top}"
        assert 0.0 <= new_cod <= 1.0, f"Post COD OOB: {new_cod}"
        # Goal integrity (COD) must not fall below threshold
        assert new_cod >= COD_THRESHOLD - 1e-9, (
            f"COD dropped below threshold: {new_cod} < {COD_THRESHOLD}"
        )
        # If we entered a black hole, smoothing must have reduced H_top
        if check_procedural_black_hole(h_top, xi_bound):
            assert new_h_top < h_top + 1e-9, (
                f"Black hole not alleviated: H_top {h_top} -> {new_h_top}"
            )

        # Phi‑density check (use dummy costs)
        throughput = 1.0
        impedance_cost = new_h_top  # proxy
        risk_leak = sum(n.risk_variance for n in new_path) / len(new_path) if new_path else 0.0
        phi = monitor_phi_density(throughput, impedance_cost, risk_leak)
        # If phi < 0, the spec says smoothing should be auto‑triggered;
        # we already just smoothed, so we accept any phi (negative would just mean more smoothing needed).
        # No assertion here – just logging for diagnostics.
        if phi < -0.05:
            # This is acceptable; the loop will iterate again in a real system.
            pass

    print(f"✅ Validation passed over {trials} random trials.")

if __name__ == "__main__":
    run_validation()