# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script for Trauma‑Performance Manifold (v37.0-Ω-Trauma-QS)
--------------------------------------------------------------------------------
This script mirrors the essential mathematics from the provided C++ implementation
and enforces the Omega Protocol invariants programmatically.
"""

import math
from dataclasses import dataclass, field
from typing import List, Tuple

# ----------------------------------------------------------------------
# Constants (dimensionless [1])
# ----------------------------------------------------------------------
K_BOLTZMANN = 1.0
LAMBDA_COUPLING = 1.0          # Entropic damping
GAMMA_COUPLING = 0.7           # Stiffness penalty
H_TRAUMA_LIMIT = 0.90          # Max unresolved entropy
XI_MAX_DIFF = 1.5              # Max allowed |Ξ_supp - Ξ_safe|
PSI_IDENTITY_MIN = 0.95        # Identity continuity threshold (Phi_N)
PSI_IDENTITY_MIN_LOG = math.log(PSI_IDENTITY_MIN)   # ≈ -0.051293
COD_THRESHOLD = 0.75           # Minimum acceptable COD
IDENTITY_DRIFT_CRITICAL = 0.90 # psi threshold for drift detection (Phi_N)
IDENTITY_DRIFT_CRITICAL_LOG = math.log(IDENTITY_DRIFT_CRITICAL)

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def shannon_entropy(probs: List[float]) -> float:
    """Normalized Shannon entropy: H = - Σ p log p / log(N)"""
    if not probs:
        return 0.0
    # Clip to avoid log(0)
    probs = [max(p, 1e-12) for p in probs]
    raw = -sum(p * math.log(p) for p in probs)
    max_ent = math.log(len(probs))
    if max_ent < 1e-12:
        max_ent = 1.0
    return min(1.0, max(0.0, raw / max_ent))

def fidelity(u: List[float], v: List[float]) -> float:
    """|⟨u|v⟩|² normalized by ‖u‖²‖v‖²"""
    if len(u) != len(v):
        raise ValueError("Vectors must be same length")
    dot = sum(a * b for a, b in zip(u, v))
    norm_u = sum(a * a for a in u)
    norm_v = sum(b * b for b in v)
    if norm_u == 0.0 or norm_v == 0.0:
        return 0.0
    fid = dot / math.sqrt(norm_u * norm_v)
    fid = max(0.0, min(1.0, fid))   # clamp to [0,1]
    return fid * fid                # square magnitude

def trauma_cod(perf: List[float], safe: List[float],
               H_trauma: float, xi_supp: float, xi_safe: float) -> float:
    """COD = fidelity * exp(-Λ*H) * exp(-Γ*|ΔΞ|)"""
    fid = fidelity(perf, safe)
    damping = math.exp(-LAMBDA_COUPLING * H_trauma)
    stiffness_penalty = math.exp(-GAMMA_COUPLING * abs(xi_supp - xi_safe))
    return fid * damping * stiffness_penalty

# ----------------------------------------------------------------------
# Data structures
# ----------------------------------------------------------------------
@dataclass
class TraumaInvariants:
    psi: float               # ln(Phi_N) – identity continuity
    xi_supp: float           # Suppression stiffness
    xi_safe: float           # Safety capacity
    phi_K: float = 0.0       # Performance density (covariant mode)
    phi_Sigma: float = 0.0   # Trauma entropy density
    # coupling constants as class attributes (already defined globally)

    def verify_invariants(self) -> None:
        """Active boundary condition – raise if violated."""
        if self.psi < PSI_IDENTITY_MIN_LOG:
            raise AssertionError(
                f"Identity Shredding: psi={self.psi} < ln({PSI_IDENTITY_MIN})"
            )
        if abs(self.xi_supp - self.xi_safe) > XI_MAX_DIFF:
            raise AssertionError(
                f"Decoherence Crash Risk: |xi_supp-xi_safe|={abs(self.xi_supp-self.xi_safe)} > {XI_MAX_DIFF}"
            )
        if self.phi_Sigma > 0.10:
            # Warning only, not fatal per original code
            pass  # could log; we keep as non‑fatal

@dataclass
class TraumaState:
    psi_perf: List[float] = field(default_factory=list)
    psi_safe: List[float] = field(default_factory=list)
    trauma_signals: List[float] = field(default_factory=list)
    phi_K: float = 0.0
    phi_Sigma: float = 0.0
    xi_supp: float = 0.0
    xi_safe: float = 0.0
    psi: float = 0.0          # ln(Phi_N)
    t: float = 0.0
    # internal lock not needed in pure Python single‑threaded demo

    def compute_H_trauma(self) -> float:
        return shannon_entropy(self.trauma_signals)

    def current_cod(self) -> float:
        H = self.compute_H_trauma()
        return trauma_cod(self.psi_perf, self.psi_safe, H,
                          self.xi_supp, self.xi_safe)

# ----------------------------------------------------------------------
# Failure mode detector
# ----------------------------------------------------------------------
class FailureMode:
    NONE = 0
    DECOHERENCE_CRASH = 1
    IDENTITY_DRIFT = 2
    VALIDATION_LOOP = 3

class FailureModeDetector:
    @staticmethod
    def check_risk(H_trauma: float, xi_supp: float, xi_safe: float,
                   psi: float, cod: float) -> int:
        stiffness_diff = abs(xi_supp - xi_safe)
        if (H_trauma > H_TRAUMA_LIMIT and
                stiffness_diff > XI_MAX_DIFF and
                psi < PSI_IDENTITY_MIN_LOG):
            return FailureMode.DECOHERENCE_CRASH
        if psi < PSI_IDENTITY_MIN_LOG:
            return FailureMode.IDENTITY_DRIFT
        if cod < COD_THRESHOLD and stiffness_diff > 1.0:
            return FailureMode.VALIDATION_LOOP
        return FailureMode.NONE

# ----------------------------------------------------------------------
# Adiabatic Integration Protocol (AIP) – single step
# ----------------------------------------------------------------------
class AdiabaticIntegrationOperator:
    @staticmethod
    def apply(state: TraumaState, invariants: TraumaInvariants) -> None:
        # Phase 1: Diagnostic
        H_trauma = state.compute_H_trauma()
        cod = state.current_cod()
        failure = FailureModeDetector.check_risk(
            H_trauma, state.xi_supp, state.xi_safe, state.psi, cod
        )

        # Phase 2: Stiffness Modulation (Safety‑First)
        if failure == FailureMode.DECOHERENCE_CRASH:
            # Increase safety first
            state.xi_safe = min(2.0, state.xi_safe * 1.1)
        elif failure == FailureMode.IDENTITY_DRIFT:
            # Grounding: reinforce safe self
            state.psi_safe = [v + 0.05 for v in state.psi_safe]
        elif failure == FailureMode.VALIDATION_LOOP:
            # Slowly lower suppression
            state.xi_supp = max(0.5, state.xi_supp * 0.9)
        else:  # NONE but low COD -> adiabatic interpolation
            if cod < COD_THRESHOLD:
                state.xi_safe = state.xi_safe * 0.9 + state.xi_supp * 0.1

        # Phase 3: State Transformation (convex blend)
        alpha = min(1.0, (1.0 - abs(state.xi_supp - state.xi_safe)) * 0.5 + 0.5)
        state.psi_perf = [
            (1.0 - alpha) * a + alpha * b
            for a, b in zip(state.psi_perf, state.psi_safe)
        ]

        # Phase 4: Entropy Accounting (identity loss)
        identity_loss = H_trauma * 0.05
        phi_N = math.exp(state.psi)
        phi_N -= identity_loss
        state.psi = math.log(max(phi_N, 1e-12))  # guard against log(0)

        # Phase 5: Invariant Validation – hard gate
        invariants.psi = state.psi
        invariants.xi_supp = state.xi_supp
        invariants.phi_Sigma = H_trauma
        invariants.verify_invariants()   # will raise AssertionError if broken

# ----------------------------------------------------------------------
# Φ‑density ledger with audit cost subtraction
# ----------------------------------------------------------------------
class PhiDensityLedger:
    @staticmethod
    def calculate_impact(h_trauma: float, cod_gain: float,
                         audit_complexity: float = 1.0) -> float:
        raw_gain = cod_gain
        entropy_cost = h_trauma * 0.6          # higher weight for trauma
        audit_entropy = K_BOLTZMANN * math.log(2.0) * audit_complexity
        return raw_gain - entropy_cost - audit_entropy

# ----------------------------------------------------------------------
# Benchmark suite (mirrors C++ version)
# ----------------------------------------------------------------------
def run_benchmark() -> Tuple[float, float, float, float, float]:
    # Initial state
    state = TraumaState(
        psi_perf=[1.0, 0.2, 0.1],
        psi_safe=[0.2, 0.8, 0.1],
        trauma_signals=[0.9, 0.8, 0.7, 0.6],
        xi_supp=3.0,
        xi_safe=0.5,
        psi=math.log(1.0)   # Phi_N = 1.0 → psi = 0
    )
    invariants = TraumaInvariants(
        psi=state.psi,
        xi_supp=state.xi_supp,
        xi_safe=state.xi_safe
    )

    H_initial = state.compute_H_trauma()
    baseline_cod = state.current_cod()

    operator = AdiabaticIntegrationOperator()
    integration_cycles = 0.0
    try:
        for _ in range(5):
            # simulate processing by adding a moderate signal
            state.trauma_signals.append(0.5)
            operator.apply(state, invariants)
            integration_cycles += 1.0
    except AssertionError as e:
        # Invariant breach – treat as failure
        print(f"Benchmark aborted due to invariant violation: {e}")
        return baseline_cod, 0.0, 1.0, -1.0, integration_cycles

    H_final = state.compute_H_trauma()
    integrated_cod = state.current_cod()
    identity_loss = 1.0 - math.exp(state.psi)   # fraction of identity lost
    ledger = PhiDensityLedger()
    phi_net_gain = ledger.calculate_impact(
        H_final, integrated_cod - baseline_cod, audit_complexity=1.0
    )
    return baseline_cod, integrated_cod, identity_loss, phi_net_gain, integration_cycles

# ----------------------------------------------------------------------
# Self‑test / demonstration
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Omega Protocol Trauma‑Performance Manifold Validation ===")
    base_cod, int_cod, id_loss, phi_gain, cycles = run_benchmark()
    print(f"Baseline COD:               {base_cod:.4f}")
    print(f"Integrated COD (after {int(cycles)} cycles): {int_cod:.4f}")
    print(f"Identity loss (frac):       {id_loss:.4f}")
    print(f"Φ‑density net gain:         {phi_gain:.4f}")
    print("\nInvariants have been actively checked throughout.")
    print("If no AssertionError was raised, the specification is compliant.")