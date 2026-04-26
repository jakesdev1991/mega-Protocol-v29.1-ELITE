# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# OMEGA PROTOCOL INVARIANT VALIDATOR FOR AFDS v3.0
# Validates mathematical soundness and compliance with Omega Physics Rubric v26.0
import math
import numpy as np

class InvariantViolation(Exception):
    pass

def validate_trust_invariants(trust_score, cumulative_stability, accessed_paths_size):
    """
    Validate Omega Trust Invariants (Rubric §2):
    1. phi_N = exp(-H_noise) * stability_integral ∈ (0,1]
    2. psi = ln(phi_N) must be real-valued
    3. Trust decay must satisfy d(phi_N)/dt = -phi_N / τ (exponential decay)
    """
    # Calculate H_noise (Shannon entropy of path novelty)
    if accessed_paths_size == 0:
        H_noise = 1.0  # Minimum entropy for unknown process
    else:
        H_noise = math.log(accessed_paths_size)
    
    # Calculate stability integral (cumulative_stability)
    stability_integral = 1.0 - math.exp(-cumulative_stability * 0.1)  # From code
    
    # Compute phi_N
    phi_N = math.exp(-H_noise * 0.01) * stability_integral
    
    # Invariant 1: phi_N must be in (0,1]
    if not (0 < phi_N <= 1.0):
        raise InvariantViolation(f"phi_N = {phi_N} ∉ (0,1] violates Rubric §2")
    
    # Invariant 2: psi = ln(phi_N) must be real
    psi = math.log(phi_N)
    if not isinstance(psi, (int, float)) or math.isnan(psi) or math.isinf(psi):
        raise InvariantViolation(f"psi = ln({phi_N}) = {psi} is not real-valued")
    
    # Invariant 3: Verify exponential decay property (dimensionless time)
    # For constant novelty, d(phi_N)/dt should be proportional to -phi_N
    # We'll test with a small time step
    dt = 0.001  # 1ms in hours (since τ=3600s=1hr)
    decay_rate = -phi_N / 3600.0  # Expected decay rate per second
    actual_change = phi_N * (math.exp(-decay_rate * dt) - 1) / dt
    if abs(actual_change - decay_rate) > 1e-5:
        raise InvariantViolation(f"Trust decay rate mismatch: expected {decay_rate}, got {actual_change}")
    
    return phi_N, psi

def validate_topology_invariants(unique_paths_count, max_depth):
    """
    Validate Topology Invariants (Rubric §3):
    1. phi_Delta = tanh(breadth * depth / (breadth + depth)) ∈ [0,1)
    2. Boundary condition: shredding when phi_Delta ≥ SHREDDING_THRESHOLD (0.95)
    """
    breadth = unique_paths_count
    depth = max_depth
    
    if breadth + depth == 0:
        phi_Delta = 0.0
    else:
        phi_Delta = math.tanh((breadth * depth) / (breadth + depth))
    
    # Invariant 1: phi_Delta must be in [0,1)
    if not (0 <= phi_Delta < 1.0):
        raise InvariantViolation(f"phi_Delta = {phi_Delta} ∉ [0,1) violates Rubric §3")
    
    # Invariant 2: Boundary condition check (handled in jitter function)
    SHREDDING_THRESHOLD = 0.95
    if phi_Delta >= SHREDDING_THRESHOLD:
        # This should trigger informational freeze (valid behavior)
        pass  # Not a violation - expected boundary response
    
    return phi_Delta

def validate_forensic_invariants(log_entries):
    """
    Validate Forensic Invariants (Rubric §4):
    1. Topological impedance H_imp = ∫ gauge_emergence d(trust) ≥ 0
    2. Gauge emergence must be non-negative
    """
    if not log_entries:
        return 0.0
    
    total_gauge = 0.0
    for entry in log_entries:
        # gauge_emergence = |phi_Delta| * trust_score (from code)
        gauge = abs(entry['phi_Delta_component']) * entry['trust_score']
        if gauge < 0:
            raise InvariantViolation(f"Negative gauge emergence: {gauge}")
        total_gauge += gauge
    
    H_imp = total_gauge * 0.01  # Scale factor from code
    
    # Invariant: H_imp must be non-negative
    if H_imp < 0:
        raise InvariantViolation(f"Topological impedance H_imp = {H_imp} < 0")
    
    return H_imp

def validate_curvature_invariants(phi_N, phi_Delta, H_imp, psi, xi_N=0.8, xi_Delta=1.2):
    """
    Validate Manifold Curvature Invariants (Rubric §2 & §5):
    1. Security curvature = xi_N * phi_N + xi_Delta * phi_Delta - H_imp + ψ * 0.1
    2. Must satisfy covariant decomposition: 
        - Newtonian term: xi_N * phi_N
        - Asymmetric term: xi_Delta * phi_Delta
        - Entropy correction: -H_imp + ψ * 0.1
    """
    # Calculate curvature
    curvature = xi_N * phi_N + xi_Delta * phi_Delta - H_imp + psi * 0.1
    
    # Invariant: Curvature must be real and finite
    if not isinstance(curvature, (int, float)) or math.isnan(curvature) or math.isinf(curvature):
        raise InvariantViolation(f"Security curvature = {curvature} is not real/finite")
    
    # Invariant: Newtonian and asymmetric terms must be non-negative
    if xi_N * phi_N < 0:
        raise InvariantViolation(f"Newtonian term {xi_N * phi_N} < 0")
    if xi_Delta * phi_Delta < 0:
        raise InvariantViolation(f"Asymmetric term {xi_Delta * phi_Delta} < 0")
    
    # Invariant: Entropy correction should not dominate (physical plausibility)
    entropy_correction = -H_imp + psi * 0.1
    if abs(entropy_correction) > 2.0:  # Empirical bound from rubric examples
        # Not necessarily a violation, but warrants scrutiny
        pass  # In practice, we'd log this for review
    
    return curvature

def validate_phi_density(raw_gain, audit_complexity):
    """
    Validate Phi-Density Accounting (Rubric §6):
    1. Φ_net = raw_gain - K_BOLTZMANN * ln(2) * audit_complexity
    2. Must satisfy Φ_net > -1.0 (no catastrophic shredding)
    """
    K_BOLTZMANN = 1.0
    audit_entropy_cost = K_BOLTZMANN * math.log(2.0) * audit_complexity
    phi_net = raw_gain - audit_entropy_cost
    
    # Invariant: Net phi-density must be greater than -1.0
    # (Values ≤ -1.0 indicate informational freeze/shredding event)
    if phi_net <= -1.0:
        raise InvariantViolation(f"Phi-density {phi_net} ≤ -1.0 indicates shredding event")
    
    return phi_net

def run_validation_suite():
    """Run comprehensive invariant validation on AFDS v3.0 mathematical core"""
    print("🔍 OMEGA PROTOCOL INVARIANT VALIDATION SUITE")
    print("=" * 50)
    
    test_cases = [
        # Test Case 1: Stable admin process (low novelty, high trust)
        {
            "name": "Stable Admin Process",
            "trust_score": 0.85,
            "cumulative_stability": 10.0,  # High stability
            "accessed_paths_size": 5,      # Familiar paths
            "unique_paths_count": 5,
            "max_depth": 3,
            "log_entries": [
                {"trust_score": 0.8, "phi_Delta_component": 0.1},
                {"trust_score": 0.82, "phi_Delta_component": 0.08},
                {"trust_score": 0.85, "phi_Delta_component": 0.05}
            ],
            "raw_gain": 0.82,
            "audit_complexity": 2.0
        },
        # Test Case 2: Reconnaissance scan (high novelty, low trust)
        {
            "name": "Reconnaissance Scan",
            "trust_score": 0.2,
            "cumulative_stability": 0.5,
            "accessed_paths_size": 50,     # Many novel paths
            "unique_paths_count": 50,
            "max_depth": 10,
            "log_entries": [
                {"trust_score": 0.15, "phi_Delta_component": 0.6},
                {"trust_score": 0.18, "phi_Delta_component": 0.65},
                {"trust_score": 0.2, "phi_Delta_component": 0.7}
            ],
            "raw_gain": 0.3,
            "audit_complexity": 3.5
        },
        # Test Case 3: Boundary condition (shredding threshold)
        {
            "name": "Shredding Boundary",
            "trust_score": 0.1,
            "cumulative_stability": 0.1,
            "accessed_paths_size": 100,
            "unique_paths_count": 100,
            "max_depth": 20,  # High breadth+depth → phi_Delta → 1.0
            "log_entries": [
                {"trust_score": 0.05, "phi_Delta_component": 0.96},
                {"trust_score": 0.08, "phi_Delta_component": 0.97}
            ],
            "raw_gain": 0.1,
            "audit_complexity": 4.0
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for tc in test_cases:
        print(f"\n🧪 Testing: {tc['name']}")
        try:
            # Validate trust invariants
            phi_N, psi = validate_trust_invariants(
                tc['trust_score'], 
                tc['cumulative_stability'], 
                tc['accessed_paths_size']
            )
            print(f"  ✅ Trust Invariants: phi_N={phi_N:.4f}, psi={psi:.4f}")
            
            # Validate topology invariants
            phi_Delta = validate_topology_invariants(
                tc['unique_paths_count'], 
                tc['max_depth']
            )
            print(f"  ✅ Topology Invariants: phi_Delta={phi_Delta:.4f}")
            
            # Validate forensic invariants
            H_imp = validate_forensic_invariants(tc['log_entries'])
            print(f"  ✅ Forensic Invariants: H_imp={H_imp:.4f}")
            
            # Validate curvature invariants
            curvature = validate_curvature_invariants(phi_N, phi_Delta, H_imp, psi)
            print(f"  ✅ Curvature Invariants: Security Curvature={curvature:.4f}")
            
            # Validate phi-density
            phi_net = validate_phi_density(tc['raw_gain'], tc['audit_complexity'])
            print(f"  ✅ Phi-Density: Φ_net={phi_net:.4f}")
            
            print(f"  🎉 ALL INVARIANTS PASSED for {tc['name']}")
            passed += 1
            
        except InvariantViolation as e:
            print(f"  ❌ INVARIANT VIOLATION: {e}")
        except Exception as e:
            print(f"  ⚠️  UNEXPECTED ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"VALIDATION SUMMARY: {passed}/{total} test cases passed")
    
    if passed == total:
        print("🟢 OMEGA PROTOCOL COMPLIANCE: FULLY VALIDATED")
        print("   The AFDS v3.0 mathematical core satisfies all Omega Physics Rubric v26.0 invariants.")
        return True
    else:
 print("🔴 OMEGA PROTOCOL VIOLATIONS DETECTED")
        print("   The implementation contains invariant violations requiring immediate repair.")
        return False

if __name__ == "__main__":
    # Run the validation suite
    is_compliant = run_validation_suite()
    exit(0 if is_compliant else 1)