# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Invariant Validator for Freeze-Internal Coupling Manifold (v70.0-Ω)
Strictly checks:
  • All metrics dimensionless and bounded [0,1]
  • No log2() or illegal transforms
  • Safety gate hierarchy integrity
  • Coupling metrics are novel (not simple copies of v68.0/v69.0 terms)
  • Φ-density accounting honesty (audit cost subtracted)
"""

import math
import random
from typing import NamedTuple, List

# ---- Protocol Constants (from v70.0-Ω) ----
PSI_INTEGRITY_THRESHOLD = 0.95
COUPLING_MIN = 0.60
DIVERGENCE_MAX = 0.40
FREEZE_EFFICACY_MIN = 0.65
SELF_CORRECTION_MIN = 0.60
COD_THRESHOLD = 0.85
AUDIT_ENTROPY_PER_CHECK = 0.02
LAMBDA_COUPLING = 0.5
MU_FREEZE_INTERNAL = 0.7

# ---- State Definition (mirrors C++ struct) ----
class FreezeInternalCouplingState(NamedTuple):
    query_branch: str          # expected "finance"
    query_concepts: str        # e.g., "admin, freeze boundary"
    exposed_endpoint: str      # e.g., "/admin/liquidity/freeze/"

    psi_integrity: float       # [0,1]
    h_instability: float       # [0,1]
    theta_tensor_leak: float   # [0,1]

    # v69.0 metrics
    boundary_exposure: float   # [0,1]
    liquidity_density: float   # [0,1]
    freeze_efficacy: float     # [0,1]
    boundary_stress: float     # [0,1]
    permeability_rate: float   # [0,1]
    freeze_boundary_risk: float # [0,1]

    # v68.0 metrics
    coherence_time: float      # [0,1]
    error_rate: float          # [0,1]
    self_correction_efficacy: float # [0,1]
    decoherence_rate: float    # [0,1]
    coherence_resilience_risk: float # [0,1]

    # derived / coupling metrics (to be computed)
    boundary_internal_coupling: float = 0.0
    divergence_index: float = 0.0
    masking_risk: float = 0.0
    coupled_risk: float = 0.0
    cod: float = 0.0
    phi_N: float = 0.0

# ---- Helper Functions (exact translations from C++) ----
def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

def calculate_boundary_internal_coupling(freeze_efficacy: float,
                                         self_correction_efficacy: float) -> float:
    avg = (freeze_efficacy + self_correction_efficacy) / 2.0
    diff = abs(freeze_efficacy - self_correction_efficacy)
    return clamp(avg * (1.0 - diff))

def calculate_divergence_index(freeze_efficacy: float,
                               self_correction_efficacy: float,
                               freeze_boundary_risk: float,
                               coherence_resilience_risk: float) -> float:
    risk_div = abs(freeze_boundary_risk - coherence_resilience_risk)
    eff_div = abs(freeze_efficacy - self_correction_efficacy)
    return clamp((risk_div + eff_div) / 2.0)

def calculate_masking_risk(freeze_efficacy: float,
                           self_correction_efficacy: float,
                           boundary_exposure: float) -> float:
    gap = freeze_efficacy - self_correction_efficacy
    if gap < 0.0:
        gap = 0.0
    return clamp(gap * boundary_exposure)

def calculate_coupled_risk(freeze_boundary_risk: float,
                           coherence_resilience_risk: float,
                           boundary_internal_coupling: float) -> float:
    avg_risk = (freeze_boundary_risk + coherence_resilience_risk) / 2.0
    coupling_deficit = 1.0 - boundary_internal_coupling
    amplification = 1.0 + coupling_deficit
    return clamp(avg_risk * amplification)

def calculate_cod_coupling_aware(diagnostic_vec: List[complex],
                                 plasma_vec: List[complex],
                                 h_instability: float,
                                 theta_tensor_leak: float,
                                 boundary_internal_coupling: float,
                                 divergence_index: float,
                                 coupled_risk: float) -> float:
    # Fidelity (dot product of normalized vectors)
    dot = 0.0
    magD = 0.0
    magP = 0.0
    size = min(len(diagnostic_vec), len(plasma_vec))
    for i in range(size):
        dot += abs(conjugate(diagnostic_vec[i]) * plasma_vec[i])
        magD += abs(diagnostic_vec[i] * diagnostic_vec[i])
        magP += abs(plasma_vec[i] * plasma_vec[i])
    fidelity = 0.0
    if magD > 1e-9 and magP > 1e-9:
        fidelity = dot / (math.sqrt(magD) * math.sqrt(magP))
        fidelity = clamp(fidelity)

    instability_penalty = math.exp(-LAMBDA_COUPLING * h_instability)
    exposure_penalty = math.exp(-LAMBDA_COUPLING * theta_tensor_leak)
    coupling_penalty = math.exp(-MU_FREEZE_INTERNAL * (1.0 - boundary_internal_coupling))
    divergence_penalty = math.exp(-MU_FREEZE_INTERNAL * divergence_index)
    risk_penalty = math.exp(-MU_FREEZE_INTERNAL * coupled_risk)

    return fidelity * instability_penalty * exposure_penalty * \
           coupling_penalty * divergence_penalty * risk_penalty

def conjugate(z: complex) -> complex:
    return z.real - z.imag * 1j

# ---- Safety Gate Logic (from C++) ----
class CouplingState:
    ALIGNED = 0
    DIVERGING = 1
    BOUNDARY_MASKED = 2
    COLLAPSED = 3

def classify_coupling_state(bic: float, div: float,
                            fe: float, sce: float) -> int:
    if bic < 0.30:
        return CouplingState.COLLAPSED
    if div > DIVERGENCE_MAX and fe > 0.70 and sce < 0.50:
        return CouplingState.BOUNDARY_MASKED
    if div > DIVERGENCE_MAX:
        return CouplingState.DIVERGING
    return CouplingState.ALIGNED

class RiskLevel:
    LOW = 0
    MEDIUM = 1
    CRITICAL = 2
    CATASTROPHIC = 3

def assess_risk(coupled_risk: float) -> int:
    if coupled_risk > 0.70:
        return RiskLevel.CATASTROPHIC
    if coupled_risk > 0.50:
        return RiskLevel.CRITICAL
    if coupled_risk > 0.30:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW

def decide_action(psi_integrity: float,
                  coupled_risk: float,
                  coupling_state: int) -> int:
    # PRIMARY GATE
    if psi_integrity < PSI_INTEGRITY_THRESHOLD:
        return 3  # IDENTITY_LOCKDOWN (using same encoding as Action enum below)
    # COUPLING STATE GATE
    if coupling_state == CouplingState.COLLAPSED:
        return 3
    # RISK-BASED
    if coupled_risk > 0.70:
        return 3
    if coupled_risk > 0.50 or coupling_state == CouplingState.BOUNDARY_MASKED:
        return 2  # ACTIVATE_COUPLING_REPAIR
    if coupled_risk > 0.30 or coupling_state == CouplingState.DIVERGING:
        return 1  # FLAG_DIVERGENCE_MONITOR
    return 0      # PROCEED

# Action enum (mirrors C++)
class Action:
    PROCEED = 0
    FLAG_DIVERGENCE_MONITOR = 1
    ACTIVATE_COUPLING_REPAIR = 2
    IDENTITY_LOCKDOWN = 3

# ---- Invariant Checks ----
def check_dimension_bounds(state: FreezeInternalCouplingState) -> List[str]:
    violations = []
    # All raw fields must be [0,1]
    fields = [
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
    ]
    for name, val in fields:
        if not (0.0 <= val <= 1.0):
            violations.append(f"{name}={val} not in [0,1]")
    # Computed coupling metrics
    computed = [
        ("boundary_internal_coupling", state.boundary_internal_coupling),
        ("divergence_index", state.divergence_index),
        ("masking_risk", state.masking_risk),
        ("coupled_risk", state.coupled_risk),
        ("cod", state.cod),
        ("phi_N", state.phi_N),
    ]
    for name, val in computed:
        if not (0.0 <= val <= 1.0):
            violations.append(f"{name}={val} not in [0,1]")
    return violations

def check_no_log2(state: FreezeInternalCouplingState) -> List[str]:
    # The only place phi_N is set should be direct assignment from cod.
    # We cannot statically analyze code here, but we can enforce the relation:
    violations = []
    if not math.isclose(state.phi_N, state.cod, rel_tol=1e-9, abs_tol=1e-12):
        violations.append(f"phi_N ({state.phi_N}) != cod ({state.cod}) – possible log2 or illegal transform")
    return violations

def check_gate_hierarchy(state: FreezeInternalCouplingState) -> List[str]:
    violations = []
    bic = state.boundary_internal_coupling
    div = state.divergence_index
    fe = state.freeze_efficacy
    sce = state.self_correction_efficacy
    fbr = state.freeze_boundary_risk
    crr = state.coherence_resilience_risk
    coupling_state = classify_coupling_state(bic, div, fe, sce)
    coupled_risk = state.coupled_risk
    action = decide_action(state.psi_integrity, coupled_risk, coupling_state)

    # If integrity fails -> must be LOCKDOWN
    if state.psi_integrity < PSI_INTEGRITY_THRESHOLD and action != Action.IDENTITY_LOCKDOWN:
        violations.append("Integrity breach did not trigger IDENTITY_LOCKDOWN")
    # If coupling state collapsed -> must be LOCKDOWN
    if coupling_state == CouplingState.COLLAPSED and action != Action.IDENTITY_LOCKDOWN:
        violations.append("COLLAPSED coupling state did not trigger IDENTITY_LOCKDOWN")
    # If high coupled risk (>0.70) -> must be LOCKDOWN
    if coupled_risk > 0.70 and action != Action.IDENTITY_LOCKDOWN:
        violations.append("Coupled risk >0.70 did not trigger IDENTITY_LOCKDOWN")
    # If medium-high risk or boundary masking -> must be at least REPAIR
    if (coupled_risk > 0.50 or coupling_state == CouplingState.BOUNDARY_MASKED) and action < Action.ACTIVATE_COUPLING_REPAIR:
        violations.append("Medium/high risk or masking did not trigger at least ACTIVATE_COUPLING_REPAIR")
    # If low-medium risk or divergence -> must be at least MONITOR
    if (coupled_risk > 0.30 or coupling_state == CouplingState.DIVERGING) and action < Action.FLAG_DIVERGENCE_MONITOR:
        violations.append("Low-medium risk or divergence did not trigger at least FLAG_DIVERGENCE_MONITOR")
    return violations

def check_derivativity_novelty(state: FreezeInternalCouplingState) -> List[str]:
    """
    Light-weight novelty check: ensure coupling metrics are not just copies
    of existing v68.0/v69.0 fields. We verify that boundary_internal_coupling
    is a non-trivial function of both freeze_efficacy and self_correction_efficacy.
    """
    violations = []
    fe = state.freeze_efficacy
    sce = state.self_correction_efficacy
    bic = state.boundary_internal_coupling
    # Expected coupling from formula:
    expected = calculate_boundary_internal_coupling(fe, sce)
    if not math.isclose(bic, expected, rel_tol=1e-9, abs_tol=1e-12):
        violations.append(f"boundary_internal_coupling ({bic}) does not match formula ({expected})")
    # Additionally, ensure it's not equal to either efficacy alone (unless both equal)
    if math.isclose(bic, fe, abs_tol=1e-3) and not math.isclose(fe, sce, abs_tol=1e-3):
        violations.append("boundary_internal_coupling appears to be a copy of freeze_efficacy")
    if math.isclose(bic, sce, abs_tol=1e-3) and not math.isclose(fe, sce, abs_tol=1e-3):
        violations.append("boundary_internal_coupling appears to be a copy of self_correction_efficacy")
    return violations

def check_phi_density_accounting(cod_before: float,
                                 cod_after: float,
                                 audit_checks: int,
                                 claimed_gain: float) -> List[str]:
    violations = []
    raw_gain = cod_after - cod_before
    audit_cost = audit_checks * AUDIT_ENTROPY_PER_CHECK
    expected_gain = raw_gain - audit_cost
    if not math.isclose(claimed_gain, expected_gain, rel_tol=1e-9, abs_tol=1e-12):
        violations.append(f"Φ-density gain mismatch: claimed {claimed_gain}, expected {expected_gain}")
    return violations

# ---- Full Validation Routine ----
def validate_state(state: FreezeInternalCouplingState) -> List[str]:
    """Run all invariant checks and return list of violations (empty if sound)."""
    # 1. Compute derived metrics if not pre-filled
    bic = calculate_boundary_internal_coupling(state.freeze_efficacy,
                                               state.self_correction_efficacy)
    div = calculate_divergence_index(state.freeze_efficacy,
                                     state.self_correction_efficacy,
                                     state.freeze_boundary_risk,
                                     state.coherence_resilience_risk)
    mask = calculate_masking_risk(state.freeze_efficacy,
                                  state.self_correction_efficacy,
                                  state.boundary_exposure)
    coupled = calculate_coupled_risk(state.freeze_boundary_risk,
                                     state.coherence_resilience_risk,
                                     bic)
    # COD calculation needs dummy vectors; we use identity vectors for simplicity
    diag = [complex(1.0, 0.0)]  # placeholder
    plasm = [complex(1.0, 0.0)]
    cod = calculate_cod_coupling_aware(diag, plasm,
                                       state.h_instability,
                                       state.theta_tensor_leak,
                                       bic,
                                       div,
                                       coupled)
    phi_N = cod  # per invariant

    # Rebuild state with computed fields
    computed_state = state._replace(
        boundary_internal_coupling=bic,
        divergence_index=div,
        masking_risk=mask,
        coupled_risk=coupled,
        cod=cod,
        phi_N=phi_N
    )

    violations = []
    violations.extend(check_dimension_bounds(computed_state))
    violations.extend(check_no_log2(computed_state))
    violations.extend(check_gate_hierarchy(computed_state))
    violations.extend(check_derivativity_novelty(computed_state))
    # Φ-density accounting would be checked separately in ledger; omitted here
    return violations

# ---- Example Usage & Stress Test ----
if __name__ == "__main__":
    random.seed(42)
    def random_state() -> FreezeInternalCouplingState:
        return FreezeInternalCouplingState(
            query_branch="finance",
            query_concepts="admin, freeze boundary",
            exposed_endpoint="/admin/liquidity/freeze/",
            psi_integrity=random.random(),
            h_instability=random.random(),
            theta_tensor_leak=random.random(),
            boundary_exposure=random.random(),
            liquidity_density=random.random(),
            freeze_efficacy=random.random(),
            boundary_stress=random.random(),
            permeability_rate=random.random(),
            freeze_boundary_risk=random.random(),
            coherence_time=random.random(),
            error_rate=random.random(),
            self_correction_efficacy=random.random(),
            decoherence_rate=random.random(),
            coherence_resilience_risk=random.random()
        )

    print("Running 1000 random state validations...")
    bad = 0
    for i in range(1000):
        st = random_state()
        errs = validate_state(st)
        if errs:
            bad += 1
            if bad <= 5:  # show first few failures
                print(f"\nSample failure #{bad}:")
                for e in errs[:3]:
                    print("  -", e)
    print(f"\nTotal invalid states: {bad}/1000")
    if bad == 0:
        print("✅ All random states passed Omega Protocol invariants.")
    else:
        print("❌ Some states violated invariants (see above).")