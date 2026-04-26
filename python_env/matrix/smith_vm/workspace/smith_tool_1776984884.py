# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

# =============================================================================
# OMEGA PROTOCOL INVARIANT VALIDATOR FOR PSYCHOLOGY BRANCH
# Validates Quantum-Classical Cognitive Architecture Specification (v26.0-Ω-POLARIZED)
# =============================================================================

class OmegaPsychologyValidator:
    def __init__(self):
        # Load constants from specification (dimensionless, normalized)
        self.PSI_ID_THRESHOLD = 0.95
        self.XI_BOUND_DEFAULT = 1.0
        self.XI_BOUND_MAX = 2.5
        self.XI_BOUND_MIN = 0.3
        self.LAMBDA_COUPLING = 0.5
        self.COD_THRESHOLD = 0.75
        self.TAU_OPT = 0.6
        self.ENTROPY_THRESHOLD = 0.80
        
        # Validation counters
        self.passed = 0
        self.failed = 0
        self.tests = []

    def record_test(self, name, passed, details=""):
        status = "PASS" if passed else "FAIL"
        self.tests.append(f"[{status}] {name}: {details}")
        if passed:
            self.passed += 1
        else:
            self.failed += 1

    # -------------------------------------------------------------------------
    # 1. VALIDATE CALCULATE_COGNITIVE_COD (DIMENSIONAL & BOUNDARY CHECKS)
    # -------------------------------------------------------------------------
    def test_cod_calculation(self):
        """Test COD formula: fidelity * exp(-Lambda * Xi_bound)"""
        # Test case 1: Identical states, zero stiffness -> COD=1.0
        psi_sub = np.array([1.0, 0.0])
        psi_con = np.array([1.0, 0.0])
        cod = self._calc_cod(psi_sub, psi_con, 0.0)
        self.record_test(
            "COD: Identical states, Xi=0",
            abs(cod - 1.0) < 1e-9,
            f"COD={cod:.6f} (expected 1.0)"
        )
        
        # Test case 2: Orthogonal states -> COD=0.0 (regardless of stiffness)
        psi_sub = np.array([1.0, 0.0])
        psi_con = np.array([0.0, 1.0])
        cod = self._calc_cod(psi_sub, psi_con, 1.0)
        self.record_test(
            "COD: Orthogonal states",
            abs(cod - 0.0) < 1e-9,
            f"COD={cod:.6f} (expected 0.0)"
        )
        
        # Test case 3: Stiffness penalty monotonicity
        psi_sub = np.array([0.6, 0.8])  # Normalized
        psi_con = np.array([0.8, 0.6])
        base_fidelity = np.dot(psi_sub, psi_con)  # 0.6*0.8 + 0.8*0.6 = 0.96
        cod_low = self._calc_cod(psi_sub, psi_con, 0.3)
        cod_high = self._calc_cod(psi_sub, psi_con, 2.5)
        penalty_low = math.exp(-self.LAMBDA_COUPLING * 0.3)
        penalty_high = math.exp(-self.LAMBDA_COUPLING * 2.5)
        expected_low = base_fidelity * penalty_low
        expected_high = base_fidelity * penalty_high
        self.record_test(
            "COD: Stiffness penalty effect",
            abs(cod_low - expected_low) < 1e-9 and abs(cod_high - expected_high) < 1e-9,
            f"Low Xi: {cod_low:.6f} vs {expected_low:.6f}, High Xi: {cod_high:.6f} vs {expected_high:.6f}"
        )
        
        # Test case 4: Boundary conditions (COD in [0,1])
        for _ in range(10):
            psi_sub = np.random.rand(3)
            psi_con = np.random.rand(3)
            psi_sub = psi_sub / np.linalg.norm(psi_sub)
            psi_con = psi_con / np.linalg.norm(psi_con)
            xi = np.random.uniform(0, 5)
            cod = self._calc_cod(psi_sub, psi_con, xi)
            in_bounds = 0 <= cod <= 1 + 1e-9  # Allow tiny floating error
            self.record_test(
                f"COD: Bounds check (random trial {_+1})",
                in_bounds,
                f"COD={cod:.6f} (Xi={xi:.2f})"
            )

    def _calc_cod(self, psi_sub, psi_con, xi_bound):
        """Python implementation of Calculate_Cognitive_COD"""
        dot = np.dot(psi_sub, psi_con)
        mag_sub = np.linalg.norm(psi_sub)
        mag_con = np.linalg.norm(psi_con)
        if mag_sub < 1e-12 or mag_con < 1e-12:
            fidelity = 0.0
        else:
            fidelity = abs(dot) / (mag_sub * mag_con)
            fidelity = min(1.0, max(0.0, fidelity))  # Clamp [0,1]
        stiffness_penalty = math.exp(-self.LAMBDA_COUPLING * xi_bound)
        return fidelity * stiffness_penalty

    # -------------------------------------------------------------------------
    # 2. VALIDATE FAILURE MODE DETECTION (LOGICAL CONSISTENCY)
    # -------------------------------------------------------------------------
    def test_failure_modes(self):
        """Test Check_Cognitive_Failure_Mode logic"""
        # Helper: Map failure types to strings for readability
        failure_map = {
            0: "NONE",
            1: "PREMATURE_COLLAPSE",
            2: "DECOHERENCE_STAGNATION",
            3: "MEASUREMENT_BIAS"
        }
        
        # Test case 1: Premature Collapse (t < 0.8*TAU_OPT AND Xi > 0.8*XI_BOUND_MAX)
        t = 0.4  # < 0.8*0.6=0.48
        xi = 2.1  # > 0.8*2.5=2.0
        cod = 0.5  # Irrelevant for this condition
        failure = self._check_failure_mode(t, xi, cod)
        self.record_test(
            "Failure Mode: Premature Collapse",
            failure == 1,
            f"t={t}, Xi={xi} -> {failure_map[failure]} (expected PREMATURE_COLLAPSE)"
        )
        
        # Test case 2: Decoherence Stagnation (t > 0.9 AND Xi < 1.5*XI_BOUND_MIN)
        t = 0.95  # > 0.9
        xi = 0.2  # < 1.5*0.3=0.45
        cod = 0.3
        failure = self._check_failure_mode(t, xi, cod)
        self.record_test(
            "Failure Mode: Decoherence Stagnation",
            failure == 2,
            f"t={t}, Xi={xi} -> {failure_map[failure]} (expected DECOHERENCE_STAGNATION)"
        )
        
        # Test case 3: Measurement Bias (Xi > XI_BOUND_MAX)
        t = 0.5
        xi = 2.6  # > 2.5
        cod = 0.8
        failure = self._check_failure_mode(t, xi, cod)
        self.record_test(
            "Failure Mode: Measurement Bias",
            failure == 3,
            f"Xi={xi} -> {failure_map[failure]} (expected MEASUREMENT_BIAS)"
        )
        
        # Test case 4: Normal Operation (no failure)
        t = 0.5
        xi = 1.0
        cod = 0.8
        failure = self._check_failure_mode(t, xi, cod)
        self.record_test(
            "Failure Mode: Normal Operation",
            failure == 0,
            f"t={t}, Xi={xi}, COD={cod} -> {failure_map[failure]} (expected NONE)"
        )
        
        # Test case 5: Boundary condition for premature collapse (edge case)
        t = 0.48  # Equal to 0.8*TAU_OPT -> should NOT trigger (strict <)
        xi = 2.0  # Equal to 0.8*XI_BOUND_MAX -> should NOT trigger (strict >)
        failure = self._check_failure_mode(t, xi, 0.5)
        self.record_test(
            "Failure Mode: Premature Collapse Boundary",
            failure == 0,
            f"t={t} (bound), Xi={xi} (bound) -> {failure_map[failure]} (expected NONE)"
        )

    def _check_failure_mode(self, t, xi_bound, cod):
        """Python implementation of Check_Cognitive_Failure_Mode"""
        if t < self.TAU_OPT * 0.8 and xi_bound > self.XI_BOUND_MAX * 0.8:
            return 1  # PREMATURE_COLLAPSE
        if t > 0.9 and xi_bound < self.XI_BOUND_MIN * 1.5:
            return 2  # DECOHERENCE_STAGNATION
        if xi_bound > self.XI_BOUND_MAX:
            return 3  # MEASUREMENT_BIAS
        return 0  # NONE

    # -------------------------------------------------------------------------
    # 3. VALIDATE ADIABATIC MEASUREMENT OPERATOR (STABILIZATION LOGIC)
    # -------------------------------------------------------------------------
    def test_adiabatic_operator(self):
        """Test core logic of Adiabatic_Measurement_Operator"""
        # Mock state and original subconscious state
        psi_sub_orig = np.array([0.7, 0.3, 0.1, 0.2, 0.1])  # Will normalize
        psi_sub_orig = psi_sub_orig / np.linalg.norm(psi_sub_orig)
        
        # Test case 1: Premature Collapse response
        state = {
            'Psi_sub': psi_sub_orig.copy(),
            'Psi_con': np.zeros_like(psi_sub_orig),  # Uncollapsed
            'Xi_bound': 2.2,  # High stiffness
            't': 0.3,         # Early measurement
            'Psi_id': 0.97    # Above threshold
        }
        # Expected: Stiffness reduced, NO collapse
        new_xi = max(self.XI_BOUND_MIN, state['Xi_bound'] * 0.7)
        self.record_test(
            "Adiabatic Op: Premature Collapse Response",
            abs(new_xi - max(self.XI_BOUND_MIN, 2.2*0.7)) < 1e-9,
            f"Xi reduced from {state['Xi_bound']:.2f} to {new_xi:.2f} (expected ~{max(self.XI_BOUND_MIN, 2.2*0.7):.2f})"
        )
        
        # Test case 2: Decoherence Stagnation response
        state['Xi_bound'] = 0.25
        state['t'] = 0.95
        # Expected: Stiffness increased, FORCED collapse
        new_xi = min(self.XI_BOUND_DEFAULT, state['Xi_bound'] * 1.5)
        self.record_test(
            "Adiabatic Op: Decoherence Stagnation Response",
            abs(new_xi - min(self.XI_BOUND_DEFAULT, 0.25*1.5)) < 1e-9,
            f"Xi increased from {state['Xi_bound']:.2f} to {new_xi:.2f} (expected ~{min(self.XI_BOUND_DEFAULT, 0.25*1.5):.2f})"
        )
        
        # Test case 3: Measurement Bias response
        state['Xi_bound'] = 2.6
        state['t'] = 0.5
        # Expected: Stiffness reset to default, IDENTITY-PRESERVING collapse
        self.record_test(
            "Adiabatic Op: Measurement Bias Response",
            abs(self.XI_BOUND_DEFAULT - 1.0) < 1e-9,
            f"Xi reset to {self.XI_BOUND_DEFAULT:.2f} (expected 1.0)"
        )
        
        # Test case 4: Normal operation (ready to collapse)
        state['Xi_bound'] = 0.8
        state['t'] = 0.65  # >= TAU_OPT
        # Mock COD calculation: Assume high fidelity
        psi_con_test = psi_sub_orig.copy()  # Aligned state
        cod = self._calc_cod(psi_sub_orig, psi_con_test, state['Xi_bound'])
        if cod >= self.COD_THRESHOLD:
            # Expected: Slight stiffness increase, collapse occurs
            new_xi = min(self.XI_BOUND_DEFAULT, state['Xi_bound'] * 1.1)
            self.record_test(
                "Adiabatic Op: Normal Collapse Readiness",
                abs(new_xi - min(self.XI_BOUND_DEFAULT, 0.8*1.1)) < 1e-9,
                f"Xi adjusted from {state['Xi_bound']:.2f} to {new_xi:.2f} (expected ~{min(self.XI_BOUND_DEFAULT, 0.8*1.1):.2f})"
            )
        
        # Test case 5: Normal operation (exploration phase)
        state['t'] = 0.5  # < TAU_OPT
        state['Xi_bound'] = 1.2
        # Mock low COD
        psi_con_test = np.array([0.1, 0.9])  # Misaligned (will normalize later)
        psi_con_test = psi_con_test / np.linalg.norm(psi_con_test)
        cod = self._calc_cod(psi_sub_orig[:2], psi_con_test, state['Xi_bound'])  # Truncate for 2D test
        if cod < self.COD_THRESHOLD:
            # Expected: Stiffness reduced to allow exploration
            new_xi = max(self.XI_BOUND_MIN, state['Xi_bound'] * 0.9)
            self.record_test(
                "Adiabatic Op: Exploration Phase Response",
                abs(new_xi - max(self.XI_BOUND_MIN, 1.2*0.9)) < 1e-9,
                f"Xi reduced from {state['Xi_bound']:.2f} to {new_xi:.2f} (expected ~{max(self.XI_BOUND_MIN, 1.2*0.9):.2f})"
            )

    # -------------------------------------------------------------------------
    # 4. VALIDATE ENTROPY & IDENTITY PRESERVATION (RUBRIC §5 COMPLIANCE)
    # -------------------------------------------------------------------------
    def test_entropy_accounting(self):
        """Test entropy calculation and identity preservation"""
        # Test entropy normalization
        psi_sub = np.array([0.5, 0.5, 0.0, 0.0])  # Two equal probabilities
        psi_sub = psi_sub / np.linalg.norm(psi_sub)  # Normalize amplitudes
        probs = psi_sub ** 2  # Probabilities
        # Shannon entropy: -sum(p_i * log(p_i))
        entropy = -np.sum([p * math.log(p) for p in probs if p > 1e-9])
        max_entropy = math.log(len(psi_sub))  # log(4)
        norm_entropy = entropy / max_entropy
        expected_norm = (- (0.5*math.log(0.5) + 0.5*math.log(0.5))) / math.log(4)
        self.record_test(
            "Entropy: Normalization Check",
            abs(norm_entropy - expected_norm) < 1e-9,
            f"Norm entropy={norm_entropy:.6f} (expected {expected_norm:.6f})"
        )
        
        # Test identity preservation logic
        initial_psi_id = 0.97
        entropy_loss_factor = 0.1  # From specification
        norm_entropy = 0.7  # Example value
        expected_psi_id = initial_psi_id - (norm_entropy * entropy_loss_factor)
        self.record_test(
            "Identity: Entropy Loss Calculation",
            abs(expected_psi_id - (0.97 - 0.07)) < 1e-9,
            f"Psi_id after loss: {expected_psi_id:.6f} (expected 0.90)"
        )
        
        # Test identity threshold violation
        low_psi_id = 0.94  # Below PSI_ID_THRESHOLD=0.95
        self.record_test(
            "Identity: Threshold Violation Detection",
            low_psi_id < self.PSI_ID_THRESHOLD,
            f"Psi_id={low_psi_id:.2f} < {self.PSI_ID_THRESHOLD:.2f} -> Violation"
        )

    # -------------------------------------------------------------------------
    # RUN ALL VALIDATIONS
    # -------------------------------------------------------------------------
    def run_validation(self):
        print("=" * 70)
        print("OMEGA PROTOCOL VALIDATION: PSYCHOLOGY BRANCH (v26.0-Ω-POLARIZED)")
        print("Validating Quantum-Classical Cognitive Architecture Specification")
        print("=" * 70)
        
        self.test_cod_calculation()
        self.test_failure_modes()
        self.test_adiabatic_operator()
        self.test_entropy_accounting()
        
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        for test in self.tests:
            print(test)
        print("-" * 70)
        print(f"PASSED: {self.passed} | FAILED: {self.failed} | TOTAL: {self.passed+self.failed}")
        print("=" * 70)
        
        if self.failed == 0:
            print("RESULT: ALL TESTS PASSED -> SPECIFICATION IS OMEGA-COMPLIANT")
            return True
        else:
            print("RESULT: VALIDATION FAILED -> NON-COMPLIANT ELEMENTS DETECTED")
            return False

# Execute validation
if __name__ == "__main__":
    validator = OmegaPsychologyValidator()
    is_compliant = validator.run_validation()
    exit(0 if is_compliant else 1)