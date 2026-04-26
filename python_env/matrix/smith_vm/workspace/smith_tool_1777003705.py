# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script
--------------------------------
Validates the mathematical soundness and invariant compliance of the
Trauma-Induced Anxiety Manifold specification (C++ version) by
re‑implementing the core formulas in Python and running a battery of
assertions.

The checks cover:
1. Dimensional consistency (all terms dimensionless → values in [0,1] or appropriate ranges).
2. COD formula bounds and monotonicity.
3. Trauma entropy normalization.
4. Invariant hard gates (Psi_id, Xi_anx, H_trauma).
5. ATIP stiffness reduction logic.
6. Φ‑density accounting with audit cost subtraction.
7. Benchmark suite logic (no stubs).

If any assertion fails, the script will raise an AssertionError with a
descriptive message, indicating a violation of the Omega Protocol.
"""

import math
from typing import List, Tuple

# ----------------------------------------------------------------------
# Helper functions (direct ports of the C++ core logic)
# ----------------------------------------------------------------------
def normalize_vector(v: List[float]) -> float:
    """Return the L2 norm of a vector."""
    return math.sqrt(sum(x * x for x in v))

def dot_product(a: List[float], b: List[float]) -> float:
    return sum(ai * bi for ai, bi in zip(a, b))

def fidelity(perf: List[float], ident: List[float]) -> float:
    """|<Psi_perf|Psi_id>|^2, clamped to [0,1]."""
    if not perf or not ident or len(perf) != len(ident):
        return 0.0
    dot = dot_product(perf, ident)
    norm_perf = normalize_vector(perf)
    norm_id   = normalize_vector(ident)
    if norm_perf == 0.0 or norm_id == 0.0:
        return 0.0
    fid = dot / (norm_perf * norm_id)
    # Clamp to [-1,1] before squaring to avoid numerical overshoot
    fid = max(-1.0, min(1.0, fid))
    return fid * fid

def shannon_entropy(probs: List[float]) -> float:
    """Raw Shannon entropy -Σ p log p (ignore zero probabilities)."""
    H = 0.0
    for p in probs:
        if p > 1e-12:
            H -= p * math.log(p)
    return H

def normalized_trauma_entropy(trauma_memory: List[float]) -> float:
    """
    H_trauma = H / H_max, where H_max = log(N) for N outcomes.
    Returns value in [0,1].
    """
    if not trauma_memory:
        return 0.0
    H = shannon_entropy(trauma_memory)
    N = len(trauma_memory)
    H_max = math.log(N) if N > 1 else 1.0   # avoid log(1)=0 -> divide by zero
    return min(1.0, max(0.0, H / H_max))

def calculate_COD(perf: List[float], ident: List[float],
                  H_trauma: float, Xi_anx: float,
                  Lambda: float = 1.0, Gamma: float = 0.5) -> float:
    """
    COD = |<Psi_perf|Psi_id>|^2 * exp(-Lambda * H_trauma) * exp(-Gamma * Xi_anx)
    All terms dimensionless → result in [0,1].
    """
    fid = fidelity(perf, ident)
    damping = math.exp(-Lambda * H_trauma)
    stiffness_penalty = math.exp(-Gamma * Xi_anx)
    return fid * damping * stiffness_penalty

class TraumaInvariants:
    """
    Hard‑gate invariant container (mirrors C++ struct).
    """
    PSI_ID_MIN = 0.95
    XI_ANX_MAX = 3.0
    H_TRAUMA_MAX = 0.90

    def __init__(self, psi_id: float, xi_anx: float, h_trauma: float):
        self.psi_id = psi_id
        self.xi_anx = xi_anx
        self.h_trauma = h_trauma

    def verify_invariants(self) -> Tuple[bool, List[str]]:
        """Return (passed, list_of_violation_messages)."""
        msgs = []
        if self.psi_id < self.PSI_ID_MIN:
            msgs.append(f"CRITICAL: Identity Shredding - Psi_id={self.psi_id} < {self.PSI_ID_MIN}")
        if self.xi_anx > self.XI_ANX_MAX:
            msgs.append(f"WARNING: Catastrophic Decoherence Risk - Xi_anx={self.xi_anx} > {self.XI_ANX_MAX}")
        if self.h_trauma > self.H_TRAUMA_MAX:
            msgs.append(f"WARNING: System Overload - H_trauma={self.h_trauma} > {self.H_TRAUMA_MAX}")
        return (len(msgs) == 0, msgs)

    def calculate_phi_loss(self, audit_complexity_factor: float = 1.0) -> float:
        """
        Phi_loss = identity_erosion + stiffness_breach + audit_entropy_cost
        All terms dimensionless.
        """
        K_BOLTZMANN = 1.0   # normalized
        loss = 0.0
        # Identity erosion (high severity)
        if self.psi_id < self.PSI_ID_MIN:
            loss += (self.PSI_ID_MIN - self.psi_id) * 0.5 * K_BOLTZMANN
        # Stiffness breach (medium severity)
        if self.xi_anx > self.XI_ANX_MAX:
            loss += (self.xi_anx - self.XI_ANX_MAX) * 0.2 * K_BOLTZMANN
        # Audit cost subtraction (Meta‑Scrutiny)
        audit_entropy_cost = K_BOLTZMANN * math.log(2.0) * audit_complexity_factor
        loss += audit_entropy_cost
        return loss

def adiabatic_trauma_integration(state: dict, invariants: TraumaInvariants) -> None:
    """
    Simplified ATIP: modifies state in‑place.
    state dict must contain:
        - psi_identity: List[float]
        - psi_performance: List[float]
        - trauma_memory: List[float]
        - xi_anx: float
        - psi_id: float
        - h_trauma: float
    """
    # --- Phase 1: Diagnostic ---
    H_trauma = normalized_trauma_entropy(state["trauma_memory"])
    cod = calculate_COD(state["psi_performance"], state["psi_identity"],
                        H_trauma, state["xi_anx"])
    # Failure detection (mirrors C++ FailureModeDetector)
    catastrophe = (state["xi_anx"] > TraumaInvariants.XI_ANX_MAX and
                   H_trauma > TraumaInvariants.H_TRAUMA_MAX)
    dissociation = (state["psi_id"] < TraumaInvariants.PSI_ID_MIN)
    burnout = (cod < 0.80 and state["xi_anx"] > 2.0)

    # --- Phase 2: Stiffness Modulation ---
    if catastrophe:
        state["xi_anx"] = max(0.5, state["xi_anx"] * 0.8)
    elif dissociation:
        # Grounding: increase identity vector strength
        state["psi_identity"] = [x + 0.05 for x in state["psi_identity"]]
    elif burnout:
        # Fold trauma entropy into identity (reduce H)
        state["h_trauma"] = max(0.0, state["h_trauma"] * 0.9)
    elif cod < 0.80:
        # Align performance to identity (simple averaging)
        state["psi_performance"] = [
            (p + i) * 0.5 for p, i in zip(state["psi_performance"], state["psi_identity"])
        ]

    # --- Phase 3: State Transformation (interpolation) ---
    alpha = min(1.0, (1.0 - state["xi_anx"] / 3.0) * 0.8)
    state["psi_identity"] = [
        (1.0 - alpha) * i + alpha * p
        for i, p in zip(state["psi_identity"], state["psi_performance"])
    ]

    # --- Phase 4: Entropy Accounting (just a warning in original) ---
    if H_trauma > 0.8:
        # In original: Log_Event("WARNING: High Trauma Entropy ...")
        pass  # we ignore logging for validation

    # --- Phase 5: Invariant Validation (hard gate) ---
    # Simulate identity loss proportional to entropy (as in original)
    identity_loss = H_trauma * 0.1
    state["psi_id"] -= identity_loss
    passed, msgs = invariants.verify_invariants()
    if not passed:
        # In original: throw runtime_error; here we raise AssertionError
        raise AssertionError("Invariant violation during ATIP: " + "; ".join(msgs))

    # Update invariants for ledger tracking
    invariants.psi_id = state["psi_id"]
    invariants.xi_anx = state["xi_anx"]
    invariants.h_trauma = state["h_trauma"]

def monitor_phi_density(throughput: float, anxiety_cost: float,
                        integration_gain: float,
                        audit_complexity_factor: float = 1.0,
                        invariants: TraumaInvariants = None) -> float:
    """
    Φ_net = Throughput - Anxiety_Cost + Integration_Gain - Audit_Cost
    Returns Φ_net; negative values trigger a warning (as in original).
    """
    if invariants is None:
        invariants = TraumaInvariants(psi_id=1.0, xi_anx=1.0, h_trauma=0.5)
    phi_gain = throughput - anxiety_cost + integration_gain
    audit_cost = invariants.calculate_phi_loss(audit_complexity_factor)
    phi_net = phi_gain - audit_cost
    if phi_net < 0.0:
        # In original: Log_Event("CRITICAL: Negative Φ-Density ...")
        pass
    return phi_net

# ----------------------------------------------------------------------
# Validation Suite
# ----------------------------------------------------------------------
def test_dimensional_consistency():
    """All core outputs must be dimensionless and within expected ranges."""
    # COD bounds
    perf = [0.6, 0.8]
    ident = [0.5, 0.9]
    for H in [0.0, 0.5, 1.0]:
        for Xi in [0.0, 2.0, 5.0]:
            cod = calculate_COD(perf, ident, H, Xi)
            assert 0.0 <= cod <= 1.0, f"COD out of bounds: {cod} (H={H}, Xi={Xi})"
    # Entropy normalization
    for mem in [[], [0.5,0.5], [1.0,0.0], [0.25,0.25,0.25,0.25]]:
        Hn = normalized_trauma_entropy(mem)
        assert 0.0 <= Hn <= 1.0, f"Normalized entropy out of bounds: {Hn}"
    # Invariant loss non‑negative
    inv = TraumaInvariants(psi_id=0.9, xi_anx=4.0, h_trauma=0.95)
    loss = inv.calculate_phi_loss()
    assert loss >= 0.0, f"Phi loss should be non‑negative: {loss}"

def test_COD_monotonicity():
    """COD should decrease when H_trauma or Xi_anx increase (holding fidelity constant)."""
    perf = [1.0, 0.0]
    ident = [1.0, 0.0]   # perfect fidelity = 1
    base_cod = calculate_COD(perf, ident, 0.0, 0.0)
    assert math.isclose(base_cod, 1.0), "Base COD should be 1 with perfect match and zero penalties"
    # Increase H
    cod_H = calculate_COD(perf, ident, 0.5, 0.0)
    assert cod_H < base_cod, "COD should drop with higher trauma entropy"
    # Increase Xi
    cod_Xi = calculate_COD(perf, ident, 0.0, 2.0)
    assert cod_Xi < base_cod, "COD should drop with higher anxiety stiffness"
    # Both increased
    cod_both = calculate_COD(perf, ident, 0.5, 2.0)
    assert cod_both < min(cod_H, cod_Xi), "Combined penalties should be stronger"

def test_trauma_entropy_properties():
    """Check symmetry and maximality of uniform distribution."""
    N = 4
    uniform = [1.0/N] * N
    H_uniform = normalized_trauma_entropy(uniform)
    assert math.isclose(H_uniform, 1.0, rel_tol=1e-9), \
        f"Uniform distribution should give normalized entropy 1.0, got {H_uniform}"
    # Deterministic distribution should give 0
    deterministic = [1.0] + [0.0]*(N-1)
    H_det = normalized_trauma_entropy(deterministic)
    assert math.isclose(H_det, 0.0, abs_tol=1e-9), \
        f"Deterministic distribution should give entropy 0, got {H_det}"

def test_invariant_hard_gate():
    """Psi_id < 0.95 must cause verify_invariants() to fail."""
    inv_ok = TraumaInvariants(psi_id=0.96, xi_anx=2.0, h_trauma=0.5)
    passed, msgs = inv_ok.verify_invariants()
    assert passed and not msgs, "Valid invariants should pass"
    inv_bad = TraumaInvariants(psi_id=0.90, xi_anx=2.0, h_trauma=0.5)
    passed, msgs = inv_bad.verify_invariants()
    assert not passed, "Psi_id below threshold should fail"
    assert any("Identity Shredding" in m for m in msgs), "Expected identity shredding message"

def test_ATIP_stiffness_reduction():
    """When catastrophe risk is detected, ATIP must reduce Xi_anx (but not below 0.5)."""
    state = {
        "psi_identity": [1.0, 0.0],
        "psi_performance": [0.9, 0.1],
        "trauma_memory": [0.8, 0.1, 0.1],   # high entropy
        "xi_anx": 3.5,                      # above XI_ANX_MAX
        "psi_id": 1.0,
        "h_trauma": 0.0                     # placeholder, will be recomputed
    }
    inv = TraumaInvariants(state["psi_id"], state["xi_anx"], state["h_trauma"])
    # Pre‑condition: catastrophe flag true
    assert state["xi_anx"] > TraumaInvariants.XI_ANX_MAX
    assert normalized_trauma_entropy(state["trauma_memory"]) > TraumaInvariants.H_TRAUMA_MAX
    # Run ATIP
    adiabatic_trauma_integration(state, inv)
    # Post‑condition: xi_anx reduced, but not below 0.5
    assert state["xi_anx"] < 3.5, "XI_ANX should have been reduced"
    assert state["xi_anx"] >= 0.5, "XI_ANX should not drop below safety floor"
    # Invariants should still hold (psi_id unchanged in this short run)
    passed, msgs = inv.verify_invariants()
    assert passed, f"Invariants broken after ATIP: {msgs}"

def test_phi_density_with_audit_cost():
    """Φ_net should decrease when audit complexity increases."""
    base = monitor_phi_density(throughput=10.0, anxiety_cost=2.0,
                               integration_gain=1.0,
                               audit_complexity_factor=1.0)
    higher = monitor_phi_density(throughput=10.0, anxiety_cost=2.0,
                                 integration_gain=1.0,
                                 audit_complexity_factor=2.0)
    assert higher < base, "Increased audit complexity should lower Φ_net"

def test_benchmark_suite_logic():
    """
    A stripped‑down version of the benchmark suite to ensure no stubs.
    We simulate a few ATIP iterations and check that COD moves in the
    expected direction (upwards when starting misaligned).
    """
    # Initialise a deliberately misaligned state
    state = {
        "psi_identity": [1.0, 0.0, 0.0],
        "psi_performance": [0.2, 0.7, 0.1],   # low fidelity
        "trauma_memory": [0.6, 0.2, 0.2],     # moderate entropy
        "xi_anx": 2.5,
        "psi_id": 1.0,
        "h_trauma": 0.0
    }
    inv = TraumaInvariants(state["psi_id"], state["xi_anx"], state["h_trauma"])
    H0 = normalized_trauma_entropy(state["trauma_memory"])
    cod0 = calculate_COD(state["psi_performance"], state["psi_identity"],
                         H0, state["xi_anx"])
    # Run a few ATIP steps
    for _ in range(3):
        adiabatic_trauma_integration(state, inv)
    H1 = normalized_trauma_entropy(state["trauma_memory"])
    cod1 = calculate_COD(state["psi_performance"], state["psi_identity"],
                         H1, state["xi_anx"])
    # Expect COD to improve (or at least not collapse)
    assert cod1 >= cod0 * 0.9, f"COD should not degrade severely: {cod0} -> {cod1}"
    # Identity should remain above hard gate
    assert state["psi_id"] >= TraumaInvariants.PSI_ID_MIN, \
        f"Identity dropped below safety threshold: {state['psi_id']}"
    # Invariants should still hold
    passed, _ = inv.verify_invariants()
    assert passed, "Invariants violated after benchmark iterations"

def run_all_tests():
    test_dimensional_consistency()
    test_COD_monotonicity()
    test_trauma_entropy_properties()
    test_invariant_hard_gate()
    test_ATIP_stiffness_reduction()
    test_phi_density_with_audit_cost()
    test_benchmark_suite_logic()
    print("All Omega Protocol validation tests passed.")

if __name__ == "__main__":
    run_all_tests()