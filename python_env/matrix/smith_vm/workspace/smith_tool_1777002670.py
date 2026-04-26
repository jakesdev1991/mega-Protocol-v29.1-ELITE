# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

# =============================================================================
# OMEGA PROTOCOL INVARIANTS (FROM C++ SPECIFICATION)
# =============================================================================
class RebootInvariants:
    # Dimensionless constants [1]
    LAMBDA_COUPLING = 1.0
    GAMMA_COUPLING = 0.5
    H_VAL_LIMIT = 0.85
    COD_THRESHOLD = 0.80
    PSI_ID_MIN = 0.95
    XI_RESET_MAX = 2.5  # Measurement shock threshold
    PSI_ID_CRITICAL = 0.90  # For shredding condition

# =============================================================================
# CORE MATHEMATICAL FUNCTIONS (VALIDATION TARGETS)
# =============================================================================
def calculate_reboot_cod(Psi_old, Psi_new, H_val, Xi_reset):
    """
    Calculate Chain Overlap Density (COD) for reboot alignment.
    Formula: COD = |<Psi_old | Psi_new>|^2 * exp(-Lambda * H_val) * exp(-Gamma * Xi_reset)
    """
    # Ensure vectors are numpy arrays for dot product
    Psi_old = np.array(Psi_old, dtype=float)
    Psi_new = np.array(Psi_new, dtype=float)
    
    # Calculate fidelity (normalized dot product)
    dot = np.dot(Psi_old, Psi_new)
    mag_old = np.linalg.norm(Psi_old)
    mag_new = np.linalg.norm(Psi_new)
    
    if mag_old < 1e-9 or mag_new < 1e-9:
        fidelity = 0.0
    else:
        fidelity = dot / (mag_old * mag_new)
        fidelity = max(0.0, min(1.0, fidelity))  # Clamp [0,1]
    
    # Entropic damping and stiffness penalty
    damping = math.exp(-RebootInvariants.LAMBDA_COUPLING * H_val)
    stiffness_penalty = math.exp(-RebootInvariants.GAMMA_COUPLING * Xi_reset)
    
    return fidelity * damping * stiffness_penalty

def calculate_validation_entropy(validation_data):
    """
    Calculate normalized Shannon entropy of validation data.
    Formula: H_val = H(D|I) / H_max, where H(D|I) = -sum p log p
    """
    if not validation_data or len(validation_data) == 0:
        return 0.0
    
    # Convert to numpy array and normalize to probabilities
    data = np.array(validation_data, dtype=float)
    total = np.sum(data)
    if total < 1e-9:
        return 0.0
    probs = data / total
    
    # Calculate Shannon entropy
    H = 0.0
    for p in probs:
        if p > 1e-9:
            H -= p * math.log(p)
    
    # Normalize by maximum possible entropy (log(n))
    n = len(probs)
    max_entropy = math.log(n) if n > 1 else 1.0
    if max_entropy < 1e-9:
        max_entropy = 1.0
    
    H_normalized = H / max_entropy
    return max(0.0, min(1.0, H_normalized))  # Clamp [0,1]

def verify_invariants(psi_id, xi_reset):
    """
    Hard gate invariant verification (from RebootInvariants.VerifyInvariants).
    Returns True if invariants hold, False if critical failure (shredding).
    """
    # Identity conservation hard gate
    if psi_id < RebootInvariants.PSI_ID_MIN:
        print(f"CRITICAL: Shredding Event - Psi_id = {psi_id:.3f} < {RebootInvariants.PSI_ID_MIN}")
        return False
    
    # Measurement shock warning (not hard fail)
    if xi_reset > RebootInvariants.XI_RESET_MAX:
        print(f"WARNING: Measurement Shock Risk - Xi_reset = {xi_reset:.3f} > {RebootInvariants.XI_RESET_MAX}")
    
    return True

def check_failure_mode(H_val, xi_reset, psi_id):
    """
    Detect systemic failure modes (from FailureModeDetector.CheckRisk).
    Returns failure type string.
    """
    # Identity Shredding: High entropy + high force + low identity
    if (H_val > RebootInvariants.H_VAL_LIMIT and 
        xi_reset > RebootInvariants.XI_RESET_MAX and 
        psi_id < RebootInvariants.PSI_ID_CRITICAL):
        return "IDENTITY_SHREDDING"
    
    # Validation Paralysis: High entropy + low force
    if H_val > RebootInvariants.H_VAL_LIMIT and xi_reset < 0.3:
        return "VALIDATION_PARALYSIS"
    
    # Measurement Shock: High force
    if xi_reset > RebootInvariants.XI_RESET_MAX:
        return "MEASUREMENT_SHOCK"
    
    return "NONE"

def adiabatic_reboot_step(Psi_old, Psi_new, validation_data, xi_reset, psi_id):
    """
    Simplified adiabatic reboot step (core logic from Adiabatic_Reboot_Operator.Apply).
    Returns updated state and success flag.
    """
    # Phase 1: Diagnostic
    H_val = calculate_validation_entropy(validation_data)
    current_cod = calculate_reboot_cod(Psi_old, Psi_new, H_val, xi_reset)
    failure = check_failure_mode(H_val, xi_reset, psi_id)
    
    # Early exit if stable
    if failure == "NONE" and current_cod >= RebootInvariants.COD_THRESHOLD:
        return Psi_old, xi_reset, psi_id, True, "Stable state achieved"
    
    # Phase 2: Stiffness Modulation
    if failure == "IDENTITY_SHREDDING":
        xi_reset = max(0.3, xi_reset * 0.8)
        action = "Reducing reboot force (IDENTITY_SHREDDING risk)"
    elif failure == "VALIDATION_PARALYSIS":
        xi_reset = min(1.5, xi_reset * 1.2)
        action = "Increasing force or reducing data (VALIDATION_PARALYSIS)"
    elif failure == "MEASUREMENT_SHOCK":
        xi_reset = max(0.3, xi_reset * 0.5)
        action = "Slowing transition (MEASUREMENT_SHOCK risk)"
    else:  # NONE but low COD
        if current_cod < RebootInvariants.COD_THRESHOLD:
            xi_reset = min(1.5, xi_reset * 1.1)
            action = "Increasing stiffness for alignment (low COD)"
        else:
            action = "Nominal operation"
    
    # Phase 3: State Transformation (basis change)
    alpha = min(1.0, (1.0 - xi_reset) * 0.5 + 0.5)
    Psi_old_updated = [(1.0 - alpha) * old + alpha * new for old, new in zip(Psi_old, Psi_new)]
    
    # Phase 4: Entropy Accounting (simulated)
    if H_val > 0.8:
        print(f"WARNING: High Informational Heat (H_val = {H_val:.3f})")
    
    # Phase 5: Invariant Validation (hard gate)
    # Simulate identity loss proportional to entropy
    identity_loss = H_val * 0.1
    psi_id_updated = psi_id - identity_loss
    
    if not verify_invariants(psi_id_updated, xi_reset):
        return Psi_old_updated, xi_reset, psi_id_updated, False, "Invariant violation: Identity integrity compromised"
    
    return Psi_old_updated, xi_reset, psi_id_updated, True, action

# =============================================================================
# VALIDATION TEST SUITE
# =============================================================================
def run_validation_tests():
    """Run comprehensive validation tests for mathematical soundness."""
    print("=" * 60)
    print("OMEGA PROTOCOL SYSTEMIC REBOOT MATHEMATICAL VALIDATION")
    print("=" * 60)
    
    # Test 1: COD calculation correctness
    print("\n[TEST 1] COD Calculation Verification")
    print("-" * 40)
    
    # Orthogonal vectors should have fidelity 0
    Psi_old = [1.0, 0.0]
    Psi_new = [0.0, 1.0]
    H_val = 0.0
    xi_reset = 0.0
    cod = calculate_reboot_cod(Psi_old, Psi_new, H_val, xi_reset)
    print(f"Orthogonal vectors: COD = {cod:.6f} (expected ~0.0)")
    assert abs(cod) < 1e-5, "Orthogonal vectors should yield near-zero COD"
    
    # Identical vectors should have fidelity 1 (before damping)
    Psi_old = [1.0, 0.0]
    Psi_new = [1.0, 0.0]
    cod = calculate_reboot_cod(Psi_old, Psi_new, H_val, xi_reset)
    print(f"Identical vectors: COD = {cod:.6f} (expected 1.0)")
    assert abs(cod - 1.0) < 1e-5, "Identical vectors should yield COD=1.0"
    
    # Damping effect: higher H_val reduces COD
    cod_high_entropy = calculate_reboot_cod([1.0,0.0], [1.0,0.0], 0.5, 0.0)
    cod_low_entropy = calculate_reboot_cod([1.0,0.0], [1.0,0.0], 0.1, 0.0)
    print(f"High entropy (0.5): COD = {cod_high_entropy:.6f}")
    print(f"Low entropy (0.1): COD = {cod_low_entropy:.6f}")
    assert cod_high_entropy < cod_low_entropy, "Higher entropy should reduce COD"
    
    # Stiffness penalty effect
    cod_low_stiffness = calculate_reboot_cod([1.0,0.0], [1.0,0.0], 0.0, 0.1)
    cod_high_stiffness = calculate_reboot_cod([1.0,0.0], [1.0,0.0], 0.0, 1.0)
    print(f"Low stiffness (0.1): COD = {cod_low_stiffness:.6f}")
    print(f"High stiffness (1.0): COD = {cod_high_stiffness:.6f}")
    assert cod_high_stiffness < cod_low_stiffness, "Higher stiffness should reduce COD"
    
    # Test 2: Validation entropy calculation
    print("\n[TEST 2] Validation Entropy Verification")
    print("-" * 40)
    
    # Uniform distribution: max entropy
    uniform_data = [0.25, 0.25, 0.25, 0.25]
    entropy_uniform = calculate_validation_entropy(uniform_data)
    print(f"Uniform [0.25,0.25,0.25,0.25]: Entropy = {entropy_uniform:.6f} (expected ~1.0)")
    assert abs(entropy_uniform - 1.0) < 1e-5, "Uniform distribution should yield normalized entropy=1.0"
    
    # Delta distribution: zero entropy
    delta_data = [1.0, 0.0, 0.0, 0.0]
    entropy_delta = calculate_validation_entropy(delta_data)
    print(f"Delta [1.0,0.0,0.0,0.0]: Entropy = {entropy_delta:.6f} (expected 0.0)")
    assert entropy_delta < 1e-5, "Delta distribution should yield near-zero entropy"
    
    # Empty data
    entropy_empty = calculate_validation_entropy([])
    print(f"Empty data: Entropy = {entropy_empty:.6f} (expected 0.0)")
    assert entropy_empty == 0.0, "Empty data should yield zero entropy"
    
    # Test 3: Invariant verification
    print("\n[TEST 3] Invariant Verification")
    print("-" * 40)
    
    # Valid identity
    assert verify_invariants(0.96, 1.0) == True, "Psi_id=0.96 should pass invariant check"
    print("Psi_id=0.96: PASS (>=0.95)")
    
    # Critical identity failure
    assert verify_invariants(0.94, 1.0) == False, "Psi_id=0.94 should fail invariant check"
    print("Psi_id=0.94: FAIL (<0.95) -> Shredding event")
    
    # Measurement shock warning (should not fail invariants)
    assert verify_invariants(0.96, 3.0) == True, "High xi_reset should warn but not fail invariants"
    print("Psi_id=0.96, Xi_reset=3.0: PASS (with warning)")
    
    # Test 4: Failure mode detection
    print("\n[TEST 4] Failure Mode Detection")
    print("-" * 40)
    
    # Identity Shredding condition
    failure = check_failure_mode(0.9, 3.0, 0.85)  # H_val>0.85, Xi_reset>2.5, Psi_id<0.90
    print(f"H_val=0.9, Xi_reset=3.0, Psi_id=0.85 -> Failure: {failure}")
    assert failure == "IDENTITY_SHREDDING", "Should detect identity shredding"
    
    # Validation Paralysis
    failure = check_failure_mode(0.9, 0.2, 0.95)  # H_val>0.85, Xi_reset<0.3
    print(f"H_val=0.9, Xi_reset=0.2, Psi_id=0.95 -> Failure: {failure}")
    assert failure == "VALIDATION_PARALYSIS", "Should detect validation paralysis"
    
    # Measurement Shock
    failure = check_failure_mode(0.5, 3.0, 0.95)  # Xi_reset>2.5
    print(f"H_val=0.5, Xi_reset=3.0, Psi_id=0.95 -> Failure: {failure}")
    assert failure == "MEASUREMENT_SHOCK", "Should detect measurement shock"
    
    # Normal operation
    failure = check_failure_mode(0.5, 1.0, 0.96)
    print(f"H_val=0.5, Xi_reset=1.0, Psi_id=0.96 -> Failure: {failure}")
    assert failure == "NONE", "Should detect no failure"
    
    # Test 5: Adiabatic reboot step
    print("\n[TEST 5] Adiabatic Reboot Step Validation")
    print("-" * 40)
    
    # Initial state: degraded identity
    Psi_old = [0.6, 0.8]  # Not normalized, but we'll use as-is
    Psi_new = [0.8, 0.6]   # Target state
    validation_data = [0.7, 0.3]  # Moderate entropy
    xi_reset = 1.0
    psi_id = 0.98
    
    print(f"Initial state: Psi_old={Psi_old}, Psi_new={Psi_new}")
    print(f"Validation data: {validation_data} (H_val ≈ {calculate_validation_entropy(validation_data):.3f})")
    print(f"Initial Xi_reset: {xi_reset}, Psi_id: {psi_id}")
    
    # Run reboot step
    Psi_updated, xi_updated, psi_id_updated, success, message = adiabatic_reboot_step(
        Psi_old, Psi_new, validation_data, xi_reset, psi_id
    )
    
    print(f"Reboot step result: {message}")
    print(f"Updated Psi_old: {[round(x, 4) for x in Psi_updated]}")
    print(f"Updated Xi_reset: {xi_updated:.4f}")
    print(f"Updated Psi_id: {psi_id_updated:.4f}")
    print(f"Success: {success}")
    
    # Verify identity preservation
    assert psi_id_updated >= RebootInvariants.PSI_ID_MIN, f"Identity violated: {psi_id_updated} < {RebootInvariants.PSI_ID_MIN}"
    assert success == True, "Reboot step should succeed with valid parameters"
    
    # Verify COD improvement (should move toward target)
    H_val_post = calculate_validation_entropy(validation_data)
    cod_initial = calculate_reboot_cod(Psi_old, Psi_new, H_val_post, xi_reset)
    cod_updated = calculate_reboot_cod(Psi_updated, Psi_new, H_val_post, xi_updated)
    print(f"Initial COD: {cod_initial:.4f}")
    print(f"Updated COD: {cod_updated:.4f}")
    assert cod_updated > cod_initial, "COD should increase after alignment step"
    
    print("\n" + "=" * 60)
    print("ALL VALIDATION TESTS PASSED")
    print("Mathematical framework is sound and compliant with Omega Protocol invariants")
    print("=" * 60)

# =============================================================================
# EXECUTE VALIDATION
# =============================================================================
if __name__ == "__main__":
    run_validation_tests()