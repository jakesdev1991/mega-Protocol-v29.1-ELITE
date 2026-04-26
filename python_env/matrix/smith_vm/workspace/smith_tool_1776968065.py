# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math

def validate_trust_decay():
    """Validate the trust decay formula in TrustManager.UpdateTrust"""
    # Test parameters
    normalized_time = 1.0  # 1 hour
    initial_trust = 1.0
    
    # Code's current implementation: trust_score *= exp(-log(0.95) * normalized_time)
    factor_code = math.exp(-math.log(0.95) * normalized_time)
    trust_after_code = initial_trust * factor_code
    
    # Correct implementation should be decay: trust_score *= exp(log(0.95) * normalized_time)
    factor_correct = math.exp(math.log(0.95) * normalized_time)
    trust_after_correct = initial_trust * factor_correct
    
    print("TRUST DECAY VALIDATION:")
    print(f"Initial trust score: {initial_trust}")
    print(f"After 1 hour (code): {trust_after_code:.4f}")
    print(f"After 1 hour (correct): {trust_after_correct:.4f}")
    print(f"Code produces growth? {trust_after_code > initial_trust}")
    print(f"Correct produces decay? {trust_after_correct < initial_trust}")
    print(f"Error: Code increases trust by {(trust_after_code - initial_trust)*100:.2f}%")
    print(f"Should decrease by {(initial_trust - trust_after_correct)*100:.2f}%")
    print()

def validate_phi_density():
    """Validate the PhiDensity calculation"""
    K_BOLTZMANN = 1.0
    audit_complexity = 2.5
    audit_entropy_cost = K_BOLTZMANN * math.log(2.0) * audit_complexity
    raw_gain = 0.85
    calculated_density = raw_gain - audit_entropy_cost
    
    print("PHI-DENSITY VALIDATION:")
    print(f"Raw gain: {raw_gain}")
    print(f"Audit entropy cost: {K_BOLTZMANN} * ln(2) * {audit_complexity} = {audit_entropy_cost:.4f}")
    print(f"Calculated Φ-density: {calculated_density:.4f}")
    print(f"Claimed Φ-density: +0.75")
    print(f"Match? {abs(calculated_density - 0.75) < 1e-5}")
    print(f"Discrepancy: {calculated_density - 0.75:.4f}")
    print()

def validate_traversal_score():
    """Validate the traversal score formula"""
    # Test case: 10 unique paths, max depth 5
    unique_paths = 10
    max_depth = 5
    traversal_score = unique_paths * 0.6 + max_depth * 0.4
    
    print("TRAVERSAL SCORE VALIDATION:")
    print(f"Unique paths: {unique_paths}, Max depth: {max_depth}")
    print(f"Calculated score: {traversal_score}")
    print(f"Expected: 10*0.6 + 5*0.4 = 6.0 + 2.0 = 8.0")
    print(f"Match? {abs(traversal_score - 8.0) < 1e-5}")
    print()

def validate_asymmetric_threat():
    """Validate the asymmetric threat (φΔ) calculation"""
    # Test case: breadth=10, depth=5
    breadth = 10
    depth = 5
    phi_delta = abs(breadth - depth) / (breadth + depth)
    
    print("ASYMMETRIC THREAT (φΔ) VALIDATION:")
    print(f"Breadth: {breadth}, Depth: {depth}")
    print(f"Calculated φΔ: {phi_delta:.4f}")
    print(f"Expected: |10-5|/(10+5) = 5/15 ≈ 0.3333")
    print(f"Match? {abs(phi_delta - 1/3) < 1e-5}")
    print()

def validate_topological_impedance():
    """Validate the topological impedance calculation"""
    # Simple test case: two log entries
    # Entry 1: trust=0.5, phi_Delta=0.2
    # Entry 2: trust=0.6, phi_Delta=0.3
    # psi = ln(trust + 1e-10)
    # gauge = trust * |phi_Delta|
    # impedance = Σ[(gauge_i + gauge_{i-1})/2 * (psi_i - psi_{i-1})]
    
    trust_scores = [0.5, 0.6]
    phi_deltas = [0.2, 0.3]
    
    psi_vals = [math.log(t + 1e-10) for t in trust_scores]
    gauge_vals = [t * abs(p) for t, p in zip(trust_scores, phi_deltas)]
    
    impedance = 0.0
    for i in range(1, len(trust_scores)):
        delta_psi = psi_vals[i] - psi_vals[i-1]
        avg_gauge = (gauge_vals[i] + gauge_vals[i-1]) / 2
        impedance += avg_gauge * delta_psi
    
    print("TOPOLOGICAL IMPEDANCE VALIDATION:")
    print(f"Entry 1: trust={trust_scores[0]}, phi_Delta={phi_deltas[0]}")
    print(f"Entry 2: trust={trust_scores[1]}, phi_Delta={phi_deltas[1]}")
    print(f"Psi values: {psi_vals[0]:.4f}, {psi_vals[1]:.4f}")
    print(f"Gauge values: {gauge_vals[0]:.4f}, {gauge_vals[1]:.4f}")
    print(f"Calculated impedance: {impedance:.6f}")
    print(f"Manual calculation:")
    print(f"  Δψ = {psi_vals[1]-psi_vals[0]:.4f}")
    print(f"  Avg gauge = {(gauge_vals[0]+gauge_vals[1])/2:.4f}")
    print(f"  Contribution = {((gauge_vals[0]+gauge_vals[1])/2)*(psi_vals[1]-psi_vals[0]):.6f}")
    print()

def main():
    print("=" * 60)
    print("OMEGA PROTOCOL INVARIANT VALIDATION FOR AFDS v3.0")
    print("=" * 60)
    print()
    
    validate_trust_decay()
    validate_phi_density()
    validate_traversal_score()
    validate_asymmetric_threat()
    validate_topological_impedance()
    
    print("=" * 60)
    print("SUMMARY OF VIOLATIONS:")
    print("1. TRUST DECAY: Code implements growth instead of decay")
    print("2. PHI-DENSITY: Calculated value (-0.8829) ≠ claimed (+0.75)")
    print("3. AUDIT COST: Uses ln(2)*2.5 ≈ 1.7328 instead of 0.15")
    print("4. TRUST SCORE BOUNDS: Novelty penalty can push score negative")
    print("   (before clamping: trust_score - 0.05 could be <0)")
    print("5. TOPOLOGICAL IMPEDANCE: Formula correct but depends on")
    print("   faulty trust scores and φΔ calculations")
    print("=" * 60)

if __name__ == "__main__":
    main()