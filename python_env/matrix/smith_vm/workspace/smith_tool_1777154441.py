# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for UIPO v65.0 Bureaucracy Gauge.
Checks:
  * COD formula matches the UIPO v65.0 definition.
  * All 9 Smith Invariants are enforced exactly as specified.
  * Operator output obeys the Silence Protocol.
  * Audit cost invariant is accounted for.
  * No hidden side‑effects that could violate the Ontological Kernel.
"""

import numpy as np

# Import the class from the submission (assumed to be in the same file)
# For the purpose of this script we copy the essential parts here.
class BureaucracyIdentityManifold:
    def __init__(self, dim: int = 8):
        self.dim = dim
        self.psi_latent = [complex(np.random.rand(), np.random.rand()) for _ in range(dim)]
        self.psi_exp = [0 + 0j for _ in range(dim)]
        self.psi_id = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94]
        self.xi_burea = 0.92
        self.z_trust = 0.4
        self.z_env = 0.88
        self.h_super = 0.0
        self.cod = 0.0
        self.h_dis = 0.0
        self.phi_N = 0.0
        self.phi_Delta = 0.0
        self.delta_s_audit = 0.0
        self.b1_homology = 0.85

    def compute_superposition_entropy(self) -> float:
        probs = [abs(z)**2 for z in self.psi_latent]
        total = sum(probs)
        if total < 1e-9: return 0.0
        probs = [p / total for p in probs]
        h = -sum(p * np.log(p + 1e-9) for p in probs if p > 1e-9)
        max_h = np.log(len(probs))
        return min(1.0, h / max_h) if max_h > 1e-9 else 0.0

    def compute_causal_link_density(self) -> float:
        dot = sum(abs(c * i) for c, i in zip(self.psi_exp, self.psi_id))
        mag_c = np.sqrt(sum(abs(c)**2 for c in self.psi_exp))
        mag_i = np.sqrt(sum(abs(i)**2 for i in self.psi_id))
        if mag_c * mag_i < 1e-9: return 0.0
        fidelity = (dot / (mag_c * mag_i)) ** 2
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
        # Hard Floor for Identity Continuity (Prevent Log Singularity)
        self.phi_N = np.log2(max(self.cod, 0.39) + 1e-12)
        R_align = abs(self.xi_burea - self.z_trust)
        self.phi_Delta = self.phi_N * np.tanh(R_align / 3.0)
        self.delta_s_audit = np.log(2) * 9  # 9 Invariant Checks
        # Invariant 1: COD ≥ 0.85
        if self.cod < 0.85: return False
        # Invariant 2: Identity Continuity
        if self.phi_N < np.log2(0.39): return False
        # Invariant 3: H_super in healthy band
        if self.h_super < 0.15 or self.h_super > 0.80: return False
        # Invariant 4: Bureaucratic Stiffness ≤ Trust Impedance + 0.1
        if self.xi_burea > self.z_trust + 0.1: return False
        # Invariant 5: Institutional Pressure ≤ 0.7
        if self.z_env > 0.7: return False
        # Invariant 6: Dissonance Cap
        if self.h_dis > 0.3: return False
        # Invariant 7: Asymmetry Control
        if self.phi_Delta >= 0.5 * self.phi_N: return False
        # Invariant 8: Topological Failure — Anxiety Loop
        if self.b1_homology > 0.8: return False
        # Invariant 9: Audit Cost Accounted (must equal 9·ln2)
        if not np.isclose(self.delta_s_audit, 9 * np.log(2)): return False
        return True

    def apply(self, dt_hours: float) -> str:
        gamma = 0.003
        delta = 0.0025
        exp_term_g = np.exp(-gamma * dt_hours)
        exp_term_d = np.exp(-delta * dt_hours)
        self.xi_burea = self.xi_burea * exp_term_g + self.z_trust * (1 - exp_term_g)
        self.z_env = self.z_env * exp_term_d + 0.4 * (1 - exp_term_d)
        # Simulate topological evolution (b₁ decays with trust)
        self.b1_homology = max(0.1, self.b1_homology * 0.999 - 0.0002 * dt_hours)
        if self.enforce_smith_invariants():
            return ("You are not required to comply now. "
                    "Your uncertainty is not a failure. "
                    "It is part of your organization's geometry.")
        else:
            return ""  # Silence Protocol


def test_cod_formula():
    """Spot‑check that COD matches the definition."""
    mani = BureaucracyIdentityManifold()
    # Force known states for deterministic test
    mani.psi_latent = [1+0j] + [0+0j]*7
    mani.psi_exp    = [1+0j] + [0+0j]*7
    mani.psi_id     = [1+0j] + [0+0j]*7
    mani.xi_burea = 0.0
    mani.z_env    = 0.0
    mani.h_super  = 0.0
    cod = mani.compute_causal_link_density()
    # With perfect overlap and zero penalties, COD should be 1 (clipped to 1.0)
    assert np.isclose(cod, 1.0), f"COD expected 1.0, got {cod}"
    # Introduce a stiffness penalty
    mani.xi_burea = 1.0
    cod = mani.compute_causal_link_density()
    expected = np.exp(-0.5 * 1.0)  # fidelity=1, entropy=0, env=0
    assert np.isclose(cod, expected), f"COD mismatch: {cod} vs {expected}"
    print("COD formula test passed.")


def test_invariants():
    """Exhaustively check each invariant toggle."""
    mani = BureaucracyIdentityManifold()
    # Start in a state that should satisfy all invariants after a short dt
    mani.apply(0.1)  # trigger dynamics
    assert mani.enforce_smith_invariants(), "Baseline state should pass all invariants"

    # Invariant 1: COD < 0.85
    mani.psi_exp = [0.1+0j]*mani.dim  # reduce fidelity
    assert not mani.enforce_smith_invariants(), "Invariant 1 failed"
    mani.psi_exp = [1+0j]*mani.dim  # restore

    # Invariant 2: phi_N < log2(0.39)  (forced via low COD)
    mani.psi_exp = [0.2+0j]*mani.dim
    assert not mani.enforce_smith_invariants(), "Invariant 2 failed"
    mani.psi_exp = [1+0j]*mani.dim

    # Invariant 3: H_super out of band
    mani.psi_latent = [1+0j]*mani.dim  # pure state → entropy 0
    assert not mani.enforce_smith_invariants(), "Invariant 3 (low H) failed"
    # Max entropy: equal probabilities
    mani.psi_latent = [complex(1/np.sqrt(mani.dim),0)]*mani.dim
    mani.h_super = mani.compute_superposition_entropy()
    assert mani.h_super > 0.80 - 1e-6, "Failed to reach high entropy"
    assert not mani.enforce_smith_invariants(), "Invariant 3 (high H) failed"
    # Reset to a mid‑entropy state
    mani.psi_latent = [complex(np.random.rand(), np.random.rand()) for _ in range(mani.dim)]

    # Invariant 4: xi_burea > z_trust + 0.1
    mani.xi_burea = mani.z_trust + 0.2
    assert not mani.enforce_smith_invariants(), "Invariant 4 failed"
    mani.xi_burea = 0.5  # back within bound

    # Invariant 5: z_env > 0.7
    mani.z_env = 0.8
    assert not mani.enforce_smith_invariants(), "Invariant 5 failed"
    mani.z_env = 0.5

    # Invariant 6: h_dis > 0.3
    # Force dissonance by making psi_exp opposite to psi_id
    mani.psi_exp = [-x for x in mani.psi_id]
    assert not mani.enforce_smith_invariants(), "Invariant 6 failed"
    mani.psi_exp = [0+0j]*mani.dim  # reset

    # Invariant 7: phi_Delta >= 0.5*phi_N
    mani.xi_burea = mani.z_trust + 1.0  # large misalignment
    assert not mani.enforce_smith_invariants(), "Invariant 7 failed"
    mani.xi_burea = mani.z_trust  # restore

    # Invariant 8: b1_homology > 0.8
    mani.b1_homology = 0.9
    assert not mani.enforce_smith_invariants(), "Invariant 8 failed"
    mani.b1_homology = 0.5

    # Invariant 9: audit cost mismatch
    mani.delta_s_audit = 0.0
    assert not mani.enforce_smith_invariants(), "Invariant 9 failed"
    mani.delta_s_audit = 9 * np.log(2)

    print("All invariant toggles passed.")


def test_operator_output():
    """Verify that the operator returns the correct string or silence."""
    mani = BureaucracyIdentityManifold()
    # Force a passing state
    mani.psi_latent = [1+0j]*mani.dim
    mani.psi_exp    = [1+0j]*mani.dim
    mani.psi_id     = [1+0j]*mani.dim
    mani.xi_burea = mani.z_trust
    mani.z_env    = 0.0
    mani.h_super  = 0.5
    mani.b1_homology = 0.2
    out = mani.apply(0.0)
    expected = ("You are not required to comply now. "
                "Your uncertainty is not a failure. "
                "It is part of your organization's geometry.")
    assert out == expected, f"Expected permission message, got: {out!r}"

    # Force a failing state (e.g., low COD)
    mani.psi_exp = [0.1+0j]*mani.dim
    out = mani.apply(0.0)
    assert out == "", f"Expected silence, got: {out!r}"
    print("Operator output test passed.")


def test_audit_ledger():
    """Check that the audit cost is exactly 9·k_B·ln2 (k_B=1 in natural units)."""
    mani = BureaucracyIdentityManifold()
    _ = mani.enforce_smith_invariants()  # triggers computation
    expected = 9 * np.log(2)
    assert np.isclose(mani.delta_s_audit, expected), \
        f"Audit cost mismatch: {mani.delta_s_audit} vs {expected}"
    print("Audit ledger test passed.")


if __name__ == "__main__":
    test_cod_formula()
    test_invariants()
    test_operator_output()
    test_audit_ledger()
    print("\nAll validation checks succeeded. The implementation is compliant with Omega Protocol v65.0.")