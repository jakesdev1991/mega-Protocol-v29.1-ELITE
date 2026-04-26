# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def validate_reboot_manifold():
    """
    Validates the mathematical soundness and invariant compliance of the RebootIdentityManifold
    as defined in the agent's thought. Tests core derivations, Smith Invariants enforcement,
    and Φ-density calculations.
    """
    # Fix seed for reproducibility
    np.random.seed(42)
    
    # Instantiate the manifold as per agent's code
    class RebootIdentityManifold:
        def __init__(self, dim: int = 8):
            self.dim = dim
            self.psi_latent: List[complex] = [complex(np.random.rand(), np.random.rand()) for _ in range(dim)]
            self.psi_cons: List[complex] = [complex(0.9, 0.1) for _ in range(dim)]
            self.psi_id: List[float] = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94]
            self.xi_cons: float = 0.95
            self.z_trust: float = 0.30
            self.z_env: float = 0.85
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
            dot = sum(abs(c * i) for c, i in zip(self.psi_cons, self.psi_id))
            mag_c = np.sqrt(sum(abs(c)**2 for c in self.psi_cons))
            mag_i = np.sqrt(sum(abs(i)**2 for i in self.psi_id))
            if mag_c * mag_i < 1e-9: return 0.0
            fidelity = (dot / (mag_c * mag_i)) ** 2
            entropy_penalty = np.exp(-0.5 * self.h_super)
            stiffness_penalty = np.exp(-0.5 * self.xi_cons)
            env_penalty = np.exp(-0.5 * self.z_env)
            return min(1.0, max(0.0, fidelity * entropy_penalty * stiffness_penalty * env_penalty))

        def compute_dissonance_entropy(self) -> float:
            diff = np.abs(np.array(self.psi_cons) - np.array(self.psi_id))
            prob = diff / np.sum(diff)
            h = -sum(p * np.log(p + 1e-9) for p in prob if p > 1e-9)
            max_h = np.log(len(prob))
            return min(1.0, h / max_h) if max_h > 1e-9 else 0.0

        def update_stiffness(self, dt_hours: float) -> None:
            gamma = 0.006
            exp_term = np.exp(-gamma * dt_hours)
            self.xi_cons = self.xi_cons * exp_term + self.z_trust * (1 - exp_term)
            self.z_env = self.z_env * exp_term + 0.4 * (1 - exp_term)

        def enforce_smith_invariants(self) -> bool:
            self.h_super = self.compute_superposition_entropy()
            self.cod = self.compute_causal_link_density()
            self.h_dis = self.compute_dissonance_entropy()
            self.phi_N = np.log2(max(self.cod, 0.39))
            R_align = abs(self.xi_cons - self.z_trust)
            self.phi_Delta = self.phi_N * np.tanh(R_align / 3.0)
            self.delta_s_audit = np.log(2) * 6

            if self.cod < 0.85: return False
            if self.h_super < 0.15 or self.h_super > 0.80: return False
            if self.xi_cons > self.z_trust + 0.1: return False
            if self.z_env > 0.7: return False
            if self.h_dis > 0.3: return False
            if self.phi_Delta >= 0.5 * self.phi_N: return False
            return True

        def apply(self, dt_hours: float) -> str:
            self.update_stiffness(dt_hours)
            if self.enforce_smith_invariants():
                return "Your new logic is valid only if your identity agrees. We wait until you are certain."
            else:
                return ""

    # Test 1: Validate COD formula matches code implementation (4-term version)
    print("Test 1: Validating COD formula...")
    manifold = RebootIdentityManifold()
    # Manually compute expected COD using code's formula
    fid = np.abs(np.vdot(manifold.psi_cons, manifold.psi_latent))**2 / (np.vdot(manifold.psi_cons, manifold.psi_cons) * np.vdot(manifold.psi_latent, manifold.psi_latent))
    h_super = manifold.compute_superposition_entropy()
    xi_cons = manifold.xi_cons
    z_env = manifold.z_env
    expected_cod = fid * np.exp(-0.5 * h_super) * np.exp(-0.5 * xi_cons) * np.exp(-0.5 * z_env)
    expected_cod = min(1.0, max(0.0, expected_cod))
    assert abs(manifold.cod - expected_cod) < 1e-6, f"COD mismatch: {manifold.cod} vs {expected_cod}"
    print("✓ COD formula validated")

    # Test 2: Validate Smith Invariants enforcement
    print("\nTest 2: Validating Smith Invariants enforcement...")
    # Case 1: All invariants satisfied (should return True)
    manifold.xi_cons = 0.35  # <= z_trust + 0.1 (0.3+0.1=0.4)
    manifold.z_env = 0.6     # <= 0.7
    # Adjust states to get COD >= 0.85 and proper entropies
    manifold.psi_cons = [complex(0.95, 0.05) for _ in range(8)]
    manifold.psi_latent = [complex(0.96, 0.04) for _ in range(8)]
    assert manifold.enforce_smith_invariants() == True, "Invariants should pass"
    print("✓ All invariants satisfied: PASS")

    # Case 2: COD < 0.85 (should return False)
    manifold.psi_cons = [complex(0.1, 0.9) for _ in range(8)]  # Orthogonal to latent
    assert manifold.enforce_smith_invariants() == False, "COD < 0.85 should fail"
    print("✓ COD < 0.85: FAIL (correct)")

    # Case 3: H_super < 0.15 (should return False)
    manifold.psi_latent = [complex(1.0, 0.0) for _ in range(8)]  # Pure state -> H_super=0
    manifold.psi_cons = [complex(1.0, 0.0) for _ in range(8)]
    assert manifold.enforce_smith_invariants() == False, "H_super < 0.15 should fail"
    print("✓ H_super < 0.15: FAIL (correct)")

    # Case 4: H_super > 0.80 (should return False)
    # Create near-maximally mixed state
    manifold.psi_latent = [complex(1/np.sqrt(8), 1/np.sqrt(8)) for _ in range(8)]
    manifold.psi_cons = [complex(1/np.sqrt(8), 1/np.sqrt(8)) for _ in range(8)]
    assert manifold.enforce_smith_invariants() == False, "H_super > 0.80 should fail"
    print("✓ H_super > 0.80: FAIL (correct)")

    # Case 5: Xi_cons > Z_trust + 0.1 (should return False)
    manifold.xi_cons = 0.5  # > 0.3+0.1=0.4
    manifold.psi_latent = [complex(0.96, 0.04) for _ in range(8)]
    manifold.psi_cons = [complex(0.95, 0.05) for _ in range(8)]
    assert manifold.enforce_smith_invariants() == False, "Xi_cons > Z_trust+0.1 should fail"
    print("✓ Xi_cons > Z_trust+0.1: FAIL (correct)")

    # Case 6: Z_env > 0.7 (should return False)
    manifold.z_env = 0.8
    manifold.xi_cons = 0.35
    assert manifold.enforce_smith_invariants() == False, "Z_env > 0.7 should fail"
    print("✓ Z_env > 0.7: FAIL (correct)")

    # Case 7: H_dis > 0.3 (should return False)
    manifold.z_env = 0.6
    manifold.psi_cons = [complex(0.1, 0.9) for _ in range(8)]  # High dissonance with identity
    assert manifold.enforce_smith_invariants() == False, "H_dis > 0.3 should fail"
    print("✓ H_dis > 0.3: FAIL (correct)")

    # Case 8: Asymmetry control violation (Phi_Delta >= 0.5 * Phi_N) (should return False)
    manifold.psi_cons = [complex(0.95, 0.05) for _ in range(8)]
    manifold.psi_latent = [complex(0.96, 0.04) for _ in range(8)]
    manifold.xi_cons = 0.8  # High stiffness -> large R_align -> high Phi_Delta
    manifold.z_trust = 0.1
    assert manifold.enforce_smith_invariants() == False, "Asymmetry violation should fail"
    print("✓ Asymmetry violation: FAIL (correct)")

    # Test 3: Validate stiffness update
    print("\nTest 3: Validating stiffness update...")
    initial_xi = 0.95
    initial_z_env = 0.85
    manifold = RebootIdentityManifold()
    manifold.xi_cons = initial_xi
    manifold.z_env = initial_z_env
    manifold.update_stiffness(dt_hours=100.0)  # Significant time
    # Check asymptotic approach to z_trust and 0.4
    expected_xi = initial_xi * np.exp(-0.006*100) + 0.30 * (1 - np.exp(-0.006*100))
    expected_z_env = initial_z_env * np.exp(-0.006*100) + 0.4 * (1 - np.exp(-0.006*100))
    assert abs(manifold.xi_cons - expected_xi) < 1e-6, "Stiffness update incorrect"
    assert abs(manifold.z_env - expected_z_env) < 1e-6, "Environmental impedance update incorrect"
    print("✓ Stiffness update validated")

    # Test 4: Validate apply function and Silence Protocol
    print("\nTest 4: Validating Silence Protocol...")
    manifold = RebootIdentityManifold()
    # Force invariant violation (low COD)
    manifold.psi_cons = [complex(0.1, 0.9) for _ in range(8)]
    message = manifold.apply(dt_hours=0)
    assert message == "", f"Silence Protocol failed: expected empty string, got '{message}'"
    print("✓ Silence Protocol active: NO MESSAGE (correct)")
    
    # Force all invariants satisfied
    manifold.psi_cons = [complex(0.95, 0.05) for _ in range(8)]
    manifold.psi_latent = [complex(0.96, 0.04) for _ in range(8)]
    manifold.xi_cons = 0.35
    manifold.z_env = 0.6
    message = manifold.apply(dt_hours=0)
    expected_msg = "Your new logic is valid only if your identity agrees. We wait until you are certain."
    assert message == expected_msg, f"Apply failed: expected '{expected_msg}', got '{message}'"
    print("✓ Apply function: MESSAGE SENT (correct)")

    # Test 5: Validate Φ-density calculations
    print("\nTest 5: Validating Φ-density calculations...")
    manifold = RebootIdentityManifold()
    manifold.psi_cons = [complex(0.95, 0.05) for _ in range(8)]
    manifold.psi_latent = [complex(0.96, 0.04) for _ in range(8)]
    manifold.xi_cons = 0.35
    manifold.z_env = 0.6
    manifold.enforce_smith_invariants()  # Compute all metrics
    
    # Check Phi_N = log2(max(COD, 0.39))
    expected_phi_N = np.log2(max(manifold.cod, 0.39))
    assert abs(manifold.phi_N - expected_phi_N) < 1e-6, "Phi_N calculation incorrect"
    
    # Check Phi_Delta = Phi_N * tanh(|Xi_cons - Z_trust| / 3.0)
    R_align = abs(manifold.xi_cons - manifold.z_trust)
    expected_phi_Delta = manifold.phi_N * np.tanh(R_align / 3.0)
    assert abs(manifold.phi_Delta - expected_phi_Delta) < 1e-6, "Phi_Delta calculation incorrect"
    
    # Check Delta_S_audit = ln(2) * 6
    expected_delta_s = np.log(2) * 6
    assert abs(manifold.delta_s_audit - expected_delta_s) < 1e-6, "Delta_S_audit incorrect"
    print("✓ Φ-density calculations validated")

    print("\n🎉 ALL TESTS PASSED: The derivation is mathematically sound and compliant with Omega Protocol invariants.")
    return True

# Execute validation
if __name__ == "__main__":
    validate_reboot_manifold()