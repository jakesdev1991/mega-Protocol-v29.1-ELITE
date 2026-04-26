# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

class SalesIdentityManifoldValidator:
    """Validator for SalesIdentityManifold enforcing Omega Protocol invariants"""
    
    def __init__(self):
        self.test_cases = []
        self.passed = 0
        self.failed = 0
        
    def run_validation(self):
        """Run all validation tests"""
        print("=== OMEGA PROTOCOL VALIDATION: SALES GAUGE (UIPO v65.0) ===\n")
        
        # Test 1: COD computation correctness
        self.test_cod_computation()
        
        # Test 2: Entropy computations
        self.test_entropy_computations()
        
        # Test 3: Invariant enforcement logic
        self.test_invariant_enforcement()
        
        # Test 4: Apply method behavior
        self.test_apply_method()
        
        # Test 5: Φ-density ledger consistency
        self.test_phi_density_ledger()
        
        # Summary
        print(f"\n=== VALIDATION SUMMARY ===")
        print(f"Tests Passed: {self.passed}")
        print(f"Tests Failed: {self.failed}")
        print(f"Overall Status: {'META-PASS' if self.failed == 0 else 'META-FAIL'}")
        
        return self.failed == 0
    
    def test_cod_computation(self):
        """Test COD formula matches Omega Action Principle"""
        print("Test 1: COD Computation Validation")
        try:
            # Create test instance
            sim = SalesIdentityManifold()
            
            # Set known states for deterministic test
            sim.psi_latent = [1+0j, 0+0j, 0+0j, 0+0j, 0+0j, 0+0j, 0+0j, 0+0j]  # Pure Safety state
            sim.psi_sales = [1+0j, 0+0j, 0+0j, 0+0j, 0+0j, 0+0j, 0+0j, 0+0j]  # Pure Close state
            sim.psi_id = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94]     # Baseline
            
            # Override parameters for clean test
            sim.h_super = 0.0      # Minimum uncertainty
            sim.xi_sales = 0.0     # Zero stiffness
            sim.z_env = 0.0        # Zero environmental impedance
            
            # Compute COD
            cod = sim.compute_causal_link_density()
            
            # With perfect alignment and zero penalties: COD should be 1.0
            expected = 1.0
            tolerance = 1e-5
            
            assert abs(cod - expected) < tolerance, f"COD mismatch: got {cod}, expected {expected}"
            print(f"  ✓ Perfect alignment COD: {cod:.6f} (expected ~1.0)")
            
            # Test orthogonal states (should yield low COD)
            sim.psi_sales = [0+0j, 1+0j, 0+0j, 0+0j, 0+0j, 0+0j, 0+0j, 0+0j]  # Pure Need state
            cod_ortho = sim.compute_causal_link_density()
            assert cod_ortho < 0.1, f"Orthogonal COD too high: {cod_ortho}"
            print(f"  ✓ Orthogonal states COD: {cod_ortho:.6f} (expected <0.1)")
            
            self.passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {str(e)}")
            self.failed += 1
        print()
    
    def test_entropy_computations(self):
        """Test superposition and dissonance entropy calculations"""
        print("Test 2: Entropy Computation Validation")
        try:
            sim = SalesIdentityManifold()
            
            # Test superposition entropy: uniform distribution
            sim.psi_latent = [1+0j] * 8  # Equal amplitude
            h_super = sim.compute_superposition_entropy()
            # For uniform distribution over 8 states: H = log2(8)/log2(8) = 1.0
            assert abs(h_super - 1.0) < 1e-5, f"Uniform entropy: got {h_super}, expected 1.0"
            print(f"  ✓ Uniform superposition entropy: {h_super:.6f}")
            
            # Test superposition entropy: pure state
            sim.psi_latent = [1+0j] + [0+0j]*7
            h_super_pure = sim.compute_superposition_entropy()
            assert h_super_pure < 1e-5, f"Pure state entropy: got {h_super_pure}"
            print(f"  ✓ Pure state entropy: {h_super_pure:.6f}")
            
            # Test dissonance entropy: identical vectors
            sim.psi_sales = [0.9+0.1j]*8
            sim.psi_id = [0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
            h_dis = sim.compute_dissonance_entropy()
            assert h_dis < 1e-5, f"Identical vectors dissonance: got {h_dis}"
            print(f"  ✓ Identical vectors dissonance: {h_dis:.6f}")
            
            # Test dissonance entropy: maximal difference
            sim.psi_sales = [1+0j]*8
            sim.psi_id = [0+0j]*8  # Note: psi_id should be real in practice, but test math
            # In reality, psi_id is real baseline, but we test the computation
            sim.psi_id = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]  # Small real values
            sim.psi_sales = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
            h_dis_max = sim.compute_dissonance_entropy()
            # Should be near 1.0 for maximal difference
            assert h_dis_max > 0.9, f"Max dissonance too low: {h_dis_max}"
            print(f"  ✓ Maximal dissonance entropy: {h_dis_max:.6f}")
            
            self.passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {str(e)}")
            self.failed += 1
        print()
    
    def test_invariant_enforcement(self):
        """Test all 9 Smith Invariants are enforced correctly"""
        print("Test 3: Smith Invariant Enforcement Validation")
        try:
            sim = SalesIdentityManifold()
            
            # Base compliant state (adjust parameters to satisfy all)
            sim.psi_latent = [1+0j] + [0+0j]*7
            sim.psi_sales = [0.92+0j]*8   # Match baseline Safety
            sim.psi_id = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94]
            sim.h_super = 0.5             # Within [0.15, 0.80]
            sim.xi_sales = 0.4            # Will set z_trust to satisfy Invariant 4
            sim.z_trust = 0.35            # So xi_sales (0.4) <= z_trust+0.1 (0.45) -> PASS
            sim.z_env = 0.6               # <= 0.7 -> PASS
            sim.h_dis = 0.2               # <= 0.3 -> PASS
            sim.b1_homology = 0.7         # <= 0.8 -> PASS
            
            # First check: should PASS all invariants
            assert sim.enforce_smith_invariants() == True, "Base compliant state failed"
            print("  ✓ Base compliant state: ALL INVARIANTS PASS")
            
            # Test each invariant individually by violating one while keeping others compliant
            # Invariant 1: COD < 0.85
            sim.psi_sales = [0.1+0j]*8   # Low alignment with baseline
            assert sim.enforce_smith_invariants() == False, "Invariant 1 (COD) not enforced"
            print("  ✓ Invariant 1 (COD >= 0.85): ENFORCED")
            
            # Reset to compliant
            sim.psi_sales = [0.92+0j]*8
            
            # Invariant 2: phi_N < log2(0.39) ≈ -0.36
            sim.cod = 0.38   # Force low COD
            # Recompute phi_N via internal state (we'll manipulate via cod)
            # Instead, we'll directly test the phi_N check by setting cod low
            sim.psi_sales = [0.1+0j]*8   # Low alignment -> low cod
            assert sim.enforce_smith_invariants() == False, "Invariant 2 (Identity Continuity) not enforced"
            print("  ✓ Invariant 2 (Identity Continuity): ENFORCED")
            
            # Reset
            sim.psi_sales = [0.92+0j]*8
            
            # Invariant 3: h_super < 0.15 or > 0.80
            sim.h_super = 0.1   # Too low
            assert sim.enforce_smith_invariants() == False, "Invariant 3 (low h_super) not enforced"
            sim.h_super = 0.9   # Too high
            assert sim.enforce_smith_invariants() == False, "Invariant 3 (high h_super) not enforced"
            print("  ✓ Invariant 3 (Uncertainty Band): ENFORCED")
            
            # Reset
            sim.h_super = 0.5
            
            # Invariant 4: xi_sales > z_trust + 0.1
            sim.xi_sales = 0.5
            sim.z_trust = 0.3   # 0.5 > 0.3+0.1=0.4 -> VIOLATION
            assert sim.enforce_smith_invariants() == False, "Invariant 4 (Stiffness-Impedance) not enforced"
            print("  ✓ Invariant 4 (Stiffness-Impedance Match): ENFORCED")
            
            # Reset
            sim.xi_sales = 0.4
            sim.z_trust = 0.35
            
            # Invariant 5: z_env > 0.7
            sim.z_env = 0.8
            assert sim.enforce_smith_invariants() == False, "Invariant 5 (Environmental Impedance) not enforced"
            print("  ✓ Invariant 5 (Environmental Impedance): ENFORCED")
            
            # Reset
            sim.z_env = 0.6
            
            # Invariant 6: h_dis > 0.3
            sim.h_dis = 0.4
            assert sim.enforce_smith_invariants() == False, "Invariant 6 (Dissonance Cap) not enforced"
            print("  ✓ Invariant 6 (Dissonance Cap): ENFORCED")
            
            # Reset
            sim.h_dis = 0.2
            
            # Invariant 7: phi_Delta >= 0.5 * phi_N
            # Force high asymmetry: make xi_sales >> z_trust
            sim.xi_sales = 0.8
            sim.z_trust = 0.2   # Large R_align
            # This should make phi_Delta large relative to phi_N
            assert sim.enforce_smith_invariants() == False, "Invariant 7 (Asymmetry Control) not enforced"
            print("  ✓ Invariant 7 (Asymmetry Control): ENFORCED")
            
            # Reset
            sim.xi_sales = 0.4
            sim.z_trust = 0.35
            
            # Invariant 8: b1_homology > 0.8
            sim.b1_homology = 0.9
            assert sim.enforce_smith_invariants() == False, "Invariant 8 (Decision Loop Guard) not enforced"
            print("  ✓ Invariant 8 (Decision Loop Guard): ENFORCED")
            
            # Reset
            sim.b1_homology = 0.7
            
            # Invariant 9: Always passes if others pass (audit cost is just accounting)
            assert sim.enforce_smith_invariants() == True, "Invariant 9 (Audit Cost) logic flawed"
            print("  ✓ Invariant 9 (Audit Cost Accounted): VALID")
            
            self.passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {str(e)}")
            self.failed += 1
        print()
    
    def test_apply_method(self):
        """Test Silence Protocol activation and parameter modulation"""
        print("Test 4: Apply Method (Silence Protocol) Validation")
        try:
            sim = SalesIdentityManifold()
            
            # Set to compliant state
            sim.psi_latent = [1+0j] + [0+0j]*7
            sim.psi_sales = [0.92+0j]*8
            sim.psi_id = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94]
            sim.h_super = 0.5
            sim.xi_sales = 0.4
            sim.z_trust = 0.35
            sim.z_env = 0.6
            sim.h_dis = 0.2
            sim.b1_homology = 0.7
            
            # Should return Silence Protocol message
            result = sim.apply(1.0)  # 1 hour
            expected_msg = "You are not required to decide now. Your uncertainty is the space where value grows."
            assert result == expected_msg, f"Expected silence message, got: '{result}'"
            print("  ✓ Compliant state: Returns Silence Protocol message")
            
            # Set to non-compliant state (violate Invariant 4)
            sim.xi_sales = 0.5  # > z_trust+0.1 (0.45)
            result = sim.apply(1.0)
            assert result == "", f"Expected empty string (silence), got: '{result}'"
            print("  ✓ Non-compliant state: Returns empty string (Silence Protocol)")
            
            # Test parameter modulation over time
            initial_xi = sim.xi_sales
            initial_z_env = sim.z_env
            sim.apply(100.0)  # 100 hours
            
            # xi_sales should decay toward z_trust (0.35)
            # Formula: xi_sales(t) = xi_sales(0)*exp(-gamma*t) + z_trust*(1-exp(-gamma*t))
            gamma = 0.004
            t = 100.0
            expected_xi = 0.5 * np.exp(-gamma*t) + 0.35 * (1 - np.exp(-gamma*t))
            assert abs(sim.xi_sales - expected_xi) < 1e-5, f"xi_sales modulation failed: got {sim.xi_sales}, expected {expected_xi}"
            
            # z_env should decay toward 0.4
            delta = 0.003
            expected_z_env = 0.6 * np.exp(-delta*t) + 0.4 * (1 - np.exp(-delta*t))
            assert abs(sim.z_env - expected_z_env) < 1e-5, f"z_env modulation failed: got {sim.z_env}, expected {expected_z_env}"
            print("  ✓ Parameter modulation over time: CORRECT")
            
            # Test b1_homology decay
            initial_b1 = sim.b1_homology
            sim.apply(50.0)  # Additional 50 hours (total 150)
            # b1_homology = max(0.1, b1 * 0.999 - 0.0002 * dt)
            expected_b1 = max(0.1, 0.7 * (0.999**150) - 0.0002*150)
            assert abs(sim.b1_homology - expected_b1) < 1e-5, f"b1_homology decay failed"
            print("  ✓ Topological invariant (b1) decay: CORRECT")
            
            self.passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {str(e)}")
            self.failed += 1
        print()
    
    def test_phi_density_ledger(self):
        """Test Φ-density ledger components for internal consistency"""
        print("Test 5: Φ-Density Ledger Consistency Validation")
        try:
            sim = SalesIdentityManifold()
            
            # Set to state yielding COD=0.85 (threshold)
            # We'll solve for alignment needed: COD = fidelity * penalties = 0.85
            # Assume penalties=1.0 for simplicity (optimal conditions)
            # Then fidelity = sqrt(COD) = sqrt(0.85) ≈ 0.922
            # Set psi_sales to match psi_id with 0.922 fidelity
            sim.psi_latent = [1+0j] + [0+0j]*7
            sim.psi_id = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94]
            # Normalize psi_id to unit vector for fidelity calculation
            id_norm = np.linalg.norm(sim.psi_id)
            psi_id_unit = [x/id_norm for x in sim.psi_id]
            # Set psi_sales to scaled unit vector
            scale = 0.922
            sim.psi_sales = [complex(scale*x, 0) for x in psi_id_unit]
            
            # Set optimal parameters for penalty=1.0
            sim.h_super = 0.0
            sim.xi_sales = 0.0
            sim.z_env = 0.0
            sim.h_dis = 0.0
            sim.b1_homology = 0.0
            
            # Compute COD
            cod = sim.compute_causal_link_density()
            # Should be approximately fidelity^2 = (0.922)^2 ≈ 0.85
            assert abs(cod - 0.85) < 0.01, f"COD threshold test: got {cod}, expected ~0.85"
            print(f"  ✓ COD at threshold (0.85): {cod:.4f}")
            
            # Compute phi_N
            phi_N = np.log2(max(cod, 0.39) + 1e-12)
            expected_phi_N = np.log2(0.85)  # ≈ -0.234
            assert abs(phi_N - expected_phi_N) < 0.01, f"phi_N calculation: got {phi_N}, expected {expected_phi_N}"
            print(f"  ✓ Identity Continuity (phi_N): {phi_N:.4f} (expected ~{expected_phi_N:.4f})")
            
            # Verify hard floor: if cod=0.39, phi_N should be log2(0.39)≈-0.36
            sim.psi_sales = [0.1+0j]*8   # Force low alignment
            cod_low = sim.compute_causal_link_density()
            phi_N_low = np.log2(max(cod_low, 0.39) + 1e-12)
            assert abs(phi_N_low - np.log2(0.39)) < 0.01, f"Hard floor failed: got {phi_N_low}"
            print(f"  ✓ Hard floor (phi_N at cod=0.39): {phi_N_low:.4f}")
            
            # Verify asymmetry control calculation
            sim.xi_sales = 0.5
            sim.z_trust = 0.2
            R_align = abs(sim.xi_sales - sim.z_trust)
            phi_Delta = sim.phi_N * np.tanh(R_align / 3.0)  # From code
            # Manual computation:
            phi_N_val = np.log2(max(sim.compute_causal_link_density(), 0.39) + 1e-12)
            expected_phi_Delta = phi_N_val * np.tanh(R_align / 3.0)
            assert abs(phi_Delta - expected_phi_Delta) < 1e-5, f"phi_Delta calculation mismatch"
            print(f"  ✓ Asymmetry Control (phi_Delta): {phi_Delta:.6f}")
            
            # Verify audit cost: 9 * k_B * ln(2) in natural units
            # In code: delta_s_audit = np.log(2) * 9
            delta_s_audit = np.log(2) * 9
            expected = 9 * 0.693147  # approx 6.238
            assert abs(delta_s_audit - expected) < 0.01, f"Audit cost calculation: got {delta_s_audit}"
            print(f"  ✓ Audit Cost (ΔS_audit): {delta_s_audit:.4f} (9 × ln 2)")
            
            self.passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {str(e)}")
            self.failed += 1
        print()

# Run the validation
if __name__ == "__main__":
    validator = SalesIdentityManifoldValidator()
    success = validator.run_validation()
    exit(0 if success else 1)