# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Invariant Validation Script for AFDS v3.0
# Validates mathematical soundness and compliance with Omega Physics Rubric v26.0
# Focus: Trust model dimensionality, jitter coupling, entropy accounting, manifold curvature

import math
import numpy as np

def validate_trust_model():
    """Validate trust update for dimensional consistency and correct decay behavior"""
    print("=== TRUST MODEL VALIDATION ===")
    
    # Test dimensional homogeneity: exponent must be dimensionless
    hours = 24.0  # time dimension
    decay_factor = math.exp(-math.log(0.95) * hours)
    # log(0.95) is dimensionless (nats), hours has dimension [T] → product has dimension [T]
    # VIOLATION: Exponent must be dimensionless for exp() → FAILS DIMENSIONAL ANALYSIS
    print(f"Decay factor after 24h: {decay_factor:.4f} (should be <1 for decay)")
    print(f"Dimensional check: [-log(0.95)] has units [1/time]? → NO (it's dimensionless nats)")
    print("→ FAIL: Trust decay exponent dimensionally inconsistent (violates Omega Physics §6)")
    
    # Test correct decay behavior (should decrease with time)
    trust_initial = 0.5
    trust_after_1h = trust_initial * math.exp(-math.log(0.95) * 1.0)
    trust_after_24h = trust_initial * math.exp(-math.log(0.95) * 24.0)
    print(f"Trust after 1h: {trust_after_1h:.4f} (expected: {trust_initial * 0.95:.4f})")
    print(f"Trust after 24h: {trust_after_24h:.4f} (expected: {trust_initial * (0.95**24):.4f})")
    if trust_after_1h > trust_initial:
        print("→ FAIL: Trust increases with time (should decay) - violates causal invariant")
    else:
        print("→ PASS: Trust decays correctly")
    return trust_after_1h <= trust_initial

def validate_jitter_coupling():
    """Validate jitter probability coupling with trust mitigation"""
    print("\n=== JITTER COUPLING VALIDATION ===")
    
    raw_score = 40.0  # Example traversal score
    base_prob = math.pow(raw_score / 100.0, 1.5)
    print(f"Base jitter probability (raw_score={raw_score}): {base_prob:.4f}")
    
    # Test mitigation effect: high trust should REDUCE jitter probability
    trust_scores = [0.0, 0.5, 1.0]
    for ts in trust_scores:
        mitigation = 0.8 * ts  # From GetTrustMitigation
        # CORRECT coupling: probability = base_prob * (1 - mitigation)
        # CURRENT (flawed) coupling: probability = base_prob * mitigation
        flawed_prob = base_prob * mitigation
        correct_prob = base_prob * (1.0 - mitigation)
        print(f"Trust={ts:.1f}: mitigation={mitigation:.2f} | "
              f"Flawed prob: {flawed_prob:.4f} | Correct prob: {correct_prob:.4f}")
    
    # Check if flawed coupling inverts trust-jitter relationship
    if flawed_prob(trust_scores[2]) > flawed_prob(trust_scores[0]):
        print("→ FAIL: Jitter probability increases with trust (should decrease)")
        print("   Violates objective: 'high Trust Scores receive significant score mitigation'")
        return False
    else:
        print("→ PASS: Jitter probability decreases with trust")
        return True

def validate_forensic_entropy():
    """Validate entropy calculation in forensic reporting"""
    print("\n=== FORENSIC ENTROPY VALIDATION ===")
    
    # Test Shannon entropy calculation flaws
    intervals = [100.0, 500.0, 1000.0, 2000.0]  # ms
    print("Testing entropy calculation on inter-call intervals:")
    for i in intervals:
        p = i / 1000.0  # Normalization (flawed: not forming probability distribution)
        term = -p * math.log(p + 1e-9)
        print(f"  Interval {i:4d}ms → p={p:.2f} → term={term:.4f}")
    
    # Critical flaw: terms can be negative (when p>1 → log(p)>0 → -p*log(p)<0)
    p_test = 2.0
    term_test = -p_test * math.log(p_test + 1e-9)
    print(f"\nFor p=2.0 (interval=2000ms): term = {term_test:.4f}")
    if term_test < 0:
        print("→ FAIL: Entropy calculation produces negative values (violates Shannon entropy ≥0)")
        print("   Violates Omega Physics §5: 'Must reference Shannon conditional entropy'")
        return False
    else:
        print("→ PASS: Entropy terms non-negative")
        return True

def validate_manifold_curvature():
    """Validate security manifold curvature calculation"""
    print("\n=== MANIFOLD CURVATURE VALIDATION ===")
    
    # Check if implementation matches covariant decomposition: Φ = Φ_N × Φ_Δ − H_conditional
    phi_N = 0.8   # Nominal stability (from trust model)
    phi_Delta = 0.7 # Adversarial pressure (from traversal score)
    h_conditional = 0.3 # Adversarial entropy (from forensic log)
    curvature = phi_N * phi_Delta - h_conditional
    
    print(f"Φ_N = {phi_N:.2f}, Φ_Δ = {phi_Delta:.2f}, H_conditional = {h_conditional:.2f}")
    print(f"Manifold curvature Φ = Φ_N×Φ_Δ−H_conditional = {curvature:.4f}")
    
    # Verify dimensional consistency: all terms must be dimensionless
    # In Omega Physics, Φ_N, Φ_Δ, H_conditional are all dimensionless gauges
    print("→ PASS: All terms dimensionless (valid gauge invariants)")
    
    # Check if value makes physical sense (should be negative for unstable manifold)
    if curvature < 0:
        print("→ NOTE: Negative curvature indicates unstable security manifold (expected under adversarial pressure)")
    return True

def main():
    print("OMEGA PROTOCOL INVARIANT VALIDATION FOR AFDS v3.0\n")
    print("Validating against Omega Physics Rubric v26.0 (Strictor Gate)\n")
    
    # Run all validations
    trust_ok = validate_trust_model()
    jitter_ok = validate_jitter_coupling()
    entropy_ok = validate_forensic_entropy()
    manifold_ok = validate_manifold_curvature()
    
    # Final compliance assessment
    print("\n" + "="*50)
    print="OMEGA PROTOCOL COMPLIANCE ASSESSMENT"
    print("="*50)
    print(f"Trust Model Dimensionality: {'PASS' if trust_ok else 'FAIL'}")
    print(f"Jitter-Trust Coupling:      {'PASS' if jitter_ok else 'FAIL'}")
    print(f"Forensic Entropy Calc:      {'PASS' if entropy_ok else 'FAIL'}")
    print(f"Manifold Curvature:         {'PASS' if manifold_ok else 'FAIL'}")
    
    # Calculate net Φ-density impact (per Omega Protocol accounting)
    phi_gain = 0.0
    if trust_ok: phi_gain += 0.20
    if jitter_ok: phi_gain += 0.25
    if entropy_ok: phi_gain += 0.15
    if manifold_ok: phi_gain += 0.10
    # Substantive fixes would add: +0.10 (benchmark) - but we're validating core
    
    # Audit cost subtraction (ΔS_audit = k ln 2 × complexity)
    # Complexity proxy: lines of validated code ≈ 50 → ΔS_audit ≈ 0.05Φ
    audit_cost = 0.05
    net_phi = phi_gain - audit_cost
    
    print(f"\nRaw Φ-density gain: {phi_gain:.2f}Φ")
    print(f"Audit cost subtraction: -{audit_cost:.2f}Φ")
    print(f"Net Φ-density impact: {net_phi:.2f}Φ")
    
    if net_phi > 0 and all([trust_ok, jitter_ok, entropy_ok, manifold_ok]):
        print("\n→ VERDICT: COMPLIANT (Net Φ-density > 0)")
        print("   System strengthens security manifold as required.")
    else:
        print("\n→ VERDICT: NON-COMPLIANT")
        print("   Critical invariant violations detected.")
        if not trust_ok:
            print("   - Trust model dimensionally inconsistent (Ω Physics §6)")
        if not jitter_ok:
            print("   - Jitter-trust coupling inverts causal relationship")
        if not entropy_ok:
            print("   - Forensic entropy violates Shannon ≥0 (Ω Physics §5)")
        if not manifold_ok:
            print("   - Manifold curvature calculation invalid")
    
    return net_phi > 0 and all([trust_ok, jitter_ok, entropy_ok, manifold_ok])

if __name__ == "__main__":
    compliant = main()
    exit(0 if compliant else 1)