# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import unittest

class TestAFDSMath(unittest.TestCase):
    """Validates mathematical soundness and Omega Protocol compliance of AFDS v3.0 core formulas."""
    
    def test_trust_score_bounds_and_decay(self):
        """Test trust score remains in [0,1] and exhibits correct decay behavior."""
        # Simulate trust manager state
        trust_score = 0.8
        cumulative_stability = 0.0
        last_access = 0.0  # hours ago
        novelty_penalty = 0.0  # non-novel access
        
        # Test decay over time (should decrease)
        normalized_time = 1.0  # 1 hour
        decay_factor = math.exp(-math.log(0.95) * normalized_time)
        expected_score = trust_score * decay_factor - novelty_penalty
        if not novelty_penalty:  # stability bonus applies
            stability_bonus = 0.01 * math.exp(-0.1 * cumulative_stability)
            expected_score += stability_bonus
        expected_score = max(0.0, min(1.0, expected_score))
        
        # Verify bounds
        self.assertGreaterEqual(expected_score, 0.0)
        self.assertLessEqual(expected_score, 1.0)
        
        # Verify decay: score should decrease over time
        self.assertLess(expected_score, trust_score)
        
        # Test novelty penalty
        novelty_penalty = 0.05
        expected_score_novel = trust_score * decay_factor - novelty_penalty
        expected_score_novel = max(0.0, min(1.0, expected_score_novel))
        self.assertLess(expected_score_novel, expected_score)  # novelty reduces trust
        
        # Test stability bonus saturation
        cumulative_stability = 100.0
        stability_bonus = 0.01 * math.exp(-0.1 * cumulative_stability)
        self.assertAlmostEqual(stability_bonus, 0.0, places=5)  # bonus negligible at high stability

    def test_traversal_score_and_asymmetric_threat(self):
        """Test traversal score and phi_Delta calculation."""
        # Test traversal score: 0.6*breadth + 0.4*depth
        breadth = 10  # unique paths
        depth = 5     # max depth
        traversal_score = breadth * 0.6 + depth * 0.4
        self.assertAlmostEqual(traversal_score, 8.0)  # 6.0 + 2.0
        
        # Test asymmetric threat: |breadth-depth|/(breadth+depth)
        phi_delta = abs(breadth - depth) / (breadth + depth)
        self.assertAlmostEqual(phi_delta, 5.0 / 15.0, places=5)  # 1/3 ≈ 0.333
        
        # Test edge cases
        self.assertEqual(CalculateAsymmetricThreat(0, 0), 0.0)  # avoid division by zero
        self.assertEqual(CalculateAsymmetricThreat(5, 0), 1.0)   # pure breadth
        self.assertEqual(CalculateAsymmetricThreat(0, 5), 1.0)   # pure depth
        self.assertEqual(CalculateAsymmetricThreat(5, 5), 0.0)   # balanced

    def test_jitter_probability_bounds(self):
        """Test jitter probability stays in [0,1] and responds correctly to inputs."""
        # Test base case: low score, low mitigation, low phi_Delta
        prob = min(1.0, max(0.0, 
                   (5.0/100.0)**1.5 * 0.5 * (1.0 + 0.1)))
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)
        
        # Test phi_Delta shredding threshold
        self.assertTrue(ApplyAdaptiveJitterShredCondition(0.96))  # should trigger shred
        self.assertFalse(ApplyAdaptiveJitterShredCondition(0.94)) # should not
        
        # Test probability increases with traversal score
        prob_low = (10.0/100.0)**1.5 * 0.5 * 1.1
        prob_high = (50.0/100.0)**1.5 * 0.5 * 1.1
        self.assertLess(prob_low, prob_high)
        
        # Test probability increases with mitigation
        prob_low_mit = (30.0/100.0)**1.5 * 0.3 * 1.1
        prob_high_mit = (30.0/100.0)**1.5 * 0.7 * 1.1
        self.assertLess(prob_low_mit, prob_high_mit)

    def test_topological_impedance_trapezoidal_rule(self):
        """Test impedance calculation matches trapezoidal rule for ∫ gauge dψ."""
        # Simple linear case: gauge = 2*psi, from psi=0 to psi=2
        # Exact integral: ∫ 2ψ dψ = [ψ²]₀² = 4
        log_entries = [
            # (trust_score, phi_Delta) -> (psi, gauge)
            (0.1, 0.5),  # psi0 = ln(0.1) ≈ -2.302, gauge0 = 0.1*0.5=0.05
            (0.2, 0.5),  # psi1 = ln(0.2) ≈ -1.609, gauge1 = 0.2*0.5=0.1
            (0.5, 0.5),  # psi2 = ln(0.5) ≈ -0.693, gauge2 = 0.5*0.5=0.25
            (1.0, 0.5)   # psi3 = ln(1.0)=0,        gauge3 = 1.0*0.5=0.5
        ]
        
        impedance = 0.0
        prev_psi = math.log(log_entries[0][0] + 1e-10)
        prev_gauge = log_entries[0][0] * abs(log_entries[0][1])
        
        for i in range(1, len(log_entries)):
            trust, phi = log_entries[i]
            psi = math.log(trust + 1e-10)
            gauge = trust * abs(phi)
            delta_psi = psi - prev_psi
            impedance += (gauge + prev_gauge) / 2 * delta_psi
            prev_psi, prev_gauge = psi, gauge
        
        # Expected: approximate integral of gauge dψ
        # We know gauge = 0.5 * trust, and dψ = d(ln trust) = d(trust)/trust
        # So ∫ gauge dψ = ∫ 0.5 * trust * (d trust / trust) = 0.5 ∫ d trust = 0.5 * Δtrust
        # Δtrust = 1.0 - 0.1 = 0.9 → expected = 0.5 * 0.9 = 0.45
        self.assertAlmostEqual(impedance, 0.45, places=2)  # trapezoidal approximation

    def test_manifold_curvature_components(self):
        """Test curvature formula uses correct weights and terms."""
        phi_N = 0.7
        phi_Delta = 0.3
        h_imp = 0.2
        XI_N = 0.8
        XI_DELTA = 1.2
        
        curvature = XI_N * phi_N + XI_DELTA * phi_Delta - h_imp
        expected = 0.8*0.7 + 1.2*0.3 - 0.2
        self.assertAlmostEqual(curvature, expected, places=5)
        
        # Verify curvature can be negative (indicating instability)
        curvature_neg = XI_N * 0.1 + XI_DELTA * 0.1 - 0.5
        self.assertLess(curvature_neg, 0.0)

def CalculateAsymmetricThreat(breadth, depth):
    """Helper for test: asymmetric threat calculation."""
    if breadth + depth == 0:
        return 0.0
    return abs(breadth - depth) / (breadth + depth)

def ApplyAdaptiveJitterShredCondition(phi_Delta):
    """Helper for test: checks if phi_Delta triggers shredding (1000ms jitter)."""
    return phi_Delta > 0.95

if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)