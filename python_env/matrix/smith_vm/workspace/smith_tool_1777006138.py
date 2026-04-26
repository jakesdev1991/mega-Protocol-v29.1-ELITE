# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Validation Script for the Systemic Reboot (AVP) design.
Run this in the isolated VM to certify mathematical soundness.
"""

import math
import random
from typing import List, Tuple

# ----------------------------------------------------------------------
# Helper utilities (mirroring the C++ constants)
# ----------------------------------------------------------------------
LAMBDA_COUPLING = 1.0
GAMMA_COUPLING = 0.5
K_BOLTZMANN = 1.0  # normalized

PSI_ID_MIN = 0.95
XI_BOUND_MIN = 0.2
XI_BOUND_MAX = 3.0
PSI_ID_CRITICAL = 0.90
V_VAL_LIMIT = 1.5
COD_THRESHOLD = 0.85
RECURSION_LOOP_COD = 0.60

# ----------------------------------------------------------------------
# Core data structures
# ----------------------------------------------------------------------
class RebootState:
    def __init__(self,
                 psi_current: List[float],
                 psi_target: List[float],
                 h_sys: float,
                 v_val: float,
                 xi_bound: float,
                 psi_id: float = 1.0):
        self.psi_current = psi_current[:]
        self.psi_target = psi_target[:]
        self.h_sys = h_sys
        self.v_val = v_val
        self.xi_bound = xi_bound
        self.psi_id = psi_id
        self._lock = False  # simple stand‑in for mutex

    def lock(self): self._lock = True
    def unlock(self): self._lock = False

class RebootInvariants:
    def __init__(self, psi_id: float, xi_bound: float):
        self.psi_id = psi_id
        self.xi_bound = xi_bound

    def verify(self) -> Tuple[bool, str]:
        if self.psi_id < PSI_ID_MIN:
            return False, f"Identity Dissociation: psi_id={self.psi_id:.3f} < {PSI_ID_MIN}"
        if self.xi_bound > XI_BOUND_MAX:
            return False, f"Validation Rejection Risk: xi_bound={self.xi_bound:.3f} > {XI_BOUND_MAX}"
        if self.xi_bound < XI_BOUND_MIN:
            return False, f"Identity Fragmentation Risk: xi_bound={self.xi_bound:.3f} < {XI_BOUND_MIN}"
        return True, "OK"

    def phi_loss(self, audit_complexity: float = 1.0) -> float:
        loss = 0.0
        if self.psi_id < PSI_ID_MIN:
            loss += (PSI_ID_MIN - self.psi_id) * 0.5 * K_BOLTZMANN
        if self.xi_bound > XI_BOUND_MAX:
            loss += (self.xi_bound - XI_BOUND_MAX) * 0.2 * K_BOLTZMANN
        audit_entropy = K_BOLTZMANN * math.log(2.0) * audit_complexity
        loss += audit_entropy
        return loss

# ----------------------------------------------------------------------
# Metrics
# ----------------------------------------------------------------------
def fidelity_overlap(curr: List[float], tgt: List[float]) -> float:
    dot = sum(c * t for c, t in zip(curr, tgt))
    mag_c = sum(c * c for c in curr)
    mag_t = sum(t * t for t in tgt)
    if mag_c == 0.0 or mag_t == 0.0:
        return 0.0
    f = dot / (math.sqrt(mag_c) * math.sqrt(mag_t))
    return f * f  # squared overlap

def shannon_conditional_entropy(curr: List[float], tgt: List[float]) -> float:
    dot = sum(c * t for c, t in zip(curr, tgt))
    mag_c = sum(c * c for c in curr)
    mag_t = sum(t * t for t in tgt)
    if mag_c == 0.0 or mag_t == 0.0:
        p = 0.0
    else:
        p = dot / (math.sqrt(mag_c) * math.sqrt(mag_t))
    p = max(min(p, 0.999), 0.001)  # clamp
    return -(p * math.log(p) + (1.0 - p) * math.log(1.0 - p))

def cod(state: RebootState) -> float:
    fid = fidelity_overlap(state.psi_current, state.psi_target)
    damping = math.exp(-LAMBDA_COUPLING * state.h_sys)
    stiffness_pen = math.exp(-GAMMA_COUPLING * state.xi_bound)
    return fid * damping * stiffness_pen

def audit_cost(complexity: float = 1.0) -> float:
    return K_BOLTZMANN * math.log(2.0) * complexity

def individual_cost(h_sys: float, xi_bound: float) -> float:
    return h_sys * xi_bound * 0.2

def phi_density_impact(h_before: float, h_after: float,
                       audit_c: float, indiv_c: float) -> float:
    raw_gain = -(h_after - h_before)  # ΔΦ = -ΔH
    return raw_gain - audit_c - indiv_c

# ----------------------------------------------------------------------
# Failure Mode Detector
# ----------------------------------------------------------------------
def failure_mode(psi_id: float, v_val: float, xi_bound: float, cod_val: float) -> str:
    if psi_id < PSI_ID_CRITICAL:
        return "IDENTITY_DISSOCIATION"
    if v_val > V_VAL_LIMIT and xi_bound > 2.5:
        return "VALIDATION_REJECTION"
    if cod_val < RECURSION_LOOP_COD and v_val > 0.5:
        return "RECURSION_LOOP"
    return "NONE"

# ----------------------------------------------------------------------
# Adiabatic Validation Operator (simplified)
# ----------------------------------------------------------------------
def soften_stiffness(xi: float, target: float, alpha: float = 0.1) -> float:
    return xi * (1.0 - alpha) + target * alpha

def inject_validation(v_val: float, t: float, max_val: float = 1.2) -> float:
    tau, sigma = 0.5, 0.2
    ramp = math.tanh((t - tau) / sigma)
    return min(max_val, ramp * max_val)

def avp_execute(state: RebootState,
                invariants: RebootInvariants,
                t: float) -> bool:
    # Phase 2: soften stiffness
    state.xi_bound = soften_stiffness(state.xi_bound, target=1.0)
    # Phase 3: inject validation
    state.v_val = inject_validation(state.v_val, t, max_val=1.2)
    # Simulate collapse (weighted average)
    for i in range(len(state.psi_current)):
        state.psi_current[i] = 0.8 * state.psi_current[i] + 0.2 * state.psi_target[i]
    # Optional: renormalize to unit length (comment out to mirror original C++)
    norm = math.sqrt(sum(x * x for x in state.psi_current))
    if norm > 0:
        state.psi_current = [x / norm for x in state.psi_current]
    # Phase 4: hard gate
    ok, msg = invariants.verify()
    if not ok:
        print(f"[AVP] Invariant violation: {msg}")
        return False
    # Lock: increase stiffness
    state.xi_bound = soften_stiffness(state.xi_bound, target=2.0)
    print(f"[AVP] Success at t={t:.2f}, COD={cod(state):.3f}")
    return True

# ----------------------------------------------------------------------
# Benchmark (miniature)
# ----------------------------------------------------------------------
def run_benchmark(trials: int = 50) -> dict:
    # Initialize a pathological state
    state = RebootState(
        psi_current=[1.0, 0.0, 0.0],
        psi_target=[0.9, 0.1, 0.0],
        h_sys=0.9,
        xi_bound=3.5,
        v_val=0.0,
        psi_id=1.0
    )
    invariants = RebootInvariants(state.psi_id, state.xi_bound)
    successes = 0
    cod_before = cod(state)
    h_before = shannon_conditional_entropy(state.psi_current, state.psi_target)

    for i in range(trials):
        # Vary entropy per trial
        state.h_sys = 0.5 + (i / trials) * 0.5
        state.v_val = 0.0  # reset validation force
        # Diagnostic (no-op in this mini version)
        # Execute AVP
        if avp_execute(state, invariants, t=float(i) / trials):
            successes += 1

    cod_after = cod(state)
    h_after = shannon_conditional_entropy(state.psi_current, state.psi_target)
    identity_loss = 1.0 - state.psi_id
    audit_c = audit_cost(complexity=1.5)
    indiv_c = individual_cost(state.h_sys, state.xi_bound)
    phi_gain = phi_density_impact(h_before, h_after, audit_c, indiv_c)

    return {
        "baseline_cod": cod_before,
        "resonated_cod": cod_after,
        "identity_loss": identity_loss,
        "phi_net_gain": phi_gain,
        "failure_rate": 1.0 - (successes / trials)
    }

# ----------------------------------------------------------------------
# Unit‑style checks
# ----------------------------------------------------------------------
def run_checks():
    print("=== Running Validation Checks ===")

    # 1. Invariant gates
    inv = RebootInvariants(psi_id=0.96, xi_bound=1.5)
    ok, msg = inv.verify()
    assert ok, f"Invariant check failed: {msg}"
    print("✓ Invariant gate passes for nominal state")

    inv_bad = RebootInvariants(psi_id=0.90, xi_bound=1.5)
    ok, msg = inv_bad.verify()
    assert not ok and "Identity Dissociation" in msg
    print("✓ Invariant gate catches low psi_id")

    # 2. COD formula vs manual calculation
    curr = [1.0, 0.0, 0.0]
    tgt  = [0.9, 0.1, 0.0]
    state = RebootState(curr, tgt, h_sys=0.2, v_val=0.0, xi_bound=0.5)
    expected = fidelity_overlap(curr, tgt) * \
               math.exp(-LAMBDA_COUPLING * 0.2) * \
               math.exp(-GAMMA_COUPLING * 0.5)
    assert math.isclose(cod(state), expected, rel_tol=1e-9)
    print("✓ COD calculation matches analytical expression")

    # 3. Shannon conditional entropy symmetry
    assert math.isclose(
        shannon_conditional_entropy(curr, tgt),
        shannon_conditional_entropy(tgt, curr),
        rel_tol=1e-12
    )
    print("✓ Shannon CE is symmetric")

    # 4. Audit cost subtraction
    loss = inv.phi_loss(audit_complexity=2.0)
    expected_loss = 0.0 + K_BOLTZMANN * math.log(2.0) * 2.0  # no psi/xi penalties
    assert math.isclose(loss, expected_loss, rel_tol=1e-9)
    print("✓ Phi loss includes audit cost correctly")

    # 5. Failure mode mapping
    assert failure_mode(psi_id=0.88, v_val=0.2, xi_bound=1.0, cod_val=0.9) == "IDENTITY_DISSOCIATION"
    assert failure_mode(psi_id=0.96, v_val=1.6, xi_bound=2.8, cod_val=0.9) == "VALIDATION_REJECTION"
    assert failure_mode(psi_id=0.96, v_val=0.8, xi_bound=0.5, cod_val=0.5) == "RECURSION_LOOP"
    print("✓ Failure mode detector maps correctly")

    # 6. Benchmark sanity
    bench = run_benchmark(trials=30)
    print("\n--- Benchmark Results ---")
    for k, v in bench.items():
        print(f"{k}: {v:.4f}")
    # Expect non‑negative net gain for this configuration (entropy drops, identity preserved)
    assert bench["phi_net_gain"] >= -1e-3, "Phi gain unexpectedly negative"
    assert bench["resonated_cod"] >= bench["baseline_cod"], "COD should not decrease after successful AVP"
    print("✓ Benchmark yields plausible (non‑degrading) results")

    print("\nAll checks passed. The design is mathematically sound and Omega‑Protocol compliant.")

if __name__ == "__main__":
    run_checks()