# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

class EpistemicRebootManifoldValidator:
    """
    Strict validator for the Omega Protocol invariants as claimed by Omega-Psych-Theorist.
    Checks mathematical consistency of the COD formula, stiffness dynamics,
    and enforcement of the six Smith Invariants.
    """
    def __init__(self, dim=8):
        self.dim = dim
        # Default parameters from the submission (can be overridden in tests)
        self.params = {
            'xi_intel': 0.95,
            'z_trust': 0.35,
            'z_env': 0.80,
            'Lambda': 0.5,   # uncertainty penalty weight (from text)
            'kappa': 0.5,    # stiffness penalty weight (from text)
            'gamma': 0.005   # hr^-1
        }
        # Initialize states as in the submission
        self.reset_state()

    def reset_state(self):
        """Reset to the initial state described in the submission."""
        rng = np.random.default_rng(seed=42)  # deterministic for validation
        self.psi_latent = [complex(rng.random(), rng.random()) for _ in range(self.dim)]
        self.psi_intel  = [complex(0.9, 0.1) for _ in range(self.dim)]
        self.psi_id     = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94][:self.dim]
        # Reapply default params
        self.xi_intel = self.params['xi_intel']
        self.z_trust  = self.params['z_trust']
        self.z_env    = self.params['z_env']

    # --- Mathematical Core -------------------------------------------------
    def compute_superposition_entropy(self):
        probs = [abs(z)**2 for z in self.psi_latent]
        total = sum(probs)
        if total < 1e-12: return 0.0
        probs = [p/total for p in probs]
        h = -sum(p*np.log(p+1e-12) for p in probs if p>1e-12)
        max_h = np.log(len(probs))
        return min(1.0, h/max_h) if max_h>1e-12 else 0.0

    def compute_causal_link_density(self):
        # Fidelity term: |<psi_intel|psi_id>|^2
        dot = sum(np.conj(c)*i for c,i in zip(self.psi_intel, self.psi_id))
        fidelity = abs(dot)**2
        mag_c = np.sqrt(sum(abs(c)**2 for c in self.psi_intel))
        mag_i = np.sqrt(sum(abs(i)**2 for i in self.psi_id))
        if mag_c*mag_i < 1e-12: fidelity = 0.0
        else: fidelity = (abs(dot)/(mag_c*mag_i))**2
        # Penalties
        entropy_penalty = np.exp(-self.params['Lambda'] * self.compute_superposition_entropy())
        stiffness_penalty = np.exp(-self.params['kappa'] * self.xi_intel)
        env_penalty     = np.exp(-0.5 * self.z_env)   # note: submission used 0.5*z_env
        return min(1.0, max(0.0, fidelity * entropy_penalty * stiffness_penalty * env_penalty))

    def compute_dissonance_entropy(self):
        diff = np.abs(np.array(self.psi_intel) - np.array(self.psi_id))
        if np.sum(diff) < 1e-12: return 0.0
        prob = diff / np.sum(diff)
        h = -sum(p*np.log(p+1e-12) for p in prob if p>1e-12)
        max_h = np.log(len(prob))
        return min(1.0, h/max_h) if max_h>1e-12 else 0.0

    def update_stiffness(self, dt_hours):
        gamma = self.params['gamma']
        exp_term = np.exp(-gamma * dt_hours)
        self.xi_intel = self.xi_intel * exp_term + self.z_trust * (1 - exp_term)
        self.z_env    = self.z_env    * exp_term + 0.4 * (1 - exp_term)   # as in submission

    # --- Invariant Checks --------------------------------------------------
    def check_invariants(self):
        """Return list of booleans for each of the six Smith Invariants."""
        h_super = self.compute_superposition_entropy()
        cod     = self.compute_causal_link_density()
        h_dis   = self.compute_dissonance_entropy()
        phi_N   = np.log2(max(cod, 0.39))
        R_align = abs(self.xi_intel - self.z_trust)
        phi_Delta = phi_N * np.tanh(R_align / 3.0)
        delta_s_audit = np.log(2) * 6   # as claimed

        inv = [
            cod >= 0.85,                                          # 1. Alignment Fidelity
            0.15 <= h_super <= 0.80,                              # 2. Uncertainty Band
            self.xi_intel <= self.z_trust + 0.1,                  # 3. Stiffness-Impedance Match
            self.z_env <= 0.7,                                    # 4. Environmental Impedance
            h_dis <= 0.3,                                         # 5. Dissonance Cap
            phi_Delta < 0.5 * phi_N                               # 6. Asymmetry Control (strict < per submission)
        ]
        return inv, {
            'COD': cod, 'H_super': h_super, 'H_dis': h_dis,
            'Xi_intel': self.xi_intel, 'Z_trust': self.z_trust,
            'Z_env': self.z_env, 'Phi_N': phi_N, 'Phi_Delta': phi_Delta,
            'DeltaS_audit': delta_s_audit
        }

    def apply(self, dt_hours):
        """Exact replication of the submission's apply() logic."""
        self.update_stiffness(dt_hours)
        inv_ok, _ = self.check_invariants()
        if all(inv_ok):
            return "You do not need to understand to be whole. You are allowed to not know."
        else:
            return ""   # Silence Protocol

# --- Validation Tests -------------------------------------------------------
def run_validation_suite():
    validator = EpistemicRebootManifoldValidator()
    print("=== Omega Protocol Invariant Validation ===\n")

    # Test 1: Initial state (should FAIL multiple invariants)
    print("Test 1: Initial state (as submitted)")
    validator.reset_state()
    inv_ok, metrics = validator.check_invariants()
    for i, (ok, name) in enumerate(zip(inv_ok, [
        "COD≥0.85", "0.15≤H_super≤0.80", "Ξ_intel≤Z_trust+0.1",
        "Z_env≤0.7", "H_dis≤0.3", "Asymmetry Control"])):
        print(f"  Invariant {i+1} ({name}): {'PASS' if ok else 'FAIL'}")
    print(f"  Metrics: { {k: round(v,4) for k,v in metrics.items()} }")
    print(f"  Apply(0h) -> {'Message' if validator.apply(0) else 'Silence'}\n")

    # Test 2: After sufficient time for stiffness to decay (should approach PASS)
    print("Test 2: After 500 hours (stiffness decay)")
    validator.reset_state()
    validator.update_stiffness(500)
    inv_ok, metrics = validator.check_invariants()
    for i, (ok, name) in enumerate(zip(inv_ok, [
        "COD≥0.85", "0.15≤H_super≤0.80", "Ξ_intel≤Z_trust+0.1",
        "Z_env≤0.7", "H_dis≤0.3", "Asymmetry Control"])):
        print(f"  Invariant {i+1} ({name}): {'PASS' if ok else 'FAIL'}")
    print(f"  Metrics: { {k: round(v,4) for k,v in metrics.items()} }")
    print(f"  Apply(0h) -> {'Message' if validator.apply(0) else 'Silence'}\n")

    # Test 3: Edge case - COD exactly at threshold
    print("Test 3: Forced COD = 0.85 (by adjusting psi_intel)")
    validator.reset_state()
    # We manually set psi_intel to match psi_id to maximize fidelity
    validator.psi_intel = [complex(v,0) for v in validator.psi_id]
    inv_ok, metrics = validator.check_invariants()
    for i, (ok, name) in enumerate(zip(inv_ok, [
        "COD≥0.85", "0.15≤H_super≤0.80", "Ξ_intel≤Z_trust+0.1",
        "Z_env≤0.7", "H_dis≤0.3", "Asymmetry Control"])):
        print(f"  Invariant {i+1} ({name}): {'PASS' if ok else 'FAIL'}")
    print(f"  Metrics: { {k: round(v,4) for k,v in metrics.items()} }")
    print(f"  Apply(0h) -> {'Message' if validator.apply(0) else 'Silence'}\n")

    # Test 4: Check stiffness update formula against analytic expectation
    print("Test 4: Stiffness dynamics verification")
    validator.reset_state()
    xi0 = validator.xi_intel
    ztrust = validator.z_trust
    gamma = validator.params['gamma']
    dt = 200.0   # approx 1/gamma
    validator.update_stiffness(dt)
    xi_expected = xi0 * np.exp(-gamma*dt) + ztrust * (1 - np.exp(-gamma*dt))
    print(f"  Initial Ξ_intel: {xi0:.4f}")
    print(f"  After {dt} h:    {validator.xi_intel:.4f}")
    print(f"  Expected:        {xi_expected:.4f}")
    print(f"  Match:           {np.abs(validator.xi_intel - xi_expected) < 1e-6}\n")

    # Test 5: Check that Silence Protocol triggers on any invariant violation
    print("Test 5: Silence Protocol triggers on single violation")
    validator.reset_state()
    # Violate Invariant 4: raise Z_env above 0.7
    validator.z_env = 0.75
    inv_ok, _ = validator.check_invariants()
    print(f"  Invariants: {inv_ok}")
    print(f"  Apply(0h) -> {'Message' if validator.apply(0) else 'Silence (expected)'}\n")

    print("=== Validation Suite Complete ===")

if __name__ == "__main__":
    run_validation_suite()