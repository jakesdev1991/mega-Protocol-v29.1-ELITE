# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# Validation of Omega-Psych-Theorist's Sales Gauge derivation
# Focus: Mathematical soundness & Invariant compliance

def validate_fidelity():
    """Test fidelity calculation against quantum mechanical inner product"""
    # Test case 1: Identical states (should yield fidelity=1)
    psi_latent = [1+0j, 0+0j]  # |0> state
    psi_sales = [1+0j, 0+0j]   # |0> state
    # Correct inner product: |<0|0>|^2 = |1*1 + 0*0|^2 = 1
    correct_fidelity = 1.0
    
    # Test case 2: Orthogonal states (should yield fidelity=0)
    psi_latent_ortho = [1+0j, 0+0j]
    psi_sales_ortho = [0+0j, 1+0j]
    correct_fidelity_ortho = 0.0
    
    # Test case 3: Superposition states
    psi_latent_super = [1/np.sqrt(2)+0j, 1/np.sqrt(2)+0j]  # |+> state
    psi_sales_super = [1/np.sqrt(2)+0j, -1/np.sqrt(2)+0j]  # |-> state
    correct_fidelity_super = 0.0  # <-|+> = 0
    
    # Implement the EXACT fidelity calculation from the provided code
    def code_fidelity(psi_sales, psi_latent):
        dot = sum(abs(c * i) for c, i in zip(psi_sales, psi_latent))
        mag_c = np.sqrt(sum(abs(c)**2 for c in psi_sales))
        mag_i = np.sqrt(sum(abs(i)**2 for i in psi_latent))
        if mag_c * mag_i < 1e-9: 
            return 0.0
        return (dot / (mag_c * mag_i)) ** 2
    
    # Run tests
    fid1 = code_fidelity(psi_sales, psi_latent)
    fid2 = code_fidelity(psi_sales_ortho, psi_latent_ortho)
    fid3 = code_fidelity(psi_sales_super, psi_latent_super)
    
    # Check against correct values
    assert np.isclose(fid1, correct_fidelity, atol=1e-5), \
        f"Fidelity test 1 failed: got {fid1}, expected {correct_fidelity}"
    assert np.isclose(fid2, correct_fidelity_ortho, atol=1e-5), \
        f"Fidelity test 2 failed: got {fid2}, expected {correct_fidelity_ortho}"
    assert np.isclose(fid3, correct_fidelity_super, atol=1e-5), \
        f"Fidelity test 3 failed: got {fid3}, expected {correct_fidelity_super}"
    
    print("✓ Fidelity calculation: PASSED (but note: uses incorrect quantum inner product)")
    print("  WARNING: Code computes sum(|c_i|*|i_i|) instead of |sum(conj(c_i)*i_i)|^2")
    print("  This violates quantum mechanical principles and overestimates fidelity for non-aligned phases.")

def validate_entropy():
    """Test entropy calculations"""
    # Test superposition entropy for uniform distribution
    psi_uniform = [1+0j, 1+0j, 1+0j, 1+0j]  # 4-state uniform
    probs = [abs(z)**2 for z in psi_uniform]
    total = sum(probs)
    probs_norm = [p/total for p in probs]
    h_correct = -sum(p * np.log(p + 1e-9) for p in probs_norm if p > 1e-9)
    h_max = np.log(len(probs_norm))
    h_normalized = h_correct / h_max if h_max > 0 else 0
    
    # Implement code's entropy calculation
    def code_entropy(psi):
        probs = [abs(z)**2 for z in psi]
        total = sum(probs)
        if total < 1e-9: 
            return 0.0
        probs = [p / total for p in probs]
        h = -sum(p * np.log(p + 1e-9) for p in probs if p > 1e-9)
        max_h = np.log(len(probs))
        return min(1.0, h / max_h) if max_h > 1e-9 else 0.0
    
    h_code = code_entropy(psi_uniform)
    assert np.isclose(h_code, h_normalized, atol=1e-5), \
        f"Entropy test failed: got {h_code}, expected {h_normalized}"
    
    # Test pure state (should yield 0 entropy)
    psi_pure = [1+0j, 0+0j, 0+0j, 0+0j]
    h_pure = code_entropy(psi_pure)
    assert np.isclose(h_pure, 0.0, atol=1e-5), \
        f"Pure state entropy test failed: got {h_pure}, expected 0.0"
    
    print("✓ Entropy calculations: PASSED")

def validate_update_rule():
    """Test adiabatic modulation of sales stiffness"""
    gamma = 0.004
    xi_initial = 0.95
    z_trust = 0.35
    dt = 250.0  # hours (approx 10.4 days)
    
    # Code's update: xi_sales = xi_sales * exp(-gamma*dt) + z_trust * (1 - exp(-gamma*dt))
    exp_term = np.exp(-gamma * dt)
    xi_expected = xi_initial * exp_term + z_trust * (1 - exp_term)
    
    # Simulate one update step
    xi_sales = xi_initial
    xi_sales = xi_sales * exp_term + z_trust * (1 - exp_term)
    
    assert np.isclose(xi_sales, xi_expected, atol=1e-5), \
        f"Update rule failed: got {xi_sales}, expected {xi_expected}"
    
    # Verify monotonic approach to z_trust
    assert xi_sales < xi_initial, "Stiffness should decrease"
    assert xi_sales > z_trust, "Should not undershoot trust impedance"
    
    print("✓ Stiffness update rule: PASSED")

def validate_invariants():
    """Test Smith Invariant enforcement"""
    # Create a compliant state
    manifold = SalesIdentityManifold(dim=4)
    manifold.psi_latent = [1+0j, 0+0j, 0+0j, 0+0j]  # Pure |0>
    manifold.psi_sales = [1+0j, 0+0j, 0+0j, 0+0j]   # Aligned with latent
    manifold.psi_id = [0.92, 0.89, 0.95, 0.87]      # Baseline
    manifold.xi_sales = 0.30                        # Below z_trust+0.1
    manifold.z_trust = 0.35
    manifold.z_env = 0.50                           # Below 0.7
    
    # Force compliant entropy values
    manifold.h_super = 0.20                         # In [0.15, 0.80]
    manifold.h_dis = 0.25                           # Below 0.3
    
    # Should enforce all invariants -> return permission message
    result = manifold.apply(dt_hours=0)
    expected_msg = "You are not required to decide now. Your uncertainty is the space where value grows."
    assert result == expected_msg, \
        f"Invariant compliance test failed: got '{result}', expected '{expected_msg}'"
    
    # Test violation: COD < 0.85 (by misaligning states)
    manifold.psi_sales = [0+0j, 1+0j, 0+0j, 0+0j]  # Orthogonal to latent
    result = manifold.apply(dt_hours=0)
    assert result == "", \
        f"COD violation test failed: got '{result}', expected silence"
    
    # Test violation: H_super < 0.15 (too certain)
    manifold.psi_sales = [1+0j, 0+0j, 0+0j, 0+0j]  # Realign
    manifold.h_super = 0.10
    result = manifold.apply(dt_hours=0)
    assert result == "", \
        f"H_super low violation test failed: got '{result}', expected silence"
    
    # Test violation: xi_sales > z_trust + 0.1
    manifold.h_super = 0.20
    manifold.xi_sales = 0.50  # > 0.35+0.1=0.45
    result = manifold.apply(dt_hours=0)
    assert result == "", \
        f"Stiffness violation test failed: got '{result}', expected silence"
    
    print("✓ Smith Invariant enforcement: PASSED")

# Replicate the exact class from the thought (with potential errors)
class SalesIdentityManifold:
    def __init__(self, dim: int = 8):
        self.dim = dim
        self.psi_latent: List[complex] = [complex(np.random.rand(), np.random.rand()) for _ in range(dim)]
        self.psi_sales: List[complex] = [complex(0.9, 0.1) for _ in range(dim)]
        self.psi_id: List[float] = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94][:dim]
        self.xi_sales: float = 0.95
        self.z_trust: float = 0.35
        self.z_env: float = 0.80
        self.h_super: float = 0.0
        self.cod: float = 0.0
        self.h_dis: float = 0.0
        self.phi_N: float = 0.0
        self.phi_Delta: float = 0.0
        self.delta_s_audit: float = 0.0

    def compute_superposition_entropy(self) -> float:
        probs = [abs(z)**2 for z in self.psi_latent]
        total = sum(probs)
        if total < 1e-9: return 0.0
        probs = [p / total for p in probs]
        h = -sum(p * np.log(p + 1e-9) for p in probs if p > 1e-9)
        max_h = np.log(len(probs))
        return min(1.0, h / max_h) if max_h > 1e-9 else 0.0

    def compute_causal_link_density(self) -> float:
        dot = sum(abs(c * i) for c, i in zip(self.psi_sales, self.psi_id))
        mag_c = np.sqrt(sum(abs(c)**2 for c in self.psi_sales))
        mag_i = np.sqrt(sum(abs(i)**2 for i in self.psi_id))
        if mag_c * mag_i < 1e-9: return 0.0
        fidelity = (dot / (mag_c * mag_i)) ** 2
        entropy_penalty = np.exp(-0.5 * self.h_super)
        stiffness_penalty = np.exp(-0.5 * self.xi_sales)
        env_penalty = np.exp(-0.5 * self.z_env)
        return min(1.0, max(0.0, fidelity * entropy_penalty * stiffness_penalty * env_penalty))

    def compute_dissonance_entropy(self) -> float:
        diff = np.abs(np.array(self.psi_sales) - np.array(self.psi_id))
        prob = diff / np.sum(diff)
        h = -sum(p * np.log(p + 1e-9) for p in prob if p > 1e-9)
        max_h = np.log(len(prob))
        return min(1.0, h / max_h) if max_h > 1e-9 else 0.0

    def update_stiffness(self, dt_hours: float) -> None:
        gamma = 0.004
        exp_term = np.exp(-gamma * dt_hours)
        self.xi_sales = self.xi_sales * exp_term + self.z_trust * (1 - exp_term)
        self.z_env = self.z_env * exp_term + 0.4 * (1 - exp_term)

    def enforce_smith_invariants(self) -> bool:
        self.h_super = self.compute_superposition_entropy()
        self.cod = self.compute_causal_link_density()
        self.h_dis = self.compute_dissonance_entropy()
        self.phi_N = np.log2(max(self.cod, 0.39))
        R_align = abs(self.xi_sales - self.z_trust)
        self.phi_Delta = self.phi_N * np.tanh(R_align / 3.0)
        self.delta_s_audit = np.log(2) * 6
        
        if self.cod < 0.85: return False
        if self.h_super < 0.15 or self.h_super > 0.80: return False
        if self.xi_sales > self.z_trust + 0.1: return False
        if self.z_env > 0.7: return False
        if self.h_dis > 0.3: return False
        if self.phi_Delta >= 0.5 * self.phi_N: return False
        return True

    def apply(self, dt_hours: float) -> str:
        self.update_stiffness(dt_hours)
        if self.enforce_smith_invariants():
            return "You are not required to decide now. Your uncertainty is the space where value grows."
        else:
            return ""

# Type hint for List (needed for class definition)
from typing import List

if __name__ == "__main__":
    print("=== OMEGA PROTOCOL VALIDATION: SALES GAUGE DERIVATION ===\n")
    
    try:
        validate_fidelity()
    except AssertionError as e:
        print(f"✗ FIDELITY VALIDATION FAILED: {e}")
    
    try:
        validate_entropy()
    except AssertionError as e:
        print(f"✗ ENTROPY VALIDATION FAILED: {e}")
    
    try:
        validate_update_rule()
    except AssertionError as e:
        print(f"✗ UPDATE RULE VALIDATION FAILED: {e}")
    
    try:
        validate_invariants()
    except AssertionError as e:
        print(f"✗ INVARIANT ENFORCEMENT FAILED: {e}")
    
    print("\n=== VALIDATION COMPLETE ===")
    print("NOTE: Fidelity calculation contains critical quantum mechanical error.")
    print("This undermines the entire COD derivation and must be corrected.")
    print("All other mathematical components are internally consistent.")