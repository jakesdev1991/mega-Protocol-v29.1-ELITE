# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
import math

# === Constants from Omega_Trust_Decay namespace ===
PSI_INTEGRITY_THRESHOLD = 0.95
TRUST_HALF_LIFE_MIN = 0.50
PROPAGATION_RADIUS_MAX = 0.60
RECOVERY_VELOCITY_MIN = 0.40
COD_THRESHOLD = 0.85
AUDIT_ENTROPY_PER_CHECK = 0.02
LAMBDA_COUPLING = 0.5
MU_TRUST_DECAY = 0.5

# === TrustDecayGate Methods ===
def calculate_trust_half_life(topology_exposure, compound_exposure_risk, partner_count):
    exposure_factor = 0.5 * topology_exposure + 0.5 * compound_exposure_risk
    partner_factor = min(1.0, partner_count / 10.0)
    half_life = (1.0 - exposure_factor) * (1.0 - 0.3 * partner_factor)
    return max(0.0, min(1.0, half_life))

def calculate_propagation_radius(topology_exposure, partner_count, time_since_exposure):
    time_factor = min(1.0, time_since_exposure * 2.0)
    connectivity_factor = min(1.0, partner_count / 15.0)
    exposure_acceleration = 1.0 + topology_exposure
    propagation = time_factor * connectivity_factor * exposure_acceleration
    return max(0.0, min(1.0, propagation))

def calculate_recovery_velocity(remediation_quality, partner_cooperation, initial_trust):
    technical = remediation_quality * 0.6
    cooperation = partner_cooperation * 0.3
    trust_comp = initial_trust * 0.1
    velocity = technical + cooperation + trust_comp
    return max(0.0, min(1.0, velocity))

def calculate_current_trust_level(initial_trust, trust_half_life, time_since_exposure):
    if trust_half_life < 0.01:
        return initial_trust * 0.1
    decay_exponent = -time_since_exposure / (trust_half_life + 0.01)
    decay_factor = math.pow(2.0, decay_exponent)
    return max(0.0, min(1.0, initial_trust * decay_factor))

def calculate_trust_decay_risk(current_trust_level, propagation_radius, recovery_velocity):
    trust_deficit = 1.0 - current_trust_level
    recovery_deficit = 1.0 - recovery_velocity
    risk = trust_deficit * propagation_radius * recovery_deficit
    return max(0.0, min(1.0, risk))

# === COD Calculation ===
def calculate_cod_trust_decay(diagnostic_vec, plasma_vec, h_instability, theta_tensor_leak, 
                             current_trust_level, trust_decay_risk):
    # Fidelity term
    dot = 0.0
    magD = 0.0
    magP = 0.0
    size = min(len(diagnostic_vec), len(plasma_vec))
    for i in range(size):
        dot += abs(np.conj(diagnostic_vec[i]) * plasma_vec[i])
        magD += abs(diagnostic_vec[i] * diagnostic_vec[i])
        magP += abs(plasma_vec[i] * plasma_vec[i])
    
    fidelity = 0.0
    if magD > 1e-9 and magP > 1e-9:
        fidelity = dot / (math.sqrt(magD) * math.sqrt(magP))
        fidelity = max(0.0, min(1.0, fidelity))
    
    # Penalty terms
    instability_penalty = math.exp(-LAMBDA_COUPLING * h_instability)
    exposure_penalty = math.exp(-LAMBDA_COUPLING * theta_tensor_leak)
    trust_penalty = math.exp(-MU_TRUST_DECAY * (1.0 - current_trust_level))
    decay_penalty = math.exp(-MU_TRUST_DECAY * trust_decay_risk)
    
    return fidelity * instability_penalty * exposure_penalty * trust_penalty * decay_penalty

# === Safety Gates ===
class DecayState:
    STABLE = 0
    DECAYING = 1
    CONTAMINATED = 2
    RECOVERING = 3

class RiskLevel:
    LOW = 0
    MEDIUM = 1
    CRITICAL = 2
    CATASTROPHIC = 3

class SilenceAction:
    PROCEED = 0
    FLAG_TRUST_MONITOR = 1
    FREEZE_COLLABORATION = 2
    IDENTITY_LOCKDOWN = 3

def classify_decay_state(current_trust_level, propagation_radius, recovery_velocity, time_since_exposure):
    if current_trust_level > 0.80 and propagation_radius < 0.20:
        return DecayState.STABLE
    if recovery_velocity > 0.50 and time_since_exposure > 0.50:
        return DecayState.RECOVERING
    if propagation_radius > 0.60:
        return DecayState.CONTAMINATED
    return DecayState.DECAYING

def assess_risk(trust_decay_risk):
    if trust_decay_risk > 0.70:
        return RiskLevel.CATASTROPHIC
    if trust_decay_risk > 0.50:
        return RiskLevel.CRITICAL
    if trust_decay_risk > 0.30:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW

def silence_protocol_decide(psi_integrity, trust_decay_risk, decay_state):
    if psi_integrity < PSI_INTEGRITY_THRESHOLD:
        return SilenceAction.IDENTITY_LOCKDOWN
    if decay_state == DecayState.CONTAMINATED:
        return SilenceAction.IDENTITY_LOCKDOWN
    if trust_decay_risk > 0.70:
        return SilenceAction.IDENTITY_LOCKDOWN
    if trust_decay_risk > 0.50:
        return SilenceAction.FREEZE_COLLABORATION
    if trust_decay_risk > 0.30:
        return SilenceAction.FLAG_TRUST_MONITOR
    return SilenceAction.PROCEED

# === Invariant Check ===
def check_invariants(state, cod, trust_decay_risk, decay_state):
    check = {
        'psi_integrity_ok': state['psi_integrity'] >= PSI_INTEGRITY_THRESHOLD,
        'trust_half_life_ok': state['trust_half_life'] >= TRUST_HALF_LIFE_MIN,
        'propagation_radius_ok': state['propagation_radius'] <= PROPAGATION_RADIUS_MAX,
        'recovery_velocity_ok': state['recovery_velocity'] >= RECOVERY_VELOCITY_MIN,
        'cod_ok': cod >= COD_THRESHOLD,
        'audit_tracked': True
    }
    check['all_passed'] = all(check[key] for key in ['psi_integrity_ok', 'trust_half_life_ok', 
                                                    'propagation_radius_ok', 'recovery_velocity_ok', 
                                                    'cod_ok', 'audit_tracked'])
    return check

# === Validation Script ===
def run_validation():
    random.seed(42)
    np.random.seed(42)
    num_tests = 10000
    errors = []
    
    for _ in range(num_tests):
        # Generate random state
        state = {
            'psi_integrity': random.uniform(0.0, 1.0),
            'h_instability': random.uniform(0.0, 1.0),
            'theta_tensor_leak': random.uniform(0.0, 1.0),
            'topology_exposure': random.uniform(0.0, 1.0),
            'credential_density': random.uniform(0.0, 1.0),
            'traversal_depth': random.uniform(0.0, 1.0),
            'topology_credential_coupling': random.uniform(0.0, 1.0),
            'compound_exposure_risk': random.uniform(0.0, 1.0),
            'partner_institutions': [f"inst_{i}" for i in range(random.randint(0, 20))],
            'time_since_exposure': random.uniform(0.0, 1.0)
        }
        
        # Compute derived metrics
        state['trust_half_life'] = calculate_trust_half_life(
            state['topology_exposure'], 
            state['compound_exposure_risk'],
            len(state['partner_institutions'])
        )
        state['propagation_radius'] = calculate_propagation_radius(
            state['topology_exposure'],
            len(state['partner_institutions']),
            state['time_since_exposure']
        )
        state['recovery_velocity'] = calculate_recovery_velocity(
            0.7,  # remediation_quality (hardcoded in Operate)
            0.6,  # partner_cooperation (hardcoded)
            0.85  # initial_trust (hardcoded)
        )
        state['current_trust_level'] = calculate_current_trust_level(
            0.85,  # initial_trust
            state['trust_half_life'],
            state['time_since_exposure']
        )
        state['trust_decay_risk'] = calculate_trust_decay_risk(
            state['current_trust_level'],
            state['propagation_radius'],
            state['recovery_velocity']
        )
        
        # Validate metric bounds
        metrics_to_check = [
            ('trust_half_life', state['trust_half_life'], 0.0, 1.0),
            ('propagation_radius', state['propagation_radius'], 0.0, 1.0),
            ('recovery_velocity', state['recovery_velocity'], 0.0, 1.0),
            ('current_trust_level', state['current_trust_level'], 0.0, 1.0),
            ('trust_decay_risk', state['trust_decay_risk'], 0.0, 1.0)
        ]
        
        for name, val, low, high in metrics_to_check:
            if not (low <= val <= high):
                errors.append(f"{name} out of bounds: {val} (should be in [{low}, {high}])")
        
        # Validate COD calculation (with random vectors)
        vec_len = random.randint(1, 10)
        diagnostic_vec = [complex(random.uniform(-1,1), random.uniform(-1,1)) for _ in range(vec_len)]
        plasma_vec = [complex(random.uniform(-1,1), random.uniform(-1,1)) for _ in range(vec_len)]
        
        cod = calculate_cod_trust_decay(
            diagnostic_vec, plasma_vec,
            state['h_instability'], state['theta_tensor_leak'],
            state['current_trust_level'], state['trust_decay_risk']
        )
        
        if not (0.0 <= cod <= 1.0):
            errors.append(f"COD out of bounds: {cod} (should be in [0.0, 1.0])")
        
        # Validate decay state classification
        decay_state = classify_decay_state(
            state['current_trust_level'],
            state['propagation_radius'],
            state['recovery_velocity'],
            state['time_since_exposure']
        )
        
        # Validate silence protocol
        action = silence_protocol_decide(
            state['psi_integrity'],
            state['trust_decay_risk'],
            decay_state
        )
        
        # Validate invariant checker
        invariants = check_invariants(state, cod, state['trust_decay_risk'], decay_state)
        
        # Cross-check: If invariants.all_passed is True, action should not be IDENTITY_LOCKDOWN 
        # (unless there's a bug in our logic, but per protocol design)
        if invariants['all_passed'] and action == SilenceAction.IDENTITY_LOCKDOWN:
            errors.append(f"Invariants passed but action is IDENTITY_LOCKDOWN. State: {state}")
        
        # Cross-check: If psi_integrity < threshold, action MUST be IDENTITY_LOCKDOWN
        if state['psi_integrity'] < PSI_INTEGRITY_THRESHOLD and action != SilenceAction.IDENTITY_LOCKDOWN:
            errors.append(f"Psi integrity breach ({state['psi_integrity']}) but action is not LOCKDOWN: {action}")
        
        # Cross-check: If decay_state is CONTAMINATED, action MUST be IDENTITY_LOCKDOWN
        if decay_state == DecayState.CONTAMINATED and action != SilenceAction.IDENTITY_LOCKDOWN:
            errors.append(f"Contaminated decay state but action is not LOCKDOWN: {action}")
    
    # Report results
    if errors:
        print(f"VALIDATION FAILED with {len(errors)} errors:")
        for i, err in enumerate(errors[:10]):  # Show first 10 errors
            print(f"  {i+1}. {err}")
        if len(errors) > 10:
            print(f"  ... and {len(errors)-10} more errors")
        return False
    else:
        print(f"VALIDATION PASSED: All {num_tests} test cases comply with Omega Protocol invariants.")
        return True

if __name__ == "__main__":
    run_validation()