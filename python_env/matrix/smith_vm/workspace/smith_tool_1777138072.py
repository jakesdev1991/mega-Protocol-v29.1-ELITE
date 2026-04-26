# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Agent Smith Validation Script
# Purpose: Verify that the TraumaIdentityManifold implementation
#          strictly adheres to the Omega Protocol v64.2 Smith Invariants
#          and that the COD derivation is mathematically consistent.

import numpy as np

# ----- Exact copy of the provided class (for self‑contained validation) -----
class TraumaIdentityManifold:
    def __init__(self, dim: int = 6):
        self.dim = dim
        self.psi_latent = [complex(np.random.rand(), np.random.rand()) for _ in range(dim)]
        self.psi_perf   = [0 + 0j for _ in range(dim)]
        self.psi_id     = [0.92, 0.89, 0.95, 0.87, 0.91, 0.94]   # Identity Baseline
        self.xi_perf    = 0.95   # High Performance Rigidity
        self.z_trust    = 0.3    # Low Self‑Safety (Trauma State)
        self.z_env      = 0.9    # High External Expectation
        self.h_super    = 0.0
        self.cod        = 0.0
        self.h_dis      = 0.0
        self.phi_N      = 0.0
        self.phi_Delta  = 0.0
        self.delta_s_audit = 0.0
        self.b1_homology = 0.85   # Topological defect: Anxiety Loop

    # ----- Helper entropies (as implied in the text) -----
    def compute_superposition_entropy(self) -> float:
        # Shannon‑like entropy of the latent state amplitudes
        probs = np.abs(self.psi_latent) ** 2
        probs = probs / probs.sum() if probs.sum() > 0 else probs
        return -np.sum(probs * np.log(probs + 1e-12))

    def compute_dissonance_entropy(self) -> float:
        # Simple proxy: variance between latent and performance states
        diff = np.abs(np.array(self.psi_latent) - np.array(self.psi_perf))
        return np.var(diff) / (np.mean(diff) + 1e-12)

    # ----- COD computation (exact formula from the proposal) -----
    def compute_causal_link_density(self) -> float:
        dot   = sum(abs(c * i) for c, i in zip(self.psi_perf, self.psi_id))
        mag_c = np.sqrt(sum(abs(c)**2 for c in self.psi_perf))
        mag_i = np.sqrt(sum(abs(i)**2 for i in self.psi_id))
        if mag_c * mag_i < 1e-9:
            fidelity = 0.0
        else:
            fidelity = (dot / (mag_c * mag_i)) ** 2
        stiffness_penalty = np.exp(-0.5 * self.xi_perf)
        env_penalty       = np.exp(-0.3 * self.z_env)
        entropy_penalty   = np.exp(-0.4 * self.h_super)
        return min(1.0, max(0.0, fidelity * stiffness_penalty * env_penalty * entropy_penalty))

    # ----- Smith Invariant Enforcer (exact) -----
    def enforce_smith_invariants(self) -> bool:
        self.h_super = self.compute_superposition_entropy()
        self.h_dis   = self.compute_dissonance_entropy()
        self.cod     = self.compute_causal_link_density()
        # Hard Floor for Identity Continuity (Prevent Log Singularity)
        self.phi_N   = np.log2(max(self.cod, 0.39) + 1e-12)
        R_align      = abs(self.xi_perf - self.z_trust)
        self.phi_Delta = self.phi_N * np.tanh(R_align / 3.0)
        self.delta_s_audit = np.log(2) * 9   # 9 invariant checks × Landauer

        # Invariant 1: COD ≥ 0.85
        if self.cod < 0.85:  return False
        # Invariant 2: Identity Continuity
        if self.phi_N < np.log2(0.39): return False
        # Invariant 3: Uncertainty Band
        if self.h_super < 0.15 or self.h_super > 0.80: return False
        # Invariant 4: Stiffness‑Impedance Match
        if self.xi_perf > self.z_trust + 0.1: return False
        # Invariant 5: Environmental Impedance
        if self.z_env > 0.7: return False
        # Invariant 6: Dissonance Cap
        if self.h_dis > 0.3: return False
        # Invariant 7: Asymmetry Control
        if self.phi_Delta >= 0.5 * self.phi_N: return False
        # Invariant 8: Anxiety Loop Guard
        if self.b1_homology > 0.8: return False
        # Invariant 9: Audit Cost Accounted (always true if we reach here)
        return True

    # ----- Adiabatic modulation and message emission -----
    def apply(self, dt_hours: float) -> str:
        gamma = 0.005
        delta = 0.004
        exp_g = np.exp(-gamma * dt_hours)
        exp_d = np.exp(-delta * dt_hours)
        self.xi_perf = self.xi_perf * exp_g + self.z_trust * (1 - exp_g)
        self.z_env   = self.z_env   * exp_d + 0.4 * (1 - exp_d)
        # Simulate topological evolution (b₁ decays with trust)
        self.b1_homology = max(0.1, self.b1_homology * 0.999 - 0.0002 * dt_hours)
        if self.enforce_smith_invariants():
            return ("You are not required to perform now. "
                    "Your anxiety is the energy of your uncollapsed self. "
                    "We are here if you choose to remember your safety.")
        else:
            return ""   # Silence Protocol

# ----- Validation Routine -----
def validate_invariants():
    """Run a battery of deterministic and random states to ensure
       the Smith invariants are never violated when a non‑empty message is returned."""
    np.random.seed(42)   # reproducibility
    failures = []

    # 1. Deterministic baseline (the instance as initialized)
    tm = TraumaIdentityManifold()
    msg = tm.apply(dt_hours=0.0)   # no time evolution yet
    if msg == "" and not tm.enforce_smith_invariants():
        # Expected: initial state violates several invariants (high xi_perf, high z_env, b1>0.8)
        pass
    else:
        failures.append("Baseline should be silent but returned a message or passed invariants.")

    # 2. After sufficient adiabatic decay – should become compliant
    tm2 = TraumaIdentityManifold()
    # Evolve long enough to bring xi_perf ~ z_trust and z_env down, b1 decayed
    msg2 = tm2.apply(dt_hours=300.0)   # ~12.5 days
    if msg2 == "":
        failures.append("After 300h evolution the manifold should be compliant and emit a message.")
    else:
        # Verify that all invariants truly hold
        if not tm2.enforce_smith_invariants():
            failures.append("Message emitted but invariants still violated.")
        # Additionally, check the COD formula numerically
        cod_recalc = tm2.compute_causal_link_density()
        if abs(cod_recalc - tm2.cod) > 1e-6:
            failures.append("COD storage mismatch with recomputed value.")
        # Check that COD >= 0.85 (hard gate for message)
        if tm2.cod < 0.85:
            failures.append("Message emitted while COD < 0.85.")
        # Check that phi_N >= log2(0.39)
        if tm2.phi_N < np.log2(0.39):
            failures.append("Message emitted while phi_N below hard floor.")
        # Uncertainty band
        if not (0.15 <= tm2.h_super <= 0.80):
            failures.append("Message emitted while h_super outside [0.15,0.80].")
        # Stiffness‑impedance
        if tm2.xi_perf > tm2.z_trust + 0.1:
            failures.append("Message emitted while xi_perf > z_trust + 0.1.")
        # Environmental impedance
        if tm2.z_env > 0.7:
            failures.append("Message emitted while z_env > 0.7.")
        # Dissonance cap
        if tm2.h_dis > 0.3:
            failures.append("Message emitted while h_dis > 0.3.")
        # Asymmetry control
        if tm2.phi_Delta >= 0.5 * tm2.phi_N:
            failures.append("Message emitted while phi_Delta >= 0.5*phi_N.")
        # Anxiety loop guard
        if tm2.b1_homology > 0.8:
            failures.append("Message emitted while b1_homology > 0.8.")
        # Audit cost invariant is trivially satisfied if we reach here.

    # 3. Random stress test – ensure no false positives
    for _ in range(200):
        tm_r = TraumaIdentityManifold()
        # Randomize key parameters within plausible ranges
        tm_r.xi_perf = np.random.uniform(0.0, 1.0)
        tm_r.z_trust = np.random.uniform(0.0, 1.0)
        tm_r.z_env   = np.random.uniform(0.0, 1.0)
        tm_r.b1_homology = np.random.uniform(0.0, 1.0)
        # Force a random latent state
        tm_r.psi_latent = [complex(np.random.randn(), np.random.randn()) for _ in range(tm_r.dim)]
        # Evolve a random time step
        dt = np.random.uniform(0, 500)
        msg_r = tm_r.apply(dt_hours=dt)
        passed = tm_r.enforce_smith_invariants()
        if (msg_r != "") != passed:
            failures.append(f"Random test mismatch: msg={bool(msg_r)} vs passed={passed}")
            break

    if failures:
        print("VALIDATION FAILED:")
        for f in failures:
            print(" -", f)
        return False
    else:
        print("VALIDATION PASSED: All Smith invariants correctly enforced.")
        return True

# ----- Execute validation -----
if __name__ == "__main__":
    validate_invariants()