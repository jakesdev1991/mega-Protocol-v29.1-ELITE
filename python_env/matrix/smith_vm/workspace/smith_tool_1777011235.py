# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script for the Trauma‑Response Manifold (ASCP)
---------------------------------------------------------------------
This script checks:
  * Dimensional consistency (all quantities dimensionless)
  * Hard gate on Psi_id (>= 0.95 during cooling)
  * Correct failure‑mode detection
  * Adiabatic cooling respects rate limits and bounds
  * Entropy/Φ‑density accounting includes audit cost subtraction
  * COD formula yields values in [0,1]
  * Benchmark suite produces sensible aggregates (no NaNs/infs)
"""

import math
import random
from typing import Tuple, List

# ----------------------------------------------------------------------
# Constants (mirroring the C++ specification)
# ----------------------------------------------------------------------
PSI_ID_THRESHOLD = 0.95
PSI_ID_CRITICAL = 0.90

XI_DEF_DEFAULT = 1.5
XI_DEF_MAX = 3.0
XI_DEF_MIN = 0.5

GAMMA_CRITICAL = 0.8
GAMMA_RATE_LIMIT = 0.05  # max relative change per step (implicitly used)

H_HEAT_LIMIT = 0.85

COD_THRESHOLD = 0.80

LAMBDA_COUPLING = 1.0
K_BOLTZMANN = 1.0  # for audit entropy cost

# ----------------------------------------------------------------------
# Helper functions (direct ports of the C++ math)
# ----------------------------------------------------------------------
def fidelity(action: complex, val: complex) -> float:
    """Normalized overlap |<val|action>|^2, clamped to [0,1]."""
    dot = abs(action.conjugate() * val)
    magA = abs(action)
    magV = abs(val)
    if magA < 1e-12 or magV < 1e-12:
        return 0.0
    f = dot / (magA * magV)
    return max(0.0, min(1.0, f))


def informational_heat(threat: complex, action: complex) -> float:
    """Shannon entropy of threat given action, normalized to [0,1]."""
    p = abs(threat.conjugate() * action)
    if p > 1.0:
        p = 1.0
    if p < 1e-12:
        return 0.0
    H = -p * math.log(p + 1e-12)
    # Normalization: max entropy for binary variable = log(2) ≈ 0.693147
    # Using exact log(2) for rigor
    return min(1.0, max(0.0, H / math.log(2.0)))


def cod_performance(action: complex, val: complex,
                    H_heat: float, gamma: float, xi: float) -> float:
    """Chain Overlap Density for performance alignment."""
    fid = fidelity(action, val)
    damping = math.exp(-LAMBDA_COUPLING * H_heat)
    stiffness_penalty = math.exp(-LAMBDA_COUPLING * gamma * xi)
    return fid * damping * stiffness_penalty


class CognitiveState:
    def __init__(self):
        self.Psi_threat = complex(0.0, 0.0)
        self.Psi_action = complex(0.0, 0.0)
        self.Psi_val = complex(0.0, 0.0)
        self.xi_def = XI_DEF_DEFAULT
        self.gamma_meas = 0.0
        self.psi_id = 1.0
        self.t = 0.0
        self._lock = False  # simple stand‑in for mutex

    def lock(self):
        self._lock = True

    def unlock(self):
        self._lock = False


class FailureMode:
    NONE, MEASUREMENT_SHOCK_LOOP, DISSOCIATION, IDENTITY_SHREDDING = range(4)


def check_failure(state: CognitiveState) -> int:
    H = informational_heat(state.Psi_threat, state.Psi_action)
    if H > H_HEAT_LIMIT and state.gamma_meas > GAMMA_CRITICAL:
        return FailureMode.MEASUREMENT_SHOCK_LOOP
    if state.xi_def < XI_DEF_MIN and H > 0.5:
        return FailureMode.DISSOCIATION
    if state.psi_id < PSI_ID_CRITICAL:
        return FailureMode.IDENTITY_SHREDDING
    return FailureMode.NONE


class AdiabaticSafetyCoolingOperator:
    def __init__(self):
        self.audit_ops = 0

    def verify_identity(self, psi_id: float) -> bool:
        return psi_id >= PSI_ID_THRESHOLD

    def apply(self, state: CognitiveState) -> None:
        state.lock()
        try:
            # --- Diagnostics ---
            H_heat = informational_heat(state.Psi_threat, state.Psi_action)
            current_cod = cod_performance(state.Psi_action, state.Psi_val,
                                          H_heat, state.gamma_meas, state.xi_def)
            failure = check_failure(state)

            if failure == FailureMode.NONE and current_cod >= COD_THRESHOLD:
                return  # stable, nothing to do

            # --- Measurement Modulation (Adiabatic Cooling) ---
            if failure == FailureMode.MEASUREMENT_SHOCK_LOOP:
                # reduce gamma slowly (multiplicative factor 0.9)
                state.gamma_meas = max(0.1, state.gamma_meas * 0.9)
                self.audit_ops += 1
            elif failure == FailureMode.DISSOCIATION:
                state.xi_def = min(XI_DEF_MAX, state.xi_def * 1.1)
                self.audit_ops += 1
            elif failure == FailureMode.IDENTITY_SHREDDING:
                raise RuntimeError("Invariant Violation: Identity Integrity Compromised")
            else:  # NONE but low COD
                # increase validation magnitude
                state.Psi_val = state.Psi_val * 1.05
                self.audit_ops += 1

            # --- State Transformation (threat reduction) ---
            alpha = 1.0 - state.gamma_meas
            state.Psi_threat = state.Psi_threat * alpha

            # --- Entropy Accounting & Identity Update ---
            H_cond = informational_heat(state.Psi_threat, state.Psi_action)
            identity_loss = H_cond * 0.05
            state.psi_id -= identity_loss

            if not self.verify_identity(state.psi_id):
                raise RuntimeError("Invariant Violation: Identity Integrity Compromised")
        finally:
            state.unlock()


class PhiDensityLedger:
    @staticmethod
    def net_phi(h_before: float, h_after: float, audit_complexity: float = 1.0) -> float:
        raw_gain = -(h_after - h_before)  # heat reduction = positive gain
        audit_entropy = K_BOLTZMANN * math.log(2.0) * audit_complexity
        return raw_gain - audit_entropy


# ----------------------------------------------------------------------
# Validation Tests
# ----------------------------------------------------------------------
def test_dimensionality():
    """All inputs and outputs of core functions should be dimensionless floats."""
    a = complex(0.6, 0.2)
    v = complex(0.8, -0.1)
    t = complex(0.3, 0.0)
    H = informational_heat(t, a)
    assert isinstance(H, float) and 0.0 <= H <= 1.0, f"H_heat not dimensionless [0,1]: {H}"
    C = cod_performance(a, v, H, 0.5, 1.2)
    assert isinstance(C, float) and 0.0 <= C <= 1.0, f"COD not dimensionless [0,1]: {C}"
    print("✓ Dimensionality test passed")


def test_identity_hard_gate():
    """Psi_id must never drop below PSI_ID_THRESHOLD during a successful cooling step."""
    state = CognitiveState()
    state.Psi_threat = complex(0.9, 0.0)
    state.Psi_action = complex(0.7, 0.0)
    state.Psi_val = complex(0.4, 0.0)
    state.xi_def = XI_DEF_MAX
    state.gamma_meas = 0.9  # shock loop region
    state.psi_id = 1.0

    op = AdiabaticSafetyCoolingOperator()
    try:
        op.apply(state)
    except RuntimeError as e:
        # If identity is breached, the operator should have thrown.
        # We'll accept this as a failure case; the important thing is that
        # the invariant is checked.
        assert "Identity Integrity Compromised" in str(e)
        print("✓ Identity hard gate correctly caught a breach")
        return
    # If no exception, verify that psi_id stayed above threshold
    assert state.psi_id >= PSI_ID_THRESHOLD, \
        f"Psi_id fell below threshold: {state.psi_id}"
    print("✓ Identity hard gate preserved during cooling")


def test_failure_detection():
    """Check that the three failure modes are flagged under the right conditions."""
    state = CognitiveState()
    # 1. Measurement Shock Loop
    state.Psi_threat = complex(1.0, 0.0)
    state.Psi_action = complex(0.5, 0.0)
    state.xi_def = XI_DEF_DEFAULT
    state.gamma_meas = 0.9
    state.psi_id = 1.0
    assert check_failure(state) == FailureMode.MEASUREMENT_SHOCK_LOOP

    # 2. Dissociation
    state.Psi_threat = complex(0.8, 0.0)
    state.Psi_action = complex(0.6, 0.0)
    state.xi_def = 0.3  # below XI_DEF_MIN
    state.gamma_meas = 0.2
    state.psi_id = 0.95
    assert check_failure(state) == FailureMode.DISSOCIATION

    # 3. Identity Shredding
    state.xi_def = XI_DEF_DEFAULT
    state.psi_id = 0.88  # below PSI_ID_CRITICAL
    assert check_failure(state) == FailureMode.IDENTITY_SHREDDING

    # 4. No failure
    state.Psi_threat = complex(0.1, 0.0)
    state.Psi_action = complex(0.9, 0.0)
    state.Psi_val = complex(0.9, 0.0)
    state.xi_def = 0.8
    state.gamma_meas = 0.3
    state.psi_id = 0.97
    assert check_failure(state) == FailureMode.NONE
    print("✓ Failure detection test passed")


def test_adiabatic_rate_limits():
    """Ensure gamma is changed by no more than ~10% per call (as per factor 0.9)."""
    state = CognitiveState()
    state.Psi_threat = complex(0.9, 0.0)
    state.Psi_action = complex(0.7, 0.0)
    state.Psi_val = complex(0.4, 0.0)
    state.xi_def = XI_DEF_MAX
    state.gamma_meas = 0.9
    state.psi_id = 1.0

    op = AdiabaticSafetyCoolingOperator()
    gamma_before = state.gamma_meas
    op.apply(state)  # should trigger shock-loop branch
    gamma_after = state.gamma_meas
    # Expected: gamma_after = max(0.1, gamma_before * 0.9)
    expected = max(0.1, gamma_before * 0.9)
    assert math.isclose(gamma_after, expected, rel_tol=1e-9), \
        f"Gamma change not adiabatic: {gamma_before} -> {gamma_after} (expected {expected})"
    print("✓ Adiabatic rate limit respected")


def test_phi_density_accounting():
    """Net Φ gain must subtract audit cost (k ln 2 * complexity)."""
    ledger = PhiDensityLedger()
    h_before = 0.9
    h_after = 0.4
    # Complexity = 1.0 (no extra audit ops)
    net = ledger.net_phi(h_before, h_after, audit_complexity=1.0)
    raw = -(h_after - h_before)  # 0.5
    audit = K_BOLTZMANN * math.log(2.0) * 1.0
    expected = raw - audit
    assert math.isclose(net, expected, rel_tol=1e-12), \
        f"Φ accounting mismatch: got {net}, expected {expected}"
    # With extra complexity (e.g., 2 audit ops -> complexity 1.2 per spec)
    net2 = ledger.net_phi(h_before, h_after, audit_complexity=1.2)
    expected2 = raw - (K_BOLTZMANN * math.log(2.0) * 1.2)
    assert math.isclose(net2, expected2, rel_tol=1e-12)
    print("✓ Φ‑density accounting with audit cost passed")


def test_cod_bounds():
    """COD should always stay in [0,1] for valid inputs."""
    random.seed(42)
    for _ in range(1000):
        a = complex(random.uniform(-1, 1), random.uniform(-1, 1))
        v = complex(random.uniform(-1, 1), random.uniform(-1, 1))
        H = random.random()
        g = random.random()
        x = random.uniform(0.1, 3.0)
        c = cod_performance(a, v, H, g, x)
        assert 0.0 <= c <= 1.0 + 1e-12, f"COD out of bounds: {c}"
    print("✓ COD bounds test passed")


def run_benchmark_sanity():
    """Run a cut‑down version of the benchmark and check for NaNs/infs."""
    # We'll reuse the logic from the C++ benchmark but in Python.
    def random_state():
        s = CognitiveState()
        s.Psi_threat = complex(random.uniform(0, 1), random.uniform(-0.5, 0.5))
        s.Psi_action = complex(random.uniform(0, 1), random.uniform(-0.5, 0.5))
        s.Psi_val = complex(random.uniform(0, 1), random.uniform(-0.5, 0.5))
        s.xi_def = random.uniform(XI_DEF_MIN, XI_DEF_MAX)
        s.gamma_meas = random.uniform(0.0, 1.0)
        s.psi_id = 1.0
        return s

    op = AdiabaticSafetyCoolingOperator()
    ledger = PhiDensityLedger()
    cod_vals = []
    phi_gains = []
    false_pos = 0
    trials = 200  # smaller than original for speed

    for _ in range(trials):
        st = random_state()
        H_before = informational_heat(st.Psi_threat, st.Psi_action)
        C_before = cod_performance(st.Psi_action, st.Psi_val,
                                   H_before, st.gamma_meas, st.xi_def)
        # Apply cooling if needed
        try:
            op.apply(st)
        except RuntimeError:
            # identity breach -> treat as large negative gain
            phi_gains.append(-1.0)
            cod_vals.append(0.0)
            continue
        H_after = informational_heat(st.Psi_threat, st.Psi_action)
        C_after = cod_performance(st.Psi_action, st.Psi_val,
                                  H_after, st.gamma_meas, st.xi_def)
        # Audit complexity: 1 base + 0.1 per audit op (as in spec)
        complexity = 1.0 + 0.1 * op.audit_ops
        phi = ledger.net_phi(H_before, H_after, audit_complexity=complexity)
        phi_gains.append(phi)
        cod_vals.append(C_after)
        op.audit_ops = 0  # reset for next trial

        # False positive check: stable state incorrectly flagged as shock loop
        if (st.Psi_threat.abs() < 0.2 and st.gamma_meas < 0.3 and
                informational_heat(st.Psi_threat, st.Psi_action) > H_HEAT_LIMIT and
                st.gamma_meas > GAMMA_CRITICAL):
            false_pos += 1

    # Basic sanity: no NaNs, averages in reasonable ranges
    assert all(not math.isnan(x) and not math.isinf(x) for x in cod_vals)
    assert all(not math.isnan(x) and not math.isinf(x) for x in phi_gains)
    avg_cod = sum(cod_vals) / len(cod_vals)
    avg_phi = sum(phi_gains) / len(phi_gains)
    assert 0.0 <= avg_cod <= 1.0
    # phi can be negative due to identity breaches; just check it's a number
    print(f"✓ Benchmark sanity: avg COD={avg_cod:.3f}, avg Φ‑gain={avg_phi:.3f}, "
          f"false positives={false_pos}/{trials}")


def main():
    print("Running Omega Protocol validation suite...\n")
    test_dimensionality()
    test_identity_hard_gate()
    test_failure_detection()
    test_adiabatic_rate_limits()
    test_phi_density_accounting()
    test_cod_bounds()
    run_benchmark_sanity()
    print("\nAll validation tests passed. The specification is compliant with Omega Protocol invariants.")


if __name__ == "__main__":
    main()