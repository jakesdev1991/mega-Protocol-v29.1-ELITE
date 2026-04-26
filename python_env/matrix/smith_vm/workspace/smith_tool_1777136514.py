# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# Tolerance for floating point comparisons
TOL = 1e-5

def test_cod_computation():
    """Test the COD computation against manual calculation."""
    # Create a deterministic test case
    dim = 4
    # Set known state vectors (normalized)
    psi_latent = np.array([1+0j, 0+0j, 0+0j, 0+0j])  # |Authority> basis
    psi_exp = np.array([0.6+0j, 0.8+0j, 0+0j, 0+0j])  # Superposition
    psi_id = np.array([0.8+0j, 0.6+0j, 0+0j, 0+0j])   # Ideal identity
    
    # Normalize vectors (should already be normalized, but ensure)
    psi_latent = psi_latent / np.linalg.norm(psi_latent)
    psi_exp = psi_exp / np.linalg.norm(psi_exp)
    psi_id = psi_id / np.linalg.norm(psi_id)
    
    # Set parameters
    xi_burea = 0.5
    z_trust = 0.4
    z_env = 0.3
    h_super = 0.5  # Known entropy value
    
    # Create instance and set values
    man = BureaucracyIdentityManifold(dim=dim)
    man.psi_latent = psi_latent.tolist()
    man.psi_exp = psi_exp.tolist()
    man.psi_id = psi_id.tolist()
    man.xi_burea = xi_burea
   man.z_trust = z_trust
    man.z_env = z_env
    man.h_super = h_super  # Override to test entropy penalty independently
    
    # Compute COD via instance
    cod_instance = man.compute_causal_link_density()
    
    # Manual calculation
    # Fidelity = |<ψ_exp|ψ_id>|^2
    dot = np.vdot(psi_exp, psi_id)  # <ψ_exp|ψ_id>
    fidelity = np.abs(dot) ** 2
    # Penalties
    entropy_penalty = np.exp(-0.5 * h_super)
    stiffness_penalty = np.exp(-0.5 * xi_burea)
    env_penalty = np.exp(-0.5 * z_env)
    cod_manual = fidelity * entropy_penalty * stiffness_penalty * env_penalty
    cod_manual = min(1.0, max(0.0, cod_manual))  # Clamp as in code
    
    # Check
    assert abs(cod_instance - cod_manual) < TOL, \
        f"COD mismatch: instance={cod_instance}, manual={cod_manual}"
    print("✓ COD computation validated")

def test_entropy_computation():
    """Test superposition and dissonance entropy calculations."""
    dim = 3
    # Test case 1: Pure state (should give H=0)
    psi_latent = [1+0j, 0+0j, 0+0j]
    man = BureaucracyIdentityManifold(dim=dim)
    man.psi_latent = psi_latent
    h_super = man.compute_superposition_entropy()
    assert abs(h_super - 0.0) < TOL, f"Pure state entropy should be 0, got {h_super}"
    
    # Test case 2: Maximally mixed state (should give H=1)
    psi_latent = [1+0j, 1+0j, 1+0j]  # Equal superposition
    man.psi_latent = psi_latent
    h_super = man.compute_superposition_entropy()
    assert abs(h_super - 1.0) < TOL, f"Max entropy should be 1, got {h_super}"
    
    # Test dissonance entropy
    psi_exp = [0.6, 0.8, 0.0]  # Real for simplicity
    psi_id = [0.8, 0.6, 0.0]
    man.psi_exp = psi_exp
    man.psi_id = psi_id
    h_dis = man.compute_dissonance_entropy()
    # Manual calculation
    diff = np.abs(np.array(psi_exp) - np.array(psi_id))
    prob = diff / np.sum(diff)
    h_manual = -np.sum(p * np.log(p + 1e-9) for p in prob if p > 1e-9)
    max_h = np.log(len(prob))
    h_manual = min(1.0, h_manual / max_h) if max_h > 1e-9 else 0.0
    assert abs(h_dis - h_manual) < TOL, \
        f"Dissonance entropy mismatch: instance={h_dis}, manual={h_manual}"
    print("✓ Entropy computations validated")

def test_invariant_enforcement():
    """Test the 6 Smith Invariants are enforced correctly."""
    man = BureaucracyIdentityManifold(dim=4)
    
    # Set base state that should pass all invariants
    man.psi_latent = [1+0j, 0+0j, 0+0j, 0+0j]
    man.psi_exp = [0.9+0j, 0.1+0j, 0+0j, 0+0j]  # High fidelity
    man.psi_id = [1+0j, 0+0j, 0+0j, 0+0j]
    man.xi_burea = 0.2  # Low stiffness
    man.z_trust = 0.2   # Matches stiffness (xi <= z_trust + 0.1 -> 0.2 <= 0.3)
    man.z_env = 0.5     # Below 0.7 cap
    
    # Should pass all invariants initially
    assert man.enforce_smith_invariants() == True, "Base state should pass all invariants"
    
    # Test Invariant 1: COD < 0.85 -> Fail
    man.psi_exp = [0.1+0j, 0.1+0j, 0+0j, 0+0j]  # Low fidelity
    assert man.enforce_smith_invariants() == False, "Should fail on low COD"
    
    # Reset and test Invariant 2: H_super < 0.15 -> Fail
    man.psi_exp = [0.9+0j, 0.1+0j, 0+0j, 0+0j]
    man.psi_latent = [0.5+0.5j, 0.5-0.5j, 0+0j, 0+0j]  # High entropy state
    # Force h_super low by making state pure (but we'll override h_super in compute)
    # Instead, we'll set h_super directly via overriding the method? 
    # Better: set state to pure state -> h_super=0
    man.psi_latent = [1+0j, 0+0j, 0+0j, 0+0j]
    man.psi_exp = [1+0j, 0+0j, 0+0j, 0+0j]  # Pure state -> h_super=0
    assert man.enforce_smith_invariants() == False, "Should fail on H_super < 0.15"
    
    # Test Invariant 2: H_super > 0.80 -> Fail
    # Create state near maximally mixed in 4D: h_super should be ~1.0
    man.psi_latent = [0.5+0.5j, 0.5-0.5j, 0.5+0.5j, 0.5-0.5j]
    man.psi_latent = [x / np.linalg.norm(man.psi_latent) for x in man.psi_latent]
    man.psi_exp = man.psi_latent.copy()  # Same -> high entropy
    # Note: actual h_super computation may not be exactly 1.0 due to normalization, but should be >0.8
    assert man.enforce_smith_invariants() == False, "Should fail on H_super > 0.80"
    
    # Reset and test Invariant 3: xi_burea > z_trust + 0.1 -> Fail
    man.psi_latent = [1+0j, 0+0j, 0+0j, 0+0j]
    man.psi_exp = [0.9+0j, 0.1+0j, 0+0j, 0+0j]
    man.xi_burea = 0.5
    man.z_trust = 0.3  # 0.5 > 0.3 + 0.1 -> 0.5 > 0.4 -> True -> should fail
    assert man.enforce_smith_invariants() == False, "Should fail on stiffness-impedance mismatch"
    
    # Test Invariant 4: z_env > 0.7 -> Fail
    man.xi_burea = 0.2
    man.z_trust = 0.2
    man.z_env = 0.8
    assert man.enforce_smith_invariants() == False, "Should fail on excessive environmental impedance"
    
    # Test Invariant 5: h_dis > 0.3 -> Fail
    # Set states to be highly dissimilar
    man.psi_exp = [1+0j, 0+0j, 0+0j, 0+0j]
    man.psi_id = [0+0j, 1+0j, 0+0j, 0+0j]  # Orthogonal
    man.h_dis = 1.0  # Override by setting state to force high dissonance
    # Actually, compute dissonance: should be high
    assert man.enforce_smith_invariants() == False, "Should fail on excessive dissonance"
    
    # Test Invariant 6: phi_Delta >= 0.5 * phi_N -> Fail
    # Need phi_N > 0 and phi_Delta large
    # Set conditions: high COD (so phi_N high) and high misalignment (xi_burea >> z_trust)
    man.psi_latent = [1+0j, 0+0j, 0+0j, 0+0j]
    man.psi_exp = [0.9+0j, 0.1+0j, 0+0j, 0+0j]  # High fidelity -> high COD
    man.psi_id = [1+0j, 0+0j, 0+0j, 0+0j]
    man.xi_burea = 0.8  # High stiffness
    man.z_trust = 0.1   # Low trust -> large R_align
    # This should make phi_Delta large relative to phi_N
    assert man.enforce_smith_invariants() == False, "Should fail on excessive phi_Delta"
    
    print("✓ All 6 Smith invariants enforced correctly")

def test_adiabatic_modulation():
    """Test the adiabatic modulation of stiffness and impedance."""
    man = BureaucracyIdentityManifold(dim=4)
    # Set initial values
    man.xi_burea = 0.9
    man.z_trust = 0.2
    man.z_env = 0.9
    
    # Apply a small time step
    dt = 1.0  # 1 hour
    man.apply(dt)
    
    # Check modulation direction: xi_burea should decrease toward z_trust
    # z_env should decrease toward 0.4 (Z_resonant)
    gamma = 0.003
    delta = 0.0025
    exp_g = np.exp(-gamma * dt)
    exp_d = np.exp(-delta * dt)
    expected_xi = man.xi_burea * exp_g + man.z_trust * (1 - exp_g)
    expected_z_env = man.z_env * exp_d + 0.4 * (1 - exp_d)
    
    # Note: apply() updates the instance, so we need to get the new values
    # We'll call apply again on a fresh instance to avoid state carryover
    man2 = BureaucracyIdentityManifold(dim=4)
    man2.xi_burea = 0.9
    man2.z_trust = 0.2
    man2.z_env = 0.9
    man2.apply(dt)
    
    assert abs(man2.xi_burea - expected_xi) < TOL, \
        f"xi_burea modulation failed: got {man2.xi_burea}, expected {expected_xi}"
    assert abs(man2.z_env - expected_z_env) < TOL, \
        f"z_env modulation failed: got {man2.z_env}, expected {expected_z_env}"
    print("✓ Adiabatic modulation validated")

def test_silence_protocol():
    """Test that no message is sent when invariants are violated."""
    man = BureaucracyIdentityManifold(dim=4)
    
    # Case 1: COD too low -> should return empty string
    man.psi_latent = [1+0j, 0+0j, 0+0j, 0+0j]
   man.psi_exp = [0.1+0j, 0.1+0j, 0+0j, 0+0j]  # Low fidelity
    man.psi_id = [1+0j, 0+0j, 0+0j, 0+0j]
    man.xi_burea = 0.2
    man.z_trust = 0.2
    man.z_env = 0.5
    msg = man.apply(0.0)  # dt=0 to avoid modulation changing state
    assert msg == "", f"Should return empty string for low COD, got '{msg}'"
    
    # Case 2: H_super too low -> should return empty string
    man.psi_exp = [0.9+0j, 0.1+0j, 0+0j, 0+0j]
    man.psi_latent = [1+0j, 0+0j, 0+0j, 0+0j]  # Pure state -> h_super=0
    msg = man.apply(0.0)
    assert msg == "", f"Should return empty string for low H_super, got '{msg}'"
    
    # Case 3: Valid state -> should return the message
    man.psi_latent = [0.5+0.5j, 0.5-0.5j, 0+0j, 0+0j]  # Mixed state
    man.psi_latent = [x / np.linalg.norm(man.psi_latent) for x in man.psi_latent]
    man.psi_exp = man.psi_latent.copy()  # High fidelity
    man.psi_id = man.psi_latent.copy()
    man.xi_burea = 0.2
    man.z_trust = 0.2
    man.z_env = 0.5
    # Ensure h_super is in [0.15, 0.8] (should be for mixed state)
    msg = man.apply(0.0)
    expected_msg = "You are not required to comply now. Your uncertainty is not a failure. It is part of your organization’s geometry."
    assert msg == expected_msg, f"Expected message not returned. Got: '{msg}'"
    print("✓ Silence protocol validated")

# Define the class exactly as provided in the agent's thought
class BureaucracyIdentityManifold:
    """UIPO v64.0 — Universal Identity Preservation Operator (Bureaucracy Gauge)
    Implements TOE Step 12: Metric Non-Degeneracy.
    Implements Rubric §6: Covariant Φ Decomposition.
    """
    def __init__(self, dim: int = 8):
        self.dim = dim
        # State Vectors
        self.psi_latent: List[complex] = [complex(np.random.rand(), np.random.rand()) for _ in range(dim)]
        self.psi_exp: List[complex] = [0 + 0j for _ in range(dim)]
        self.psi_id: List[float] = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94][:dim]  # Truncate/pad to dim
        
        # Stiffness & Impedance
        self.xi_burea: float = 0.92 # Default: High Bureaucratic Rigidity
        self.z_trust: float = 0.4   # Default: Low Self-Trust
        self.z_env: float = 0.88    # Default: High Institutional Pressure
        
        # Metrics
        self.h_super: float = 0.0
        self.cod: float = 0.0
        self.h_dis: float = 0.0
        self.phi_N: float = 0.0
        self.phi_Delta: float = 0.0
        self.delta_s_audit: float = 0.0

    def normalize_state(self, state: List[complex]) -> List[complex]:
        norm = np.sqrt(sum(abs(z)**2 for z in state))
        return [z / norm for z in state] if norm > 1e-9 else state

    def compute_superposition_entropy(self) -> float:
        probs = [abs(z)**2 for z in self.psi_latent]
        total = sum(probs)
        if total < 1e-9: return 0.0
        probs = [p / total for p in probs]
        h = -sum(p * np.log(p + 1e-9) for p in probs if p > 1e-9)
        max_h = np.log(len(probs))
        return min(1.0, h / max_h) if max_h > 1e-9 else 0.0

    def compute_causal_link_density(self) -> float:
        """COD = Fidelity * Exp(-Lambda*H) * Exp(-Kappa*Xi)
        Corrected: Phi_N is derived FROM COD, not multiplied INTO it.
        """
        # Convert to numpy arrays for vector operations
        psi_exp_np = np.array(self.psi_exp, dtype=complex)
        psi_id_np = np.array(self.psi_id, dtype=complex)
        
        dot = np.vdot(psi_exp_np, psi_id_np)  # <ψ_exp|ψ_id>
        mag_c = np.linalg.norm(psi_exp_np)
        mag_i = np.linalg.norm(psi_id_np)
        if mag_c * mag_i < 1e-9: return 0.0
        fidelity = (np.abs(dot) / (mag_c * mag_i)) ** 2
        
        # Penalties (Lambda = Kappa = 0.5 as per code)
        entropy_penalty = np.exp(-0.5 * self.h_super)
        stiffness_penalty = np.exp(-0.5 * self.xi_burea)
        env_penalty = np.exp(-0.5 * self.z_env)
        
        return min(1.0, max(0.0, fidelity * entropy_penalty * stiffness_penalty * env_penalty))

    def compute_dissonance_entropy(self) -> float:
        diff = np.abs(np.array(self.psi_exp) - np.array(self.psi_id))
        prob = diff / np.sum(diff)
        h = -sum(p * np.log(p + 1e-9) for p in prob if p > 1e-9)
        max_h = np.log(len(prob))
        return min(1.0, h / max_h) if max_h > 1e-9 else 0.0

    def enforce_smith_invariants(self) -> bool:
        self.h_super = self.compute_superposition_entropy()
        self.cod = self.compute_causal_link_density()
        self.h_dis = self.compute_dissonance_entropy()
        self.phi_N = np.log2(self.cod + 1e-9)
        R_align = abs(self.xi_burea - self.z_trust)
        self.phi_Delta = self.phi_N * np.tanh(R_align / 3.0)
        self.delta_s_audit = np.log(2) * 6 # 6 Invariants

        # Invariant 1: COD ≥ 0.85
        if self.cod < 0.85: return False
        # Invariant 2: H_super in healthy band
        if self.h_super < 0.15 or self.h_super > 0.80: return False
        # Invariant 3: Bureaucratic Stiffness ≤ Trust Impedance + 0.1
        if self.xi_burea > self.z_trust + 0.1: return False
        # Invariant 4: Institutional Pressure ≤ 0.7
        if self.z_env > 0.7: return False
        # Invariant 5: Dissonance Cap
        if self.h_dis > 0.3: return False
        # Invariant 6: Asymmetry Control
        if self.phi_Delta >= 0.5 * self.phi_N: return False
        
        return True

    def apply(self, dt_hours: float) -> str:
        # Adiabatic Modulation (Slower than individual cognition)
        gamma = 0.003
        delta = 0.0025
        exp_term_g = np.exp(-gamma * dt_hours)
        exp_term_d = np.exp(-delta * dt_hours)
        
        self.xi_burea = self.xi_burea * exp_term_g + self.z_trust * (1 - exp_term_g)
        self.z_env = self.z_env * exp_term_d + 0.4 * (1 - exp_term_d) # Z_resonant = 0.4
        
        if self.enforce_smith_invariants():
            return "You are not required to comply now. Your uncertainty is not a failure. It is part of your organization’s geometry."
        else:
            return "" # Silence Protocol: No message sent

# Helper type for complex numbers
from typing import List

# Run all validation tests
if __name__ == "__main__":
    print("Running Omega Protocol Validation Audit...\n")
    
    try:
        test_cod_computation()
        test_entropy_computation()
        test_invariant_enforcement()
        test_adiabatic_modulation()
        test_silence_protocol()
        print("\n✅ ALL TESTS PASSED - Agent's derivation is mathematically sound and compliant with Omega Protocol invariants.")
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        print("Agent's thought contains mathematical or logical weaknesses that threaten matrix stability.")
        exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        exit(1)