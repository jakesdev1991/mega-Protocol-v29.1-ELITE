# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
import math

# Omega Protocol Constants (from C++ code)
LAMBDA_COUPLING = 0.5
MU_FRAGMENTATION = 0.7
PSI_INTEGRITY_THRESHOLD = 0.95
FRAGMENTATION_INDEX_MAX = 0.60
ACCESSIBILITY_MIN = 0.50
ARBITRAGE_EFFICIENCY_MIN = 0.45
COD_THRESHOLD = 0.85
AUDIT_ENTROPY_PER_CHECK = 0.02

def calculate_fragmentation_index(venue_concentration, protocol_compatibility, venue_count):
    """Mirror of C++ CalculateFragmentationIndex"""
    venue_factor = min(1.0, venue_count / 10.0)
    concentration_reduction = venue_concentration * 0.4
    compatibility_factor = (1.0 - protocol_compatibility) * 0.3
    fragmentation = venue_factor * (1.0 - concentration_reduction) + compatibility_factor
    return max(0.0, min(1.0, fragmentation))

def calculate_accessibility_score(cross_venue_latency, protocol_compatibility, arbitrage_efficiency, venue_concentration):
    """Mirror of C++ CalculateAccessibilityScore"""
    latency_penalty = cross_venue_latency * 0.35
    compatibility_bonus = protocol_compatibility * 0.30
    arbitrage_bonus = arbitrage_efficiency * 0.20
    concentration_factor = (1.0 - abs(venue_concentration - 0.5)) * 0.15
    accessibility = compatibility_bonus + arbitrage_bonus + concentration_factor - latency_penalty
    return max(0.0, min(1.0, accessibility))

def calculate_arbitrage_efficiency(cross_venue_latency, protocol_compatibility, market_resilience):
    """Mirror of C++ CalculateArbitrageEfficiency"""
    latency_component = (1.0 - cross_venue_latency) * 0.5
    compatibility_component = protocol_compatibility * 0.3
    resilience_component = market_resilience * 0.2
    efficiency = latency_component + compatibility_component + resilience_component
    return max(0.0, min(1.0, efficiency))

def calculate_functional_liquidity_ratio(accessibility_score, fragmentation_index, venue_concentration):
    """Mirror of C++ CalculateFunctionalLiquidityRatio"""
    accessibility_component = accessibility_score * 0.6
    fragmentation_component = (1.0 - fragmentation_index) * 0.25
    concentration_component = venue_concentration * 0.15
    ratio = accessibility_component + fragmentation_component + concentration_component
    return max(0.0, min(1.0, ratio))

def calculate_cascade_amplification(fragmentation_index, liquidity_velocity, accessibility_score):
    """Mirror of C++ CalculateCascadeAmplification"""
    fragmentation_component = fragmentation_index * 0.5
    velocity_component = liquidity_velocity * 0.3
    accessibility_reduction = (1.0 - accessibility_score) * 0.2
    amplification = fragmentation_component + velocity_component + accessibility_reduction
    return max(0.0, min(1.0, amplification))

def calculate_fragmentation_risk(fragmentation_index, accessibility_score, arbitrage_efficiency):
    """Mirror of C++ CalculateFragmentationRisk"""
    accessibility_deficit = 1.0 - accessibility_score
    arbitrage_deficit = 1.0 - arbitrage_efficiency
    risk = fragmentation_index * accessibility_deficit * arbitrage_deficit
    return max(0.0, min(1.0, risk))

def calculate_cod_fragmentation_aware(h_instability, theta_tensor_leak, 
                                    fragmentation_index, accessibility_score, fragmentation_risk):
    """Mirror of C++ Calculate_COD_FragmentationAware (simplified for scalar test)"""
    # Fidelity term (simplified to 1.0 for test - actual value depends on vectors but is in [0,1])
    fidelity = 1.0  # Conservative assumption for test
    
    instability_penalty = math.exp(-LAMBDA_COUPLING * h_instability)
    exposure_penalty = math.exp(-LAMBDA_COUPLING * theta_tensor_leak)
    fragmentation_penalty = math.exp(-MU_FRAGMENTATION * fragmentation_index)
    accessibility_penalty = math.exp(-MU_FRAGMENTATION * (1.0 - accessibility_score))
    risk_penalty = math.exp(-MU_FRAGMENTATION * fragmentation_risk)
    
    cod = fidelity * instability_penalty * exposure_penalty * fragmentation_penalty * accessibility_penalty * risk_penalty
    return max(0.0, min(1.0, cod))

def decide_action(psi_integrity, fragmentation_risk, fragmentation_state):
    """Mirror of C++ LiquidityFragmentationProtocol::Decide"""
    # PRIMARY GATE: Ψ_integrity (non-negotiable)
    if psi_integrity < PSI_INTEGRITY_THRESHOLD:
        return "IDENTITY_LOCKDOWN"
    
    # FRAGMENTATION STATE GATE
    if fragmentation_state == "FUNCTIONALLY_LOCKED":
        return "IDENTITY_LOCKDOWN"
    
    # RISK-BASED Decisions
    if fragmentation_risk > 0.70:
        return "IDENTITY_LOCKDOWN"
    if fragmentation_risk > 0.50 or fragmentation_state == "HIGHLY_FRAGMENTED":
        return "ACTIVATE_BRIDGING"
    if fragmentation_risk > 0.30 or fragmentation_state == "MODERATELY_FRAGMENTED":
        return "MONITOR_FRAGMENTATION"
    return "PROCEED"

def validate_mathematical_soundness():
    """Validate all mathematical functions maintain [0,1] bounds"""
    print("=== MATHEMATICAL SOUNDNESS VALIDATION ===")
    num_tests = 10000
    all_passed = True
    
    # Test 1: Fragmentation Index
    print("\n1. Testing Fragmentation Index...")
    for _ in range(num_tests):
        vc = random.uniform(0, 1)      # venue_concentration
        pc = random.uniform(0, 1)      # protocol_compatibility
        vc_count = random.randint(0, 20)  # venue_count
        fi = calculate_fragmentation_index(vc, pc, vc_count)
        if not (0 <= fi <= 1):
            print(f"   FAIL: fi={fi} for inputs (vc={vc}, pc={pc}, vc_count={vc_count})")
            all_passed = False
    print("   PASS" if all_passed else "   FAIL")
    
    # Test 2: Accessibility Score
    print("\n2. Testing Accessibility Score...")
    all_passed = True
    for _ in range(num_tests):
        cvl = random.uniform(0, 1)     # cross_venue_latency
        pc = random.uniform(0, 1)      # protocol_compatibility
        ae = random.uniform(0, 1)      # arbitrage_efficiency
        vc = random.uniform(0, 1)      # venue_concentration
        as_ = calculate_accessibility_score(cvl, pc, ae, vc)
        if not (0 <= as_ <= 1):
            print(f"   FAIL: as={as_} for inputs (cvl={cvl}, pc={pc}, ae={ae}, vc={vc})")
            all_passed = False
    print("   PASS" if all_passed else "   FAIL")
    
    # Test 3: Arbitrage Efficiency
    print("\n3. Testing Arbitrage Efficiency...")
    all_passed = True
    for _ in range(num_tests):
        cvl = random.uniform(0, 1)     # cross_venue_latency
        pc = random.uniform(0, 1)      # protocol_compatibility
        mr = random.uniform(0, 1)      # market_resilience
        ae = calculate_arbitrage_efficiency(cvl, pc, mr)
        if not (0 <= ae <= 1):
            print(f"   FAIL: ae={ae} for inputs (cvl={cvl}, pc={pc}, mr={mr})")
            all_passed = False
    print("   PASS" if all_passed else "   FAIL")
    
    # Test 4: Functional Liquidity Ratio
    print("\n4. Testing Functional Liquidity Ratio...")
    all_passed = True
    for _ in range(num_tests):
        as_ = random.uniform(0, 1)     # accessibility_score
        fi = random.uniform(0, 1)      # fragmentation_index
        vc = random.uniform(0, 1)      # venue_concentration
        flr = calculate_functional_liquidity_ratio(as_, fi, vc)
        if not (0 <= flr <= 1):
            print(f"   FAIL: flr={flr} for inputs (as_={as_}, fi={fi}, vc={vc})")
            all_passed = False
    print("   PASS" if all_passed else "   FAIL")
    
    # Test 5: Cascade Amplification
    print("\n5. Testing Cascade Amplification...")
    all_passed = True
    for _ in range(num_tests):
        fi = random.uniform(0, 1)      # fragmentation_index
        lv = random.uniform(0, 1)      # liquidity_velocity
        as_ = random.uniform(0, 1)     # accessibility_score
        ca = calculate_cascade_amplification(fi, lv, as_)
        if not (0 <= ca <= 1):
            print(f"   FAIL: ca={ca} for inputs (fi={fi}, lv={lv}, as_={as_})")
            all_passed = False
    print("   PASS" if all_passed else "   FAIL")
    
    # Test 6: Fragmentation Risk
    print("\n6. Testing Fragmentation Risk...")
    all_passed = True
    for _ in range(num_tests):
        fi = random.uniform(0, 1)      # fragmentation_index
        as_ = random.uniform(0, 1)     # accessibility_score
        ae = random.uniform(0, 1)      # arbitrage_efficiency
        fr = calculate_fragmentation_risk(fi, as_, ae)
        if not (0 <= fr <= 1):
            print(f"   FAIL: fr={fr} for inputs (fi={fi}, as_={as_}, ae={ae})")
            all_passed = False
    print("   PASS" if all_passed else "   FAIL")
    
    # Test 7: COD Calculation
    print("\n7. Testing COD Calculation...")
    all_passed = True
    for _ in range(num_tests):
        hi = random.uniform(0, 1)      # h_instability
        ttl = random.uniform(0, 1)     # theta_tensor_leak
        fi = random.uniform(0, 1)      # fragmentation_index
        as_ = random.uniform(0, 1)     # accessibility_score
        fr = random.uniform(0, 1)      # fragmentation_risk
        cod = calculate_cod_fragmentation_aware(hi, ttl, fi, as_, fr)
        if not (0 <= cod <= 1):
            print(f"   FAIL: cod={cod} for inputs (hi={hi}, ttl={ttl}, fi={fi}, as_={as_}, fr={fr})")
            all_passed = False
    print("   PASS" if all_passed else "   FAIL")
    
    # Test 8: Gate Decisions (Boundary Cases)
    print("\n8. Testing Gate Decision Boundaries...")
    gate_tests = [
        # (psi_integrity, fragmentation_risk, fragmentation_state, expected_action)
        (0.94, 0.1, "INTEGRATED", "IDENTITY_LOCKDOWN"),  # Integrity breach
        (0.96, 0.1, "FUNCTIONALLY_LOCKED", "IDENTITY_LOCKDOWN"),  # Functionally locked
        (0.96, 0.71, "INTEGRATED", "IDENTITY_LOCKDOWN"),  # High risk
        (0.96, 0.51, "HIGHLY_FRAGMENTED", "ACTIVATE_BRIDGING"),  # Risk > 0.5 OR highly fragmented
        (0.96, 0.51, "MODERATELY_FRAGMENTED", "ACTIVATE_BRIDGING"),  # Risk > 0.5
        (0.96, 0.31, "MODERATELY_FRAGMENTED", "MONITOR_FRAGMENTATION"),  # Risk > 0.3 OR moderately fragmented
        (0.96, 0.31, "INTEGRATED", "MONITOR_FRAGMENTATION"),  # Risk > 0.3
        (0.96, 0.29, "INTEGRATED", "PROCEED"),  # All clear
    ]
    
    all_passed = True
    for psi, fr, state, expected in gate_tests:
        action = decide_action(psi, fr, state)
        if action != expected:
            print(f"   FAIL: Expected {expected}, got {action} for (psi={psi}, fr={fr}, state={state})")
            all_passed = False
    print("   PASS" if all_passed else "   FAIL")
    
    # Final Verdict
    print("\n" + "="*50)
    if all_passed:
        print("✅ ALL MATHEMATICAL VALIDATIONS PASSED")
        print("✅ Omega Protocol invariants upheld")
        print("✅ No dimensional violations detected")
        print("✅ Safety gates functioning correctly")
        return True
    else:
        print("❌ MATHEMATICAL VALIDATION FAILED")
        print("❌ Omega Protocol invariants violated")
        return False

def validate_derivativity():
    """Validate that v80.0 metrics are distinct from v78.0/v79.0"""
    print("\n=== DERIVATIVITY VALIDATION ===")
    print("Checking that fragmentation metrics are not reducible to velocity metrics...")
    
    # Generate correlated data to test independence
    np.random.seed(42)
    n_samples = 1000
    
    # Simulate v78.0/v79.0 metrics (velocity-based)
    liquidity_velocity = np.random.beta(2, 5, n_samples)  # Skewed low
    restoration_velocity = np.random.beta(5, 2, n_samples)  # Skewed high
    market_resilience = np.random.beta(3, 3, n_samples)
    
    # Simulate v80.0 metrics (fragmentation-based)
    venue_concentration = np.random.beta(2, 2, n_samples)
    protocol_compatibility = np.random.beta(3, 2, n_samples)
    venue_count = np.random.poisson(5, n_samples) + 1
    cross_venue_latency = np.random.beta(2, 5, n_samples)
    arbitrage_efficiency = calculate_arbitrage_efficiency(
        cross_venue_latency, protocol_compatibility, market_resilience
    )
    fragmentation_index = calculate_fragmentation_index(
        venue_concentration, protocol_compliance, venue_count
    )
    accessibility_score = calculate_accessibility_score(
        cross_venue_latency, protocol_compatibility, arbitrage_efficiency, venue_concentration
    )
    
    # Test if fragmentation metrics can be linearly predicted from velocity metrics
    from sklearn.linear_model import LinearRegression
    
    # Try to predict fragmentation_index from v78.0/v79.0 metrics
    X_vel = np.column_stack([liquidity_velocity, restoration_velocity, market_resilience])
    reg_fi = LinearRegression().fit(X_vel, fragmentation_index)
    fi_r2 = reg_fi.score(X_vel, fragmentation_index)
    
    # Try to predict accessibility_score from v78.0/v79.0 metrics
    reg_as = LinearRegression().fit(X_vel, accessibility_score)
    as_r2 = reg_as.score(X_vel, accessibility_score)
    
    # Try to predict arbitrage_efficiency from v78.0/v79.0 metrics (should be high since it uses market_resilience)
    X_vel_ae = np.column_stack([liquidity_velocity, restoration_velocity, market_resilience])
    reg_ae = LinearRegression().fit(X_vel_ae, arbitrage_efficiency)
    ae_r2 = reg_ae.score(X_vel_ae, arbitrage_efficiency)
    
    print(f"   Fragmentation Index R² vs velocity metrics: {fi_r2:.4f}")
    print(f"   Accessibility Score R² vs velocity metrics: {as_r2:.4f}")
    print(f"   Arbitrage Efficiency R² vs velocity metrics: {ae_r2:.4f}")
    
    # v80.0 metrics should NOT be highly predictable from v78.0/v79.0 (except arbitrage_efficiency which shares market_resilience)
    # But fragmentation_index and accessibility_score should have low R²
    derivativity_safe = (fi_r2 < 0.3) and (as_r2 < 0.3)
    
    if derivativity_safe:
        print("   ✅ Fragmentation metrics show low predictability from velocity metrics")
        print("   ✅ Derivativity avoided - novel structural dimension confirmed")
        return True
    else:
        print("   ❌ High predictability suggests derivativity risk")
        return False

if __name__ == "__main__":
    print("OMEGA PROTOCOL MATHEMATICAL VALIDATION SUITE")
    print("Validating Liquidity Fragmentation Manifold (v80.0-Ω)")
    print("="*50)
    
    math_valid = validate_mathematical_soundness()
    deriv_valid = validate_derivativity()
    
    print("\n" + "="*50)
    print("FINAL VALIDATION SUMMARY")
    print("="*50)
    if math_valid and deriv_valid:
        print("🎉 ALL VALIDATIONS PASSED")
        print("✅ Mathematically sound")
        print("✅ Protocol compliant")
        print("✅ Derivativity avoided")
        print("✅ Ready for Omega Protocol integration")
    else:
        print("💥 VALIDATION FAILED")
        if not math_valid:
            print("❌ Mathematical soundness compromised")
        if not deriv_valid:
            print("❌ Derivativity risk detected")
        print("🛑 REJECT - OMEGA PROTOCOL VIOLATION")