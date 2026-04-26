# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator – Bureaucratic Decision Manifold
=========================================================
This script mirrors the key mathematical constructs from the supplied C++ code
and asserts that all Omega‑Protocol invariants are respected under random
stress tests.
"""

import random
import math
from typing import List, Tuple

# ----------------------------------------------------------------------
# Helper utilities (stand‑ins for Log_Event, etc.)
# ----------------------------------------------------------------------
def Log_Event(msg: str):
    """Simple logger – in a real system this would feed the audit trail."""
    print(f"[LOG] {msg}")

# ----------------------------------------------------------------------
# Core data structures
# ----------------------------------------------------------------------
class SystemInvariants:
    def __init__(self, psi_id: float, xi_sys: float, kappa_sys_ind: float):
        self.psi_id = psi_id          # Goal Integrity
        self.xi_sys = xi_sys          # Bureaucratic Stiffness
        self.kappa_sys_ind = kappa_sys_ind  # System‑Individual Coupling

    # Hard invariant checks (Omega Rubric §3)
    def VerifyInvariants(self) -> bool:
        PSI_ID_MIN = 0.95
        XI_SYS_MAX = 3.0
        KAPPA_MAX = 1.0

        if self.psi_id < PSI_ID_MIN:
            Log_Event(f"CRITICAL: Goal Integrity Breached (psi_id={self.psi_id:.3f})")
            return False
        if self.xi_sys > XI_SYS_MAX:
            Log_Event(f"WARNING: Bureaucratic Stiffness Critical (xi_sys={self.xi_sys:.3f})")
            # Not a hard fail, but we note it
        if self.kappa_sys_ind > KAPPA_MAX:
            Log_Event(f"CRITICAL: System-Individual Coupling Overload (kappa={self.kappa_sys_ind:.3f})")
            return False
        return True

    def CalculatePhiLoss(self) -> float:
        loss = 0.0
        if self.psi_id < 0.95:
            loss += (0.95 - self.psi_id) * 0.5
        if self.xi_sys > 3.0:
            loss += (self.xi_sys - 3.0) * 0.2
        return loss


class DecisionNode:
    def __init__(self, approval_cost: float, risk_variance: float, node_id: str):
        # Clamp to [0,1] as per spec
        self.approval_cost = max(0.0, min(1.0, approval_cost))
        self.risk_variance = max(0.0, min(1.0, risk_variance))
        self.node_id = node_id


class DecisionManifold:
    def __init__(self, path: List[DecisionNode],
                 intent_vector: List[float],
                 outcome_vector: List[float],
                 urgency_force: float):
        self.path = path
        self.intent_vector = intent_vector
        self.outcome_vector = outcome_vector
        self.urgency_force = max(0.0, min(1.0, urgency_force))  # dimensionless drive


# ----------------------------------------------------------------------
# Core mathematical functions (direct translations)
# ----------------------------------------------------------------------
def Calculate_Topological_Impedance(path: List[DecisionNode]) -> float:
    total_impedance = 0.0
    total_length = 0.0
    for node in path:
        total_impedance += node.approval_cost * node.risk_variance
        total_length += node.approval_cost
    if total_length == 0.0:
        return 0.0
    raw = total_impedance / total_length
    # Clamp to [0,1] for dimensionless consistency
    return max(0.0, min(1.0, raw))


def Calculate_COD_Decision(intent: List[float],
                           outcome: List[float],
                           H_top: float) -> float:
    # Fidelity = normalized dot product
    dot = sum(i * o for i, o in zip(intent, outcome))
    magI = sum(i * i for i in intent)
    magO = sum(o * o for o in outcome)
    if magI == 0.0 or magO == 0.0:
        fidelity = 0.0
    else:
        fidelity = dot / (math.sqrt(magI) * math.sqrt(magO))
    # Entropic damping
    LAMBDA_COUPLING = 1.0
    damping = math.exp(-LAMBDA_COUPLING * H_top)
    return fidelity * damping  # guaranteed in [0,1]


class FailureModeDetector:
    H_TOP_LIMIT = 0.85
    XI_SYS_MAX = 3.0
    XI_IND_THRESHOLD = 2.0

    @staticmethod
    def CheckRisk(H_top: float, Urgency: float, Xi_ind: float) -> str:
        if H_top > FailureModeDetector.H_TOP_LIMIT and Urgency < (FailureModeDetector.H_TOP_LIMIT * 0.5):
            return "PROCEDURAL_BLACK_HOLE"
        if Xi_ind > FailureModeDetector.XI_IND_THRESHOLD:
            return "INDIVIDUAL_BURNOUT"
        return "NONE"


def Geodesic_Smoothing_Operator(manifold: DecisionManifold,
                                invariants: SystemInvariants) -> None:
    # PHASE 1: DIAGNOSTIC
    current_H_top = Calculate_Topological_Impedance(manifold.path)
    current_COD = Calculate_COD_Decision(manifold.intent_vector,
                                         manifold.outcome_vector,
                                         current_H_top)
    Xi_ind = invariants.xi_sys * invariants.kappa_sys_ind
    detector = FailureModeDetector()
    failure = detector.CheckRisk(current_H_top, manifold.urgency_force, Xi_ind)

    if failure == FailureModeDetector.NONE and current_COD >= 0.80:
        return  # stable

    # PHASE 2: CURVATURE REDUCTION (node pruning)
    high_curvature_idx = []
    for i, node in enumerate(manifold.path):
        if node.approval_cost * node.risk_variance > 0.5:
            high_curvature_idx.append(i)
    high_curvature_idx.sort(key=lambda i: (manifold.path[i].approval_cost *
                                           manifold.path[i].risk_variance),
                            reverse=True)

    for idx in high_curvature_idx:
        if current_H_top <= detector.H_TOP_LIMIT * 0.9:
            break  # safety buffer

        # Simulate outcome shift to test psi_id preservation
        shift = 0.05
        temp_outcome = [v - shift for v in manifold.outcome_vector]
        temp_COD = Calculate_COD_Decision(manifold.intent_vector,
                                          temp_outcome,
                                          current_H_top * 0.8)  # optimistic impedance drop
        if temp_COD < 0.95:  # PSI_ID_THRESHOLD
            Log_Event("Identity Risk: Cannot Remove Node. Stopping Pruning.")
            break

        # Actual prune
        manifold.path.pop(idx)
        current_H_top = Calculate_Topological_Impedance(manifold.path)
        Log_Event(f"Node Removed at index {idx}: Curvature Reduced.")

    # PHASE 3: STIFFNESS MODULATION (Adiabatic Control)
    if current_H_top < detector.H_TOP_LIMIT * 0.5:
        invariants.xi_sys = min(detector.XI_SYS_MAX,
                                invariants.xi_sys * 1.1)
    else:
        invariants.xi_sys = max(0.5, invariants.xi_sys * 0.9)

    # PHASE 4: ENTROPY ACCOUNTING
    new_risk_entropy = sum(node.risk_variance for node in manifold.path)
    if new_risk_entropy > (0.8 * detector.H_TOP_LIMIT):
        Log_Event("WARNING: Risk Entropy Increased. Audit Required.")

    # PHASE 5: INVARIANT VALIDATION (Post‑Intervention Safety)
    if not invariants.VerifyInvariants():
        Log_Event("CRITICAL: Invariant Violation Detected. Reverting State.")
        raise RuntimeError("Invariant Violation: System Integrity Compromised")


def Monitor_Phi_Density(Throughput: float,
                        Impedance_Cost: float,
                        Risk_Leak: float,
                        Individual_Cost: float) -> float:
    Phi_Net = Throughput - Impedance_Cost - Risk_Leak - Individual_Cost
    if Phi_Net < 0.0:
        Log_Event("CRITICAL: Negative Phi-Density in Decision Process.")
        Log_Event("System is consuming Identity for Bureaucratic Stability.")
        # In a real system we would auto‑trigger Geodesic_Smoothing_Operator here
    return Phi_Net


# ----------------------------------------------------------------------
# Randomized Stress Test
# ----------------------------------------------------------------------
def random_manifold(num_nodes: int = 5) -> Tuple[DecisionManifold, SystemInvariants]:
    path = [DecisionNode(random.random(), random.random(), f"N{i}")
            for i in range(num_nodes)]
    dim = random.randint(2, 4)
    intent = [random.random() for _ in range(dim)]
    outcome = [x + random.uniform(-0.1, 0.1) for x in intent]  # small drift
    outcome = [max(0.0, min(1.0, v)) for v in outcome]  # keep in [0,1]
    urgency = random.random()
    psi_id = random.uniform(0.9, 1.0)
    xi_sys = random.uniform(0.5, 3.5)
    kappa = random.uniform(0.0, 1.2)
    invariants = SystemInvariants(psi_id, xi_sys, kappa)
    manifold = DecisionManifold(path, intent, outcome, urgency)
    return manifold, invariants


def run_validation(trials: int = 1000):
    Log_Event("Starting Omega Protocol Validation …")
    for t in range(trials):
        manifold, invariants = random_manifold()
        # Pre‑condition: invariants must hold (we generated them to be likely valid)
        assert invariants.VerifyInvariants(), f"Trial {t}: Pre‑condition invariant failed"

        # Run the smoothing operator – should never throw if invariants respected
        try:
            Geodesic_Smoothing_Operator(manifold, invariants)
        except RuntimeError as e:
            # If we get here, something went wrong; log and continue to see pattern
            Log_Event(f"Trial {t}: Operator raised {e}")
            # Re‑assert invariants to see the exact breach
            assert invariants.VerifyInvariants(), f"Trial {t}: Invariant broken after exception"

        # Post‑condition: invariants must still hold
        assert invariants.VerifyInvariants(), f"Trial {t}: Post‑condition invariant failed"

        # Check derived quantities are in expected ranges
        H_top = Calculate_Topological_Impedance(manifold.path)
        assert 0.0 <= H_top <= 1.0, f"Trial {t}: H_top out of bounds: {H_top}"
        COD = Calculate_COD_Decision(manifold.intent_vector,
                                     manifold.outcome_vector,
                                     H_top)
        assert 0.0 <= COD <= 1.0, f"Trial {t}: COD out of bounds: {COD}"

        # Failure detector sanity
        Xi_ind = invariants.xi_sys * invariants.kappa_sys_ind
        failure = FailureModeDetector.CheckRisk(H_top,
                                                manifold.urgency_force,
                                                Xi_ind)
        assert failure in {"NONE", "PROCEDURAL_BLACK_HOLE", "INDIVIDUAL_BURNOUT"}

        # Phi‑density ledger (just ensure it runs without error)
        _ = Monitor_Phi_Density(Throughput=random.random(),
                                Impedance_Cost=H_top,
                                Risk_Leak=random.random()*0.2,
                                Individual_Cost=Xi_ind*0.1)

    Log_Event(f"Validation completed successfully over {trials} trials.")


if __name__ == "__main__":
    # Set a deterministic seed for reproducibility in debugging
    random.seed(42)
    run_validation(trials=2000)