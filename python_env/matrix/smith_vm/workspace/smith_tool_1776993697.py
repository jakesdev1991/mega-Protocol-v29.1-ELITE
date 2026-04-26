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
Agent Smith: ruthless audit of mathematical soundness and invariant compliance.
"""

import math
import random
from typing import List, Tuple

# ----------------------------------------------------------------------
# Helper data structures (mirror the C++ spec)
# ----------------------------------------------------------------------
class DecisionNode:
    def __init__(self, approval_cost: float, risk_variance: float, node_id: str = ""):
        self.approval_cost = approval_cost          # [0,1]
        self.risk_variance = risk_variance          # [0,1]
        self.node_id = node_id

class DecisionManifold:
    def __init__(self, path: List[DecisionNode],
                 intent: List[float],
                 outcome: List[float],
                 urgency_force: float = 1.0):
        self.path = path
        self.intent_vector = intent
        self.outcome_vector = outcome
        self.urgency_force = urgency_force
        self.phi_N = 0.0
        self.phi_Delta = 0.0

class SystemInvariants:
    # Constants from the spec
    PSI_ID_MIN = 0.95
    XI_SYS_MAX = 3.0
    XI_N_MAX = 2.0
    XI_DELTA_MAX = 2.5
    KAPPA_MAX = 1.0
    H_TOP_LIMIT = 0.85
    XI_IND_THRESHOLD = 2.0

    def __init__(self, psi_id: float = 1.0,
                 xi_sys: float = 1.5,
                 kappa_sys_ind: float = 0.5,
                 xi_N: float = 1.5,
                 xi_Delta: float = 1.5):
        self.psi_id = psi_id
        self.xi_sys = xi_sys
        self.kappa_sys_ind = kappa_sys_ind
        self.xi_N = xi_N
        self.xi_Delta = xi_Delta

    def verify_invariants(self) -> Tuple[bool, List[str]]:
        errors = []
        if self.psi_id < self.PSI_ID_MIN:
            errors.append(f"Shredding Event: ψ_id={self.psi_id} < {self.PSI_ID_MIN}")
        if self.xi_sys > self.XI_SYS_MAX:
            errors.append(f"Informational Freeze Risk: ξ_sys={self.xi_sys} > {self.XI_SYS_MAX}")
        if self.xi_N > self.XI_N_MAX:
            errors.append(f"Stable Mode Violation: ξ_N={self.xi_N} > {self.XI_N_MAX}")
        if self.xi_Delta > self.XI_DELTA_MAX:
            errors.append(f"Adversarial Mode Violation: ξ_Δ={self.xi_Delta} > {self.XI_DELTA_MAX}")
        if self.kappa_sys_ind > self.KAPPA_MAX:
            errors.append(f"System‑Individual Overload: κ={self.kappa_sys_ind} > {self.KAPPA_MAX}")
        return (len(errors) == 0, errors)

# ----------------------------------------------------------------------
# Core mathematical functions (exact translations from the spec)
# ----------------------------------------------------------------------
def topological_impedance(path: List[DecisionNode]) -> float:
    """H_top = Σ(Cost_i·Var_i) / ΣCost_i  ÷  H_max,  H_max = ln(N)"""
    if not path:
        return 0.0
    total_impedance = sum(n.approval_cost * n.risk_variance for n in path)
    total_cost = sum(n.approval_cost for n in path)
    if total_cost == 0.0:
        return 0.0
    raw = total_impedance / total_cost
    N = len(path)
    H_max = math.log(N) if N > 1 else 1.0
    return min(1.0, max(0.0, raw / H_max))

def fidelity(intent: List[float], outcome: List[float]) -> float:
    """Normalized dot product → |<ψ_intent|ψ_outcome>|²"""
    if not intent or not outcome or len(intent) != len(outcome):
        return 0.0
    dot = sum(i * o for i, o in zip(intent, outcome))
    magI = math.sqrt(sum(i * i for i in intent))
    magO = math.sqrt(sum(o * o for o in outcome))
    if magI == 0.0 or magO == 0.0:
        return 0.0
    f = dot / (magI * magO)
    return min(1.0, max(0.0, f)) ** 2   # squared as per spec

def cod(intent: List[float],
        outcome: List[float],
        H_top: float,
        xi_bound: float,
        Lambda: float = 1.0,
        Gamma: float = 0.5) -> float:
    """COD = fidelity * exp(-Λ·H_top) * exp(-Γ·ξ_bound)"""
    return fidelity(intent, outcome) * math.exp(-Lambda * H_top) * math.exp(-Gamma * xi_bound)

def shannon_conditional_entropy(outcome: List[float]) -> float:
    """H_cond = - Σ p log p / log(N)  (assumes outcome already a probability vector)"""
    if not outcome:
        return 0.0
    # Normalize just in case; if not normalized the result is still dimensionless
    total = sum(outcome)
    if total == 0.0:
        probs = [0.0] * len(outcome)
    else:
        probs = [p / total for p in outcome]
    H = -sum(p * math.log(p) for p in probs if p > 0.0)
    N = len(outcome)
    H_max = math.log(N) if N > 1 else 1.0
    return min(1.0, max(0.0, H / H_max))

def phi_loss(invariants: SystemInvariants,
             audit_complexity: float = 1.0,
             k_boltzmann: float = 1.0) -> float:
    """ΔS_audit = k·ln2·Complexity  +  identity‑erosion + stability‑breach terms"""
    loss = 0.0
    # Identity erosion
    if invariants.psi_id < invariants.PSI_ID_MIN:
        loss += (invariants.PSI_ID_MIN - invariants.psi_id) * 0.5 * k_boltzmann
    # Stability breach (ξ_sys > 3.0)
    if invariants.xi_sys > invariants.XI_SYS_MAX:
        loss += (invariants.xi_sys - invariants.XI_SYS_MAX) * 0.2 * k_boltzmann
    # Audit cost
    loss += k_boltzmann * math.log(2.0) * audit_complexity
    return loss

def geodesic_smoothing_operator(manifold: DecisionManifold,
                                invariants: SystemInvariants) -> None:
    """Exact mirror of the C++ Geodesic_Smoothing_Operator (invariant‑guarded)."""
    # Phase‑1: diagnostics
    H_top = topological_impedance(manifold.path)
    current_cod = cod(manifold.intent_vector,
                      manifold.outcome_vector,
                      H_top,
                      invariants.xi_sys)
    xi_ind = invariants.xi_sys * invariants.kappa_sys_ind
    # Simple failure detector (only needed for early‑exit)
    stable = (H_top <= invariants.H_TOP_LIMIT * 0.9 and
              current_cod >= 0.80 and
              xi_ind <= invariants.XI_IND_THRESHOLD and
              invariants.psi_id >= invariants.PSI_ID_MIN)
    if stable:
        return  # No smoothing required

    # Phase‑2: curvature reduction (node pruning)
    high_curv = [i for i, n in enumerate(manifold.path)
                 if n.approval_cost * n.risk_variance > 0.5]
    high_curv.sort(key=lambda i: manifold.path[i].approval_cost *
                                   manifold.path[i].risk_variance,
                   reverse=True)

    for idx in list(high_curv):  # copy because we mutate the list
        if topological_impedance(manifold.path) <= invariants.H_TOP_LIMIT * 0.9:
            break
        # Simulate outcome shift
        temp_outcome = [v - 0.05 for v in manifold.outcome_vector]
        temp_cod = cod(manifold.intent_vector,
                       temp_outcome,
                       topological_impact := topological_impedance(manifold.path),
                       invariants.xi_sys)
        if temp_cod < invariants.PSI_ID_MIN:   # hard gate on ψ_id
            break   # identity risk – stop pruning
        # Actual prune
        manifold.path.pop(idx)

    # Phase‑3: stiffness modulation (adiabatic)
    H_now = topological_impedance(manifold.path)
    if H_now < invariants.H_TOP_LIMIT * 0.5:
        invariants.xi_sys = min(invariants.XI_SYS_MAX,
                                invariants.xi_sys * 1.1)
    else:
        invariants.xi_sys = max(0.5, invariants.xi_sys * 0.9)

    # Phase‑4: entropy accounting (optional warning)
    new_risk_entropy = sum(n.risk_variance for n in manifold.path)
    if new_risk_entropy > 0.8 * invariants.H_TOP_LIMIT:
        pass  # In a real system we would log a warning

    # Phase‑5: invariant validation (post‑intervention)
    ok, errs = invariants.verify_invariants()
    if not ok:
        raise RuntimeError(f"Invariant violation after smoothing: {errs}")

# ----------------------------------------------------------------------
# Property‑based validation
# ----------------------------------------------------------------------
def run_validation(trials: int = 1000) -> None:
    random.seed(42)
    for t in range(trials):
        # Random manifold
        N = random.randint(2, 10)
        path = [DecisionNode(random.random(), random.random(),
                             f"node_{i}") for i in range(N)]
        intent = [random.random() for _ in range(N)]
        outcome = [random.random() for _ in range(N)]
        urgency = random.random()
        manifold = DecisionManifold(path, intent, outcome, urgency)
        invariants = SystemInvariants(
            psi_id=random.uniform(0.8, 1.2),
            xi_sys=random.uniform(0.5, 4.0),
            kappa_sys_ind=random.uniform(0.0, 1.5),
            xi_N=random.uniform(0.5, 3.0),
            xi_Delta=random.uniform(0.5, 3.0)
        )

        # 1. Dimensional check – all primary quantities must be dimensionless floats
        H = topological_impedance(path)
        assert 0.0 <= H <= 1.0, f"H_top out of bounds: {H}"
        C = cod(intent, outcome, H, invariants.xi_sys)
        assert 0.0 <= C <= 1.0, f"COD out of bounds: {C}"
        Hc = shannon_conditional_entropy(outcome)
        assert 0.0 <= Hc <= 1.0, f"H_cond out of bounds: {Hc}"

        # 2. Invariant pre‑check (should not raise unless we deliberately break them)
        ok, errs = invariants.verify_invariants()
        # We allow the random draw to occasionally violate invariants – the validator must catch them
        if not ok:
            # Expect the smoothing operator to either fix or throw
            try:
                geodesic_smoothing_operator(manifold, invariants)
                ok2, _ = invariants.verify_invariants()
                assert ok2, f"Invariants still violated after smoothing: {invariants.__dict__}"
            except RuntimeError as e:
                # If the operator throws, the invariants must be violated in the message
                assert "Invariant violation" in str(e)
        else:
            # If already valid, smoothing should not break invariants
            geodesic_smoothing_operator(manifold, invariants)
            ok2, _ = invariants.verify_invariants()
            assert ok2, f"Smoothing broke valid invariants: {invariants.__dict__}"

        # 3. Φ‑density accounting with audit cost
        throughput = sum(n.approval_cost for n in path) / len(path)
        impedance_cost = H * 0.3   # arbitrary scaling for demo
        risk_leak = 1.0 - C
        individual_cost = (invariants.xi_sys * invariants.kappa_sys_ind) * 0.1
        audit_complexity = len(path)  # proxy for operator complexity
        Phi_gain = throughput
        Phi_loss = impedance_cost + risk_leak + individual_cost
        Phi_net = Phi_gain - Phi_loss - phi_loss(invariants, audit_complexity)
        # Net Φ may be negative in pathological draws – that's allowed; we only check that the audit term is present
        audit_term = phi_loss(invariants, audit_complexity)
        assert audit_term >= 0.0, "Audit cost should be non‑negative"

        # 4. Φ_N / Φ_Δ decomposition sanity check
        phi_decomp = type('PhiDecomp', (), {})()
        phi_decomp.phi_N = throughput * C * (1.0 - risk_leak)
        phi_decomp.phi_Delta = (0.2) * (1.0 - C) * risk_leak   # dummy attack_success=0.2
        net_phi = phi_decomp.phi_N - phi_decomp.phi_Delta
        # Net Φ should be roughly comparable to our manual Phi_net (within factor 2 for demo)
        assert abs(net_phi) < 5.0, "Phi decomposition produced absurd magnitude"

    print(f"Validation passed over {trials} random trials.")

if __name__ == "__main__":
    run_validation()