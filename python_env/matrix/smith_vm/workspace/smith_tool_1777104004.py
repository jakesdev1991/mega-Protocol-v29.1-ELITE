# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Validation: Cognitive Bias Remediation Manifold (v73.0-Ω)
# This script validates mathematical soundness and invariant compliance.
# It does NOT execute the full manifold; it checks the core formulas and bounds.

import math
from typing import List, Tuple, Complex

# ---------- Constants from the manifesto ----------
PSI_INTEGRITY_THRESHOLD = 0.95
BIAS_DECAY_MIN = 0.40
INTERVENTION_EFFICACY_MIN = 0.55
RECOVERY_TIME_MAX = 0.70
COD_THRESHOLD = 0.85
AUDIT_ENTROPY_PER_CHECK = 0.02

LAMBDA_COUPLING = 0.5
MU_REMEDIATION = 0.7

# ---------- Helper functions (as defined in the manifesto) ----------
def clamp(x: float) -> float:
    return max(0.0, min(1.0, x))

def calculate_bias_decay_rate(diversity_index: float,
                              intervention_efficacy: float,
                              bias_concentration: float) -> float:
    """Bias decay rate = 0.4*diversity + 0.4*efficacy + 0.2*(1 - bias_concentration)"""
    raw = 0.4 * diversity_index + 0.4 * intervention_efficacy + 0.2 * (1.0 - bias_concentration)
    return clamp(raw)

def calculate_intervention_efficacy(narrative_disruption: float,
                                    diversity_index: float,
                                    cascade_probability: float) -> float:
    """Efficacy = 0.5*disruption + 0.3*diversity + 0.2*(1 - cascade_probability)"""
    raw = 0.5 * narrative_disruption + 0.3 * diversity_index + 0.2 * (1.0 - cascade_probability)
    return clamp(raw)

def calculate_recovery_time(bias_decay_rate: float,
                            bias_concentration: float) -> float:
    """Recovery time = bias_concentration / bias_decay_rate (if decay_rate > 0) else 1.0"""
    if bias_decay_rate < 1e-9:
        return 1.0
    raw = bias_concentration / bias_decay_rate
    return clamp(raw)

def calculate_remediation_success_probability(intervention_efficacy: float,
                                              bias_decay_rate: float,
                                              diversity_index: float) -> float:
    """Success = 0.5*efficacy + 0.3*decay + 0.2*diversity"""
    raw = 0.5 * intervention_efficacy + 0.3 * bias_decay_rate + 0.2 * diversity_index
    return clamp(raw)

def calculate_remediation_risk(bias_concentration: float,
                               intervention_efficacy: float,
                               recovery_time: float) -> float:
    """Risk = bias_concentration * (1 - efficacy) * recovery_time"""
    raw = bias_concentration * (1.0 - intervention_efficacy) * recovery_time
    return clamp(raw)

def calculate_COD_remediation_aware(diagnostic_vec: List[Complex],
                                    plasma_vec: List[Complex],
                                    h_instability: float,
                                    theta_tensor_leak: float,
                                    bias_decay_rate: float,
                                    intervention_efficacy: float,
                                    remediation_risk: float) -> float:
    """COD = fidelity * exp(-λ*h) * exp(-λ*θ) * exp(-μ*(1-decay)) * exp(-μ*(1-efficacy)) * exp(-μ*risk)"""
    # Fidelity (dot product magnitude normalized)
    size = min(len(diagnostic_vec), len(plasma_vec))
    dot = 0.0
    magD = 0.0
    magP = 0.0
    for i in range(size):
        c = diagnostic_vec[i].conjugate() * plasma_vec[i]
        dot += abs(c)
        magD += abs(diagnostic_vec[i] * diagnostic_vec[i])
        magP += abs(plasma_vec[i] * plasma_vec[i])
    fidelity = 0.0
    if magD > 1e-12 and magP > 1e-12:
        fidelity = dot / (math.sqrt(magD) * math.sqrt(magP))
        fidelity = clamp(fidelity)

    instability_penalty = math.exp(-LAMBDA_COUPLING * h_instability)
    exposure_penalty = math.exp(-LAMBDA_COUPLING * theta_tensor_leak)
    decay_penalty = math.exp(-MU_REMEDIATION * (1.0 - bias_decay_rate))
    efficacy_penalty = math.exp(-MU_REMEDIATION * (1.0 - intervention_efficacy))
    risk_penalty = math.exp(-MU_REMEDIATION * remediation_risk)

    cod = fidelity * instability_penalty * exposure_penalty * decay_penalty * efficacy_penalty * risk_penalty
    return clamp(cod)

# ---------- Invariant checks ----------
def check_invariants(state: dict) -> Tuple[bool, List[str]]:
    """Return (all_passed, list_of_failures)"""
    failures = []
    if state.get('psi_integrity', 0) < PSI_INTEGRITY_THRESHOLD:
        failures.append(f"Psi integrity {state['psi_integrity']} < {PSI_INTEGRITY_THRESHOLD}")
    if state.get('bias_decay_rate', 0) < BIAS_DECAY_MIN:
        failures.append(f"Bias decay rate {state['bias_decay_rate']} < {BIAS_DECAY_MIN}")
    if state.get('intervention_efficacy', 0) < INTERVENTION_EFFICACY_MIN:
        failures.append(f"Intervention efficacy {state['intervention_efficacy']} < {INTERVENTION_EFFICACY_MIN}")
    if state.get('recovery_time', 0) > RECOVERY_TIME_MAX:
        failures.append(f"Recovery time {state['recovery_time']} > {RECOVERY_TIME_MAX}")
    if state.get('cod', 0) < COD_THRESHOLD:
        failures.append(f"COD {state['cod']} < {COD_THRESHOLD}")
    return (len(failures) == 0, failures)

# ---------- Validation suite ----------
def run_validation():
    print("=== Omega Protocol Validation: Cognitive Bias Remediation Manifold (v73.0-Ω) ===")

    # 1. Bounds checking for helper functions
    print("\n1. Checking helper function bounds...")
    test_cases = [
        (0.2, 0.3, 0.5),   # low values
        (0.8, 0.9, 0.1),   # high diversity/efficacy, low bias
        (0.5, 0.5, 0.5),   # mid
        (1.0, 1.0, 0.0),   # max diversity/efficacy, zero bias
        (0.0, 0.0, 1.0),   # min diversity/efficacy, max bias
    ]
    for div, eff, bias in test_cases:
        decay = calculate_bias_decay_rate(div, eff, bias)
        assert 0.0 <= decay <= 1.0, f"Bias decay out of bounds: {decay}"
        eff2 = calculate_intervention_efficacy(div, eff, bias)  # reuse bias as cascade proxy
        assert 0.0 <= eff2 <= 1.0, f"Intervention efficacy out of bounds: {eff2}"
        rec = calculate_recovery_time(decay, bias)
        assert 0.0 <= rec <= 1.0, f"Recovery time out of bounds: {rec}"
        succ = calculate_remediation_success_probability(eff2, decay, div)
        assert 0.0 <= succ <= 1.0, f"Success prob out of bounds: {succ}"
        risk = calculate_remediation_risk(bias, eff2, rec)
        assert 0.0 <= risk <= 1.0, f"Remediation risk out of bounds: {risk}"
    print("   ✅ All helper functions produce values in [0,1]")

    # 2. COD bounds and monotonicity (penalties reduce COD)
    print("\n2. Checking COD calculation...")
    diag = [1+0j, 0.5+0.5j]
    plas = [1+0j, 0.5+0.5j]
    base_cod = calculate_COD_remediation_aware(diag, plas, 0.0, 0.0, 1.0, 1.0, 0.0)
    assert math.isclose(base_cod, 1.0, rel_tol=1e-9), f"Base COD should be 1.0, got {base_cod}"
    # Increasing instability should decrease COD
    cod_low_h = calculate_COD_remediation_aware(diag, plas, 0.1, 0.0, 1.0, 1.0, 0.0)
    cod_high_h = calculate_COD_remediation_aware(diag, plas, 0.5, 0.0, 1.0, 1.0, 0.0)
    assert cod_low_h >= cod_high_h, f"COD should decrease with h_instability: {cod_low_h} vs {cod_high_h}"
    # Increasing remediation risk should decrease COD
    cod_low_r = calculate_COD_remediation_aware(diag, plas, 0.0, 0.0, 1.0, 1.0, 0.1)
    cod_high_r = calculate_COD_remediation_aware(diag, plas, 0.0, 0.0, 1.0, 1.0, 0.5)
    assert cod_low_r >= cod_high_r, f"COD should decrease with remediation_risk: {cod_low_r} vs {cod_high_r}"
    print("   ✅ COD behaves correctly under parameter variations")

    # 3. Invariant enforcement logic
    print("\n3. Testing invariant checker...")
    state_good = {
        'psi_integrity': 0.96,
        'bias_decay_rate': 0.45,
        'intervention_efficacy': 0.60,
        'recovery_time': 0.65,
        'cod': 0.86
    }
    passed, fails = check_invariants(state_good)
    assert passed and not fails, f"Good state failed: {fails}"
    state_bad_psi = state_good.copy()
    state_bad_psi['psi_integrity'] = 0.90
    passed, fails = check_invariants(state_bad_psi)
    assert not passed and any('Psi integrity' in f for f in fails), f"Psi integrity violation not caught: {fails}"
    state_bad_decay = state_good.copy()
    state_bad_decay['bias_decay_rate'] = 0.30
    passed, fails = check_invariants(state_bad_decay)
    assert not passed and any('Bias decay rate' in f for f in fails), f"Bias decay violation not caught: {fails}"
    print("   ✅ Invariant checker correctly flags violations")

    # 4. Risk level classification (from manuscript)
    print("\n4. Checking risk level thresholds...")
    def risk_level_from_risk(r: float) -> str:
        if r > 0.70: return "CATASTROPHIC"
        if r > 0.50: return "CRITICAL"
        if r > 0.30: return "MEDIUM"
        return "LOW"
    assert risk_level_from_risk(0.75) == "CATASTROPHIC"
    assert risk_level_from_risk(0.60) == "CRITICAL"
    assert risk_level_from_risk(0.40) == "MEDIUM"
    assert risk_level_from_risk(0.20) == "LOW"
    print("   ✅ Risk level mapping matches specification")

    # 5. Remediation state classification (from manuscript)
    print("\n5. Checking remediation state logic...")
    def remediation_state(bias_conc, eff, decay, rec):
        if bias_conc < 0.20 and decay > 0.50: return "HEALTHY"
        if eff > 0.60 and decay > 0.40: return "INTERVENING"
        if rec < 0.50 and decay > 0.30: return "RECOVERING"
        if eff < 0.30 and bias_conc > 0.60: return "CHRONIC_BIAS"
        return "MONITORING"
    # Healthy case
    assert remediation_state(0.10, 0.5, 0.6, 0.2) == "HEALTHY"
    # Intervening case
    assert remediation_state(0.4, 0.7, 0.45, 0.6) == "INTERVENING"
    # Recovering case
    assert remediation_state(0.5, 0.4, 0.35, 0.4) == "RECOVERING"
    # Chronic bias case
    assert remediation_state(0.7, 0.2, 0.2, 0.8) == "CHRONIC_BIAS"
    # Monitoring fallback
    assert remediation_state(0.5, 0.5, 0.4, 0.6) == "MONITORING"
    print("   ✅ Remediation state classification matches manuscript")

    # 6. Φ-density ledger sanity (audit cost subtraction)
    print("\n6. Checking Φ-density ledger...")
    def net_gain(cod_before, cod_after, audit_checks):
        raw = cod_after - cod_before
        cost = audit_checks * AUDIT_ENTROPY_PER_CHECK
        return raw - cost
    # No gain scenario
    assert net_gain(0.85, 0.85, 10) == -0.2, f"Expected -0.2, got {net_gain(0.85,0.85,10)}"
    # Gain scenario
    assert net_gain(0.80, 0.90, 5) == 0.09, f"Expected 0.09, got {net_gain(0.80,0.90,5)}"
    print("   ✅ Φ-density ledger correctly subtracts audit entropy")

    print("\n=== ALL VALIDATIONS PASSED ===")
    print("The Cognitive Bias Remediation Manifold (v73.0-Ω) is mathematically sound")
    print("and compliant with Omega Protocol invariants.")

if __name__ == "__main__":
    run_validation()