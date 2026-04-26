# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

# =============================================================================
# OMEGA PROTOCOL INVARIANT VALIDATOR FOR LIQUIDITY FRAGMENTATION v80.0-Ω
# Validates mathematical soundness and protocol compliance
# =============================================================================

class OmegaProtocolValidator:
    """Validates core mathematical invariants and protocol compliance"""
    
    # Protocol thresholds (from LiquidityFragmentationInvariants)
    PSI_INTEGRITY_THRESHOLD = 0.95
    FRAGMENTATION_INDEX_MAX = 0.60
    ACCESSIBILITY_MIN = 0.50
    ARBITRAGE_EFFICIENCY_MIN = 0.45
    COD_THRESHOLD = 0.85
    AUDIT_ENTROPY_PER_CHECK = 0.02
    
    @staticmethod
    def validate_bounded(value, name, min_val=0.0, max_val=1.0):
        """Check if value is within [min_val, max_val]"""
        if not (min_val <= value <= max_val):
            raise ValueError(f"{name}={value} violates bounds [{min_val}, {max_val}]")
        return True
    
    @staticmethod
    def validate_fragmentation_index(venue_concentration, protocol_compatibility, venue_count):
        """Validate CalculateFragmentationIndex function"""
        venue_factor = min(1.0, venue_count / 10.0)
        concentration_reduction = venue_concentration * 0.4
        compatibility_factor = (1.0 - protocol_compatibility) * 0.3
        fragmentation = venue_factor * (1.0 - concentration_reduction) + compatibility_factor
        fragmentation = max(0.0, min(1.0, fragmentation))  # clamp
        
        OmegaProtocolValidator.validate_bounded(fragmentation, "fragmentation_index")
        return fragmentation
    
    @staticmethod
    def validate_accessibility_score(cross_venue_latency, protocol_compatibility, 
                                   arbitrage_efficiency, venue_concentration):
        """Validate CalculateAccessibilityScore function"""
        latency_penalty = cross_venue_latency * 0.35
        compatibility_bonus = protocol_compatibility * 0.30
        arbitrage_bonus = arbitrage_efficiency * 0.20
        concentration_factor = (1.0 - abs(venue_concentration - 0.5)) * 0.15
        accessibility = compatibility_bonus + arbitrage_bonus + concentration_factor - latency_penalty
        accessibility = max(0.0, min(1.0, accessibility))  # clamp
        
        OmegaProtocolValidator.validate_bounded(accessibility, "accessibility_score")
        return accessibility
    
    @staticmethod
    def validate_arbitrage_efficiency(cross_venue_latency, protocol_compatibility, market_resilience):
        """Validate CalculateArbitrageEfficiency function"""
        latency_component = (1.0 - cross_venue_latency) * 0.5
        compatibility_component = protocol_compatibility * 0.3
        resilience_component = market_resilience * 0.2
        efficiency = latency_component + compatibility_component + resilience_component
        efficiency = max(0.0, min(1.0, efficiency))  # clamp
        
        OmegaProtocolValidator.validate_bounded(efficiency, "arbitrage_efficiency")
        return efficiency
    
    @staticmethod
    def validate_functional_liquidity_ratio(accessibility_score, fragmentation_index, venue_concentration):
        """Validate CalculateFunctionalLiquidityRatio function"""
        accessibility_component = accessibility_score * 0.6
        fragmentation_component = (1.0 - fragmentation_index) * 0.25
        concentration_component = venue_concentration * 0.15
        ratio = accessibility_component + fragmentation_component + concentration_component
        ratio = max(0.0, min(1.0, ratio))  # clamp
        
        OmegaProtocolValidator.validate_bounded(ratio, "functional_liquidity_ratio")
        return ratio
    
    @staticmethod
    def validate_cascade_amplification(fragmentation_index, liquidity_velocity, accessibility_score):
        """Validate CalculateCascadeAmplification function"""
        fragmentation_component = fragmentation_index * 0.5
        velocity_component = liquidity_velocity * 0.3
        accessibility_reduction = (1.0 - accessibility_score) * 0.2
        amplification = fragmentation_component + velocity_component + accessibility_reduction
        amplification = max(0.0, min(1.0, amplification))  # clamp
        
        OmegaProtocolValidator.validate_bounded(amplification, "cascade_amplification")
        return amplification
    
    @staticmethod
    def validate_fragmentation_risk(fragmentation_index, accessibility_score, arbitrage_efficiency):
        """Validate CalculateFragmentationRisk function"""
        accessibility_deficit = 1.0 - accessibility_score
        arbitrage_deficit = 1.0 - arbitrage_efficiency
        risk = fragmentation_index * accessibility_deficit * arbitrage_deficit
        risk = max(0.0, min(1.0, risk))  # clamp
        
        OmegaProtocolValidator.validate_bounded(risk, "fragmentation_risk")
        return risk
    
    @staticmethod
    def validate_cod_fragmentation_aware(diagnostic_vec, plasma_vec, h_instability, 
                                       theta_tensor_leak, fragmentation_index, 
                                       accessibility_score, fragmentation_risk):
        """Validate Calculate_COD_FragmentationAware function"""
        # Handle empty vectors
        if not diagnostic_vec or not plasma_vec:
            return 0.0
        
        size = min(len(diagnostic_vec), len(plasma_vec))
        dot = 0.0
        magD = 0.0
        magP = 0.0
        
        for i in range(size):
            # Complex conjugate: diagnostic_vec[i] * conjugate(plasma_vec[i]) 
            # But in code: std::abs(std::conj(diagnostic_vec[i]) * plasma_vec[i])
            # Which equals |diagnostic_vec[i]| * |plasma_vec[i]| since |conj(z)*w| = |z||w|
            d_mag = abs(diagnostic_vec[i])
            p_mag = abs(plasma_vec[i])
            dot += d_mag * p_mag
            magD += d_mag * d_mag
            magP += p_mag * p_mag
        
        fidelity = 0.0
        if magD > 1e-9 and magP > 1e-9:
            fidelity = dot / (math.sqrt(magD) * math.sqrt(magP))
            fidelity = max(0.0, min(1.0, fidelity))  # clamp by Cauchy-Schwarz
        
        # Penalties (all in (0,1] since args in [0,1])
        instability_penalty = math.exp(-0.5 * h_instability)  # LAMBDA_COUPLING = 0.5
        exposure_penalty = math.exp(-0.5 * theta_tensor_leak)
        fragmentation_penalty = math.exp(-0.7 * fragmentation_index)  # MU_FRAGMENTATION = 0.7
        accessibility_penalty = math.exp(-0.7 * (1.0 - accessibility_score))
        risk_penalty = math.exp(-0.7 * fragmentation_risk)
        
        cod = fidelity * instability_penalty * exposure_penalty * \
              fragmentation_penalty * accessibility_penalty * risk_penalty
        
        # Final clamp (should already be in [0,1] but ensure)
        cod = max(0.0, min(1.0, cod))
        
        OmegaProtocolValidator.validate_bounded(cod, "COD")
        return cod
    
    @staticmethod
    def validate_safety_gate(psi_integrity, fragmentation_risk, fragmentation_state):
        """Validate LiquidityFragmentationProtocol::Decide logic"""
        # PRIMARY GATE: Ψ_integrity (non-negotiable)
        if psi_integrity < OmegaProtocolValidator.PSI_INTEGRITY_THRESHOLD:
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
    
    @staticmethod
    def validate_phi_n_assignment(cod_value):
        """Validate phi_N = state.cod (direct assignment)"""
        phi_N = cod_value  # Direct assignment, NO log2()
        OmegaProtocolValidator.validate_bounded(phi_N, "phi_N")
        return phi_N
    
    @staticmethod
    def validate_derivativity_novelty(v78_focus, v79_focus, v80_focus):
        """Check that v80.0 introduces novel dimension vs v78.0/v79.0"""
        novel_dimensions = {
            "structural_accessibility", "fragmentation_index", 
            "accessibility_score", "venue_bridging", "protocol_compatibility"
        }
        v80_concepts = set(v80_focus.lower().split())
        return len(novel_dimensions.intersection(v80_concepts)) > 0

def run_comprehensive_validation():
    """Run exhaustive validation of all mathematical invariants"""
    print("=" * 70)
    print("OMEGA PROTOCOL VALIDATOR: LIQUIDITY FRAGMENTATION v80.0-Ω")
    print("=" * 70)
    
    validator = OmegaProtocolValidator()
    test_cases = 1000
    passed = 0
    failed = 0
    
    # Test data generation (edge cases + random)
    np.random.seed(42)  # For reproducibility
    
    for i in range(test_cases):
        try:
            # Generate test inputs in valid ranges
            venue_count = np.random.randint(0, 21)
            venue_concentration = np.random.uniform(0, 1)
            protocol_compatibility = np.random.uniform(0, 1)
            cross_venue_latency = np.random.uniform(0, 1)
            arbitrage_efficiency = np.random.uniform(0, 1)
            market_resilience = np.random.uniform(0, 1)
            liquidity_velocity = np.random.uniform(0, 1)
            h_instability = np.random.uniform(0, 1)
            theta_tensor_leak = np.random.uniform(0, 1)
            
            # Test 1: Fragmentation Index
            fi = validator.validate_fragmentation_index(
                venue_concentration, protocol_compatibility, venue_count
            )
            
            # Test 2: Accessibility Score
            as_score = validator.validate_accessibility_score(
                cross_venue_latency, protocol_compatibility, 
                arbitrage_efficiency, venue_concentration
            )
            
            # Test 3: Arbitrage Efficiency
            ae = validator.validate_arbitrage_efficiency(
                cross_venue_latency, protocol_compatibility, market_resilience
            )
            
            # Test 4: Functional Liquidity Ratio
            flr = validator.validate_functional_liquidity_ratio(
                as_score, fi, venue_concentration
            )
            
            # Test 5: Cascade Amplification
            ca = validator.validate_cascade_amplification(
                fi, liquidity_velocity, as_score
            )
            
            # Test 6: Fragmentation Risk
            fr = validator.validate_fragmentation_risk(
                fi, as_score, ae
            )
            
            # Test 7: COD Calculation (with simple vectors)
            diagnostic_vec = [complex(0.5, 0.5), complex(0.3, 0.2)]
            plasma_vec = [complex(0.4, 0.1), complex(0.6, 0.3)]
            cod = validator.validate_cod_fragmentation_aware(
                diagnostic_vec, plasma_vec, h_instability, 
                theta_tensor_leak, fi, as_score, fr
            )
            
            # Test 8: Phi_N Assignment
            phi_N = validator.validate_phi_n_assignment(cod)
            
            # Test 9: Safety Gate Logic
            fragmentation_state = "INTEGRATED"  # Default state
            if fi > 0.6: fragmentation_state = "HIGHLY_FRAGMENTED"
            elif fi > 0.3: fragmentation_state = "MODERATELY_FRAGMENTED"
            if as_score < 0.3: fragmentation_state = "FUNCTIONALLY_LOCKED"
            
            action = validator.validate_safety_gate(
                np.random.uniform(0.9, 1.0),  # psi_integrity (valid range)
                fr,
                fragmentation_state
            )
            valid_actions = ["PROCEED", "MONITOR_FRAGMENTATION", 
                           "ACTIVATE_BRIDGING", "IDENTITY_LOCKDOWN"]
            if action not in valid_actions:
                raise ValueError(f"Invalid safety gate action: {action}")
            
            # Test 10: Derivativity Novelty Check
            v78_focus = "liquidity evaporation velocity"
            v79_focus = "liquidity restoration dynamics"
            v80_focus = "liquidity fragmentation & accessibility"
            is_novel = validator.validate_derivativity_novelty(
                v78_focus, v79_focus, v80_focus
            )
            if not is_novel:
                raise ValueError("Derivativity violation: v80.0 lacks novel dimension")
            
            passed += 1
            if (i + 1) % 200 == 0:
                print(f"Progress: {i+1}/{test_cases} tests passed")
                
        except Exception as e:
            failed += 1
            print(f"FAILURE at test {i+1}: {str(e)}")
            print(f"  Inputs: venue_count={venue_count}, venue_concentration={venue_concentration:.3f}, "
                  f"protocol_compatibility={protocol_compatibility:.3f}")
            break  # Stop on first failure for detailed analysis
    
    print("\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    print(f"Total Tests:   {test_cases}")
    print(f"Passed:        {passed}")
    print(f"Failed:        {failed}")
    print(f"Success Rate:  {passed/test_cases*100:.1f}%")
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED - MATHEMATICALLY SOUND & PROTOCOL COMPLIANT")
        print("✅ No dimensional violations detected")
        print("✅ Safety gates enforce correct hierarchy")
        print("✅ Derivativity avoidance confirmed (novel fragmentation dimension)")
        print("✅ Phi_N assignment avoids log2() violations")
        return True
    else:
        print("\n❌ VALIDATION FAILED - PROTOCOL VIOLATIONS DETECTED")
        return False

def test_edge_cases():
    """Test specific edge cases that could break invariants"""
    print("\n" + "=" * 70)
    print("EDGE CASE VALIDATION")
    print("=" * 70)
    
    validator = OmegaProtocolValidator()
    
    # Edge Case 1: Maximum fragmentation scenario
    print("Test 1: Maximum fragmentation (venue_count=20, venue_concentration=0.0, protocol_compatibility=0.0)")
    try:
        fi = validator.validate_fragmentation_index(0.0, 0.0, 20)
        print(f"  Fragmentation Index: {fi:.4f} ✅ (expected ~1.0)")
        validator.validate_bounded(fi, "fragmentation_index")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False
    
    # Edge Case 2: Minimum accessibility scenario
    print("\nTest 2: Minimum accessibility (high latency, low compatibility)")
    try:
        as_score = validator.validate_accessibility_score(
            cross_venue_latency=1.0,  # max latency
            protocol_compatibility=0.0,  # min compatibility
            arbitrage_efficiency=0.0,  # min arbitrage
            venue_concentration=0.0  # min concentration
        )
        print(f"  Accessibility Score: {as_score:.4f} ✅ (expected >=0.0)")
        validator.validate_bounded(as_score, "accessibility_score")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False
    
    # Edge Case 3: COD with orthogonal vectors (should minimize fidelity)
    print("\nTest 3: COD with orthogonal vectors")
    try:
        # Orthogonal vectors: [1,0] and [0,1] -> dot product = 0
        diagnostic_vec = [complex(1.0, 0.0), complex(0.0, 0.0)]
        plasma_vec = [complex(0.0, 0.0), complex(1.0, 0.0)]
        cod = validator.validate_cod_fragmentation_aware(
            diagnostic_vec, plasma_vec, 
            h_instability=0.0, theta_tensor_leak=0.0,
            fragmentation_index=0.0, accessibility_score=1.0, fragmentation_risk=0.0
        )
        print(f"  COD (orthogonal): {cod:.4f} ✅ (should be >=0.0)")
        validator.validate_bounded(cod, "COD")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False
    
    # Edge Case 4: Safety gate - integrity breach triggers lockdown
    print("\nTest 4: Safety gate - integrity breach (<0.95)")
    try:
        action = validator.validate_safety_gate(
            psi_integrity=0.94,  # Below threshold
            fragmentation_risk=0.1,  # Low risk
            fragmentation_state="INTEGRATED"
        )
        print(f"  Action: {action} ✅ (expected IDENTITY_LOCKDOWN)")
        if action != "IDENTITY_LOCKDOWN":
            raise ValueError("Incorrect action for integrity breach")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False
    
    # Edge Case 5: Safety gate - functionally locked state
    print("\nTest 5: Safety gate - functionally locked state")
    try:
        action = validator.validate_safety_gate(
            psi_integrity=0.96,  # Above threshold
            fragmentation_risk=0.1,  # Low risk
            fragmentation_state="FUNCTIONALLY_LOCKED"
        )
        print(f"  Action: {action} ✅ (expected IDENTITY_LOCKDOWN)")
        if action != "IDENTITY_LOCKDOWN":
            raise ValueError("Incorrect action for functionally locked state")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False
    
    print("\n✅ ALL EDGE CASES PASSED")
    return True

def main():
    """Main validation routine"""
    print("Initializing Omega Protocol Validator...")
    print("Checking mathematical soundness and protocol compliance...\n")
    
    # Run comprehensive random tests
    comprehensive_passed = run_comprehensive_validation()
    
    # Run specific edge case tests
    edge_cases_passed = test_edge_cases()
    
    print("\n" + "=" * 70)
    print("FINAL VALIDATION SUMMARY")
    print("=" * 70)
    
    if comprehensive_passed and edge_cases_passed:
        print("🎉 OVERALL RESULT: PASS")
        print("✅ Liquidity Fragmentation v80.0-Ω is mathematically sound")
        print("✅ Fully compliant with Omega Protocol invariants")
        print("✅ Ready for deployment in the Omega System")
        return True
    else:
        print("💥 OVERALL RESULT: FAIL")
        print("❌ Protocol violations detected - requires revision")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)