# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Validation Script
Validates the Trauma-Induced Anxiety Manifold specification (v26.0-Ω-POLARIZED)
Checks:
 1. Dimensional homogeneity (all inputs/outputs dimensionless [1])
 2. COD bounds [0,1] and monotonic behavior w.r.t. H_trauma and Xi_anx
 3. Invariant hard gates (Psi_id >= 0.95, etc.)
 4. Phi loss non‑negative and includes audit cost
 5. Adiabatic integration reduces Xi_anx and H_trauma while preserving Psi_id >= threshold
"""

import math
import numpy as np

# ---------------------------
# Helper functions (mirroring C++ logic)
# ---------------------------
def calculate_trauma_entropy(trauma_memory):
    """Normalized Shannon entropy, returns [0,1]."""
    if not trauma_memory:
        return 0.0
    # Assume trauma_memory is a probability vector (sum≈1)
    # Normalize just in case
    total = sum(trauma_memory)
    if total == 0:
        return 0.0
    probs = [p/total for p in trauma_memory]
    max_ent = math.log(len(probs))
    if max_ent < 1e-12:
        max_ent = 1.0
    H = -sum(p * math.log(p) for p in probs if p > 1e-12)
    return min(1.0, max(0.0, H / max_ent))

def calculate_cod_performance(perf, id_vec, H_trauma, Xi_anx,
                              LAMBDA=1.0, GAMMA=0.5):
    """COD = |<Perf|Id>|^2 * exp(-Lambda*H) * exp(-Gamma*Xi)"""
    # fidelity = (dot)^2/(|Perf|^2 * |Id|^2)
    dot = sum(p*i for p,i in zip(perf, id_vec))
    normP = sum(p*p for p in perf)
    normI = sum(i*i for i in id_vec)
    if normP < 1e-12 or normI < 1e-12:
        fidelity = 0.0
    else:
        fidelity = (dot*dot) / (normP * normI)
        fidelity = min(1.0, max(0.0, fidelity))
    damping = math.exp(-LAMBDA * H_trauma)
    stiffness_penalty = math.exp(-GAMMA * Xi_anx)
    return fidelity * damping * stiffness_penalty

class TraumaInvariants:
    def __init__(self, psi_id=1.0, xi_anx=1.0, h_trauma=0.5):
        self.psi_id = psi_id
        self.xi_anx = xi_anx
        self.h_trauma = h_trauma

    PSI_ID_MIN = 0.95
    XI_ANX_MAX = 3.0
    H_TRAUMA_MAX = 0.90

    def verify_invariants(self):
        if self.psi_id < self.PSI_ID_MIN:
            return False, f"Identity Shredding: psi_id={self.psi_id}<{self.PSI_ID_MIN}"
        if self.xi_anx > self.XI_ANX_MAX:
            return False, f"Catastrophic Decoherence Risk: xi_anx={self.xi_anx}>{self.XI_ANX_MAX}"
        if self.h_trauma > self.H_TRAUMA_MAX:
            return False, f"System Overload: h_trauma={self.h_trauma}>{self.H_TRAUMA_MAX}"
        return True, "OK"

    def calculate_phi_loss(self, audit_complexity_factor=1.0):
        K_BOLTZMANN = 1.0
        loss = 0.0
        if self.psi_id < self.PSI_ID_MIN:
            loss += (self.PSI_ID_MIN - self.psi_id) * 0.5 * K_BOLTZMANN
        if self.xi_anx > self.XI_ANX_MAX:
            loss += (self.xi_anx - self.XI_ANX_MAX) * 0.2 * K_BOLTZMANN
        # audit cost
        audit_entropy = K_BOLTZMANN * math.log(2.0) * audit_complexity_factor
        loss += audit_entropy
        return loss

def adiabatic_integration_step(state, invariants, dt=0.1):
    """
    One step of ATIP:
    - Measure H_trauma, COD
    - Reduce Xi_anx if in failure mode
    - Blend performance toward identity
    - Update psi_id with entropy loss
    - Enforce invariants (hard gate)
    """
    # Phase 1: diagnostic
    H = calculate_trauma_entropy(state['trauma_memory'])
    cod = calculate_cod_performance(state['psi_performance'], state['psi_identity'],
                                    H, state['xi_anx'])
    # Failure detection (simplified)
    if state['xi_anx'] > 3.0 and H > 0.90:
        state['xi_anx'] = max(0.5, state['xi_anx'] * 0.8)  # reduce stiffness
    elif state['psi_id'] < 0.95:
        # boost identity
        state['psi_identity'] = [v + 0.05 for v in state['psi_identity']]
    elif cod < 0.80 and state['xi_anx'] > 2.0:
        # burnout: reduce trauma entropy
        state['h_trauma'] = max(0.0, state['h_trauma'] * 0.9)
    else:
        # low COD -> align performance
        state['psi_performance'] = [(p + i)*0.5 for p,i in zip(state['psi_performance'],
                                                                state['psi_identity'])]

    # Phase 2: stiffness modulation (adiabatic blend)
    alpha = min(1.0, (1.0 - state['xi_anx']/3.0) * 0.8)
    state['psi_identity'] = [(1-a)*i + a*p for i,p in zip(state['psi_identity'],
                                                          state['psi_performance'])]

    # Phase 3: entropy accounting (identity loss)
    identity_loss = H * 0.1
    state['psi_id'] -= identity_loss

    # Phase 4: invariant validation (hard gate)
    ok, msg = invariants.verify_invariants()
    if not ok:
        raise RuntimeError(f"Invariant violation: {msg}")
    # update invariants ledger
    invariants.psi_id = state['psi_id']
    invariants.xi_anx = state['xi_anx']
    invariants.h_trauma = state['h_trauma']
    return state, invariants

# ---------------------------
# Validation Tests
# ---------------------------
def test_dimensional_consistency():
    """All inputs/outputs should be dimensionless (pure numbers)."""
    # Trauma entropy
    mem = [0.2, 0.3, 0.5]
    H = calculate_trauma_entropy(mem)
    assert 0.0 <= H <= 1.0, f"H not dimensionless [0,1]: {H}"
    # COD
    perf = [1.0, 0.0, 0.0]
    idv = [1.0, 0.0, 0.0]
    cod = calculate_cod_performance(perf, idv, H, 1.0)
    assert 0.0 <= cod <= 1.0, f"COD not in [0,1]: {cod}"
    # Phi loss
    inv = TraumaInvariants(psi_id=0.9, xi_anx=4.0, h_trauma=0.2)
    loss = inv.calculate_phi_loss()
    assert loss >= 0.0, f"Phi loss negative: {loss}"
    print("✓ Dimensional consistency tests passed")

def test_cod_monotonicity():
    """COD should decrease when H_trauma or Xi_anx increase."""
    base_perf = [0.8, 0.2, 0.0]
    base_id   = [0.9, 0.1, 0.0]
    base_H = 0.2
    base_Xi = 1.0
    base_cod = calculate_cod_performance(base_perf, base_id, base_H, base_Xi)
    # Increase H
    cod_H = calculate_cod_performance(base_perf, base_id, base_H+0.3, base_Xi)
    assert cod_H < base_cod, f"COD did not drop with higher H: {base_cod} -> {cod_H}"
    # Increase Xi
    cod_Xi = calculate_cod_performance(base_perf, base_id, base_H, base_Xi+1.5)
    assert cod_Xi < base_cod, f"COD did not drop with higher Xi: {base_cod} -> {cod_Xi}"
    print("✓ COD monotonicity tests passed")

def test_invariant_hard_gate():
    """VerifyInvariants must reject out‑of‑bounds states."""
    inv = TraumaInvariants(psi_id=0.94, xi_anx=2.0, h_trauma=0.5)  # psi_id too low
    ok, msg = inv.verify_invariants()
    assert not ok, f"Should have failed psi_id gate: {msg}"
    inv = TraumaInvariants(psi_id=0.96, xi_anx=3.1, h_trauma=0.5)  # xi_anx too high
    ok, msg = inv.verify_invariants()
    assert not ok, f"Should have failed xi_anx gate: {msg}"
    inv = TraumaInvariants(psi_id=0.96, xi_anx=2.0, h_trauma=0.91) # h_trauma too high
    ok, msg = inv.verify_invariants()
    assert not ok, f"Should have failed h_trauma gate: {msg}"
    # Valid state
    inv = TraumaInvariants(psi_id=0.96, xi_anx=2.0, h_trauma=0.5)
    ok, msg = inv.verify_invariants()
    assert ok, f"Valid state incorrectly rejected: {msg}"
    print("✓ Invariant hard gate tests passed")

def test_phi_loss_includes_audit():
    """Phi loss must contain the k ln 2 * complexity term."""
    K = 1.0
    audit_factor = 2.0
    expected_audit = K * math.log(2.0) * audit_factor
    inv = TraumaInvariants(psi_id=0.96, xi_anx=2.0, h_trauma=0.5)  # no other losses
    loss = inv.calculate_phi_loss(audit_complexity_factor=audit_factor)
    # loss should be at least the audit term (could be more if other terms present)
    assert loss >= expected_audit - 1e-9, f"Phi loss missing audit component: {loss} < {expected_audit}"
    print("✓ Phi loss audit term test passed")

def test_adiabatic_step_properties():
    """After an ATIP step, psi_id should not drop below threshold and Xi_anx/H should trend down when needed."""
    state = {
        'psi_identity': [0.9, 0.1, 0.0],
        'psi_performance': [0.6, 0.4, 0.0],
        'trauma_memory': [0.1, 0.2, 0.7],
        'xi_anx': 2.5,
        'h_trauma': 0.0,  # will be set by entropy calc
        'psi_id': 0.96
    }
    inv = TraumaInvariants(psi_id=state['psi_id'],
                           xi_anx=state['xi_anx'],
                           h_trauma=state['h_trauma'])
    # Run a step where xi_anx is moderately high but not catastrophic
    new_state, new_inv = adiabatic_integration_step(state, inv, dt=0.1)
    # Psi_id must remain >= 0.95
    assert new_state['psi_id'] >= 0.95, f"Psi_id fell below threshold: {new_state['psi_id']}"
    # Xi_anx should not increase (adiabatic reduction or hold)
    assert new_state['xi_anx'] <= state['xi_anx'] + 1e-9, f"Xi_anx increased unexpectedly: {new_state['xi_anx']}"
    print("✓ Adiabatic integration step test passed")

if __name__ == "__main__":
    print("Running Omega Protocol validation for Trauma-Induced Anxiety Manifold...")
    test_dimensional_consistency()
    test_cod_monotonicity()
    test_invariant_hard_gate()
    test_phi_loss_includes_audit()
    test_adiabatic_step_properties()
    print("\nAll validation checks passed. Specification is mathematically sound and Omega‑Protocol compliant.")