# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Runtime Validator – Freeze-Internal Coupling Manifold (v70.0-Ω)
Asserts dimensional bounds, gate hierarchy, and derivativity-safe metrics.
"""

import math
from dataclasses import dataclass
from typing import List, Tuple

# ----------------------------------------------------------------------
# Protocol Constants (must match the C++ implementation)
# ----------------------------------------------------------------------
PSI_INTEGRITY_THRESHOLD = 0.95
COUPLING_MIN = 0.60
DIVERGENCE_MAX = 0.40
FREEZE_EFFICACY_MIN = 0.65
SELF_CORRECTION_MIN = 0.60
COD_THRESHOLD = 0.85
AUDIT_ENTROPY_PER_CHECK = 0.02  # per invariant check

# ----------------------------------------------------------------------
# State Container (mirrors FreezeInternalCouplingState)
# ----------------------------------------------------------------------
@dataclass
class State:
    psi_integrity: float
    h_instability: float
    theta_tensor_leak: float
    boundary_exposure: float
    liquidity_density: float
    freeze_efficacy: float
    boundary_stress: float
    permeability_rate: float
    freeze_boundary_risk: float
    coherence_time: float
    error_rate: float
    self_correction_efficacy: float
    decoherence_rate: float
    coherence_resilience_risk: float
    # Derived / computed fields (will be filled by validator)
    boundary_internal_coupling: float = 0.0
    divergence_index: float = 0.0
    masking_risk: float = 0.0
    coupled_risk: float = 0.0
    cod: float = 0.0
    phi_N: float = 0.0

# ----------------------------------------------------------------------
# Helper Functions (exact replicas of the C++ logic)
# ----------------------------------------------------------------------
def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

def calc_boundary_internal_coupling(fe: float, sce: float) -> float:
    avg = (fe + sce) / 2.0
    diff = abs(fe - sce)
    return clamp(avg * (1.0 - diff))

def calc_divergence_index(fe: float, sce: float, fbr: float, crr: float) -> float:
    risk_div = abs(fbr - crr)
    eff_div = abs(fe - sce)
    return clamp((risk_div + eff_div) / 2.0)

def calc_masking_risk(fe: float, sce: float, be: float) -> float:
    gap = fe - sce
    if gap < 0.0:
        gap = 0.0
    return clamp(gap * be)

def calc_coupled_risk(fbr: float, crr: float, bic: float) -> float:
    avg_risk = (fbr + crr) / 2.0
    coupling_deficit = 1.0 - bic
    amplification = 1.0 + coupling_deficit   # ∈ [1,2]
    raw = avg_risk * amplification
    return clamp(raw)

def calc_cod_coupling_aware(
    diagnostic: List[complex],
    plasma: List[complex],
    h_inst: float,
    theta_leak: float,
    bic: float,
    div_idx: float,
    coupled_risk: float
) -> float:
    # Fidelity term
    size = min(len(diagnostic), len(plasma))
    dot = 0.0
    magD = 0.0
    magP = 0.0
    for i in range(size):
        dot += abs(conj(diagnostic[i]) * plasma[i])
        magD += abs(diagnostic[i] * diagnostic[i])
        magP += abs(plasma[i] * plasma[i])
    fidelity = 0.0
    if magD > 1e-9 and magP > 1e-9:
        fidelity = dot / (math.sqrt(magD) * math.sqrt(magP))
        fidelity = clamp(fidelity)

    # Penalties
    LAMBDA = 0.5
    MU = 0.7
    instability_penalty = math.exp(-LAMBDA * h_inst)
    exposure_penalty = math.exp(-LAMBDA * theta_leak)
    coupling_penalty = math.exp(-MU * (1.0 - bic))
    divergence_penalty = math.exp(-MU * div_idx)
    risk_penalty = math.exp(-MU * coupled_risk)

    return fidelity * instability_penalty * exposure_penalty * \
           coupling_penalty * divergence_penalty * risk_penalty

def conj(z: complex) -> complex:
    return z.real - z.imag * 1j

# ----------------------------------------------------------------------
# Validator
# ----------------------------------------------------------------------
class ProtocolViolation(RuntimeError):
    pass

def validate(state: State) -> Tuple[bool, List[str]]:
    """
    Returns (True, []) if all checks pass; otherwise raises ProtocolViolation
    with a list of failed assertions.
    """
    failures = []

    # 1. Recompute coupling metrics
    state.boundary_internal_coupling = calc_boundary_internal_coupling(
        state.freeze_efficacy, state.self_correction_efficacy
    )
    state.divergence_index = calc_divergence_index(
        state.freeze_efficacy, state.self_correction_efficacy,
        state.freeze_boundary_risk, state.coherence_resilience_risk
    )
    state.masking_risk = calc_masking_risk(
        state.freeze_efficacy, state.self_correction_efficacy,
        state.boundary_exposure
    )
    state.coupled_risk = calc_coupled_risk(
        state.freeze_boundary_risk, state.coherence_resilience_risk,
        state.boundary_internal_coupling
    )
    # COD uses empty diagnostic/plasma vectors as in the C++ demo
    state.cod = calc_cod_coupling_aware(
        [], [], state.h_instability, state.theta_tensor_leak,
        state.boundary_internal_coupling, state.divergence_index,
        state.coupled_risk
    )
    state.phi_N = state.cod  # direct assignment, no log2

    # 2. Dimensional bounds (hard invariant)
    bounds_checks = [
        ("psi_integrity", state.psi_integrity),
        ("h_instability", state.h_instability),
        ("theta_tensor_leak", state.theta_tensor_leak),
        ("boundary_exposure", state.boundary_exposure),
        ("liquidity_density", state.liquidity_density),
        ("freeze_efficacy", state.freeze_efficacy),
        ("boundary_stress", state.boundary_stress),
        ("permeability_rate", state.permeability_rate),
        ("freeze_boundary_risk", state.freeze_boundary_risk),
        ("coherence_time", state.coherence_time),
        ("error_rate", state.error_rate),
        ("self_correction_efficacy", state.self_correction_efficacy),
        ("decoherence_rate", state.decoherence_rate),
        ("coherence_resilience_risk", state.coherence_resilience_risk),
        ("boundary_internal_coupling", state.boundary_internal_coupling),
        ("divergence_index", state.divergence_index),
        ("masking_risk", state.masking_risk),
        ("coupled_risk", state.coupled_risk),
        ("cod", state.cod),
        ("phi_N", state.phi_N),
    ]
    for name, val in bounds_checks:
        if not (0.0 <= val <= 1.0):
            failures.append(f"BOUND VIOLATION: {name}={val:.6f} ∉ [0,1]")

    # 3. Hard Gates (non‑negotiable)
    if state.psi_integrity < PSI_INTEGRITY_THRESHOLD:
        failures.append(f"Ψ_INTEGRITY_GATE: {state.psi_integrity:.6f} < {PSI_INTEGRITY_THRESHOLD}")
    # Coupling state classification (mirrors C++)
    if state.boundary_internal_coupling < 0.30:
        coupling_state = "COLLAPSED"
    elif (state.divergence_index > DIVERGENCE_MAX and
          state.freeze_efficacy > 0.70 and
          state.self_correction_efficacy < 0.50):
        coupling_state = "BOUNDARY_MASKED"
    elif state.divergence_index > DIVERGENCE_MAX:
        coupling_state = "DIVERGING"
    else:
        coupling_state = "ALIGNED"
    if coupling_state == "COLLAPSED":
        failures.append(f"COLLAPSED_COUPLING_STATE: state={coupling_state}")

    # 4. Risk‑level consistency (optional but informative)
    if state.coupled_risk > 0.70:
        risk_level = "CATASTROPHIC"
    elif state.coupled_risk > 0.50:
        risk_level = "CRITICAL"
    elif state.coupled_risk > 0.30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    # No assertion here; just for reporting

    # 5. Φ‑density ledger sanity (example: 11 audit checks as in C++)
    audit_checks = 11
    raw_gain = state.cod - 0.0  # assume baseline COD=0 for demonstration
    audit_cost = audit_checks * AUDIT_ENTROPY_PER_CHECK
    net_gain = raw_gain - audit_cost
    if net_gain < -1e-9:  # allow tiny floating‑point underflow
        failures.append(f"Φ_DENSITY_LEDGER: net_gain={net_gain:.6f} < 0 (audit overrun)")

    if failures:
        raise ProtocolViolation("\n".join(failures))
    return True, []

# ----------------------------------------------------------------------
# Example Usage (replace with actual state from the system)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Mock state – all values well within safe bounds
    mock_state = State(
        psi_integrity=0.98,
        h_instability=0.1,
        theta_tensor_leak=0.05,
        boundary_exposure=0.2,
        liquidity_density=0.4,
        freeze_efficacy=0.8,
        boundary_stress=0.1,
        permeability_rate=0.15,
        freeze_boundary_risk=0.25,
        coherence_time=0.85,
        error_rate=0.05,
        self_correction_efficacy=0.78,
        decoherence_rate=0.07,
        coherence_resilience_risk=0.18,
    )
    try:
        ok, _ = validate(mock_state)
        print("✅ Protocol validation PASSED")
    except ProtocolViolation as e:
        print("❌ Protocol validation FAILED:\n", e)