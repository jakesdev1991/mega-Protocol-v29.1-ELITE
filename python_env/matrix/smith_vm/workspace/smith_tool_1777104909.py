# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

# =============================================================================
# OMEGA PROTOCOL INVARIANTS (FROM v74.0-Ω)
# =============================================================================
class CognitiveImmunityInvariants:
    PSI_INTEGRITY_THRESHOLD = 0.95   # Identity Continuity
    IMMUNITY_INDEX_MIN = 0.50        # Min proactive resistance
    SUSCEPTIBILITY_MAX = 0.60        # Max vulnerability state
    EXPOSURE_FREQUENCY_MAX = 0.70    # Max exposure rate
    COD_THRESHOLD = 0.85             # Alignment Fidelity
    AUDIT_ENTROPY_PER_CHECK = 0.02   # Entropy cost per audit check

# =============================================================================
# COGNITIVE IMMUNITY GATE FUNCTIONS (EXTRACTED FROM C++ CODE)
# =============================================================================
def CalculateSusceptibility(immunity_index, exposure_frequency, diversity_index):
    """Susceptibility = (1-immunity)*0.5 + exposure*0.3 - diversity*0.2"""
    s = (1.0 - immunity_index) * 0.5 + exposure_frequency * 0.3 - diversity_index * 0.2
    return max(0.0, min(1.0, s))

def CalculateImmunityIndex(exposure_history_count, booster_effectiveness, 
                          time_since_last_exposure, intervention_efficacy):
    """Immunity = [min(1, exp_hist*0.4) + booster*0.3 + intervention*0.3] * exp(-0.1*time)"""
    exp_comp = min(1.0, exposure_history_count * 0.4)
    booster_comp = booster_effectiveness * 0.3
    intervention_comp = intervention_efficacy * 0.3
    decay_factor = math.exp(-0.1 * time_since_last_exposure)
    immunity = (exp_comp + booster_comp + intervention_comp) * decay_factor
    return max(0.0, min(1.0, immunity))

def CalculateExposureFrequency(narrative_synchronization, cascade_probability, 
                              time_since_last_exposure):
    """Exposure = [sync*0.5 + cascade*0.3] * (1 + time_factor) * 0.5"""
    sync_comp = narrative_synchronization * 0.5
    cascade_comp = cascade_probability * 0.3
    time_factor = 1.0 - min(1.0, time_since_last_exposure * 2.0)
    frequency = (sync_comp + cascade_comp) * (1.0 + time_factor) * 0.5
    return max(0.0, min(1.0, frequency))

def CalculateImmunityDecayRate(diversity_index, intervention_efficacy, booster_effectiveness):
    """Decay = (1-diversity)*0.4 + (1-intervention)*0.3 + (1-booster)*0.3"""
    decay = (1.0 - diversity_index) * 0.4 + (1.0 - intervention_efficacy) * 0.3 + (1.0 - booster_effectiveness) * 0.3
    return max(0.0, min(1.0, decay))

def CalculateProphylaxisEffectiveness(immunity_index, susceptibility, exposure_frequency):
    """Effectiveness = immunity*0.5 + (1-susceptibility)*0.3 + (1-exposure)*0.2"""
    eff = immunity_index * 0.5 + (1.0 - susceptibility) * 0.3 + (1.0 - exposure_frequency) * 0.2
    return max(0.0, min(1.0, eff))

def CalculateImmunityRisk(susceptibility, exposure_frequency, immunity_index):
    """Risk = susceptibility * exposure * (1 - immunity)"""
    risk = susceptibility * exposure_frequency * (1.0 - immunity_index)
    return max(0.0, min(1.0, risk))

def Calculate_COD_ImmunityAware(diagnostic_vec, plasma_vec, h_instability, theta_tensor_leak,
                               immunity_index, susceptibility, immunity_risk):
    """COD = fidelity * instability_penalty * exposure_penalty * immunity_penalty * susc_penalty * risk_penalty"""
    # Fidelity calculation (dot product normalization)
    size = min(len(diagnostic_vec), len(plasma_vec))
    if size == 0:
        return 0.0
    
    dot = 0.0
    magD = 0.0
    magP = 0.0
    for i in range(size):
        dot += abs(np.conj(diagnostic_vec[i]) * plasma_vec[i])
        magD += abs(diagnostic_vec[i] * diagnostic_vec[i])
        magP += abs(plasma_vec[i] * plasma_vec[i])
    
    fidelity = 0.0
    if magD > 1e-9 and magP > 1e-9:
        fidelity = dot / (math.sqrt(magD) * math.sqrt(magP))
        fidelity = max(0.0, min(1.0, fidelity))
    
    # Penalties
    LAMBDA_COUPLING = 0.5
    MU_IMMUNITY = 0.7
    
    instability_penalty = math.exp(-LAMBDA_COUPLING * h_instability)
    exposure_penalty = math.exp(-LAMBDA_COUPLING * theta_tensor_leak)
    immunity_penalty = math.exp(-MU_IMMUNITY * (1.0 - immunity_index))
    susceptibility_penalty = math.exp(-MU_IMMUNITY * susceptibility)
    risk_penalty = math.exp(-MU_IMMUNITY * immunity_risk)
    
    return fidelity * instability_penalty * exposure_penalty * immunity_penalty * susceptibility_penalty * risk_penalty

# =============================================================================
# GATE HIERARCHY AND DECISION LOGIC
# =============================================================================
class ImmunityState:
    IMMUNE = 0
    DEVELOPING = 1
    SUSCEPTIBLE = 2
    COMPROMISED = 3

class RiskLevel:
    LOW = 0
    MEDIUM = 1
    CRITICAL = 2
    CATASTROPHIC = 3

def ClassifyImmunityState(immunity_index, susceptibility, immunity_risk):
    if immunity_risk > 0.70:
        return ImmunityState.COMPROMISED
    if immunity_index > 0.70 and susceptibility < 0.30:
        return ImmunityState.IMMUNE
    if susceptibility > 0.60 or immunity_index < 0.30:
        return ImmunityState.SUSCEPTIBLE
    return ImmunityState.DEVELOPING

def AssessRisk(immunity_risk):
    if immunity_risk > 0.70:
        return RiskLevel.CATASTROPHIC
    if immunity_risk > 0.50:
        return RiskLevel.CRITICAL
    if immunity_risk > 0.30:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW

def DecideAction(psi_integrity, immunity_risk, immunity_state):
    """Returns action based on gate hierarchy"""
    # PRIMARY GATE: Ψ_integrity (non-negotiable)
    if psi_integrity < CognitiveImmunityInvariants.PSI_INTEGRITY_THRESHOLD:
        return "IDENTITY_LOCKDOWN"
    
    # IMMUNITY STATE GATE
    if immunity_state == ImmunityState.COMPROMISED:
        return "IDENTITY_LOCKDOWN"
    
    # RISK-BASED Decisions
    if immunity_risk > 0.70:
        return "IDENTITY_LOCKDOWN"
    if immunity_risk > 0.50 or immunity_state == ImmunityState.SUSCEPTIBLE:
        return "ACTIVATE_PROPHYLAXIS"
    if immunity_risk > 0.30 or immunity_state == ImmunityState.DEVELOPING:
        return "MONITOR_SUSCEPTIBILITY"
    return "PROCEED"

# =============================================================================
# INVARIANT ENFORCEMENT CHECK
# =============================================================================
def CheckInvariants(state, cod, immunity_risk, immunity_state):
    """Returns True if all invariants pass"""
    check = (
        state.psi_integrity >= CognitiveImmunityInvariants.PSI_INTEGRITY_THRESHOLD and
        state.immunity_index >= CognitiveImmunityInvariants.IMMUNITY_INDEX_MIN and
        state.susceptibility <= CognitiveImmunityInvariants.SUSCEPTIBILITY_MAX and
        state.exposure_frequency <= CognitiveImmunityInvariants.EXPOSURE_FREQUENCY_MAX and
        cod >= CognitiveImmunityInvariants.COD_THRESHOLD
    )
    return check

# =============================================================================
# VALIDATION SUITE
# =============================================================================
def validate_bounded_functions():
    """Test all gate functions for [0,1] bounds"""
    print("=== VALIDATING BOUNDED FUNCTIONS ===")
    
    # Test ranges
    test_cases = [
        (0.0, 0.0, 0.0),   # Min values
        (0.5, 0.5, 0.5),   # Mid values
        (1.0, 1.0, 1.0),   # Max values
        (0.2, 0.8, 0.3),   # Mixed
        (0.8, 0.2, 0.7)    # Mixed
    ]
    
    functions = [
        ("Susceptibility", CalculateSusceptibility),
        ("Immunity Index", CalculateImmunityIndex),
        ("Exposure Frequency", CalculateExposureFrequency),
        ("Immunity Decay Rate", CalculateImmunityDecayRate),
        ("Prophylaxis Effectiveness", CalculateProphylaxisEffectiveness),
        ("Immunity Risk", CalculateImmunityRisk)
    ]
    
    all_passed = True
    for name, func in functions:
        for case in test_cases:
            try:
                if name in ["Susceptibility", "Prophylaxis Effectiveness", "Immunity Risk"]:
                    result = func(*case)
                elif name == "Immunity Index":
                    # Add time_since_last_exposure (0.0-2.0) and intervention_efficacy (0.0-1.0)
                    result = func(case[0], case[1], 0.5, 0.5)  # Using fixed extra params
                elif name == "Exposure Frequency":
                    # Add time_since_last_exposure (0.0-2.0)
                    result = func(case[0], case[1], 0.5)
                elif name == "Immunity Decay Rate":
                    result = func(*case)
                
                if not (0.0 <= result <= 1.0):
                    print(f"FAIL: {name}{case} = {result} (out of bounds)")
                    all_passed = False
            except Exception as e:
                print(f"ERROR in {name}{case}: {e}")
                all_passed = False
    
    if all_passed:
        print("✓ All bounded functions pass [0,1] validation\n")
    return all_passed

def validate_cod_bounds():
    """Test COD calculation for [0,1] bounds"""
    print("=== VALIDATING COD CALCULATION ===")
    
    # Test vectors (simple case)
    diag = [1.0+0j, 0.5+0.5j]
    plasm = [1.0+0j, 0.5+0.5j]
    
    test_cases = [
        (0.0, 0.0, 0.5, 0.5, 0.5),   # Min instability/exposure, mid immunity/susc/risk
        (1.0, 1.0, 0.0, 0.0, 0.0),   # Max instability/exposure, min immunity/susc/risk
        (0.5, 0.5, 1.0, 1.0, 1.0),   # Mid instability/exposure, max immunity/susc/risk
        (0.2, 0.3, 0.7, 0.4, 0.6)    # Mixed values
    ]
    
    all_passed = True
    for case in test_cases:
        h_instab, theta_leak, imm_idx, susc, risk = case
        try:
            cod = Calculate_COD_ImmunityAware(diag, plasm, h_instab, theta_leak, imm_idx, susc, risk)
            if not (0.0 <= cod <= 1.0):
                print(f"FAIL: COD{case} = {cod} (out of bounds)")
                all_passed = False
        except Exception as e:
            print(f"ERROR in COD{case}: {e}")
            all_passed = False
    
    if all_passed:
        print("✓ COD calculation passes [0,1] validation\n")
    return all_passed

def validate_gate_hierarchy():
    """Validate the decision gate hierarchy"""
    print("=== VALIDATING GATE HIERARCHY ===")
    
    test_scenarios = [
        # (psi_integrity, immunity_risk, immunity_state, expected_action)
        (0.90, 0.2, ImmunityState.IMMUNE, "IDENTITY_LOCKDOWN"),  # Failed integrity gate
        (0.96, 0.8, ImmunityState.IMMUNE, "IDENTITY_LOCKDOWN"),  # High risk lockdown
        (0.96, 0.6, ImmunityState.SUSCEPTIBLE, "IDENTITY_LOCKDOWN"), # Susceptible state lockdown
        (0.96, 0.6, ImmunityState.DEVELOPING, "ACTIVATE_PROPHYLAXIS"), # High risk + developing
        (0.96, 0.4, ImmunityState.DEVELOPING, "MONITOR_SUSCEPTIBILITY"), # Medium risk + developing
        (0.96, 0.2, ImmunityState.IMMUNE, "PROCEED"),           # All clear
        (0.96, 0.55, ImmunityState.IMMUNE, "ACTIVATE_PROPHYLAXIS"), # Risk >0.5 triggers prophylaxis
        (0.96, 0.35, ImmunityState.IMMUNE, "MONITOR_SUSCEPTIBILITY") # Risk >0.3 triggers monitoring
    ]
    
    all_passed = True
    for psi, risk, state, expected in test_scenarios:
        action = DecideAction(psi, risk, state)
        if action != expected:
            print(f"FAIL: psi={psi}, risk={risk}, state={state} -> got '{action}', expected '{expected}'")
            all_passed = False
    
    if all_passed:
        print("✓ Gate hierarchy validation passes\n")
    return all_passed

def validate_invariant_check():
    """Validate invariant enforcement logic"""
    print("=== VALIDATING INVARIANT CHECK ===")
    
    # Create a mock state
    class MockState:
        def __init__(self, psi, imm_idx, susc, exp_freq):
            self.psi_integrity = psi
            self.immunity_index = imm_idx
            self.susceptibility = susc
            self.exposure_frequency = exp_freq
    
    test_cases = [
        # (psi, imm_idx, susc, exp_freq, cod, risk, expected)
        (0.94, 0.5, 0.5, 0.5, 0.86, 0.2, False),  # Failed psi_integrity
        (0.96, 0.4, 0.5, 0.5, 0.86, 0.2, False),  # Failed immunity_index
        (0.96, 0.5, 0.7, 0.5, 0.86, 0.2, False),  # Failed susceptibility
        (0.96, 0.5, 0.5, 0.8, 0.86, 0.2, False),  # Failed exposure_frequency
        (0.96, 0.5, 0.5, 0.5, 0.84, 0.2, False),  # Failed COD
        (0.96, 0.5, 0.5, 0.5, 0.86, 0.2, True)    # All pass
    ]
    
    all_passed = True
    for case in test_cases:
        psi, imm_idx, susc, exp_freq, cod, risk, expected = case
        state = MockState(psi, imm_idx, susc, exp_freq)
        result = CheckInvariants(state, cod, risk, ImmunityState.DEVELOPING)
        if result != expected:
            print(f"FAIL: state={case[:4]}, cod={cod}, risk={risk} -> got {result}, expected {expected}")
            all_passed = False
    
    if all_passed:
        print("✓ Invariant check validation passes\n")
    return all_passed

def validate_phi_density_accounting():
    """Validate Φ-density ledger (audit cost subtraction)"""
    print("=== VALIDATING Φ-DENSITY ACCOUNTING ===")
    
    # Simulate net gain calculation
    def CalculateNetGain(cod_before, cod_after, audit_checks):
        raw_gain = cod_after - cod_before
        audit_cost = audit_checks * CognitiveImmunityInvariants.AUDIT_ENTROPY_PER_CHECK
        return raw_gain - audit_cost
    
    test_cases = [
        (0.80, 0.85, 10, 0.05 - 0.20),   # Raw gain 0.05, audit cost 0.20 -> net -0.15
        (0.80, 0.90, 5,  0.10 - 0.10),   # Raw gain 0.10, audit cost 0.10 -> net 0.00
        (0.80, 0.95, 0,  0.15 - 0.00),   # Raw gain 0.15, audit cost 0.00 -> net 0.15
    ]
    
    all_passed = True
    for before, after, checks, expected in test_cases:
        result = CalculateNetGain(before, after, checks)
        if abs(result - expected) > 1e-9:
            print(f"FAIL: net_gain({before}->{after}, {checks} checks) = {result}, expected {expected}")
            all_passed = False
    
    if all_passed:
        print("✓ Φ-density accounting validation passes\n")
    return all_passed

# =============================================================================
# MAIN VALIDATION EXECUTION
# =============================================================================
if __name__ == "__main__":
    print("OMEGA PROTOCOL COGNITIVE IMMUNITY v74.0-Ω MATHEMATICAL VALIDATION\n")
    
    results = []
    results.append(validate_bounded_functions())
    results.append(validate_cod_bounds())
    results.append(validate_gate_hierarchy())
    results.append(validate_invariant_check())
    results.append(validate_phi_density_accounting())
    
    if all(results):
        print("🎉 ALL VALIDATIONS PASSED - COGNITIVE IMMUNITY MANIFOLD IS MATHEMATICALLY SOUND")
        print("   AND COMPLIANT WITH OMEGA PROTOCOL INVARIANTS.")
    else:
        print("❌ VALIDATION FAILED - SEE ERRORS ABOVE")
        exit(1)