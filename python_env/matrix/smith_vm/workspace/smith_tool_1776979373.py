# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator – Bureaucratic Decision Manifold
Checks mathematical soundness and invariant compliance.
"""

import random
import math
from typing import List, Tuple

# -------------------------- INVARIANTS (Omega Protocol) --------------------------
PSI_ID_THRESHOLD = 0.95          # Goal Integrity
COD_THRESHOLD    = 0.80          # Minimum Alignment
H_TOP_LIMIT      = 0.85          # Max Topological Impedance
XI_BOUND_DEFAULT = 1.5
XI_BOUND_MAX     = 3.0
XI_BOUND_MIN     = 0.5
LAMBDA_COUPLING  = 1.0           # dimensionless

# -------------------------- DATA STRUCTURES --------------------------
class DecisionNode:
    __slots__ = ("approval_cost", "risk_variance", "node_id")
    def __init__(self, cost: float, variance: float, nid: str):
        self.approval_cost     = max(0.0, min(1.0, cost))
        self.risk_variance     = max(0.0, min(1.0, variance))
        self.node_id           = nid

# -------------------------- CORE FUNCTIONS (fixed) --------------------------
def topological_impedance(path: List[DecisionNode]) -> float:
    """H_top = Σ(cost_i * var_i) / Σ(cost_i)  → clamped [0,1]."""
    num = sum(n.approval_cost * n.risk_variance for n in path)
    den = sum(n.approval_cost for n in path)
    if den == 0.0:
        return 0.0
    raw = num / den
    return max(0.0, min(1.0, raw))

def fidelity(intent: List[float], outcome: List[float]) -> float:
    """Normalized dot‑product → [0,1]."""
    if not intent or not outcome or len(intent) != len(outcome):
        return 0.0
    dot = sum(i * o for i, o in zip(intent, outcome))
    mag_i = math.sqrt(sum(i * i for i in intent))
    mag_o = math.sqrt(sum(o * o for o in outcome))
    if mag_i == 0.0 or mag_o == 0.0:
        return 0.0
    return dot / (mag_i * mag_o)

def cod_decision(intent: List[float], outcome: List[float], H_top: float) -> float:
    """COD = fidelity * exp(-Lambda * H_top)."""
    fid = fidelity(intent, outcome)
    damping = math.exp(-LAMBDA_COUPLING * H_top)
    return fid * damping

def check_procedural_black_hole(H_top: float, Xi_bound: float) -> bool:
    """Returns True if the system is in a Procedural Black Hole."""
    return (H_top > H_TOP_LIMIT) and (Xi_bound > XI_BOUND_MAX * 0.9)

def geodesic_smoothing_operator(
    path: List[DecisionNode],
    intent: List[float],
    outcome: List[float],
    Xi_bound: float
) -> Tuple[List[DecisionNode], List[float], float]:
    """
    Attempts to reduce H_top by pruning high‑curvature nodes
    while preserving COD ≥ COD_THRESHOLD and Ψ_id ≥ PSI_ID_THRESHOLD.
    Returns (new_path, new_outcome, new_Xi_bound).
    """
    # ----- Phase 1: diagnostics -----
    H_top = topological_impedance(path)
    current_cod = cod_decision(intent, outcome, H_top)
    # Goal Integrity approximated by fidelity (no damping)
    psi_id = fidelity(intent, outcome)

    # If already within bounds, do nothing
    if current_cod >= COD_THRESHOLD and psi_id >= PSI_ID_THRESHOLD:
        return path, outcome, Xi_bound

    # ----- Phase 2: curvature‑based pruning -----
    # Nodes ranked by contribution to impedance (cost*var)
    ranked = sorted(
        [(i, n.approval_cost * n.risk_variance) for i, n in enumerate(path)],
        key=lambda x: x[1],
        reverse=True
    )

    new_path = path.copy()
    for idx, _ in ranked:
        # Tentative removal
        trial_path = new_path[:idx] + new_path[idx+1:]
        trial_H = topological_impedance(trial_path)
        trial_cod = cod_decision(intent, outcome, trial_H)
        trial_psi = fidelity(intent, outcome)   # outcome unchanged in this simple model

        # Invariant checks
        if trial_cod >= COD_THRESHOLD and trial_psi >= PSI_ID_THRESHOLD:
            new_path = trial_path
        else:
            # Removing this node would break an invariant → stop pruning
            break

        # Early exit if we are comfortably below the limit
        if topological_impedance(new_path) < H_TOP_LIMIT * 0.5:
            break

    # ----- Phase 3: stiffness modulation -----
    final_H = topological_impedance(new_path)
    if final_H < H_TOP_LIMIT * 0.5:
        Xi_bound = min(XI_BOUND_MAX, Xi_bound * 1.1)
    else:
        # If still high, we may need to increase stiffness cautiously
        Xi_bound = max(XI_BOUND_MIN, Xi_bound * 0.9)

    # Outcome is left unchanged in this toy model; in a full spec it would be
    # recomputed from the surviving nodes. For validation we keep it.
    return new_path, outcome, Xi_bound

def monitor_phi_density(throughput: float, impedance_cost: float, risk_leak: float) -> float:
    """Φ_Net = Throughput – Impedance_Cost – Risk_Leak."""
    return throughput - impedance_cost - risk_leak

# -------------------------- VALIDATION HARNESS --------------------------
def random_path(length: int = 5) -> List[DecisionNode]:
    return [DecisionNode(random.random(), random.random(), f"n{i}") for i in range(length)]

def random_vector(dim: int = 4) -> List[float]:
    v = [random.random() for _ in range(dim)]
    norm = math.sqrt(sum(x*x for x in v))
    return [x/norm for x in v] if norm > 0.0 else v

def run_trials(n_trials: int = 1000) -> None:
    failures = 0
    for t in range(n_trials):
        path   = random_path(random.randint(3, 8))
        intent = random_vector()
        outcome = random_vector()   # start with a random outcome (may be misaligned)
        Xi_bound = XI_BOUND_DEFAULT

        # Apply smoothing operator
        new_path, new_out, new_Xi = geodesic_smoothing_operator(path, intent, outcome, Xi_bound)

        # Re‑compute invariants
        H_top   = topological_impedance(new_path)
        cod     = cod_decision(intent, new_out, H_top)
        psi_id  = fidelity(intent, new_out)

        # Check invariants
        if not (cod >= COD_THRESHOLD - 1e-9 and psi_id >= PSI_ID_THRESHOLD - 1e-9):
            print(f"Trial {t:04d} FAILED:")
            print(f"  COD={cod:.4f} (need ≥{COD_THRESHOLD}), Ψ_id={psi_id:.4f} (need ≥{PSI_ID_THRESHOLD})")
            print(f"  H_top={H_top:.4f}, Xi_bound={new_Xi:.4f}")
            failures += 1

        # Also ensure we never exceed the impedance limit (should be prevented by operator)
        if H_top > H_TOP_LIMIT + 1e-9:
            print(f"Trial {t:04d} IMPEDANCE OVERFLOW: H_top={H_top:.4f} > {H_TOP_LIMIT}")
            failures += 1

    if failures == 0:
        print(f"✅ All {n_trials} trials passed – invariants respected.")
    else:
        print(f"❌ {failures}/{n_trials} trials violated invariants.")

# -------------------------- EXECUTION --------------------------
if __name__ == "__main__":
    run_trials()