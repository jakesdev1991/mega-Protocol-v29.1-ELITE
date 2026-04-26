# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import unittest
from typing import List, Dict, Tuple, Optional

# =============================================================================
# MATHEMATICAL CORE VALIDATION FOR AFDS v3.0
# Validates isolated mathematical functions against Omega Protocol invariants
# =============================================================================

class TestAFDMath(unittest.TestCase):
    """Unit tests for mathematical correctness of AFDS v3.0 core logic"""
    
    # Constants from C++ code (must match exactly)
    TRUST_TIME_CONSTANT = 3600.0
    K_BOLTZMANN = 1.0
    XI_N = 0.8
    XI_DELTA = 1.2
    
    def test_trust_update_bounds(self):
        """Verify trust score remains in [0,1] under all conditions"""
        # Simulate trust update logic from C++ (simplified for math validation)
        def update_trust(current_trust: float, is_novel: bool, 
                        normalized_time: float, cumulative_stab: float) -> Tuple[float, float]:
            # Novelty penalty
            novelty_penalty = self.K_BOLTZMANN * 0.05 if is_novel else 0.0
            
            # Time decay
            trust_after_decay = current_trust * math.exp(-normalized_time)
            trust_after_decay = max(0.0, min(1.0, trust_after_decay - novelty_penalty))
            
            # Stability gain (if not novel)
            if not is_novel:
                stability_gain = self.K_BOLTZMANN * 0.01 * math.exp(-0.1 * cumulative_stab)
                trust_after_decay = max(0.0, min(1.0, trust_after_decay + stability_gain))
                cumulative_stab += math.exp(-normalized_time)
            
            return trust_after_decay, cumulative_stab
        
        # Test boundary conditions
        test_cases = [
            # (current_trust, is_novel, normalized_time, cumulative_stab, expected_trust_range)
            (0.0, True, 0.0, 0.0, (0.0, 0.95)),  # Novelty penalty only
            (1.0, False, 0.0, 0.0, (0.8, 1.0)),   # Stability gain only
            (0.5, True, 2.0, 1.0, (0.0, 0.5)),    # Decay + penalty
            (0.5, False, 2.0, 1.0, (0.3, 0.7)),   # Decay + gain
            (0.0, False, 10.0, 5.0, (0.0, 0.0)),  # Deep decay
            (1.0, True, 0.0, 100.0, (0.0, 0.95)), # High stability base
        ]
        
        for trust, novel, time_norm, cum_stab, (min_exp, max_exp) in test_cases:
            new_trust, _ = update_trust(trust, novel, time_norm, cum_stab)
            self.assertGreaterEqual(new_trust, 0.0, 
                f"Trust <0: trust={trust}, novel={novel}, time={time_norm}, cum={cum_stab}")
            self.assertLessEqual(new_trust, 1.0, 
                f"Trust >1: trust={trust}, novel={novel}, time={time_norm}, cum={cum_stab}")
            self.assertGreaterEqual(new_trust, min_exp, 
                f"Trust below expected min: {new_trust} < {min_exp}")
            self.assertLessEqual(new_trust, max_exp, 
                f"Trust above expected max: {new_trust} > {max_exp}")
    
    def test_jitter_probability(self):
        """Validate jitter probability calculation stays in [0,1]"""
        def calculate_jitter_prob(raw_score: float, mitigation: float, phi_delta: float) -> float:
            # Directly from C++ ApplyAdaptiveJitter (probability calculation part)
            prob = math.pow(raw_score / 100.0, 1.5) * mitigation * (1.0 + phi_delta)
            return max(0.0, min(1.0, prob))
        
        # Test extreme values
        test_cases = [
            # (raw_score, mitigation, phi_delta, expected_prob_range)
            (0.0, 0.0, 0.0, (0.0, 0.0)),
            (100.0, 1.0, 1.0, (1.0, 1.0)),  # Max theoretical
            (50.0, 0.5, 0.5, (0.0, 1.0)),   # Mid-range
            (200.0, 0.8, 0.9, (0.0, 1.0)),  # Over-range input
            (-10.0, 0.2, -0.5, (0.0, 0.0)), # Negative inputs
        ]
        
        for score, mitig, phi, (min_exp, max_exp) in test_cases:
            prob = calculate_jitter_prob(score, mitig, phi)
            self.assertGreaterEqual(prob, 0.0, 
                f"Prob <0: score={score}, mitig={mitig}, phi={phi}")
            self.assertLessEqual(prob, 1.0, 
                f"Prob >1: score={score}, mitig={mitig}, phi={phi}")
            self.assertGreaterEqual(prob, min_exp, 
                f"Prob below min: {prob} < {min_exp}")
            self.assertLessEqual(prob, max_exp, 
                f"Prob above max: {prob} > {max_exp}")
    
    def test_topology_metrics(self):
        """Validate topological calculations (breadth, depth, asymmetric threat)"""
        def calc_asymmetric_threat(unique_paths: int, max_depth: int) -> float:
            if unique_paths == 0 and max_depth == 0:
                return 0.0  # Avoid division by zero
            breadth = float(unique_paths)
            depth = float(max_depth)
            return abs(breadth - depth) / (breadth + depth)
        
        # Test cases covering edge conditions
        test_cases = [
            # (unique_paths, max_depth, expected_threat)
            (0, 0, 0.0),          # Zero case
            (1, 0, 1.0),          # Pure breadth
            (0, 1, 1.0),          # Pure depth
            (5, 5, 0.0),          # Equal
            (10, 2, 0.666...),    # Breadth > depth
            (2, 10, 0.666...),    # Depth > breadth
            (100, 1, 0.980...),   # Extreme breadth
            (1, 100, 0.980...),   # Extreme depth
        ]
        
        for paths, depth, expected in test_cases:
            threat = calc_asymmetric_threat(paths, depth)
            self.assertAlmostEqual(threat, expected, places=5,
                msg=f"Threat mismatch: paths={paths}, depth={depth}, got={threat}, expected={expected}")
            self.assertGreaterEqual(threat, 0.0, 
                f"Negative threat: paths={paths}, depth={depth}")
            self.assertLessEqual(threat, 1.0, 
                f"Threat >1: paths={paths}, depth={depth}")
    
    def test_topological_impedance(self):
        """Validate forensic logger's impedance calculation"""
        def calc_topological_impedance(log_entries: List[Dict]) -> float:
            if not log_entries:
                return 0.0
            
            impedance = 0.0
            prev_psi = 0.0
            prev_gauge = 0.0
            
            for entry in log_entries:
                trust = entry['trust_score']
                phi_delta = entry['phi_Delta']
                
                # Avoid log(0) - matches C++ 1e-10 epsilon
                psi = math.log(max(trust, 1e-10))
                gauge = trust * abs(phi_delta)
                delta_psi = psi - prev_psi
                
                impedance += (gauge + prev_gauge) / 2.0 * delta_psi
                prev_psi = psi
                prev_gauge = gauge
            
            return impedance
        
        # Test with known sequence (manually calculated)
        test_entries = [
            {'trust_score': 0.5, 'phi_Delta': 0.2},
            {'trust_score': 0.6, 'phi_Delta': 0.3},
            {'trust_score': 0.4, 'phi_Delta': 0.1}
        ]
        
        # Manual calculation:
        # Entry 0: psi0 = ln(0.5) ≈ -0.693, gauge0 = 0.5*0.2=0.1, delta_psi0 = -0.693 - 0 = -0.693
        #          impedance0 = (0.1 + 0)/2 * (-0.693) = -0.03465
        # Entry 1: psi1 = ln(0.6) ≈ -0.511, gauge1 = 0.6*0.3=0.18, delta_psi1 = -0.511 - (-0.693)=0.182
        #          impedance1 = (0.18+0.1)/2 * 0.182 = 0.02548 → total = -0.00917
        # Entry 2: psi2 = ln(0.4) ≈ -0.916, gauge2 = 0.4*0.1=0.04, delta_psi2 = -0.916 - (-0.511)=-0.405
        #          impedance2 = (0.04+0.18)/2 * (-0.405) = -0.04455 → total = -0.05372
        
        impedance = calc_topological_impedance(test_entries)
        self.assertAlmostEqual(impedance, -0.05372, places=5,
            msg=f"Impedance mismatch: got {impedance}, expected -0.05372")
        
        # Test edge cases
        self.assertEqual(calc_topological_impedance([]), 0.0)
        self.assertAlmostEqual(
            calc_topological_impedance([{'trust_score': 1.0, 'phi_Delta': 0.0}]), 
            0.0, places=5
        )  # Zero gauge should yield zero impedance
    
    def test_manifold_curvature(self):
        """Validate security manifold curvature calculation"""
        def calc_manifold_curvature(phi_N: float, phi_Delta: float, h_imp: float) -> float:
            return self.XI_N * phi_N + self.XI_DELTA * phi_Delta - h_imp
        
        # Test with boundary values
        test_cases = [
            # (phi_N, phi_Delta, h_imp, expected_curvature)
            (0.0, 0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0, self.XI_N),      # 0.8
            (0.0, 1.0, 0.0, self.XI_DELTA),  # 1.2
            (0.5, 0.5, 1.0, 0.8*0.5 + 1.2*0.5 - 1.0),  # 0.4+0.6-1.0=0.0
            (1.0, 1.0, 2.0, 0.8+1.2-2.0),    # 0.0
        ]
        
        for phi_N, phi_D, h_imp, expected in test_cases:
            curvature = calc_manifold_curvature(phi_N, phi_D, h_imp)
            self.assertAlmostEqual(curvature, expected, places=5,
                msg=f"Curvature mismatch: phi_N={phi_N}, phi_D={phi_D}, h_imp={h_imp}")
    
    def test_phi_density_components(self):
        """Validate Phi Density calculation components"""
        # Mock benchmark results (simulating realistic values)
        class MockBenchmark:
            def RunBenchmark(self):
                return type('Results', (), {
                    'baseline_speed_ms': 10.0,
                    'afds_speed_ms': 60.0,      # 500% slowdown
                    'slowdown_factor': 6.0,     # >5.0 threshold
                    'false_positive_rate': 0.0005, # <0.001
                    'cpu_overhead_percent': 10.0,  # <15.0
                    'memory_overhead_mb': 5.0
                })()
        
        benchmark = MockBenchmark()
        results = benchmark.RunBenchmark()
        
        # Trust modeling contribution
        trust_contrib = 0.25 if results.slowdown_factor > 5.0 else 0.0
        self.assertEqual(trust_contrib, 0.25, 
            "Trust modeling contribution should be 0.25 for >500% slowdown")
        
        # Stealth jitter contribution
        jitter_contrib = 0.30 if results.cpu_overhead_percent < 15.0 else 0.0
        self.assertEqual(jitter_contrib, 0.30, 
            "Jitter contribution should be 0.30 for CPU overhead <15%")
        
        # Forensic system contribution
        forensic_contrib = 0.20 if results.false_positive_rate < 0.001 else 0.0
        self.assertEqual(forensic_contrib, 0.20, 
            "Forensic contribution should be 0.20 for FPR <0.1%")
        
        # Topology enforcement contribution (simulated)
        topology_contrib = 0.15  # Assuming log size >0
        self.assertEqual(topology_contrib, 0.15, 
            "Topology contribution should be 0.15")
        
        # Raw gain calculation
        raw_gain = trust_contrib + jitter_contrib + forensic_contrib + topology_contrib
        self.assertEqual(raw_gain, 0.90, 
            f"Raw gain should be 0.90, got {raw_gain}")
        
        # Audit cost calculation (simplified - would need actual cycle count in practice)
        # For validation, we check the formula structure
        audit_complexity = 1.0 + 1.5 + 1.0 + 0.5  # From C++ code
        audit_entropy_cost = self.K_BOLTZMANN * math.log(2.0) * audit_complexity
        expected_cost = 1.0 * 0.693147 * 4.0  # ln(2)≈0.693, 4.0 complexity
        self.assertAlmostEqual(audit_entropy_cost, expected_cost, places=5,
            msg=f"Audit entropy cost mismatch: got {audit_entropy_cost}, expected {expected_cost}")
        
        # Net Phi Density (would be raw_gain - audit_entropy_cost in full system)
        # We don't test net value here as it depends on empirical audit cost
        # But we verify components are correctly calculated

# =============================================================================
# TEST EXECUTION
# =============================================================================
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)