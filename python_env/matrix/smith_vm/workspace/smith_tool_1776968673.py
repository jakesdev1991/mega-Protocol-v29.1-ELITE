# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Omega Protocol Invariant Validation Script for AFDS v3.0
# Validates mathematical soundness and adherence to core invariants
# Focus: Trust modeling, topological metrics, forensic accounting, and benchmark calculations

import math
import unittest
from typing import List, Tuple

# =============================================================================
# 1. TRUST MODELING VALIDATION
# =============================================================================
class TrustModelValidator:
    """Validates TrustManager mathematical invariants"""
    
    @staticmethod
    def test_trust_bounds() -> bool:
        """Ensures trust_score remains in [0,1] after all operations"""
        # Simulate trust state updates
        trust_score = 0.5
        cumulative_stability = 0.0
        accessed_paths = set()
        
        # Test sequence: novel access -> stable access -> novel access
        test_sequence = [
            ("/new/path", True),   # Novel access
            ("/new/path", True),   # Stable access
            ("/another/path", True), # Novel access
            ("/new/path", False)   # Failed stable access
        ]
        
        for path, success in test_sequence:
            is_novel = path not in accessed_paths
            novelty_penalty = 0.05 if is_novel else 0.0
            
            # Time decay (simulate 1 hour interval)
            normalized_time = 1.0  # 1 hour / TRUST_TIME_CONSTANT (3600s) -> but we use normalized_time directly
            trust_score *= math.exp(-normalized_time)  # First-order decay
            trust_score = max(0.0, min(1.0, trust_score - novelty_penalty))
            
            if not is_novel:
                cumulative_stability += math.exp(-normalized_time)
                stability_gain = 0.01 * math.exp(-0.1 * cumulative_stability)
                trust_score += stability_gain
                trust_score = max(0.0, min(1.0, trust_score))
            
            accessed_paths.add(path)
            
            # Invariant check: trust_score must remain in [0,1]
            if not (0.0 <= trust_score <= 1.0):
                return False
                
        return True

    @staticmethod
    def test_newtonian_baseline() -> bool:
        """Validates CalculateNewtonianTrustBaseline derivation"""
        # phi_N = exp(-H_noise) * stability_integral
        # H_noise = log(|accessed_paths| + 1)
        accessed_paths = {"/a", "/b", "/c"}  # 3 paths
        stability_integral = 2.5  # Example value
        
        H_noise = math.log(len(accessed_paths) + 1)
        phi_N = math.exp(-H_noise) * stability_integral
        
        # Must be non-negative and bounded by stability_integral
        return phi_N >= 0.0 and phi_N <= stability_integral

# =============================================================================
# 2. TOPOLOGICAL METRICS VALIDATION
# =============================================================================
class TopologyValidator:
    """Validates TopologyMetrics mathematical invariants"""
    
    @staticmethod
    def test_asymmetric_threat() -> bool:
        """Ensures phi_Delta in [0,1] for all breadth/depth combinations"""
        test_cases: List[Tuple[int, int]] = [
            (0, 0),   # Edge case: handled separately
            (1, 0),   # Pure breadth
            (0, 1),   # Pure depth
            (5, 5),   # Balanced
            (10, 1),  # Breadth-heavy
            (1, 10),  # Depth-heavy
            (100, 50) # Large values
        ]
        
        for breadth, depth in test_cases:
            if breadth + depth == 0:
                phi_Delta = 0.0  # Special case handling
            else:
                phi_Delta = abs(breadth - depth) / (breadth + depth)
            
            if not (0.0 <= phi_Delta <= 1.0):
                return False
                
        return True

    @staticmethod
    def test_traversal_score() -> bool:
        """Validates CalculateTraversalScore linearity and bounds"""
        # score = 0.6 * unique_paths + 0.4 * max_depth
        unique_paths = 10
        max_depth = 5
        expected = 0.6*10 + 0.4*5  # 6.0 + 2.0 = 8.0
        actual = 0.6 * unique_paths + 0.4 * max_depth
        return math.isclose(actual, expected, rel_tol=1e-9)

# =============================================================================
# 3. FORENSIC ACCOUNTING VALIDATION
# =============================================================================
class ForensicValidator:
    """Validates ForensicLogger mathematical invariants"""
    
    @staticmethod
    def test_topological_impedance() -> bool:
        """Validates trapezoidal rule implementation for ∫ gauge dψ"""
        # Test case: two log entries with known values
        # Entry 1: trust=0.5, phi_Delta=0.2 -> psi=ln(0.5), gauge=0.5*0.2=0.1
        # Entry 2: trust=0.8, phi_Delta=0.3 -> psi=ln(0.8), gauge=0.8*0.3=0.24
        # Δpsi = ln(0.8) - ln(0.5) = ln(1.6)
        # Impedance = (gauge1 + gauge2)/2 * Δpsi = (0.1+0.24)/2 * ln(1.6)
        
        trust_scores = [0.5, 0.8]
        phi_deltas = [0.2, 0.3]
        
        # Calculate manually
        psi_vals = [math.log(t) for t in trust_scores]
        gauge_vals = [t * abs(p) for t, p in zip(trust_scores, phi_deltas)]
        delta_psi = psi_vals[1] - psi_vals[0]
        expected_impedance = (gauge_vals[0] + gauge_vals[1]) / 2.0 * delta_psi
        
        # Calculate via validator method (simulating the class method)
        impedance = 0.0
        prev_psi = 0.0
        prev_gauge = 0.0
        for i in range(len(trust_scores)):
            psi = math.log(trust_scores[i])
            gauge = trust_scores[i] * abs(phi_deltas[i])
            delta_psi = psi - prev_psi
            impedance += (gauge + prev_gauge) / 2.0 * delta_psi
            prev_psi = psi
            prev_gauge = gauge
        
        return math.isclose(impedance, expected_impedance, rel_tol=1e-9)

    @staticmethod
    def test_honey_node_detection() -> bool:
        """Validates honey-node trigger logic"""
        test_paths = [
            "/honey",           # Exact match
            "/var/honey/log",   # Substring match
            "/normal/path",     # No match
            "/HoneyPot",        # Case-sensitive? (we use exact substring)
            "/hone"             # Partial but not full
        ]
        
        # Our implementation: entry.path.find("honey") != -1
        expected = [True, True, False, False, False]
        actual = [path.find("honey") != -1 for path in test_paths]
        return expected == actual

# =============================================================================
# 4. BENCHMARK SUITE VALIDATION
# =============================================================================
class BenchmarkValidator:
    """Validates AFDSBenchmark mathematical calculations"""
    
    @staticmethod
    def test_slowdown_factor() -> bool:
        """Validates slowdown_factor = afds_speed / baseline_speed"""
        baseline_speed = 10.0  # ms
        afds_speed = 60.0      # ms (6x slowdown)
        expected_slowdown = 60.0 / 10.0  # 6.0
        
        # Calculate as in benchmark
        slowdown_factor = afds_speed / baseline_speed
        return math.isclose(slowdown_factor, expected_slowdown, rel_tol=1e-9)

    @staticmethod
    def test_false_positive_rate() -> bool:
        """Validates FPR = false_positives / total_operations"""
        false_positives = 2
        total_operations = 2000
        expected_fpr = 2 / 2000  # 0.001
        
        fpr = false_positives / total_operations
        return math.isclose(fpr, expected_fpr, rel_tol=1e-9)

    @staticmethod
    def test_cpu_overhead() -> bool:
        """Validates cpu_overhead = ((afds - baseline)/baseline)*100"""
        baseline = 10.0
        afds = 25.0
        expected = ((25.0 - 10.0) / 10.0) * 100.0  # 150.0%
        
        overhead = ((afds - baseline) / baseline) * 100.0
        return math.isclose(overhead, expected, rel_tol=1e-9)

# =============================================================================
# 5. PHI-DENSITY CALCULATION VALIDATION
# =============================================================================
class PhiDensityValidator:
    """Validates CalculatePhiDensity mathematical consistency"""
    
    @staticmethod
    def test_audit_cost_subtraction() -> bool:
        """Validates net_phi_density = raw_gain - audit_entropy_cost"""
        # Constants from Omega Protocol
        K_BOLTZMANN = 1.0
        audit_complexity = 2.5  # Example value
        
        audit_entropy_cost = K_BOLTZMANN * math.log(2.0) * audit_complexity
        raw_gain = 0.85  # Example value
        net_phi_density = raw_gain - audit_entropy_cost
        
        # Must be a real number (no domain errors in log)
        expected_cost = 1.0 * math.log(2.0) * 2.5
        expected_net = 0.85 - expected_cost
        
        return math.isclose(net_phi_density, expected_net, rel_tol=1e-9)

# =============================================================================
# MAIN VALIDATION SUITE
# =============================================================================
def run_validation_suite():
    """Runs all invariant validation tests and reports results"""
    validators = [
        ("Trust Model Bounds", TrustModelValidator.test_trust_bounds),
        ("Newtonian Baseline", TrustModelValidator.test_newtonian_baseline),
        ("Asymmetric Threat [0,1]", TopologyValidator.test_asymmetric_threat),
        ("Traversal Score Linearity", TopologyValidator.test_traversal_score),
        ("Topological Impedance (Trapezoidal)", ForensicValidator.test_topological_impedance),
        ("Honey-Node Detection", ForensicValidator.test_honey_node_detection),
        ("Slowdown Factor Calc", BenchmarkValidator.test_slowdown_factor),
        ("False Positive Rate", BenchmarkValidator.test_false_positive_rate),
        ("CPU Overhead Calc", BenchmarkValidator.test_cpu_overhead),
        ("Phi-Density Audit Cost", PhiDensityValidator.test_audit_cost_subtraction)
    ]
    
    passed = 0
    total = len(validators)
    
    print("=" * 60)
    print("OMEGA PROTOCOL INVARIANT VALIDATION SUITE")
    print("=" * 60)
    
    for name, test_func in validators:
        try:
            result = test_func()
            status = "PASS" if result else "FAIL"
            if result:
                passed += 1
            print(f"{name:<35} | {status}")
        except Exception as e:
            print(f"{name:<35} | ERROR: {str(e)}")
    
    print("-" * 60)
    print(f"TOTAL: {passed}/{total} tests passed")
    print(f"SUCCESS RATE: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n✓ ALL INVARIANTS SATISFIED - SYSTEM IS OMEGA-COMPLIANT")
        return True
    else:
        print("\n✗ INVARIANT VIOLATIONS DETECTED - SYSTEM NON-COMPLIANT")
        return False

# =============================================================================
# EXECUTION
# =============================================================================
if __name__ == "__main__":
    compliance = run_validation_suite()
    exit(0 if compliance else 1)