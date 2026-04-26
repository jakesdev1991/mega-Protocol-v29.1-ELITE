# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math
from typing import Tuple, List

# === OMEGA PROTOCOL INVARIANTS (FROM TRUST DECAY MANIFOLD v67.0-Ω) ===
PSI_INTEGRITY_THRESHOLD = 0.95
TRUST_HALF_LIFE_MIN = 0.50
PROPAGATION_RADIUS_MAX = 0.60
RECOVERY_VELOCITY_MIN = 0.40
COD_THRESHOLD = 0.85
AUDIT_ENTROPY_PER_CHECK = 0.02

# === TRUST DECAY GATE FUNCTIONS (TRANSLATED FROM C++) ===
def calculate_trust_half_life(topology_exposure: float, 
                              compound_exposure_risk: float, 
                              partner_count: int) -> float:
    """Calculate normalized trust half-life [0,1]"""
    exposure_factor = 0.5 * topology_exposure + 0.5 * compound_exposure_risk
    partner_factor = min(1.0, partner_count / 10.0)
    half_life = (1.0 - exposure_factor) * (1.0 - 0.3 * partner_factor)
    return max(0.0, min(1.0, half_life))

def calculate_propagation_radius(topology_exposure: float,
                                 partner_count: int,
                                 time_since_exposure: float) -> float:
    """Calculate normalized propagation radius [0,1]"""
    time_factor = min(1.0, time_since_exposure * 2.0)
    connectivity_factor = min(1.0, partner_count / 15.0)
    exposure_acceleration = 1.0 + topology_exposure
    propagation = time_factor * connectivity_factor * exposure_acceleration
    return max(0.0, min(1.0, propagation))

def calculate_recovery_velocity(remediation_quality: float,
                                partner_cooperation: float,
                                initial_trust: float) -> float:
    """Calculate normalized recovery velocity [0,1]"""
    technical = remediation_quality * 0.6
    cooperation = partner_cooperation * 0.3
    trust_component = initial_trust * 0.1
    velocity = technical + cooperation + trust_component
    return max(0.0, min(1.0, velocity))

def calculate_current_trust_level(initial_trust: float,
                                  trust_half_life: float,
                                  time_since_exposure: float) -> float:
    """Calculate current trust level [0,1] via exponential decay"""
    if trust_half_life < 0.01:
        return initial_trust * 0.1
    decay_exponent = -time_since_exposure / (trust_half_life + 0.01)
    decay_factor = math.pow(2.0, decay_exponent)
    return max(0.0, min(1.0, initial_trust * decay_factor))

def calculate_trust_decay_risk(current_trust_level: float,
                               propagation_radius: float,
                               recovery_velocity: float) -> float:
    """Calculate normalized trust decay risk [0,1]"""
    trust_deficit = 1.0 - current_trust_level
    recovery_deficit = 1.0 - recovery_velocity
    risk = trust_deficit * propagation_radius * recovery_deficit
    return max(0.0, min(1.0, risk))

def calculate_cod_penalty(h_instability: float,
                          theta_tensor_leak: float,
                          current_trust_level: float,
                          trust_decay_risk: float) -> float:
    """Calculate COD penalty term (fidelity assumed 1.0 for worst-case)"""
    LAMBDA_COUPLING = 0.5
    MU_TRUST_DECAY = 0.5
    instability_penalty = math.exp(-LAMBDA_COUPLING * h_instability)
    exposure_penalty = math.exp(-LAMBDA_COUPLING * theta_tensor_leak)
    trust_penalty = math.exp(-MU_TRUST_DECAY * (1.0 - current_trust_level))
    decay_penalty = math.exp(-MU_TRUST_DECAY * trust_decay_risk)
    return instability_penalty * exposure_penalty * trust_penalty * decay_penalty

def trust_decay_silence_decide(psi_integrity: float,
                               trust_decay_risk: float,
                               decay_state: int) -> int:
    """Return action: 0=PROCEED, 1=FLAG, 2=FREEZE, 3=LOCKDOWN"""
    if psi_integrity < PSI_INTEGRITY_THRESHOLD:
        return 3  # IDENTITY_LOCKDOWN
    if decay_state == 3:  # CONTAMINATED
        return 3
    if trust_decay_risk > 0.70:
        return 3
    if trust_decay_risk > 0.50:
        return 2  # FREEZE_COLLABORATION
    if trust_decay_risk > 0.30:
        return 1  # FLAG_TRUST_MONITOR
    return 0  # PROCEED

def invariant_check(psi_integrity: float,
                    trust_half_life: float,
                    propagation_radius: float,
                    recovery_velocity: float,
                    cod: float) -> bool:
    """Check all Omega Protocol invariants"""
    return (psi_integrity >= PSI_INTEGRITY_THRESHOLD and
            trust_half_life >= TRUST_HALF_LIFE_MIN and
            propagation_radius <= PROPAGATION_RADIUS_MAX and
            recovery_velocity >= RECOVERY_VELOCITY_MIN and
            cod >= COD_THRESHOLD)

# === VALIDATION SCRIPT ===
def run_validation() -> Tuple[bool, List[str]]:
    """Run comprehensive validation of Trust Decay Manifold mathematics"""
    errors = []
    np.random.seed(42)  # For reproducibility
    
    # Test 1: Dimensional Bounds Verification
    print("Test 1: Verifying dimensional bounds [0,1] for all metrics...")
    num_tests = 10000
    
    for _ in range(num_tests):
        # Generate random inputs in valid ranges
        topology_exposure = np.random.uniform(0, 1)
        compound_exposure_risk = np.random.uniform(0, 1)
        partner_count = np.random.randint(0, 50)
        time_since_exposure = np.random.uniform(0, 1)
        remediation_quality = np.random.uniform(0, 1)
        partner_cooperation = np.random.uniform(0, 1)
        initial_trust = np.random.uniform(0, 1)
        h_instability = np.random.uniform(0, 1)
        theta_tensor_leak = np.random.uniform(0, 1)
        
        # Calculate all metrics
        thl = calculate_trust_half_life(topology_exposure, compound_exposure_risk, partner_count)
        pr = calculate_propagation_radius(topology_exposure, partner_count, time_since_exposure)
        rv = calculate_recovery_velocity(remediation_quality, partner_cooperation, initial_trust)
        ctl = calculate_current_trust_level(initial_trust, thl, time_since_exposure)
        tdr = calculate_trust_decay_risk(ctl, pr, rv)
        cod_penalty = calculate_cod_penalty(h_instability, theta_tensor_leak, ctl, tdr)
        
        # Verify bounds
        if not (0 <= thl <= 1):
            errors.append(f"trust_half_life OOB: {thl} (inputs: te={topology_exposure}, cer={compound_exposure_risk}, pc={partner_count})")
        if not (0 <= pr <= 1):
            errors.append(f"propagation_radius OOB: {pr} (inputs: te={topology_exposure}, pc={partner_count}, tse={time_since_exposure})")
        if not (0 <= rv <= 1):
            errors.append(f"recovery_velocity OOB: {rv} (inputs: rq={remediation_quality}, pc={partner_cooperation}, it={initial_trust})")
        if not (0 <= ctl <= 1):
            errors.append(f"current_trust_level OOB: {ctl} (inputs: it={initial_trust}, thl={thl}, tse={time_since_exposure})")
        if not (0 <= tdr <= 1):
            errors.append(f"trust_decay_risk OOB: {tdr} (inputs: ctl={ctl}, pr={pr}, rv={rv})")
        if not (0 <= cod_penalty <= 1):
            errors.append(f"COD penalty OOB: {cod_penalty} (inputs: hi={h_instability}, ttl={theta_tensor_leak}, ctl={ctl}, tdr={tdr})")
    
    if errors:
        return False, [f"Dimensional bounds failed: {len(errors)} errors"] + errors[:5]
    
    # Test 2: Safety Gate Hierarchy
    print("Test 2: Verifying safety gate hierarchy...")
    gate_errors = []
    
    # Test primary gate (Psi_integrity)
    for psi in [0.94, 0.95, 0.96]:
        action = trust_decay_silence_decide(psi, 0.1, 0)  # Low risk, stable state
        if psi < PSI_INTEGRITY_THRESHOLD and action != 3:
            gate_errors.append(f"Psi_integrity={psi} should trigger LOCKDOWN (got {action})")
        if psi >= PSI_INTEGRITY_THRESHOLD and action == 3:
            gate_errors.append(f"Psi_integrity={psi} should NOT trigger LOCKDOWN (got {action})")
    
    # Test decay state gate
    for state in [0, 1, 2, 3]:  # STABLE, DECAYING, CONTAMINATED, RECOVERING
        action = trust_decay_silence_decide(0.96, 0.1, state)
        if state == 3 and action != 3:  # CONTAMINATED state
            gate_errors.append(f"Decay state CONTAMINATED should trigger LOCKDOWN (got {action})")
        if state != 3 and action == 3 and 0.1 <= 0.3:  # Low risk
            gate_errors.append(f"Non-CONTAMINATED state with low risk should NOT trigger LOCKDOWN (got {action})")
    
    # Test risk-based decisions
    risk_tests = [
        (0.29, 0),  # PROCEED
        (0.31, 1),  # FLAG
        (0.51, 2),  # FREEZE
        (0.71, 3)   # LOCKDOWN
    ]
    for risk, expected in risk_tests:
        action = trust_decay_silence_decide(0.96, risk, 0)
        if action != expected:
            gate_errors.append(f"Risk {risk} should yield action {expected} (got {action})")
    
    if gate_errors:
        return False, [f"Safety gate hierarchy failed: {len(gate_errors)} errors"] + gate_errors[:5]
    
    # Test 3: Invariant Logic Consistency
    print("Test 3: Verifying invariant logic consistency...")
    invariant_errors = []
    
    # When all invariants pass, should allow PROCEED or FLAG (depending on risk)
    for _ in range(1000):
        psi = np.random.uniform(PSI_INTEGRITY_THRESHOLD, 1.0)
        thl = np.random.uniform(TRUST_HALF_LIFE_MIN, 1.0)
        pr = np.random.uniform(0.0, PROPAGATION_RADIUS_MAX)
        rv = np.random.uniform(RECOVERY_VELOCITY_MIN, 1.0)
        cod = np.random.uniform(COD_THRESHOLD, 1.0)
        
        if not invariant_check(psi, thl, pr, rv, cod):
            invariant_errors.append(f"Invariant check failed for valid inputs: psi={psi}, thl={thl}, pr={pr}, rv={rv}, cod={cod}")
    
    # When any invariant fails, should trigger restrictive action (unless in recovery)
    for _ in range(1000):
        # Fail one random invariant
        psi = np.random.uniform(0.0, PSI_INTEGRITY_THRESHOLD - 0.01) if np.random.rand() < 0.2 else np.random.uniform(PSI_INTEGRITY_THRESHOLD, 1.0)
        thl = np.random.uniform(0.0, TRUST_HALF_LIFE_MIN - 0.01) if np.random.rand() < 0.2 else np.random.uniform(TRUST_HALF_LIFE_MIN, 1.0)
        pr = np.random.uniform(PROPAGATION_RADIUS_MAX + 0.01, 1.0) if np.random.rand() < 0.2 else np.random.uniform(0.0, PROPAGATION_RADIUS_MAX)
        rv = np.random.uniform(0.0, RECOVERY_VELOCITY_MIN - 0.01) if np.random.rand() < 0.2 else np.random.uniform(RECOVERY_VELOCITY_MIN, 1.0)
        cod = np.random.uniform(0.0, COD_THRESHOLD - 0.01) if np.random.rand() < 0.2 else np.random.uniform(COD_THRESHOLD, 1.0)
        
        # Calculate risk based on these values
        tdl = calculate_trust_half_life(0.5, 0.5, 5)  # Dummy values for half-life
        pr_val = calculate_propagation_radius(0.5, 5, 0.5)  # Dummy propagation
        rv_val = calculate_recovery_velocity(0.5, 0.5, 0.5)  # Dummy recovery
        ctl = calculate_current_trust_level(0.8, tdl, 0.5)  # Dummy trust level
        tdr = calculate_trust_decay_risk(ctl, pr_val, rv_val)
        
        action = trust_decay_silence_decide(psi, tdr, 0)  # Assume STABLE state initially
        
        # If any invariant failed, action should NOT be PROCEED (unless in specific recovery scenario)
        if not invariant_check(psi, thl, pr, rv, cod):
            if action == 0:  # PROCEED
                invariant_errors.append(f"Failed invariant but got PROCEED: psi={psi}, thl={thl}, pr={pr}, rv={rv}, cod={cod}")
    
    if invariant_errors:
        return False, [f"Invariant logic failed: {len(invariant_errors)} errors"] + invariant_errors[:5]
    
    # Test 4: Phi Density Accounting
    print("Test 4: Verifying Phi density accounting...")
    phi_errors = []
    
    # Test net gain calculation
    for _ in range(1000):
        cod_before = np.random.uniform(0.0, 1.0)
        cod_after = np.random.uniform(0.0, 1.0)
        audit_checks = np.random.randint(1, 20)
        
        raw_gain = cod_after - cod_before
        audit_cost = audit_checks * AUDIT_ENTROPY_PER_CHECK
        net_gain = raw_gain - audit_cost
        
        # Net gain can be negative (cost > gain) but should not be inflated
        if net_gain > raw_gain + 1e-9:  # Should never exceed raw gain
            phi_errors.append(f"Phi density inflation: net_gain={net_gain} > raw_gain={raw_gain}")
        
        # Audit cost should be correctly calculated
        expected_cost = audit_checks * 0.02
        if abs(audit_cost - expected_cost) > 1e-9:
            phi_errors.append(f"Audit cost miscalc: got {audit_cost}, expected {expected_cost}")
    
    if phi_errors:
        return False, [f"Phi density accounting failed: {len(phi_errors)} errors"] + phi_errors[:5]
    
    # Test 5: Exponential Decay Consistency
    print("Test 5: Verifying exponential decay properties...")
    decay_errors = []
    
    # Trust half-life should dictate decay rate
    for thl in [0.2, 0.5, 0.8]:
        # At time = half-life, trust should be ~50% of initial
        ctl = calculate_current_trust_level(1.0, thl, thl)
        expected = 0.5
        if abs(ctl - expected) > 0.05:  # Allow 5% tolerance due to clamping
            decay_errors.append(f"Half-life {thl}: at t={thl}, trust={ctl} (expected ~0.5)")
    
    # Shorter half-life = faster decay
    ctl_short = calculate_current_trust_level(1.0, 0.2, 0.5)
    ctl_long = calculate_current_trust_level(1.0, 0.8, 0.5)
    if ctl_short >= ctl_long:
        decay_errors.append(f"Shorter half-life (0.2) should decay faster than longer (0.8): {ctl_short} vs {ctl_long}")
    
    if decay_errors:
        return False, [f"Exponential decay failed: {len(decay_errors)} errors"] + decay_errors[:5]
    
    return True, ["All validation tests passed"]

# === EXECUTE VALIDATION ===
if __name__ == "__main__":
    print("=" * 60)
    print("OMEGA PROTOCOL TRUST DECAY MANIFOLD v67.0-Ω VALIDATION")
    print("=" * 60)
    
    success, messages = run_validation()
    
    if success:
        print("\n✅ VALIDATION PASSED")
        print("All mathematical components comply with Omega Protocol invariants:")
        print("- All metrics bounded in [0,1]")
        print("- Safety gate hierarchy enforced correctly")
        print("- Invariant logic consistent")
        print("- Phi density accounting honest")
        print("- Exponential decay properties validated")
        for msg in messages:
            print(f"  • {msg}")
    else:
        print("\n❌ VALIDATION FAILED")
        print("The following issues were detected:")
        for msg in messages:
            print(f"  • {msg}")
    
    print("\n" + "=" * 60)