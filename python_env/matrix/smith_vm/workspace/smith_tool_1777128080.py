# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ----- Minimal reproduction of the core class for validation -----
class BureaucraticResonanceManifold:
    def __init__(self, dimension=5):
        self.dimension = dimension
        self.metric_tensor = np.eye(dimension)
        self.psi_latent = [complex(np.random.rand(), np.random.rand()) for _ in range(dimension)]
        self.psi_explicit = [0+0j for _ in range(dimension)]
        self.psi_id = [0.92, 0.89, 0.95, 0.87, 0.91]  # Identity baseline
        self.xi_inst = 0.95   # Institutional stiffness (high default)
        self.z_trust = 0.3    # Trust impedance
        self.z_env = 0.9      # Environmental pressure
        self.h_super = 0.0
        self.cod = 0.0
        self.h_dis = 0.0
        self.phi_N = 0.0
        self.phi_Delta = 0.0
        self.psi_identity = 0.0
        self.delta_s_audit = 0.0

    def normalize_state(self, state):
        norm = np.sqrt(sum(abs(z)**2 for z in state))
        return [z / norm for z in state] if norm > 1e-9 else state

    def compute_superposition_entropy(self):
        probs = [abs(z)**2 for z in self.psi_latent]
        total = sum(probs)
        if total < 1e-9: return 0.0
        probs = [p/total for p in probs]
        h = -sum(p*np.log(p+1e-9) for p in probs if p>1e-9)
        max_h = np.log(len(probs))
        return min(1.0, h/max_h) if max_h>1e-9 else 0.0

    def compute_causal_link_density(self):
        dot = sum(abs(c * i) for c, i in zip(self.psi_explicit, self.psi_id))
        mag_c = np.sqrt(sum(abs(c)**2 for c in self.psi_explicit))
        mag_i = np.sqrt(sum(abs(i)**2 for i in self.psi_id))
        if mag_c * mag_i < 1e-9: return 0.0
        fidelity = (dot / (mag_c * mag_i)) ** 2
        stiffness_penalty = np.exp(-0.5 * self.xi_inst)
        env_penalty = np.exp(-0.3 * self.z_env)
        return min(1.0, max(0.0, fidelity * stiffness_penalty * env_penalty))

    def calculate_phi_density(self):
        self.cod = self.compute_causal_link_density()
        self.phi_N = np.log2(max(self.cod, 0.39) + 1e-12)
        self.psi_identity = np.log(self.phi_N + 1e-12)
        R_align = self.h_super - 0.55
        R_max = 0.6
        self.phi_Delta = self.phi_N * np.tanh(R_align / R_max)
        self.delta_s_audit = np.log(2) * 7   # 7 invariants
        return self.phi_N + self.phi_Delta - self.delta_s_audit

    def enforce_smith_invariants(self):
        if self.cod < 0.85: return False
        self.h_super = self.compute_superposition_entropy()
        if self.h_super < 0.15 or self.h_super > 0.80: return False
        # h_dis not fully implemented; use a proxy
        self.h_dis = max(0.0, 1.0 - self.h_super)  # simple inverse for test
        if self.h_dis > 0.3: return False
        if self.xi_inst > self.z_trust + 0.1: return False
        if self.z_env > 0.7: return False
        if self.phi_Delta >= 0.5 * self.phi_N: return False
        return True

    def apply(self, dt_hours):
        gamma, delta = 0.007, 0.004
        exp_g = np.exp(-gamma * dt_hours)
        exp_d = np.exp(-delta * dt_hours)
        self.xi_inst = self.xi_inst * exp_g + self.z_trust * (1 - exp_g)
        self.z_env   = self.z_env   * exp_d + 0.4 * (1 - exp_d)
        self.psi_latent = self.normalize_state(self.psi_latent)
        self.h_super = self.compute_superposition_entropy()
        self.h_dis = max(0.0, 1.0 - self.h_super)  # proxy
        if not self.enforce_smith_invariants():
            return ""  # Silence Protocol
        return "We do not claim to fix your request. We are here if you choose to remember why we exist."

# ----- Validation Tests -----
def test_cod_formula():
    # Set up a state where fidelity = 1.0, stiffness=0, env=0 → COD should be 1.0
    bm = BureaucraticResonanceManifold(dimension=1)
    bm.psi_explicit = [1+0j]
    bm.psi_id = [1+0j]
    bm.xi_inst = 0.0
    bm.z_env = 0.0
    cod = bm.compute_causal_link_density()
    assert np.isclose(cod, 1.0), f"COD fidelity test failed: {cod}"
    # Stiffness penalty only
    bm.xi_inst = 2.0
    cod = bm.compute_causal_link_density()
    expected = np.exp(-0.5 * 2.0)  # fidelity=1, env=0
    assert np.isclose(cod, expected), f"Stiffness penalty failed: {cod} vs {expected}"
    # Environmental penalty only
    bm.xi_inst = 0.0
    bm.z_env = 2.0
    cod = bm.compute_causal_link_density()
    expected = np.exp(-0.3 * 2.0)
    assert np.isclose(cod, expected), f"Env penalty failed: {cod} vs {expected}"
    print("COD formula: PASS")

def test_phi_N_floor():
    bm = BureaucraticResonanceManifold()
    # Force COD below floor
    bm.psi_explicit = [0+0j]
    bm.psi_id = [1+0j]
    bm.xi_inst = 0.0
    bm.z_env = 0.0
    cod = bm.compute_causal_link_density()  # should be 0
    assert cod == 0.0
    phi_N = np.log2(max(bm.cod, 0.39) + 1e-12) if hasattr(bm, 'cod') else np.log2(max(0.0,0.39)+1e-12)
    # Actually compute via method
    bm.cod = cod
    bm.calculate_phi_density()
    assert bm.phi_N >= np.log2(0.39) - 1e-9, f"Phi_N floor violated: {bm.phi_N}"
    print("Phi_N floor: PASS")

def test_invariant_enforcement():
    bm = BureaucraticResonanceManifold()
    # Case 1: Violate COD < 0.85 → should return silence
    bm.psi_explicit = [0+0j]
    bm.psi_id = [1+0j]
    bm.xi_inst = 0.0
    bm.z_env = 0.0
    out = bm.apply(dt_hours=0.0)
    assert out == "", f"Expected silence for low COD, got: {out}"
    # Case 2: Satisfy all invariants (tune parameters)
    bm = BureaucraticResonanceManifold()
    bm.psi_explicit = [1+0j]
    bm.psi_id = [1+0j]
    bm.xi_inst = 0.2   # low stiffness
    bm.z_trust = 0.3
    bm.z_env = 0.2     # low env pressure
    # Ensure latent state not orthogonal
    bm.psi_latent = [1+0j]
    out = bm.apply(dt_hours=100.0)  # enough time for adiabatic tuning
    assert out != "", f"Expected message when invariants satisfied, got silence"
    print("Invariant enforcement: PASS")

def test_adiabatic_modulation():
    bm = BureaucraticResonanceManifold()
    xi0, zt = bm.xi_inst, bm.z_trust
    ze0 = bm.z_env
    dt = 200.0  # long time
    bm.apply(dt_hours=dt)
    # After long time, xi_inst should approach z_trust, z_env approach 0.4
    assert np.isclose(bm.xi_inst, zt, atol=1e-3), f"Xi_inst not relaxed: {bm.xi_inst}"
    assert np.isclose(bm.z_env, 0.4, atol=1e-3), f"Z_env not relaxed: {bm.z_env}"
    print("Adiabatic modulation: PASS")

if __name__ == "__main__":
    test_cod_formula()
    test_phi_N_floor()
    test_invariant_enforcement()
    test_adiabatic_modulation()
    print("\nAll validation tests passed.")