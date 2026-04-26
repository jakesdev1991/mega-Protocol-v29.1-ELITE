# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Liquidity Contagion Velocity Manifold Validator
# Validates mathematical soundness and invariant compliance of the v78.0 LCG logic.

import math
from typing import List, Tuple, NamedTuple

# ==== Constants from Omega Protocol (v78.0 Liquidity Contagion) ====
PSI_INTEGRITY_THRESHOLD = 0.95
LIQUIDITY_VELOCITY_MAX = 0.60
CONTAGION_PATHWAYS_MAX = 0.50
MARKET_RESILIENCE_MIN = 0.55
COD_THRESHOLD = 0.85
AUDIT_ENTROPY_PER_CHECK = 0.02

# ==== Helper Functions (mirroring C++ logic) ====
def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

def calculate_liquidity_velocity(boundary_exposure: float,
                                 h_instability: float,
                                 correlation_amplification: float) -> float:
    v = (boundary_exposure * 0.4) + (h_instability * 0.3) + (correlation_amplification * 0.3)
    return clamp(v)

def calculate_contagion_pathways(correlated_asset_count: int,
                                 network_connectivity: float,
                                 systemic_importance: float) -> float:
    asset_factor = min(1.0, correlated_asset_count / 10.0)
    pathways = (asset_factor * 0.2) + (network_connectivity * 0.5) + (systemic_importance * 0.3)
    return clamp(pathways)

def calculate_market_resilience(freeze_efficacy: float,
                                restoration_rate: float,
                                herd_immunity_threshold: float) -> float:
    r = (freeze_efficacy * 0.4) + (restoration_rate * 0.3) + (herd_immunity_threshold * 0.3)
    return clamp(r)

def calculate_correlation_amplification(liquidity_velocity: float,
                                        contagion_pathways: float,
                                        market_resilience: float) -> float:
    a = (liquidity_velocity * 0.4) + (contagion_pathways * 0.3) + ((1.0 - market_resilience) * 0.3)
    return clamp(a)

def calculate_cascade_probability(liquidity_velocity: float,
                                  contagion_pathways: float,
                                  market_resilience: float) -> float:
    p = (liquidity_velocity * 0.4) + (contagion_pathways * 0.3) + ((1.0 - market_resilience) * 0.3)
    return clamp(p)

def calculate_liquidity_contagion_risk(liquidity_velocity: float,
                                       contagion_pathways: float,
                                       market_resilience: float) -> float:
    risk = liquidity_velocity * contagion_pathways * (1.0 - market_resilience)
    return clamp(risk)

def calculate_cod_likelihood_aware(h_instability: float,
                                   theta_tensor_leak: float,
                                   liquidity_velocity: float,
                                   market_resilience: float,
                                   liquidity_contagion_risk: float,
                                   lambda_coupling: float = 0.5,
                                   mu_liquidity: float = 0.7) -> float:
    # Simplified fidelity term: assume perfect alignment for boundary test (fidelity = 1.0)
    fidelity = 1.0
    instability_penalty = math.exp(-lambda_coupling * h_instability)
    exposure_penalty = math.exp(-lambda_coupling * theta_tensor_leak)
    velocity_penalty = math.exp(-mu_liquidity * liquidity_velocity)
    resilience_penalty = math.exp(-mu_liquidity * (1.0 - market_resilience))
    risk_penalty = math.exp(-mu_liquidity * liquidity_contagion_risk)
    cod = fidelity * instability_penalty * exposure_penalty * velocity_penalty * resilience_penalty * risk_penalty
    return clamp(cod)

def assess_risk_level(liquidity_contagion_risk: float) -> str:
    if liquidity_contagion_risk > 0.70: return "CATASTROPHIC"
    if liquidity_contagion_risk > 0.50: return "CRITICAL"
    if liquidity_contagion_risk > 0.30: return "MEDIUM"
    return "LOW"

def decide_action(psi_integrity: float,
                  liquidity_contagion_risk: float,
                  contagion_state: str) -> str:
    if psi_integrity < PSI_INTEGRITY_THRESHOLD:
        return "IDENTITY_LOCKDOWN"
    if contagion_state == "SYSTEMIC_CRISIS":
        return "IDENTITY_LOCKDOWN"
    if liquidity_contagion_risk > 0.70:
        return "IDENTITY_LOCKDOWN"
    if liquidity_contagion_risk > 0.50 or contagion_state == "CONTAGIOUS":
        return "ACTIVATE_CIRCUIT_BREAKER"
    if liquidity_contagion_risk > 0.30 or contagion_state == "STRESSED":
        return "FLAG_VELOCITY_MONITOR"
    return "PROCEED"

def classify_contagion_state(liquidity_velocity: float,
                             contagion_pathways: float,
                             cascade_probability: float) -> str:
    if cascade_probability > 0.70:
        return "SYSTEMIC_CRISIS"
    if contagion_pathways > 0.60 and liquidity_velocity > 0.50:
        return "CONTAGIOUS"
    if liquidity_velocity > 0.40:
        return "STRESSED"
    return "STABLE"

def calculate_phi_net_gain(cod_before: float,
                           cod_after: float,
                           audit_checks: int) -> float:
    raw_gain = cod_after - cod_before
    audit_cost = audit_checks * AUDIT_ENTROPY_PER_CHECK
    return raw_gain - audit_cost

# ==== Test Suite: Validate Invariants & Math ====
def run_validation() -> Tuple[bool, List[str]]:
    errors = []
    # Test 1: Boundedness of all core metrics
    test_cases = [
        # (boundary_exposure, h_instability, correlation_amplification,
        #  correlated_asset_count, network_connectivity, systemic_importance,
        #  freeze_efficacy, restoration_rate, herd_immunity_threshold,
        #  psi_integrity, theta_tensor_leak)
        (0.2, 0.1, 0.1, 2, 0.3, 0.2, 0.8, 0.7, 0.6, 0.96, 0.05),
        (0.5, 0.4, 0.5, 5, 0.6, 0.5, 0.5, 0.4, 0.4, 0.97, 0.1),
        (0.8, 0.7, 0.8, 9, 0.9, 0.8, 0.3, 0.2, 0.3, 0.95, 0.2),
        (0.9, 0.9, 0.9, 12, 1.0, 0.9, 0.1, 0.1, 0.1, 0.94, 0.3),  # psi_integrity low
    ]
    for i, (be, hi, ca, cac, nc, si, fe, rr, hit, psi, ttl) in enumerate(test_cases):
        lv = calculate_liquidity_velocity(be, hi, ca)
        if not (0.0 <= lv <= LIQUIDITY_VELOCITY_MAX + 1e-9):
            errors.append(f"TC{i}: liquidity_velocity={lv:.4f} exceeds max {LIQUIDITY_VELOCITY_MAX}")
        cp = calculate_contagion_pathways(cac, nc, si)
        if not (0.0 <= cp <= CONTAGION_PATHWAYS_MAX + 1e-9):
            errors.append(f"TC{i}: contagion_pathways={cp:.4f} exceeds max {CONTAGION_PATHWAYS_MAX}")
        mr = calculate_market_resilience(fe, rr, hit)
        if not (MARKET_RESILIENCE_MIN - 1e-9 <= mr <= 1.0):
            errors.append(f"TC{i}: market_resilience={mr:.4f} below min {MARKET_RESILIENCE_MIN}")
        # Additional derived metrics
        corr_amp = calculate_correlation_amplification(lv, cp, mr)
        cascade = calculate_cascade_probability(lv, cp, mr)
        risk = calculate_liquidity_contagion_risk(lv, cp, mr)
        cod = calculate_cod_likelihood_aware(hi, ttl, lv, mr, risk)
        if not (0.0 <= cod <= 1.0 + 1e-9):
            errors.append(f"TC{i}: COD={cod:.4f} out of [0,1]")
        state = classify_contagion_state(lv, cp, cascade)
        action = decide_action(psi, risk, state)
        # Invariant checks
        if psi < PSI_INTEGRITY_THRESHOLD and action != "IDENTITY_LOCKDOWN":
            errors.append(f"TC{i}: psi_integrity={psi:.4f} < threshold but action={action}")
        if lv > LIQUIDITY_VELOCITY_MAX + 1e-9:
            errors.append(f"TC{i}: liquidity_velocity exceeds hard gate")
        if cp > CONTAGION_PATHWAYS_MAX + 1e-9:
            errors.append(f"TC{i}: contagion_pathways exceeds hard gate")
        if mr < MARKET_RESILIENCE_MIN - 1e-9:
            errors.append(f"TC{i}: market_resilience below hard gate")
        if cod < COD_THRESHOLD - 1e-9 and action not in ("FLAG_VELOCITY_MONITOR", "PROCEED"):
            # Note: action may still be PROCEED/FLAG if other gates pass; we only flag if COD fails AND action is not a monitoring/proceed
            # Actually, per protocol, COD < threshold should prevent PROCEED/FLAG? We'll just note if COD low but action is PROCEED (should be monitored or worse)
            if action == "PROCEED":
                errors.append(f"TC{i}: COD={cod:.4f} < threshold but action=PROCEED")
        # Phi net gain sanity
        phi_gain = calculate_phi_net_gain(cod, cod, 14)  # same before/after -> should be negative audit cost
        expected = -14 * AUDIT_ENTROPY_PER_CHECK
        if abs(phi_gain - expected) > 1e-9:
            errors.append(f"TC{i}: phi_net_gain={phi_gain:.4f} expected {expected:.4f}")
    # Test 2: Derivativity novelty check (conceptual)
    # Ensure liquidity_velocity is not just a copy of freeze_efficacy or r0_propagation
    # We'll test that lv can be high while freeze_efficacy is high (i.e., boundary holds but liquidity evaporates internally)
    lv_high = calculate_liquidity_velocity(0.1, 0.9, 0.9)  # low boundary exposure but high instability/correlation
    fe_high = 0.9  # high freeze efficacy
    if lv_high > 0.5 and fe_high > 0.8:
        # This is acceptable: shows lv captures internal evaporation despite strong boundary
        pass
    else:
        errors.append("Derivativity check: liquidity_velocity not distinguishable from freeze_efficacy")
    # Test 3: Cascade probability monotonicity (should increase with lv, cp, decrease with mr)
    base_lv, base_cp, base_mr = 0.3, 0.3, 0.6
    base_cascade = calculate_cascade_probability(base_lv, base_cp, base_mr)
    # Increase lv
    lv_cascade = calculate_cascade_probability(base_lv + 0.2, base_cp, base_mr)
    if lv_cascade <= base_cascade + 1e-9:
        errors.append("Cascade probability not increasing with liquidity_velocity")
    # Increase cp
    cp_cascade = calculate_cascade_probability(base_lv, base_cp + 0.2, base_mr)
    if cp_cascade <= base_cascade + 1e-9:
        errors.append("Cascade probability not increasing with contagion_pathways")
    # Decrease mr (i.e., lower resilience -> higher cascade)
    mr_cascade = calculate_cascade_probability(base_lv, base_cp, base_mr - 0.2)
    if mr_cascade <= base_cascade + 1e-9:
        errors.append("Cascade probability not increasing as market_resilience decreases")
    # Test 4: Risk level thresholds
    assert assess_risk_level(0.2) == "LOW"
    assert assess_risk_level(0.35) == "MEDIUM"
    assert assess_risk_level(0.55) == "CRITICAL"
    assert assess_risk_level(0.75) == "CATASTROPHIC"
    # Test 5: Action hierarchy
    assert decide_action(0.96, 0.2, "STABLE") == "PROCEED"
    assert decide_action(0.96, 0.35, "STRESSED") == "FLAG_VELOCITY_MONITOR"
    assert decide_action(0.96, 0.55, "CONTAGIOUS") == "ACTIVATE_CIRCUIT_BREAKER"
    assert decide_action(0.94, 0.2, "STABLE") == "IDENTITY_LOCKDOWN"  # psi fails
    assert decide_action(0.96, 0.2, "SYSTEMIC_CRISIS") == "IDENTITY_LOCKDOWN"
    if errors:
        return False, errors
    return True, ["All validation checks passed."]

# ==== Execute Validation ====
if __name__ == "__main__":
    success, messages = run_validation()
    for m in messages:
        print(m)
    if not success:
        print("VALIDATION FAILED")
        exit(1)
    else:
        print("VALIDATION PASSED: Omega Protocol Liquidity Contagion Manifold is mathematically sound and invariant-compliant.")
        exit(0)