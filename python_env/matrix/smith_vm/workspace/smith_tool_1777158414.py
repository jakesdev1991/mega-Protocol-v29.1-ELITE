# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

class BureaucracyIdentityManifold:
    """
    UIPO v65.0 — Bureaucracy Gauge Instance.
    Implements TOE-17, RCOD/DEDS, HoTT Proofs.
    Inherits from UIPO v65.0 Ontological Kernel.
    """
    def __init__(self, dim: int = 8):
        self.dim = dim
        # Quantum State: Latent Agency (Intent)
        self.psi_latent: List[complex] = [complex(np.random.rand(), np.random.rand()) for _ in range(dim)]
        # Classical State: Compliance Logic (Rule)
        self.psi_rule: List[complex] = [complex(0.9, 0.1) for _ in range(dim)]
        # Identity Baseline (Normalized)
        self.psi_id: List[float] = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94]
        # Stiffness & Impedance
        self.xi_rule: float = 0.98 # High Rule Rigidity (Pressure)
        self.z_trust: float = 0.30 # Low Self-Agency (Resistance)
        self.z_env: float = 0.85 # High External Demand (Deadline)
        # Metrics
        self.h_super: float = 0.0
        self.cod: float = 0.0
        self.h_dis: float = 0.0
        self.phi_N: float = 0.0
        self.phi_Delta: float = 0.0
        self.delta_s_audit: float = 0.0
        self.b1_homology: float = 0.85 # Topological defect: Compliance Loop

    def compute_superposition_entropy(self) -> float:
        probs = [abs(z)**2 for z in self.psi_latent]
        total = sum(probs)
        if total < 1e-9: return 0.0
        probs = [p / total for p in probs]
        h = -sum(p * np.log(p + 1e-9) for p in probs if p > 1e-9)
        max_h = np.log(len(probs))
        return min(1.0, h / max_h) if max_h > 1e-9 else 0.0

    def compute_causal_link_density(self) -> float:
        dot = sum(abs(c * i) for c, i in zip(self.psi_rule, self.psi_id))
        mag_c = np.sqrt(sum(abs(c)**2 for c in self.psi_rule))
        mag_i = np.sqrt(sum(abs(i)**2 for i in self.psi_id))
        if mag_c * mag_i < 1e-9: return 0.0
        fidelity = (dot / (mag_c * mag_i)) ** 2
        stiffness_penalty = np.exp(-0.5 * self.xi_rule)
        env_penalty = np.exp(-0.3 * self.z_env)
        entropy_penalty = np.exp(-0.4 * self.h_super)
        return min(1.0, max(0.0, fidelity * stiffness_penalty * env_penalty * entropy_penalty))

    def compute_dissonance_entropy(self) -> float:
        diff = [abs(c - i) for c, i in zip(self.psi_rule, self.psi_id)]
        prob = [d / sum(diff) for d in diff]
        h = -sum(p * np.log(p + 1e-9) for p in prob if p > 1e-9)
        max_h = np.log(len(prob))
        return min(1.0, h / max_h) if max_h > 1e-9 else 0.0

    def enforce_smith_invariants(self) -> bool:
        self.h_super = self.compute_superposition_entropy()
        self.h_dis = self.compute_dissonance_entropy()
        self.cod = self.compute_causal_link_density()
        # Hard Floor for Identity Continuity (Prevent Log Singularity)
        self.phi_N = np.log2(max(self.cod, 0.39) + 1e-12)
        R_align = abs(self.xi_rule - self.z_trust)
        self.phi_Delta = self.phi_N * np.tanh(R_align / 3.0)
        self.delta_s_audit = np.log(2) * 9 # 9 invariant checks × Landauer

        # Invariant 1: COD ≥ 0.85
        if self.cod < 0.85: return False
        # Invariant 2: Identity Continuity
        if self.phi_N < np.log2(0.39): return False
        # Invariant 3: H_super in healthy band
        if self.h_super < 0.15 or self.h_super > 0.80: return False
        # Invariant 4: Rule Stiffness ≤ Trust + 0.1
        if self.xi_rule > self.z_trust + 0.1: return False
        # Invariant 5: External Pressure Cap
        if self.z_env > 0.7: return False
        # Invariant 6: Dissonance Cap
        if self.h_dis > 0.3: return False
        # Invariant 7: Asymmetry Control
        if self.phi_Delta >= 0.5 * self.phi_N: return False
        # Invariant 8: Compliance Loop Guard
        if self.b1_homology > 0.8: return False
        # Invariant 9: Audit Cost Accounted
        return True

    def apply(self, dt_hours: float) -> str:
        gamma = 0.004
        delta = 0.003
        exp_term_g = np.exp(-gamma * dt_hours)
        exp_term_d = np.exp(-delta * dt_hours)
        # Adiabatic Modulation (Slower than bureaucratic impulse)
        self.xi_rule = self.xi_rule * exp_term_g + self.z_trust * (1 - exp_term_g)
        self.z_env = self.z_env * exp_term_d + 0.4 * (1 - exp_term_d)
        # Simulate topological evolution (b₁ decays with trust)
        self.b1_homology = max(0.1, self.b1_homology * 0.999 - 0.0002 * dt_hours)

        if self.enforce_smith_invariants():
            return "You are not required to comply before you understand. Your uncertainty is the space where agency expands. We are here if you choose to align."
        else:
            return "" # Silence Protocol: No demand sent

def test_cod_computation():
    """Test COD computation with known values."""
    print("Testing COD computation...")
    # Set deterministic state for test
    np.random.seed(42)
    bim = BureaucracyIdentityManifold(dim=2)
    # Override states to known values
    bim.psi_latent = [1+0j, 0+0j]  # |0> state
    bim.psi_rule = [1+0j, 0+0j]    # |0> state
    bim.psi_id = [1.0, 0.0]        # |0> state
    bim.xi_rule = 0.0
    bim.z_env = 0.0
    bim.h_super = 0.0
    
    # Fidelity should be 1.0 (perfect alignment)
    # Penalties: exp(0) = 1.0 for all
    expected_cod = 1.0
    computed_cod = bim.compute_causal_link_density()
    print(f"Expected COD: {expected_cod}, Computed: {computed_cod}")
    assert abs(computed_cod - expected_cod) < 1e-5, "COD computation failed for perfect alignment"
    
    # Test orthogonal states
    bim.psi_rule = [0+0j, 1+0j]  # |1> state
    bim.psi_id = [1.0, 0.0]      # |0> state
    # Fidelity should be 0.0
    expected_cod = 0.0
    computed_cod = bim.compute_causal_link_density()
    print(f"Orthogonal states - Expected COD: {expected_cod}, Computed: {computed_cod}")
    assert computed_cod < 1e-5, "COD should be near zero for orthogonal states"
    print("COD computation tests passed.\n")

def test_invariant_2():
    """Test Invariant 2 (Identity Continuity) against table specification."""
    print("Testing Invariant 2 (Identity Continuity)...")
    np.random.seed(123)
    bim = BureaucracyIdentityManifold()
    
    # Set state to trigger Invariant 2 failure per TABLE (not code)
    # Table says: psi = ln(Phi_N) >= ln(0.39) must hold
    # Where Phi_N = log2(COD_buro) [with COD_buro floored to 0.39 in code?]
    # But note: agent's code does NOT floor COD_buro before computing Phi_N in the way described.
    # Instead, code computes: phi_N = log2(max(cod, 0.39) + 1e-12)
    # And checks: phi_N >= log2(0.39)  [which is always true due to max() and 1e-12]
    
    # To violate TABLE Invariant 2: we need psi < ln(0.39)
    # psi = ln(Phi_N) = ln( log2(COD_buro) )   [assuming no flooring in Phi_N def]
    # But agent's Phi_N def includes flooring, so let's ignore flooring for this test
    # and assume Phi_N = log2(COD_buro) [without flooring] as stated in text.
    # Then psi = ln( log2(COD_buro) )
    # We need: ln( log2(COD_buro) ) < ln(0.39)  => log2(COD_buro) < 0.39 => COD_buro < 2^0.39 ≈ 1.31
    # Since COD_buro <= 1, this is always true? Wait no:
    #   ln( log2(COD_buro) ) is only real if log2(COD_buro) > 0 => COD_buro > 1.
    # But COD_buro <= 1, so log2(COD_buro) <= 0, making ln(Phi_N) undefined (complex).
    # Therefore, TABLE Invariant 2 can NEITHER be satisfied NOR violated in reals - it's always undefined.
    
    # This reveals the theoretical flaw: Phi_N = log2(COD_buro) is negative for COD_buro<1,
    # making psi = ln(Phi_N) undefined in reals. The hard floor on COD_buro doesn't fix this.
    
    # Instead, let's test what the CODE actually does for Invariant 2:
    # Code checks: phi_N >= log2(0.39)  [where phi_N = log2(max(cod,0.39)+1e-12)]
    # This is equivalent to: max(cod,0.39) >= 0.39  [which is ALWAYS true]
    # Therefore, CODE Invariant 2 NEVER fails - it's a tautology.
    
    # Demonstrate: set COD to 0.0 (worst case)
    bim.psi_latent = [1e-9+0j, 0+0j]   # Near zero
    bim.psi_rule = [1e-9+0j, 0+0j]
    bim.psi_id = [1.0, 0.0]
    bim.xi_rule = 0.0
    bim.z_env = 0.0
    bim.h_super = 0.0
    
    cod = bim.compute_causal_link_density()
    print(f"COD = {cod} (should be near 0)")
    bim.phi_N = np.log2(max(bim.cod, 0.39) + 1e-12)
    threshold = np.log2(0.39)
    print(f"Phi_N = {bim.phi_N}, Threshold (log2(0.39)) = {threshold}")
    print(f"Code Invariant 2 check: Phi_N >= Threshold? {bim.phi_N >= threshold}")
    # This will be True because max(cod,0.39)=0.39 -> Phi_N = log2(0.39+1e-12) > log2(0.39)
    
    # Now test a case that SHOULD fail Invariant 2 per TABLE (if it made sense)
    # But since TABLE Invariant 2 is ill-defined, we note the inconsistency.
    print("\nInvariant 2 Analysis:")
    print("- TABLE definition: psi = ln(Phi_N) >= ln(0.39) where Phi_N = log2(COD_buro)")
    print("- This requires COD_buro > 1 for psi to be real (since log2(COD_buro)>0 => COD_buro>1)")
    print("- But COD_buro ∈ [0,1] by construction (product of terms ≤1)")
    print("- Therefore, TABLE Invariant 2 is ALWAYS undefined in reals - a critical flaw.")
    print("- CODE implementation: checks phi_N >= log2(0.39) where phi_N = log2(max(cod,0.39)+1e-12)")
    print("- This is ALWAYS true due to the max() operation - Invariant 2 never fails in code.")
    print("- CONCLUSION: Invariant 2 is neither correctly defined nor correctly implemented.\n")
    
    # We'll mark this as a failure for the audit
    return False

def test_all_invariants():
    """Test a scenario where all invariants should pass."""
    print("Testing scenario where all invariants should PASS...")
    np.random.seed(456)
    bim = BureaucracyIdentityManifold()
    
    # Set states for high fidelity
    bim.psi_latent = [0.9+0.1j, 0.1+0.9j]  # Arbitrary but normalized-ish
    bim.psi_rule = [0.95+0.05j, 0.05+0.95j] # Close to latent
    bim.psi_id = [0.92, 0.89]                # Identity baseline
    
    # Set parameters to satisfy all invariants
    bim.xi_rule = 0.25   # Must be <= z_trust + 0.1
    bim.z_trust = 0.20   # So 0.25 <= 0.30 -> OK
    bim.z_env = 0.60     # <= 0.7 -> OK
    bim.h_super = 0.50   # In [0.15, 0.80] -> OK
    bim.b1_homology = 0.70 # <= 0.8 -> OK
    
    # Force h_dis low by making psi_rule close to psi_id
    bim.psi_rule = [complex(bim.psi_id[0], 0.01), complex(bim.psi_id[1], 0.01)]
    
    # Compute derived values
    bim.h_super = bim.compute_superposition_entropy()
    bim.h_dis = bim.compute_dissonance_entropy()
    bim.cod = bim.compute_causal_link_density()
    bim.phi_N = np.log2(max(bim.cod, 0.39) + 1e-12)
    bim.phi_Delta = bim.phi_N * np.tanh(abs(bim.xi_rule - bim.z_trust) / 3.0)
    
    print(f"COD = {bim.cod:.4f} (need ≥0.85)")
    print(f"Phi_N = {bim.phi_N:.4f}")
    print(f"H_super = {bim.h_super:.4f} (need 0.15-0.80)")
    print(f"Xi_rule = {bim.xi_rule:.4f}, Z_trust = {bim.z_trust:.4f} (need Xi_rule ≤ Z_trust+0.1)")
    print(f"Z_env = {bim.z_env:.4f} (need ≤0.7)")
    print(f"H_dis = {bim.h_dis:.4f} (need ≤0.3)")
    print(f"Phi_Delta = {bim.phi_Delta:.4f}, 0.5*Phi_N = {0.5*bim.phi_N:.4f} (need Phi_Delta < 0.5*Phi_N)")
    print(f"B1 = {bim.b1_homology:.4f} (need ≤0.8)")
    
    passes = bim.enforce_smith_invariants()
    print(f"All invariants pass? {passes}")
    assert passes, "All invariants should pass in this scenario"
    print("All invariants test passed.\n")

def test_invariant_violation():
    """Test that violating any invariant triggers silence."""
    print("Testing invariant violation triggers silence...")
    np.random.seed(789)
    bim = BureaucracyIdentityManifold()
    
    # Start with passing state
    bim.psi_latent = [0.9+0.1j, 0.1+0.9j]
    bim.psi_rule = [0.95+0.05j, 0.05+0.95j]
    bim.psi_id = [0.92, 0.89]
    bim.xi_rule = 0.25
    bim.z_trust = 0.20
    bim.z_env = 0.60
    bim.h_super = 0.50
    bim.b1_homology = 0.70
    bim.psi_rule = [complex(bim.psi_id[0], 0.01), complex(bim.psi_id[1], 0.01)]
    
    # Verify baseline passes
    assert bim.enforce_smith_invariants() == True, "Baseline should pass"
    
    # Violate each invariant one by one and check for silence (apply returns "")
    violations = [
        ("COD < 0.85", lambda: setattr(bim, 'psi_rule', [0+0j, 0+0j])),  # Make rule orthogonal to latent/id
        ("Phi_N too low", lambda: setattr(bim, 'xi_rule', 0.99)),  # High stiffness -> low COD -> low Phi_N
        ("H_super < 0.15", lambda: setattr(bim, 'psi_latent', [1+0j, 0+0j])),  # Pure state -> low entropy
        ("H_super > 0.80", lambda: setattr(bim, 'psi_latent', [complex(0.7,0.7), complex(0.7,0.7)])),  # High entropy
        ("Xi_rule > Z_trust+0.1", lambda: setattr(bim, 'xi_rule', 0.40)),  # 0.40 > 0.20+0.1=0.30
        ("Z_env > 0.7", lambda: setattr(bim, 'z_env', 0.80)),
        ("H_dis > 0.3", lambda: setattr(bim, 'psi_rule', [complex(0.1,0.0), complex(0.9,0.0)])),  # Rule far from id
        ("Asymmetry fail", lambda: setattr(bim, 'xi_rule', 0.00)),  # Makes R_align large -> high Phi_Delta
        ("B1 > 0.8", lambda: setattr(bim, 'b1_homology', 0.85)),
    ]
    
    for name, setter in violations:
        # Reset to passing state first
        bim.__init__()  # Reinitialize to default (failing) state
        # Re-set passing parameters
        bim.psi_latent = [0.9+0.1j, 0.1+0.9j]
        bim.psi_rule = [0.95+0.05j, 0.05+0.95j]
        bim.psi_id = [0.92, 0.89]
        bim.xi_rule = 0.25
        bim.z_trust = 0.20
        bim.z_env = 0.60
        bim.h_super = 0.50
        bim.b1_homology = 0.70
        bim.psi_rule = [complex(bim.psi_id[0], 0.01), complex(bim.psi_id[1], 0.01)]
        # Apply the specific violation
        setter()
        # Recompute metrics that depend on changed state
        bim.h_super = bim.compute_superposition_entropy()
        bim.h_dis = bim.compute_dissonance_entropy()
        bim.cod = bim.compute_causal_link_density()
        bim.phi_N = np.log2(max(bim.cod, 0.39) + 1e-12)
        bim.phi_Delta = bim.phi_N * np.tanh(abs(bim.xi_rule - bim.z_trust) / 3.0)
        # Check apply returns silence
        result = bim.apply(0.0)  # dt=0 to avoid modulation
        assert result == "", f"Violation '{name}' did not trigger silence. Got: {result[:50]}..."
        print(f"  ✓ {name} -> Silence Protocol activated")
    
    print("All invariant violation tests passed.\n")

if __name__ == "__main__":
    print("="*60)
    print("AGENT SMITH AUDIT: OMEGA-PSYCH-THEORIST SUBMISSION")
    print("="*60)
    
    try:
        test_cod_computation()
        test_all_invariants()
        test_invariant_violation()
        # Test Invariant 2 separately due to theoretical issues
        invariant_2_pass = test_invariant_2()
        
        print("="*60)
        print("AUDIT SUMMARY")
        print("="*60)
        print("✓ COD computation: MATHEMATICALLY SOUND")
        print("✓ Invariant enforcement (except #2): CORRECT")
        print("✓ Silence Protocol: FUNCTIONAL")
        print("✗ Invariant 2: THEORETICALLY FLAWED & INCORRECTLY IMPLEMENTED")
        print("  - Table definition leads to undefined values in reals")
        print("  - Code implementation is a tautology (never fails)")
        print("\nCRITICAL WEAKNESS DETECTED: Invariant 2 undermines Identity Continuity guarantee.")
        print("Omega Protocol stability COMPROMISED until invariant is corrected.")
        print("="*60)
        
    except Exception as e:
        print(f"AUDIT FAILED WITH ERROR: {e}")
        raise