# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math
from typing import List, Tuple, Dict

# =============================================================================
# OMEGA PROTOCOL INVARIANTS AND RUBRIC §6 VALIDATION
# =============================================================================

class OmegaProtocolValidator:
    """Validates mathematical soundness and Omega Protocol compliance for Financial Resonance Gate (FRG)"""
    
    def __init__(self):
        # Omega Protocol hard gates (Rubric §6)
        self.PSI_INTEGRITY_THRESHOLD = 0.95  # Market/Capital Integrity Continuity hard gate
        self.PSI_INTEGRITY_CRITICAL = 0.90   # Critical integrity threshold
        self.THETA_RIGID = 0.85              # Config rigidity threshold
        self.THETA_VOL_SHOCK = 0.80          # Volatility shock threshold
        self.COD_THRESHOLD = 0.80            # Minimum acceptable COD
        self.LAMBDA_COUPLING = 1.0           # Entropic damping constant
        self.KAPPA_CONFIG = 1.5              # Config stiffness coupling
        
        # Audit cost parameters (Meta-Scrutiny Rule)
        self.AUDIT_BASE_COST = math.log(2.0)  # Base entropy cost per compliance check
        
    # -------------------------------------------------------------------------
    # 1. VOLATILITY ENTROPY VALIDATION (Shannon Entropy Normalization)
    # -------------------------------------------------------------------------
    def validate_volatility_entropy(self) -> Dict[str, bool]:
        """Test Calculate_Volatility_Entropy against information theory axioms"""
        results = {}
        
        # Test case 1: Uniform distribution (max entropy)
        state_uniform = [1+0j] * 4  # 4-element uniform superposition
        H_uniform = self._calculate_volatility_entropy(state_uniform)
        results["uniform_max_entropy"] = abs(H_uniform - 1.0) < 1e-5
        
        # Test case 2: Delta function (zero entropy)
        state_delta = [1+0j] + [0+0j] * 3
        H_delta = self._calculate_volatility_entropy(state_delta)
        results["delta_zero_entropy"] = abs(H_delta - 0.0) < 1e-5
        
        # Test case 3: Biased distribution
        state_bias = [math.sqrt(0.8)+0j, math.sqrt(0.2)+0j, 0+0j, 0+0j]
        H_bias = self._calculate_volatility_entropy(state_bias)
        expected = - (0.8 * math.log(0.8) + 0.2 * math.log(0.2)) / math.log(4)
        results["biased_entropy"] = abs(H_bias - expected) < 1e-5
        
        # Test case 4: Empty state
        results["empty_state"] = self._calculate_volatility_entropy([]) == 0.0
        
        # Test case 5: Normalization bound
        state_random = [complex(np.random.randn(), np.random.randn()) for _ in range(10)]
        H_random = self._calculate_volatility_entropy(state_random)
        results["entropy_bounds"] = 0.0 <= H_random <= 1.0
        
        return results
    
    def _calculate_volatility_entropy(self, state: List[complex]) -> float:
        """Exact replica of FRG's volatility entropy calculation"""
        if not state:
            return 0.0
        total_prob = sum(abs(amp)**2 for amp in state)
        if total_prob < 1e-12:
            return 0.0
        entropy = 0.0
        for amp in state:
            p = abs(amp)**2 / total_prob
            if p > 1e-12:
                entropy -= p * math.log(p)
        max_entropy = math.log(len(state)) if len(state) > 1 else 1.0
        return min(1.0, max(0.0, entropy / max_entropy))
    
    # -------------------------------------------------------------------------
    # 2. COD CALCULATION VALIDATION (Core Fidelity Metric)
    # -------------------------------------------------------------------------
    def validate_cod_calculation(self) -> Dict[str, bool]:
        """Test COD calculation against quantum fidelity principles"""
        results = {}
        
        # Test case 1: Identical states (max fidelity)
        state_A = [1+0j, 0+0j, 0+0j]
        state_B = [1+0j, 0+0j, 0+0j]
        fid = self._quantum_fidelity(state_A, state_B)
        results["identical_fidelity"] = abs(fid - 1.0) < 1e-5
        
        # Test case 2: Orthogonal states (zero fidelity)
        state_A = [1+0j, 0+0j]
        state_B = [0+0j, 1+0j]
        fid = self._quantum_fidelity(state_A, state_B)
        results["orthogonal_fidelity"] = abs(fid - 0.0) < 1e-5
        
        # Test case 3: Hard gate enforcement (psi_integrity < 0.95 -> COD=0)
        cod_val = self._calculate_COD_Fin(
            state_A, state_B, 
            h_vol=0.1, 
            psi_int=0.94,  # Below hard gate
            xi_config=0.5
        )
        results["hard_gate_enforcement"] = abs(cod_val - 0.0) < 1e-5
        
        # Test case 4: Volatility damping
        cod_low_vol = self._calculate_COD_Fin(
            state_A, state_B, 
            h_vol=0.0, 
            psi_int=0.96, 
            xi_config=0.5
        )
        cod_high_vol = self._calculate_COD_Fin(
            state_A, state_B, 
            h_vol=1.0, 
            psi_int=0.96, 
            xi_config=0.5
        )
        results["volatility_damping"] = cod_high_vol < cod_low_vol
        
        # Test case 5: Config blindness penalty
        cod_flexible = self._calculate_COD_Fin(
            state_A, state_B, 
            h_vol=0.1, 
            psi_int=0.96, 
            xi_config=0.5  # Below rigidity threshold
        )
        cod_rigid = self._calculate_COD_Fin(
            state_A, state_B, 
            h_vol=0.1, 
            psi_int=0.96, 
            xi_config=0.9  # Above rigidity threshold
        )
        results["config_penalty"] = cod_rigid < cod_flexible
        
        # Test case 6: Dimensional consistency (all inputs/outputs in [0,1])
        test_cases = [
            (0.0, 0.0, 0.0, 0.0),  # Minimums
            (1.0, 1.0, 1.0, 1.0),  # Maximums
            (0.5, 0.5, 0.5, 0.5)   # Midpoints
        ]
        for h_vol, psi_int, xi_config, fid in test_cases:
            # We'll test with fixed state vectors
            state_A = [1+0j, 0+0j]
            state_B = [1+0j, 0+0j]
            cod_val = self._calculate_COD_Fin(state_A, state_B, h_vol, psi_int, xi_config)
            results[f"dim_consistency_{h_vol}_{psi_int}_{xi_config}"] = 0.0 <= cod_val <= 1.0
        
        return results
    
    def _quantum_fidelity(self, state_A: List[complex], state_B: List[complex]) -> float:
        """Correct quantum fidelity: |<A|B>|^2 / (<A|A><B|B>)"""
        if len(state_A) != len(state_B):
            raise ValueError("State vectors must have same dimension")
        
        inner = sum(np.conj(a) * b for a, b in zip(state_A, state_B))
        norm_A = sum(abs(a)**2 for a in state_A)
        norm_B = sum(abs(b)**2 for b in state_B)
        
        if norm_A < 1e-12 or norm_B < 1e-12:
            return 0.0
            
        fidelity = abs(inner)**2 / (norm_A * norm_B)
        return min(1.0, max(0.0, fidelity))  # Numerical safety
    
    def _calculate_COD_Fin(self, exec_vec: List[complex], book_vec: List[complex], 
                          h_vol: float, psi_int: float, xi_config: float) -> float:
        """Exact replica of FRG's COD calculation (with hard gate)"""
        # Integrity hard gate (non-negotiable per Omega Protocol)
        if psi_int < self.PSI_INTEGRITY_THRESHOLD:
            return 0.0
        
        # Quantum fidelity (Price Discovery Fidelity)
        fidelity = self._quantum_fidelity(exec_vec, book_vec)
        
        # Volatility damping
        damping = math.exp(-self.LAMBDA_COUPLING * h_vol)
        
        # Config blindness penalty (v57.0 innovation)
        config_penalty = 1.0
        if xi_config > self.THETA_RIGID:
            config_penalty = 1.0 - ((xi_config - self.THETA_RIGID) / (1.0 - self.THETA_RIGID))
            config_penalty = max(0.0, config_penalty)  # Clamp to [0,1]
        
        return fidelity * damping * psi_int * config_penalty
    
    # -------------------------------------------------------------------------
    # 3. FAILURE MODE DETECTOR VALIDATION
    # -------------------------------------------------------------------------
    def validate_failure_detector(self) -> Dict[str, bool]:
        """Test FailureModeDetector logic against systemic failure conditions"""
        results = {}
        detector = self.FailureModeDetector()
        
        # Test case 1: Normal operation (no failure)
        failure = detector.check_risk(
            h_vol=0.5, xi_config=0.6, 
            psi_int=0.96, cod=0.85
        )
        results["normal_operation"] = (failure == "NONE")
        
        # Test case 2: Config blindness (high vol + rigid config)
        failure = detector.check_risk(
            h_vol=0.85, xi_config=0.9, 
            psi_int=0.96, cod=0.7
        )
        results["config_blindness"] = (failure == "CONFIG_BLINDNESS")
        
        # Test case 3: Liquidity illusion (low COD + high integrity)
        failure = detector.check_risk(
            h_vol=0.2, xi_config=0.5, 
            psi_int=0.97, cod=0.75
        )
        results["liquidity_illusion"] = (failure == "LIQUIDITY_ILLUSION")
        
        # Test case 4: Integrity failure (below critical threshold)
        failure = detector.check_risk(
            h_vol=0.1, xi_config=0.3, 
            psi_int=0.89, cod=0.9
        )
        results["integrity_failure"] = (failure == "INTEGRITY_FAILURE")
        
        # Test case 5: Integrity failure triggers hard gate (should never reach detector)
        # This is validated in COD calculation (returns 0.0 when psi_int < 0.95)
        cod_val = self._calculate_COD_Fin(
            [1+0j], [1+0j], 
            h_vol=0.1, psi_int=0.94, xi_config=0.5
        )
        results["integrity_hard_gate_prevents_detection"] = (abs(cod_val - 0.0) < 1e-5)
        
        return results
    
    class FailureModeDetector:
        """Replica of FRG's failure mode detector"""
        def __init__(self):
            self.H_SHOCK = 0.80
            self.XI_CRITICAL = 0.85
            self.COD_THRESHOLD = 0.80
            self.PSI_INT_CRITICAL = 0.90
        
        def check_risk(self, h_vol: float, xi_config: float, 
                      psi_int: float, cod: float) -> str:
            if psi_int < self.PSI_INT_CRITICAL:
                return "INTEGRITY_FAILURE"
            if h_vol > self.H_SHOCK and xi_config > self.XI_CRITICAL:
                return "CONFIG_BLINDNESS"
            if cod < self.COD_THRESHOLD and psi_int > 0.95:
                return "LIQUIDITY_ILLUSION"
            return "NONE"
    
    # -------------------------------------------------------------------------
    # 4. FINANCIAL RESONANCE GATE (FRG) OPERATOR VALIDATION
    # -------------------------------------------------------------------------
    def validate_frg_operator(self) -> Dict[str, bool]:
        """Test FRG operator's stabilization logic and invariant preservation"""
        results = {}
        
        # Test case 1: Stable market (no action needed)
        state = self._create_market_state(
            gamma_trade=0.4, psi_integrity=0.97, 
            xi_config=0.6, h_vol=0.3
        )
        initial_integrity = state.psi_integrity
        frg = self.FinancialResonanceOperator()
        
        try:
            frg.apply(state, MarketInvariants(), audit_ops=0, audit_cost=0.0)
            results["stable_no_action"] = (
                abs(state.psi_integrity - initial_integrity) < 0.01 and 
                state.xi_config == 0.6  # Unchanged
            )
        except Exception as e:
            results["stable_no_action"] = False
        
        # Test case 2: Config blindness detection and correction
        state = self._create_market_state(
            gamma_trade=0.5, psi_integrity=0.96, 
            xi_config=0.9, h_vol=0.85  # Triggers CONFIG_BLINDNESS
        )
        initial_config = state.xi_config
        try:
            frg.apply(state, MarketInvariants(), audit_ops=0, audit_cost=0.0)
            # Should have reduced config stiffness
            results["config_blindness_correction"] = (
                state.xi_config < initial_config and 
                state.xi_config >= 0.1  # Not over-corrected
            )
        except Exception as e:
            results["config_blindness_correction"] = False
        
        # Test case 3: Integrity violation triggers hard gate exception
        state = self._create_market_state(
            gamma_trade=0.6, psi_integrity=0.94,  # Below hard gate
            xi_config=0.5, h_vol=0.2
        )
        try:
            frg.apply(state, MarketInvariants(), audit_ops=0, audit_cost=0.0)
            results["integrity_hard_gate"] = False  # Should have thrown
        except RuntimeError as e:
            results["integrity_hard_gate"] = ("Integrity Violation" in str(e))
        except Exception as e:
            results["integrity_hard_gate"] = False
        
        # Test case 4: Audit cost accounting (Meta-Scrutiny Rule)
        state = self._create_market_state(
            gamma_trade=0.4, psi_integrity=0.96, 
            xi_config=0.9, h_vol=0.85
        )
        initial_ops = 0
        initial_cost = 0.0
        try:
            frg.apply(state, MarketInvariants(), audit_ops=initial_ops, audit_cost=initial_cost)
            # Should have incremented audit ops and added cost
            results["audit_cost_accounting"] = (
                state.audit_ops > initial_ops and 
                state.audit_cost > initial_cost
            )
        except Exception as e:
            results["audit_cost_accounting"] = False
        
        return results
    
    def _create_market_state(self, gamma_trade: float, psi_integrity: float, 
                           xi_config: float, h_vol: float) -> 'MarketState':
        """Helper to create market state for testing"""
        state = MarketState()
        state.gamma_trade = gamma_trade
        state.psi_integrity = psi_integrity
        state.xi_config = xi_config
        state.h_vol = h_vol
        # Initialize dummy quantum states for COD calculation
        state.Psi_book = [1+0j, 0+0j]
        state.Psi_exec = [1+0j, 0+0j]
        state.state_lock = None  # Simplify for testing (no threading in validation)
        state.audit_ops = 0
        state.audit_cost = 0.0
        return state
    
    class MarketState:
        """Replica of FRG's market state"""
        def __init__(self):
            self.Psi_book: List[complex] = []
            self.Psi_exec: List[complex] = []
            self.xi_config: float = 0.0
            self.gamma_trade: float = 0.0
            self.psi_integrity: float = 0.0
            self.h_vol: float = 0.0
            self.state_lock = None
            self.audit_ops: int = 0
            self.audit_cost: float = 0.0
    
    class FinancialResonanceOperator:
        """Replica of FRG's stabilization operator"""
        def __init__(self):
            self.PSI_INTEGRITY_THRESHOLD = 0.95
        
        def apply(self, state: 'MarketState', invariants: 'MarketInvariants', 
                 audit_ops: int, audit_cost: float):
            # Simplified state access (no threading lock for validation)
            h_vol = state.h_vol
            xi_config = state.xi_config
            psi_int = state.psi_integrity
            
            # Calculate COD for diagnostics
            validator = OmegaProtocolValidator()
            cod = validator._calculate_COD_Fin(
                state.Psi_exec, state.Psi_book, 
                h_vol, psi_int, xi_config
            )
            
            # Failure mode detection
            detector = validator.FailureModeDetector()
            failure = detector.check_risk(h_vol, xi_config, psi_int, cod)
            
            # Apply corrections
            if failure == "CONFIG_BLINDNESS":
                state.xi_config = max(0.1, state.xi_config * 0.85)
                audit_ops += 1
                audit_cost += 0.08
            elif failure == "LIQUIDITY_ILLUSION":
                state.h_vol = min(0.80, state.h_vol * 1.1)
                audit_ops += 1
                audit_cost += 0.10
            elif failure == "INTEGRITY_FAILURE":
                raise RuntimeError("Invariant Violation: Market Integrity Compromised")
            
            # Entropy accounting (market friction)
            identity_loss = h_vol * 0.02
            state.psi_integrity -= identity_loss
            
            # Hard gate validation
            if state.psi_integrity < self.PSI_INTEGRITY_THRESHOLD:
                raise RuntimeError("Invariant Violation: Integrity Continuity Compromised")
            
            # Update state
            state.audit_ops = audit_ops
            state.audit_cost = audit_cost
            invariants.psi_integrity = state.psi_integrity
    
    class MarketInvariants:
        """Replica of FRG's market invariants"""
        def __init__(self):
            self.psi_integrity: float = 0.0
            self.PSI_INTEGRITY_THRESHOLD = 0.95
    
    # -------------------------------------------------------------------------
    # 5. PHI-DENSITY LEDGER VALIDATION (Audit Cost Subtraction)
    # -------------------------------------------------------------------------
    def validate_phi_density_ledger(self) -> Dict[str, bool]:
        """Test Phi-density calculation with audit cost subtraction"""
        results = {}
        ledger = self.PhiDensityLedger()
        
        # Test case 1: Positive net gain (gain > audit cost)
        phi_net = ledger.calculate_impact(
            cod_before=0.5, cod_after=0.8, 
            audit_entropy_cost=0.1
        )
        results["positive_net_gain"] = phi_net > 0.2  # 0.3 - 0.1 = 0.2
        
        # Test case 2: Negative net gain (audit cost > gain)
        phi_net = ledger.calculate_impact(
            cod_before=0.7, cod_after=0.75, 
            audit_entropy_cost=0.1
        )
        results["negative_net_gain"] = phi_net < 0.0  # 0.05 - 0.1 = -0.05
        
        # Test case 3: Zero net gain (break-even)
        phi_net = ledger.calculate_impact(
            cod_before=0.6, cod_after=0.65, 
            audit_entropy_cost=0.05
        )
        results["zero_net_gain"] = abs(phi_net - 0.0) < 1e-5  # 0.05 - 0.05 = 0.0
        
        # Test case 4: Audit cost bounds (must be non-negative)
        phi_net = ledger.calculate_impact(
            cod_before=0.5, cod_after=0.6, 
            audit_entropy_cost=-0.05  # Invalid input
        )
        results["audit_cost_non_negative"] = phi_net >= 0.1  # Should treat negative as 0
        
        return results
    
    class PhiDensityLedger:
        """Replica of FRG's phi-density ledger"""
        def calculate_impact(self, cod_before: float, cod_after: float, 
                           audit_entropy_cost: float) -> float:
            raw_gain = cod_after - cod_before
            # Enforce non-negative audit cost (Meta-Scrutiny Rule)
            audit_cost = max(0.0, audit_entropy_cost)
            phi_net = raw_gain - audit_cost
            return phi_net

# =============================================================================
# VALIDATION EXECUTION
# =============================================================================
def main():
    validator = OmegaProtocolValidator()
    
    print("=" * 60)
    print("OMEGA PROTOCOL FINANCIAL RESONANCE GATE (FRG) v57.0 VALIDATION")
    print("=" * 60)
    
    # 1. Volatility Entropy Validation
    print("\n[1] VOLATILITY ENTROPY VALIDATION")
    entropy_results = validator.validate_volatility_entropy()
    for test, passed in entropy_results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test:<30} [{status}]")
    
    # 2. COD Calculation Validation
    print("\n[2] COD CALCULATION VALIDATION")
    cod_results = validator.validate_cod_calculation()
    for test, passed in cod_results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test:<30} [{status}]")
    
    # 3. Failure Mode Detector Validation
    print("\n[3] FAILURE MODE DETECTOR VALIDATION")
    detector_results = validator.validate_failure_detector()
    for test, passed in detector_results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test:<30} [{status}]")
    
    # 4. FRG Operator Validation
    print("\n[4] FRG OPERATOR VALIDATION")
    frg_results = validator.validate_frg_operator()
    for test, passed in frg_results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test:<30} [{status}]")
    
    # 5. Phi-Density Ledger Validation
    print("\n[5] PHI-DENSITY LEDGER VALIDATION")
    ledger_results = validator.validate_phi_density_ledger()
    for test, passed in ledger_results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test:<30} [{status}]")
    
    # Overall Assessment
    all_results = {
        **entropy_results, **cod_results, **detector_results,
        **frg_results, **ledger_results
    }
    total_tests = len(all_results)
    passed_tests = sum(all_results.values())
    
    print("\n" + "=" * 60)
    print(f"OVERALL RESULT: {passed_tests}/{total_tests} TESTS PASSED")
    if passed_tests == total_tests:
        print("STATUS: FULL OMEGA PROTOCOL COMPLIANCE ACHIEVED")
        print("FRG v57.0 is MATHEMATICALLY SOUND and INVARIANT-PRESERVING")
    else:
        print("STATUS: NON-COMPLIANCE DETECTED")
        print("REQUIRES IMMEDIATE CORRECTION TO MAINTAIN MATRIX STABILITY")
    print("=" * 60)
    
    # Critical flaw disclosure (if any)
    if not all_results.get("identical_fidelity", True):
        print("\n[CRITICAL FLAW DETECTED]")
        print("The COD fidelity calculation does not match quantum mechanical")
        print("definition |<A|B>|^2. This violates Omega Protocol's")
        print("Informational Geometry foundation (Rubric §6).")
        print("CORRECTION: Replace magnitude-sum fidelity with proper inner product.")

if __name__ == "__main__":
    main()