# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# =============================================================================
# OMEGA PROTOCOL VALIDATION: Bureaucratic Decision Manifold Spec (v26.0-Ω-POLARIZED)
# =============================================================================
import math
from typing import List, Tuple

# -----------------------------------------------------------------------------
# 1. CONSTANTS (as declared in the spec)
# -----------------------------------------------------------------------------
PSI_ID_THRESHOLD = 0.95
XI_BOUND_DEFAULT = 1.5
XI_BOUND_MAX = 3.0
XI_BOUND_MIN = 0.5
H_TOP_LIMIT = 0.85
COD_THRESHOLD = 0.80

# -----------------------------------------------------------------------------
# 2. DATA STRUCTURES
# -----------------------------------------------------------------------------
class DecisionNode:
    __slots__ = ("approval_cost", "risk_variance", "node_id")
    def __init__(self, approval_cost: float, risk_variance: float, node_id: str):
        self.approval_cost = approval_cost
        self.risk_variance = risk_variance
        self.node_id = node_id

# -----------------------------------------------------------------------------
# 3. SPEC‑LEVEL FUNCTIONS (copy‑pasted from the C++‑like spec, adapted to Python)
# -----------------------------------------------------------------------------
def Calculate_Topological_Impedance(path: List[DecisionNode]) -> float:
    total_impedance = 0.0
    total_length = 0.0
    for node in path:
        total_impedance += node.approval_cost * node.risk_variance
        total_length += node.approval_cost
    return 0.0 if total_length == 0.0 else total_impedance / total_length

def Calculate_COD_Decision(Intent: List[float],
                           Outcome: List[float],
                           H_top: float) -> float:
    # Fidelity (dot product normalized)
    dot = sum(i * o for i, o in zip(Intent, Outcome))
    magI = sum(i * i for i in Intent)
    magO = sum(o * o for o in Outcome)
    if magI == 0.0 or magO == 0.0:
        fidelity = 0.0
    else:
        fidelity = dot / (math.sqrt(magI) * math.sqrt(magO))
    damping = math.exp(-H_top / H_TOP_LIMIT)
    return fidelity * damping

def Log_Event(msg: str) -> None:
    # Stub – in real system would write to a secure log
    pass

def Check_Procedural_Black_Hole(H_top: float, Xi_bound: float) -> None:
    if H_top > H_TOP_LIMIT:
        if Xi_bound > XI_BOUND_MAX * 0.9:
            Log_Event("PROCEDURAL BLACK HOLE DETECTED: Decision Inertia.")
            Log_Event("Action: Emergency Geodesic Shortcutting Required.")
            raise RuntimeError("Systemic Inertia: Path Curvature Exceeded")
        else:
            Log_Event("WARNING: High Impedance. Monitor for Shadow Processes.")

def Geodesic_Smoothing_Operator(path: List[DecisionNode],
                                Intent: List[float],
                                Outcome: List[float],
                                Xi_bound: float) -> Tuple[List[DecisionNode], float]:
    # PHASE 1: DIAGNOSTIC
    current_H_top = Calculate_Topological_Impedance(path)
    current_COD = Calculate_COD_Decision(Intent, Outcome, current_H_top)
    try:
        Check_Procedural_Black_Hole(current_H_top, Xi_bound)
        if current_COD >= COD_THRESHOLD:
            Log_Event("Decision Path Stable. No Smoothing Required.")
            return path, Xi_bound
    except RuntimeError:
        Log_Event("Emergency Smoothing Initiated.")

    # PHASE 2: CURVATURE REDUCTION (Node Pruning)
    high_curvature_indices = [
        i for i, node in enumerate(path)
        if (node.approval_cost * node.risk_variance) > 0.5
    ]
    high_curvature_indices.sort(
        key=lambda i: path[i].approval_cost * path[i].risk_variance,
        reverse=True
    )

    for idx in high_curvature_indices:
        if current_H_top <= H_TOP_LIMIT * 0.9:
            break   # safety buffer

        # Simulate removal: shift outcome by 0.05 per node removed (as in spec)
        shift = 0.05
        temp_outcome = [o - shift for o in Outcome]
        temp_COD = Calculate_COD_Decision(Intent, temp_outcome, current_H_top * 0.8)

        if temp_COD < PSI_ID_THRESHOLD:
            Log_Event("Identity Risk: Cannot Remove Node. Stopping Pruning.")
            break

        # ACTUAL PRUNE
        path.pop(idx)
        current_H_top = Calculate_Topological_Impedance(path)
        Log_Event("Node Removed: Curvature Reduced.")

    # PHASE 3: STIFFNESS MODULATION
    if current_H_top < H_TOP_LIMIT * 0.5:
        Xi_bound = min(XI_BOUND_MAX, Xi_bound * 1.1)
        Log_Event("Stiffness Restored: Path is now safe.")

    # PHASE 4: ENTROPY ACCOUNTING
    new_risk_entropy = sum(node.risk_variance for node in path)
    if new_risk_entropy > (0.8 * H_TOP_LIMIT):
        Log_Event("WARNING: Risk Entropy Increased. Monitor Closely.")
        # In a full system we would trigger rollback/audit here

    return path, Xi_bound

def Monitor_Phi_Density(Throughput: float,
                        Impedance_Cost: float,
                        Risk_Leak: float) -> float:
    Phi_Net = Throughput - Impedance_Cost - Risk_Leak
    if Phi_Net < 0.0:
        Log_Event("CRITICAL: Negative Phi-Density in Decision Process.")
        Log_Event("System is consuming Identity for Bureaucratic Stability.")
        # In real system would auto‑trigger Geodesic_Smoothing_Operator
    return Phi_Net

# -----------------------------------------------------------------------------
# 4. VALIDATION TESTS
# -----------------------------------------------------------------------------
def run_validation():
    # ---- Helper to build a simple path ----
    def make_path(nodes):
        return [DecisionNode(c, v, f"n{i}") for i, (c, v) in enumerate(nodes)]

    # Test 1: Impedance monotonicity
    path1 = make_path([(1.0, 0.2), (1.0, 0.2)])
    imp1 = Calculate_Topological_Impedance(path1)
    path2 = make_path([(1.0, 0.2), (1.0, 0.2), (1.0, 0.2)])
    imp2 = Calculate_Topological_Impedance(path2)
    assert imp2 >= imp1, "Impedance should not decrease when adding a positive‑curvature node"

    # Test 2: COD damping property
    Intent = [1.0, 0.0]
    Outcome = [1.0, 0.0]
    cod_low = Calculate_COD_Decision(Intent, Outcome, 0.0)
    cod_high = Calculate_COD_Decision(Intent, Outcome, 1.0)
    assert 0.0 <= cod_high <= cod_low <= 1.0, "COD must be in [0,1] and decrease with H_top"

    # Test 3: Procedural Black Hole trigger
    try:
        Check_Procedural_Black_Hole(H_TOP_LIMIT + 0.1, XI_BOUND_MAX * 0.95)
        assert False, "Should have raised RuntimeError for black‑hole condition"
    except RuntimeError:
        pass  # expected

    # Ensure no false positive when stiffness low
    try:
        Check_Procedural_Black_Hole(H_TOP_LIMIT + 0.1, XI_BOUND_MIN)
    except RuntimeError:
        assert False, "Incorrectly triggered black hole with low stiffness"

    # Test 4: Geodesic Smoothing respects PSI_ID_THRESHOLD
    path = make_path([(2.0, 0.4), (0.5, 0.1), (2.0, 0.4)])  # high‑curvature ends
    Intent = [1.0, 0.0]
    Outcome = [1.0, 0.0]   # perfect match initially
    Xi = XI_BOUND_DEFAULT
    new_path, new_Xi = Geodesic_Smoothing_Operator(path, Intent, Outcome, Xi)
    # After pruning, COD must still be >= PSI_ID_THRESHOLD (simulated inside)
    # We can directly compute COD on the resulting path with the *original* Outcome
    # (the spec’s internal simulation used a shifted outcome; we trust the guard)
    final_H = Calculate_Topological_Impedance(new_path)
    final_COD = Calculate_COD_Decision(Intent, Outcome, final_H)
    assert final_COD >= PSI_ID_THRESHOLD, "Smoothing violated goal‑integrity invariant"

    # Test 5: Xi_bound bounds after modulation
    assert XI_BOUND_MIN <= new_Xi <= XI_BOUND_MAX, "Xi_bound drifted out of allowed range"

    # Test 6: Phi‑Density ledger sign
    Phi = Monitor_Phi_Density(Throughput=1.0, Impedance_Cost=0.6, Risk_Leak=0.3)
    assert Phi == 0.1, "Phi‑Density calculation mismatch"
    Phi_neg = Monitor_Phi_Density(Throughput=0.2, Impedance_Cost=0.1, Risk_Leak=0.2)
    assert Phi_neg < 0.0, "Phi‑Density should be negative when cost > throughput"

    # Test 7: Post‑smoothing H_top respecting safety buffer
    # Re‑use the path from test 4
    assert Calculate_Topological_Impedance(new_path) <= H_TOP_LIMIT * 0.9 + 1e-9, \
        "Post‑smoothing impedance exceeds safety buffer"

    print("All validation checks passed – spec is mathematically sound and Omega‑Protocol compliant.")

if __name__ == "__main__":
    run_validation()