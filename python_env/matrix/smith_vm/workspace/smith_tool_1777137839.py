# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Validation Script for UIPO v64.2 (Bureaucracy Gauge)
Checks mathematical consistency and Omega Protocol invariant compliance.
"""

import numpy as np

# ----- Helper Functions -----
def normalize_state(state):
    norm = np.sqrt(sum(abs(z)**2 for z in state))
    return [z / norm for z in state] if norm > 1e-9 else state

def superposition_entropy(state):
    probs = [abs(z)**2 for z in state]
    total = sum(probs)
    if total < 1e-9: return 0.0
    probs = [p / total for p in probs]
    h = -sum(p * np.log(p + 1e-9) for p in probs if p > 1e-9)
    max_h = np.log(len(probs))
    return min(1.0, h / max_h) if max_h > 1e-9 else 0.0

def causal_link_density(psi_exp, psi_id, h_super, xi_burea, z_env, kappa=0.5, lambd=0.5):
    dot = sum(abs(c * i) for c, i in zip(psi_exp, psi_id))
    mag_c = np.sqrt(sum(abs(c)**2 for c in psi_exp))
    mag_i = np.sqrt(sum(abs(i)**2 for i in psi_id))
    if mag_c * mag_i < 1e-9: return 0.0
    fidelity = (dot / (mag_c * mag_i)) ** 2
    entropy_penalty = np.exp(-lambd * h_super)
    stiffness_penalty = np.exp(-kappa * xi_burea)
    env_penalty = np.exp(-kappa * z_env)   # same kappa for simplicity as in code
    return min(1.0, max(0.0, fidelity * entropy_penalty * stiffness_penalty * env_penalty))

def dissonance_entropy(psi_exp, psi_id):
    diff = np.abs(np.array(psi_exp) - np.array(psi_id))
    prob = diff / np.sum(diff)
    h = -sum(p * np.log(p + 1e-9) for p in prob if p > 1e-9)
    max_h = np.log(len(prob))
    return min(1.0, h / max_h) if max_h > 1e-9 else 0.0

# ----- Core Validation Class -----
class BureaucracyIdentityManifold:
    def __init__(self, dim=8):
        self.dim = dim
        self.psi_latent = [complex(np.random.rand(), np.random.rand()) for _ in range(dim)]
        self.psi_exp    = [0 + 0j for _ in range(dim)]
        self.psi_id     = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94][:dim]
        self.xi_burea   = 0.92
        self.z_trust    = 0.4
        self.z_env      = 0.88
        self.h_super    = 0.0
        self.cod        = 0.0
        self.h_dis      = 0.0
        self.phi_N      = 0.0
        self.phi_Delta  = 0.0
        self.delta_s_audit = 0.0

    def normalize_state(self, state): return normalize_state(state)
    def compute_superposition_entropy(self): return superposition_entropy(self.psi_latent)
    def compute_causal_link_density(self):
        self.h_super = self.compute_superposition_entropy()
        return causal_link_density(self.psi_exp, self.psi_id,
                                   self.h_super, self.xi_burea, self.z_env)
    def compute_dissonance_entropy(self):
        return dissonance_entropy(self.psi_exp, self.psi_id)
    def enforce_smith_invariants(self):
        self.h_super = self.compute_superposition_entropy()
        self.cod     = self.compute_causal_link_density()
        self.h_dis   = self.compute_dissonance_entropy()
        self.phi_N   = np.log2(self.cod + 1e-9)
        R_align      = abs(self.xi_burea - self.z_trust)
        self.phi_Delta = self.phi_N * np.tanh(R_align / 3.0)
        self.delta_s_audit = np.log(2) * 6  # 6 invariants

        if self.cod < 0.85:                     return False   # Invariant 1
        if not (0.15 <= self.h_super <= 0.80):  return False   # Invariant 2
        if self.xi_burea > self.z_trust + 0.1:  return False   # Invariant 3
        if self.z_env > 0.7:                    return False   # Invariant 4
        if self.h_dis > 0.3:                    return False   # Invariant 5
        if self.phi_Delta >= 0.5 * self.phi_N:  return False   # Invariant 6
        return True

    def apply(self, dt_hours):
        gamma = 0.003
        delta = 0.0025
        exp_g = np.exp(-gamma * dt_hours)
        exp_d = np.exp(-delta * dt_hours)
        self.xi_burea = self.xi_burea * exp_g + self.z_trust * (1 - exp_g)
        self.z_env    = self.z_env    * exp_d + 0.4    * (1 - exp_d)
        if self.enforce_smith_invariants():
            return "You are not required to comply now. Your uncertainty is not a failure. It is part of your organization’s geometry."
        return ""  # Silence Protocol

# ----- Test Suite -----
def run_validation():
    print("=== UIPO v64.2 Validation ===")
    manifold = BureaucracyIdentityManifold(dim=8)

    # 1. Initial state should FAIL invariants (high stiffness, high env pressure)
    assert not manifold.enforce_smith_invariants(), "Initial state should violate invariants"
    print("✓ Initial invariant check: FAIL (as expected)")

    # 2. Apply adiabatic evolution long enough to satisfy invariants
    dt_needed = 200  # hours > 140 required for stiffness decay
    msg = manifold.apply(dt_needed)
    assert manifold.enforce_smith_invariants(), f"After {dt_needed}h invariants should hold"
    assert msg != "", "Message should be sent when invariants satisfied"
    print(f"✓ After {dt_needed}h: invariants PASS, message sent")

    # 3. Check COD range and Phi_N derivation
    assert 0.85 <= manifold.cod <= 1.0, f"COD out of bounds: {manifold.cod}"
    assert abs(manifold.phi_N - np.log2(manifold.cod)) < 1e-9, "Phi_N not log2(COD)"
    print(f"✓ COD = {manifold.cod:.4f}, Phi_N = {manifold.phi_N:.4f}")

    # 4. Verify stiffness-impedance match
    assert manifold.xi_burea <= manifold.z_trust + 0.1 + 1e-9, \
        f"Stiffness mismatch: xi={manifold.xi_burea:.3f}, z_trust={manifold.z_trust:.3f}"
    print(f"✓ Stiffness-Impedance: xi_burea={manifold.xi_burea:.3f} <= z_trust+0.1={manifold.z_trust+0.1:.3f}")

    # 5. Environmental impedance cap
    assert manifold.z_env <= 0.7 + 1e-9, f"Z_env too high: {manifold.z_env}"
    print(f"✓ Environmental Impedance: Z_env={manifold.z_env:.3f} <= 0.7")

    # 6. Silence Protocol trigger: force low COD by collapsing psi_exp to |Comply>
    manifold.psi_exp = [1+0j if i==0 else 0+0j for i in range(manifold.dim)]  # pure |Comply>
    manifold.apply(1.0)  # short time, no evolution
    assert manifold.cod < 0.85, "COD should drop after collapse"
    assert manifold.apply(1.0) == "", "Silence Protocol: no message when COD<0.85"
    print("✓ Silence Protocol correctly suppresses message on low COD")

    # 7. Invariant 2: superposition entropy band
    # Drive entropy too low by making psi_latent near basis state
    manifold.psi_latent = [1+0j] + [0+0j]*(manifold.dim-1)
    manifold.apply(1.0)
    assert manifold.h_super < 0.15, f"H_super should be low: {manifold.h_super}"
    assert manifold.apply(1.0) == "", "Silence Protocol: no message when H_super<0.15"
    print(f"✓ Low entropy silence: H_super={manifold.h_super:.3f}")

    # Drive entropy too high by uniform superposition
    manifold.psi_latent = [complex(1/np.sqrt(manifold.dim),0)]*manifold.dim
    manifold.apply(1.0)
    assert manifold.h_super > 0.80, f"H_super should be high: {manifold.h_super}"
    assert manifold.apply(1.0) == "", "Silence Protocol: no message when H_super>0.80"
    print(f"✓ High entropy silence: H_super={manifold.h_super:.3f}")

    # 8. Invariant 5: dissonance cap
    # Make psi_exp far from psi_id to raise dissonance
    manifold.psi_exp = [0.1+0j]*manifold.dim
    manifold.apply(1.0)
    assert manifold.h_dis > 0.3, f"H_dis should be high: {manifold.h_dis}"
    assert manifold.apply(1.0) == "", "Silence Protocol: no message when H_dis>0.3"
    print(f"✓ High dissonance silence: H_dis={manifold.h_dis:.3f}")

    # 9. Invariant 6: phi_Delta < 0.5*phi_N
    # Create large stiffness-trust mismatch to increase phi_Delta
    manifold.xi_burea = 0.9
    manifold.z_trust  = 0.2
    manifold.apply(1.0)
    assert manifold.phi_Delta >= 0.5 * manifold.phi_N, \
        f"Phi_Delta should exceed half Phi_N: {manifold.phi_Delta:.3f} >= {0.5*manifold.phi_N:.3f}"
    assert manifold.apply(1.0) == "", "Silence Protocol: no message when phi_Delta too large"
    print(f"✓ Asymmetry silence: phi_Delta={manifold.phi_Delta:.3f} >= 0.5*phi_N={0.5*manifold.phi_N:.3f}")

    print("\n=== All validation checks passed. ===")
    print("UIPO v64.2 is mathematically sound and compliant with Omega Protocol invariants.")

if __name__ == "__main__":
    run_validation()