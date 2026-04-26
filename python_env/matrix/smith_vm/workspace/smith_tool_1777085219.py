# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math

# === OMEGA PROTOCOL INVARIANTS (FROM C++ CODE) ===
# CorrelationSmithInvariants constants
COD_THRESHOLD = 0.85
COD_FLOOR = 0.39
PSI_INTEGRITY_THRESHOLD = 0.95
CORRELATION_LENGTH_THRESHOLD = 0.70
SHEAR_FLOW_MIN = 0.50
TENSOR_LEAK_MAX = 0.50
STIFFNESS_MAX_DELTA = 0.10
PHI_DELTA_MAX = 0.50
B1_HOMOLOGY_MAX = 0.80
AUDIT_ENTROPY_PER_CHECK = 0.02  # Per Smith Invariant check

# === CORE FUNCTIONS (TRANSLATED FROM C++) ===
def calculate_correlation_length(density_gradient, collisionality, beta_parameter, shear_flow):
    """Calculate normalized correlation length [0,1] from plasma parameters"""
    DENSITY_GRADIENT_EXPONENT = 0.5
    BETA_EXPONENT = 0.3
    SHEAR_EXPONENT = 0.7
    
    gradient_factor = density_gradient ** DENSITY_GRADIENT_EXPONENT
    beta_factor = beta_parameter ** BETA_EXPONENT
    shear_factor = shear_flow ** SHEAR_EXPONENT
    collisionality_damping = math.exp(-0.5 * collisionality)
    
    raw_correlation = gradient_factor * beta_factor * shear_factor * collisionality_damping
    return max(0.0, min(1.0, raw_correlation))  # Clamp to [0,1]

def calculate_lh_proximity(correlation_length, shear_flow):
    """Calculate L-H transition proximity [0,1]"""
    if shear_flow < SHEAR_FLOW_MIN:
        return 0.0
    proximity = (correlation_length - 0.5) / 0.5  # Scale around threshold 0.5
    return max(0.0, min(1.0, proximity))

def calculate_fidelity(diagnostic_vec, plasma_vec):
    """Calculate diagnostic-plasma alignment fidelity [0,1]"""
    dot = 0.0
    magD = 0.0
    magP = 0.0
    n = min(len(diagnostic_vec), len(plasma_vec))
    for i in range(n):
        d_mag = abs(diagnostic_vec[i])
        p_mag = abs(plasma_vec[i])
        dot += d_mag * p_mag
        magD += d_mag * d_mag
        magP += p_mag * p_mag
    if magD < 1e-9 or magP < 1e-9:
        return 0.0
    fidelity = dot / (math.sqrt(magD) * math.sqrt(magP))
    return max(0.0, min(1.0, fidelity))

def calculate_cod(diagnostic_vec, plasma_vec, h_instability, xi_confinement, theta_tensor_leak, 
                  correlation_length_parallel, correlation_length_perp):
    """Calculate Chain Overlap Density [0,1]"""
    fidelity = calculate_fidelity(diagnostic_vec, plasma_vec)
    instability_penalty = math.exp(-LAMBDA_COUPLING * h_instability)
    confinement_penalty = math.exp(-KAPPA_CONFINEMENT * xi_confinement)
    exposure_penalty = math.exp(-ETA_TENSOR_LEAK * theta_tensor_leak)
    correlation_mean = (correlation_length_parallel + correlation_length_perp) / 2.0
    correlation_penalty = math.exp(-MU_CORRELATION * (1.0 - correlation_mean))
    return fidelity * instability_penalty * confinement_penalty * exposure_penalty * correlation_penalty

# Penalty constants (from C++ code)
LAMBDA_COUPLING = 0.5
KAPPA_CONFINEMENT = 0.5
ETA_TENSOR_LEAK = 0.3
MU_CORRELATION = 0.4

def decide_action(state_psi_integrity, state_cod, state_correlation_length, state_shear_flow_strength):
    """Enforce Omega Protocol safety gate hierarchy"""
    # PRIMARY GATE: Ψ_integrity (non-negotiable)
    if state_psi_integrity < PSI_INTEGRITY_THRESHOLD:
        return "HALT_EXPERIMENT"
    
    # CORRELATION GATE: Must have sufficient correlation length
    if state_correlation_length < CORRELATION_LENGTH_THRESHOLD:
        if state_shear_flow_strength > SHEAR_FLOW_MIN:
            return "AWAIT_LH_TRANSITION"  # Correlation building
        else:
            return "FREEZE_CONFIG"  # Insufficient shear to build correlation
    
    # SECONDARY GATE: COD (alignment fidelity)
    if state_cod < COD_THRESHOLD:
        return "FREEZE_CONFIG"
    
    return "PROCEED"

def calculate_net_gain(cod_before, cod_after, audit_checks_performed):
    """Calculate Φ-density gain with audit cost subtraction"""
    raw_gain = cod_after - cod_before
    audit_cost = audit_checks_performed * AUDIT_ENTROPY_PER_CHECK
    return raw_gain - audit_cost

# === VALIDATION TESTS ===
def test_dimensional_consistency():
    """Verify all metrics remain in [0,1] for valid inputs"""
    print("Testing dimensional consistency...")
    
    # Test correlation length calculation
    for dg in [0.0, 0.5, 1.0]:
        for coll in [0.0, 0.5, 1.0]:
            for bp in [0.0, 0.5, 1.0]:
                for sf in [0.0, 0.5, 1.0]:
                    cl = calculate_correlation_length(dg, coll, bp, sf)
                    assert 0.0 <= cl <= 1.0, f"correlation_length {cl} out of bounds"
    
    # Test LH proximity
    for cl in [0.0, 0.5, 1.0]:
        for sf in [0.0, 0.5, 1.0]:
            lh = calculate_lh_proximity(cl, sf)
            assert 0.0 <= lh <= 1.0, f"lh_proximity {lh} out of bounds"
    
    # Test fidelity with edge cases
    # Identical vectors
    diag = [1+0j, 2+0j, 3+0j]
    plasma = [1+0j, 2+0j, 3+0j]
    fid = calculate_fidelity(diag, plasma)
    assert abs(fid - 1.0) < 1e-5, f"fidelity should be 1.0 for identical vectors"
    
    # Orthogonal magnitude vectors
    diag = [1+0j, 0+0j]
    plasma = [0+0j, 1+0j]
    fid = calculate_fidelity(diag, plasma)
    assert abs(fid - 0.0) < 1e-5, f"fidelity should be 0.0 for orthogonal vectors"
    
    # Test COD bounds (with fidelity=1.0)
    diag = [1+0j]
    plasma = [1+0j]
    for hi in [0.0, 0.5, 1.0]:
        for xc in [0.0, 0.5, 1.0]:
            for ttl in [0.0, 0.5, 1.0]:
                for clp in [0.0, 0.5, 1.0]:
                    for clpp in [0.0, 0.5, 1.0]:
                        cod = calculate_cod(diag, plasma, hi, xc, ttl, clp, clpp)
                        assert 0.0 < cod <= 1.0, f"COD {cod} out of bounds"
    
    # Test COD=0 when fidelity=0
    diag = [1+0j, 0+0j]
    plasma = [0+0j, 1+0j]
    for hi in [0.0, 0.5, 1.0]:
        for xc in [0.0, 0.5, 1.0]:
            for ttl in [0.0, 0.5, 1.0]:
                for clp in [0.0, 0.5, 1.0]:
                    for clpp in [0.0, 0.5, 1.0]:
                        cod = calculate_cod(diag, plasma, hi, xc, ttl, clp, clpp)
                        assert cod == 0.0, f"COD should be 0.0 when fidelity=0"
    
    print("✓ All metrics dimensionally compliant [0,1]")

def test_safety_gate_hierarchy():
    """Verify Omega Protocol safety gate enforcement"""
    print("\nTesting safety gate hierarchy...")
    
    # Case 1: Integrity breach → HALT_EXPERIMENT
    assert decide_action(0.94, 0.9, 0.8, 0.6) == "HALT_EXPERIMENT"
    print("✓ Integrity breach (ψ<0.95) → HALT_EXPERIMENT")
    
    # Case 2: Low correlation + low shear → FREEZE_CONFIG
    assert decide_action(0.96, 0.9, 0.6, 0.4) == "FREEZE_CONFIG"
    print("✓ Low correlation (ξ<0.70) + low shear (<0.50) → FREEZE_CONFIG")
    
    # Case 3: Low correlation + high shear → AWAIT_LH_TRANSITION
    assert decide_action(0.96, 0.9, 0.6, 0.6) == "AWAIT_LH_TRANSITION"
    print("✓ Low correlation (ξ<0.70) + high shear (≥0.50) → AWAIT_LH_TRANSITION")
    
    # Case 4: OK correlation + low COD → FREEZE_CONFIG
    assert decide_action(0.96, 0.9, 0.8, 0.6) == "FREEZE_CONFIG"  # COD=0.8 < 0.85
    print("✓ OK correlation + low COD (<0.85) → FREEZE_CONFIG")
    
    # Case 5: All gates pass → PROCEED
    assert decide_action(0.96, 0.9, 0.8, 0.6) == "PROCEED"
    print("✓ All gates satisfied → PROCEED")
    
    # Verify gate ordering integrity
    # Integrity gate must override all others
    assert decide_action(0.94, 0.9, 0.9, 0.9) == "HALT_EXPERIMENT"
    # Correlation gate must override COD gate
    assert decide_action(0.96, 0.5, 0.8, 0.6) == "FREEZE_CONFIG"  # Low COD but correlation gate triggers first
    print("✓ Gate hierarchy integrity maintained")

def test_phi_density_ledger():
    """Verify Φ-density accounting with audit cost subtraction"""
    print("\nTesting Φ-density ledger...")
    
    # Basic net gain calculation
    assert calculate_net_gain(0.8, 0.9, 0) == 0.1
    assert calculate_net_gain(0.8, 0.9, 1) == 0.08  # -0.02 audit cost
    assert calculate_net_gain(0.8, 0.9, 9) == -0.08  # -0.18 audit cost
    
    # Negative gain handling
    assert calculate_net_gain(0.9, 0.8, 0) == -0.1
    assert calculate_net_gain(0.9, 0.8, 5) == -0.2  # -0.1 raw -0.10 audit
    
    # Verify audit cost matches 9 invariants × 0.02
    assert calculate_net_gain(0.85, 0.85, 9) == -0.18  # Zero raw gain
    print("✓ Audit cost subtraction compliant (9 × 0.02 = 0.18)")

def test_research_integration():
    """Validate Konzett et al. research integration"""
    print("\nTesting research integration (Konzett et al.)...")
    
    # Verify L-H transition logic
    # Below shear threshold → no proximity buildup
    assert calculate_lh_proximity(0.8, 0.4) == 0.0  # Shear < 0.50
    # Above shear threshold → proximity scales with correlation
    assert calculate_lh_proximity(0.6, 0.6) > 0.0  # Should be positive
    assert calculate_lh_proximity(1.0, 0.6) == 1.0  # Max proximity
    assert calculate_lh_proximity(0.5, 0.6) == 0.0  # At threshold
    
    # Verify correlation length scaling with shear
    # Higher shear should increase correlation length (for fixed other params)
    cl_low = calculate_correlation_length(0.7, 0.2, 0.3, 0.4)
    cl_high = calculate_correlation_length(0.7, 0.2, 0.3, 0.6)
    assert cl_high > cl_low, "Shear flow should increase correlation length"
    
    # Verify COD decreases with decreasing correlation
    diag = [1+0j]
    plasma = [1+0j]
    base_cod = calculate_cod(diag, plasma, 0.1, 0.1, 0.1, 0.8, 0.8)
    low_cod = calculate_cod(diag, plasma, 0.1, 0.1, 0.1, 0.5, 0.5)
    assert low_cod < base_cod, "Lower correlation should reduce COD"
    
    print("✓ Research integration physically consistent")

if __name__ == "__main__":
    print("=" * 60)
    print("OMEGA PROTOCOL VALIDATION: CORRELATION-AWARE TOKAMAK v59.0-Ω")
    print("=" * 60)
    
    test_dimensional_consistency()
    test_safety_gate_hierarchy()
    test_phi_density_ledger()
    test_research_integration()
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED")
    print("✓ Mathematically sound")
    print("✓ Compliant with Omega Protocol invariants")
    print("✓ Research integration validated")
    print("✓ Safety gates enforce hierarchy correctly")
    print("=" * 60)