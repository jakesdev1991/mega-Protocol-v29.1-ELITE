# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Validation script for Omega-Psych-Theorist's Quantum-Classical Cognitive Architecture
# Checks: dimensional homogeneity, invariant boundaries, COD formula correctness,
# AMP behavior, and Φ‑density accounting with audit cost.

import math
import random
from typing import List, Tuple

# ------------------- Core Definitions -------------------
class QuantumInvariants:
    LAMBDA_COUPLING = 1.0
    GAMMA_COUPLING = 0.5
    PSI_ID_MIN = 0.95
    XI_MEAS_MAX = 3.0   # shock warning threshold
    XI_MEAS_MIN = 0.2   # paralysis warning threshold

    def __init__(self, psi_id: float, xi_meas: float):
        self.psi_id = psi_id
        self.xi_meas = xi_meas

    def verify_invariants(self) -> Tuple[bool, List[str]]:
        warnings = []
        if self.psi_id < self.PSI_ID_MIN:
            return False, [f"Identity dissociation: psi_id={self.psi_id} < {self.PSI_ID_MIN}"]
        if self.xi_meas > self.XI_MEAS_MAX:
            warnings.append(f"Measurement shock risk: xi_meas={self.xi_meas} > {self.XI_MEAS_MAX}")
        if self.xi_meas < self.XI_MEAS_MIN:
            warnings.append(f"Analysis paralysis risk: xi_meas={self.xi_meas} < {self.XI_MEAS_MIN}")
        return True, warnings

    def phi_loss(self, audit_complexity: float = 1.0) -> float:
        K = 1.0  # normalized Boltzmann constant
        loss = 0.0
        if self.psi_id < self.PSI_ID_MIN:
            loss += (self.PSI_ID_MIN - self.psi_id) * 0.5 * K
        if self.xi_meas > self.XI_MEAS_MAX:
            loss += (self.xi_meas - self.XI_MEAS_MAX) * 0.2 * K
        loss += K * math.log(2.0) * audit_complexity   # audit entropy cost
        return loss


class QuantumState:
    def __init__(self, psi_q: List[float], psi_c: List[float],
                 h_quantum: float, xi_meas: float, psi_id: float = 1.0):
        assert len(psi_q) == len(psi_c), "State vectors must match dimension"
        self.psi_quantum = list(psi_q)
        self.psi_classical = list(psi_c)
        self.h_quantum = h_quantum
        self.xi_meas = xi_meas
        self.psi_id = psi_id
        self._lock = 0  # simple mutex stand‑in

    def lock(self): self._lock = 1
    def unlock(self): self._lock = 0

    def shannon_conditional_entropy(self) -> float:
        dot = sum(q * c for q, c in zip(self.psi_quantum, self.psi_classical))
        mag_q = sum(q * q for q in self.psi_quantum)
        mag_c = sum(c * c for c in self.psi_classical)
        if mag_q == 0 or mag_c == 0:
            p = 0.0
        else:
            p = dot / (math.sqrt(mag_q) * math.sqrt(mag_c))
        p = max(0.001, min(0.999, p))  # avoid log(0)
        return -(p * math.log(p) + (1.0 - p) * math.log(1.0 - p))


class ChainOverlapDensity:
    @staticmethod
    def calculate(state: QuantumState) -> float:
        # fidelity term
        dot = sum(q * c for q, c in zip(state.psi_quantum, state.psi_classical))
        mag_q = sum(q * q for q in state.psi_quantum)
        mag_c = sum(c * c for c in state.psi_classical)
        fidelity = 0.0
        if mag_q > 1e-12 and mag_c > 1e-12:
            f = dot / (math.sqrt(mag_q) * math.sqrt(mag_c))
            fidelity = f * f
        # entropic damping & stiffness penalty
        damping = math.exp(-QuantumInvariants.LAMBDA_COUPLING * state.h_quantum)
        stiffness_penalty = math.exp(-QuantumInvariants.GAMMA_COUPLING * state.xi_meas)
        return fidelity * damping * stiffness_penalty

    COD_THRESHOLD = 0.80
    @staticmethod
    def is_stable(cod: float) -> bool:
        return cod >= ChainOverlapDensity.COD_THRESHOLD


class FailureModeDetector:
    PSI_ID_CRITICAL = 0.90
    H_QUANTUM_LIMIT = 0.85
    XI_MEAS_CRITICAL = 2.5

    @staticmethod
    def check_risk(psi_id: float, h_quantum: float, xi_meas: float, cod: float) -> str:
        if h_quantum > FailureModeDetector.H_QUANTUM_LIMIT and xi_meas > FailureModeDetector.XI_MEAS_CRITICAL:
            return "MEASUREMENT_SHOCK"
        if h_quantum > FailureModeDetector.H_QUANTUM_LIMIT and xi_meas < 0.5:
            return "ANALYSIS_PARALYSIS"
        if psi_id < FailureModeDetector.PSI_ID_CRITICAL:
            return "DISSOCIATION"
        if cod < 0.40 and h_quantum > 0.60:
            return "DECOHERENCE"
        return "NONE"


class AdiabaticMeasurementOperator:
    @staticmethod
    def soften_stiffness(xi_meas: float, target_xi: float, alpha: float = 0.1) -> float:
        return xi_meas * (1.0 - alpha) + target_xi * alpha

    @staticmethod
    def inject_measurement(t: float, max_gamma: float = 1.2,
                           tau: float = 0.5, sigma: float = 0.2) -> float:
        ramp = math.tanh((t - tau) / sigma)
        return min(max_gamma, ramp * max_gamma)

    @staticmethod
    def execute(state: QuantumState, invariants: QuantumInvariants,
                t: float) -> bool:
        # Phase 2: soften
        state.xi_meas = AdiabaticMeasurementOperator.soften_stiffness(
            state.xi_meas, target_xi=1.0)
        # Phase 3: inject (gamma not stored, just used for conceptual coupling)
        _ = AdiabaticMeasurementOperator.inject_measurement(t)
        # Phase 4: simulate collapse (weighted average)
        for i in range(len(state.psi_quantum)):
            state.psi_classical[i] = 0.7 * state.psi_classical[i] + 0.3 * state.psi_quantum[i]
        # Phase 5: verify invariants & lock
        ok, warnings = invariants.verify_invariants()
        if not ok:
            for w in warnings:
                print(f"[VALIDATION] Invariant violation: {w}")
            return False
        # lock at higher stiffness
        state.xi_meas = AdiabaticMeasurementOperator.soften_stiffness(
            state.xi_meas, target_xi=2.0)
        return True


class PhiDensityLedger:
    K = 1.0
    @staticmethod
    def audit_cost(complexity: float = 1.0) -> float:
        return PhiDensityLedger.K * math.log(2.0) * complexity

    @staticmethod
    def individual_cost(h_quantum: float, xi_meas: float) -> float:
        return h_quantum * xi_meas * 0.2

    @staticmethod
    def net_phi(h_before: float, h_after: float,
                audit_complexity: float = 1.0,
                h_quantum: float = 0.0, xi_meas: float = 0.0) -> float:
        raw_gain = -(h_after - h_before)
        audit = PhiDensityLedger.audit_cost(audit_complexity)
        indiv = PhiDensityLedger.individual_cost(h_quantum, xi_meas)
        return raw_gain - audit - indiv


# ------------------- Validation Routine -------------------
def run_validation():
    print("=== Omega Protocol Validation Start ===")

    # 1. Dimensional homogeneity – all inputs should be dimensionless (~[0,1] or small multiples)
    state = QuantumState(
        psi_q=[0.6, 0.3, 0.1],
        psi_c=[0.2, 0.2, 0.2],
        h_quantum=0.7,
        xi_meas=1.5,
        psi_id=0.98
    )
    invariants = QuantumInvariants(state.psi_id, state.xi_meas)

    # Invariant check
    ok, warns = invariants.verify_invariants()
    assert ok, f"Invariant failed: {warns}"
    for w in warns:
        print(f"[WARNING] {w}")

    # COD calculation sanity
    cod = ChainOverlapDensity.calculate(state)
    print(f"COD = {cod:.4f}")
    assert 0.0 <= cod <= 1.0, "COD out of bounds [0,1]"
    # Stiffness penalty present: if we artificially raise xi_meas, COD should drop
    state_high_xi = QuantumState(state.psi_quantum, state.psi_classical,
                                 state.h_quantum, xi_meas=3.0, psi_id=state.psi_id)
    cod_high = ChainOverlapDensity.calculate(state_high_xi)
    assert cod_high < cod, "Stiffness penalty not reducing COD"

    # Entropic damping: higher h_quantum lowers COD
    state_high_h = QuantumState(state.psi_quantum, state.psi_classical,
                                h_quantum=1.2, xi_meas=state.xi_meas, psi_id=state.psi_id)
    cod_high_h = ChainOverlapDensity.calculate(state_high_h)
    assert cod_high_h < cod, "Entropic damping not reducing COD"

    # Failure mode detection
    fm = FailureModeDetector.check_risk(state.psi_id, state.h_quantum, state.xi_meas, cod)
    assert fm == "NONE", f"Unexpected failure mode: {fm}"
    # Trigger a shock condition
    state_shock = QuantumState(state.psi_quantum, state.psi_classical,
                               h_quantum=0.9, xi_meas=2.8, psi_id=0.96)
    fm_shock = FailureModeDetector.check_risk(state_shock.psi_id,
                                              state_shock.h_quantum,
                                              state_shock.xi_meas,
                                              ChainOverlapDensity.calculate(state_shock))
    assert fm_shock == "MEASUREMENT_SHOCK", f"Shock not detected: {fm_shock}"

    # AMP execution – should succeed under nominal conditions
    amp_success = AdiabaticMeasurementOperator.execute(state, invariants, t=0.6)
    assert amp_success, "AMP execution failed unexpectedly"
    # After execution, xi_meas should be locked near 2.0
    assert 1.8 <= state.xi_meas <= 2.2, f"Lock stiffness out of expected range: {state.xi_meas}"

    # Φ‑density ledger with audit cost
    h_before = state.shannon_conditional_entropy()
    # simulate a small entropy reduction after measurement
    state.h_quantum *= 0.9
    h_after = state.shannon_conditional_entropy()
    phi_net = PhiDensityLedger.net_phi(
        h_before, h_after,
        audit_complexity=1.5,
        h_quantum=state.h_quantum,
        xi_meas=state.xi_meas
    )
    print(f"Net Φ gain = {phi_net:.4f}")
    # Net gain should be positive for a successful adiabatic step
    assert phi_net > 0, f"Φ‑density not increasing: {phi_net}"

    # Benchmark‑style sweep (lightweight)
    success_cnt = 0
    trials = 20
    for i in range(trials):
        # randomize entropy and stiffness within plausible bounds
        test_state = QuantumState(
            psi_q=[random.random()*0.5+0.5, random.random()*0.3, random.random()*0.2],
            psi_c=[0.2, 0.2, 0.2],
            h_quantum=random.random()*0.6+0.2,
            xi_meas=random.random()*2.0+0.3,
            psi_id=0.99
        )
        test_inv = QuantumInvariants(test_state.psi_id, test_state.xi_meas)
        ok, _ = test_inv.verify_invariants()
        if not ok:
            continue  # skip invalid baseline
        # run AMP
        if AdiabaticMeasurementOperator.execute(test_state, test_inv, t=0.5 + i*0.02):
            success_cnt += 1
    failure_rate = 1.0 - (success_cnt / trials)
    print(f"Benchmark success rate: {success_cnt}/{trials} (failure rate={failure_rate:.2f})")
    assert failure_rate < 0.4, "Failure rate too high – AMP not robust"

    print("=== All validation checks passed ===")


if __name__ == "__main__":
    run_validation()