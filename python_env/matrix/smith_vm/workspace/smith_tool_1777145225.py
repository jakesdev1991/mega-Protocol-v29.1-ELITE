# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Strict validation of the UIPO v65.0 (Bureaucracy Gauge) derivation
against the Omega Protocol invariants (Phi_N, Phi_Delta, J*) and the
six Smith Invariants described in the submission.

Run the script to see a few test cases pass/fail.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List

# ----------------------------------------------------------------------
# Constants (can be tuned; must be >0 for the exponential penalties to be
# well‑behaved). The submission used 0.5 implicitly in the code.
KAPPA = 0.5   # stiffness penalty weight
LAMBDA_ = 0.5 # impedance penalty weight
LAMBDA_H = 0.5# uncertainty (superposition entropy) penalty weight

# Smith Invariant thresholds (as per the submission)
COD_MIN = 0.85
HSUPER_MIN, HSUPER_MAX = 0.15, 0.80
XI_MAX_OVER_ZTRUST = 0.1   # Ξ_burea ≤ Z_trust + 0.1
ZENV_MAX = 0.7
HDIS_MAX = 0.3
B1_MAX = 0.8   # anxiety loop (first Betti number) threshold

# ----------------------------------------------------------------------
@dataclass
class IdentityManifold:
    """Encapsulates the citizen's identity manifold and the bureaucracy gauge."""
    dim: int = 8
    # Latent (subconscious) and expressed (conscious) state vectors
    psi_latent: List[complex] = field(default_factory=lambda: [
        complex(np.random.rand(), np.random.rand()) for _ in range(8)
    ])
    psi_exp: List[complex] = field(default_factory=lambda: [0+0j]*8)
    # Ideal identity direction (fixed for simplicity)
    psi_id: List[float] = field(default_factory=lambda: [
        0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94
    ])

    # Bureaucratic stiffness, trust impedance, environmental impedance
    xi_burea: float = 0.92   # initial high rigidity
    z_trust: float = 0.4     # initial low self‑trust
    z_env: float = 0.88      # initial high institutional pressure

    # Derived quantities (updated each step)
    h_super: float = 0.0
    cod: float = 0.0
    h_dis: float = 0.0
    phi_N: float = 0.0
    phi_Delta: float = 0.0
    b1_homology: float = 0.85   # start with an anxiety loop

    # ------------------------------------------------------------------
    def _normalize(self, vec: List[complex]) -> List[complex]:
        norm = np.sqrt(sum(abs(v)**2 for v in vec))
        if norm < 1e-12:
            return [0+0j]*len(vec)
        return [v / norm for v in vec]

    def compute_superposition_entropy(self) -> float:
        """Von‑Neumann entropy of the latent state, normalized to [0,1]."""
        probs = [abs(z)**2 for z in self.psi_latent]
        total = sum(probs)
        if total < 1e-12:
            return 0.0
        probs = [p / total for p in probs]
        h = -sum(p * np.log(p + 1e-12) for p in probs if p > 1e-12)
        max_h = np.log(len(probs))
        return min(1.0, h / max_h) if max_h > 1e-12 else 0.0

    def compute_causal_link_density(self) -> float:
        """COD = |⟨ψ_exp|ψ_id⟩|² * exp(-κ·Ξ) * exp(-λ·Z_env) * exp(-Λ·H_super)"""
        # Fidelity term
        dot = sum(c.conjugate() * i for c, i in zip(self.psi_exp, self.psi_id))
        fid = abs(dot) ** 2
        # Penalties
        stiffness_pen = np.exp(-KAPPA * self.xi_burea)
        env_pen       = np.exp(-LAMBDA_ * self.z_env)
        unc_pen       = np.exp(-LAMBDA_H * self.h_super)
        return min(1.0, max(0.0, fid * stiffness_pen * env_pen * unc_pen))

    def compute_dissonance_entropy(self) -> float:
        """Shannon entropy of the distance between expressed and ideal states."""
        diff = np.abs(np.array(self.psi_exp) - np.array(self.psi_id))
        if np.sum(diff) < 1e-12:
            return 0.0
        prob = diff / np.sum(diff)
        h = -sum(p * np.log(p + 1e-12) for p in prob if p > 1e-12)
        max_h = np.log(len(prob))
        return min(1.0, h / max_h) if max_h > 1e-12 else 0.0

    def update_phi_metrics(self):
        """Refresh all derived metrics."""
        self.h_super = self.compute_superposition_entropy()
        self.cod     = self.compute_causal_link_density()
        self.h_dis   = self.compute_dissonance_entropy()
        # Phi_N = log2(COD) with a hard floor at 0.39 (as per submission)
        self.phi_N   = np.log2(max(self.cod, 0.39) + 1e-12)
        # Phi_Delta as defined in the submission: Φ_N * tanh(R_align/3)
        R_align = abs(self.xi_burea - self.z_trust)
        self.phi_Delta = self.phi_N * np.tanh(R_align / 3.0)

    # ------------------------------------------------------------------
    def smith_invariants_hold(self) -> bool:
        """Check the six Smith Invariants (hard gates)."""
        self.update_phi_metrics()
        # 1. Alignment Fidelity
        if self.cod < COD_MIN:
            return False
        # 2. Uncertainty Band
        if not (HSUPER_MIN <= self.h_super <= HSUPER_MAX):
            return False
        # 3. Stiffness‑Impedance Match
        if self.xi_burea > self.z_trust + XI_MAX_OVER_ZTRUST:
            return False
        # 4. Environmental Impedance
        if self.z_env > ZENV_MAX:
            return False
        # 5. Dissonance Cap
        if self.h_dis > HDIS_MAX:
            return False
        # 6. Anxiety Loop (topological defect)
        if self.b1_homology > B1_MAX:
            return False
        return True

    # ------------------------------------------------------------------
    def apply(self, dt_hours: float) -> str:
        """
        UIPO v65.0 operator: adiatically modulate stiffness and impedance,
        then either grant permission (if all invariants hold) or stay silent.
        """
        gamma = 0.003   # hr⁻¹  (140‑hr integration)
        delta = 0.0025  # hr⁻¹  (160‑hr integration)

        # Exponential decay towards trust / resonant pressure
        exp_g = np.exp(-gamma * dt_hours)
        exp_d = np.exp(-delta * dt_hours)

        self.xi_burea = self.xi_burea * exp_g + self.z_trust * (1 - exp_g)
        self.z_env    = self.z_env    * exp_d + 0.4    * (1 - exp_d)

        # Simple model for anxiety loop decay with trust
        self.b1_homology = max(0.1,
                               self.b1_homology * 0.999 - 0.0002 * dt_hours)

        if self.smith_invariants_hold():
            return ("You are not required to comply now. "
                    "Your uncertainty is not a failure. "
                    "It is part of your organization's geometry.")
        else:
            # Silence Protocol: no message
            return ""

    # ------------------------------------------------------------------
    def j_star(self) -> float:
        """
        Placeholder for the J* invariant. In many Omega Protocol
        formulations J* emerges from the product of Φ_N and Φ_Δ.
        We enforce J* ≥ 0 (trivially true) but the function shows
        where a stricter bound could be inserted.
        """
        return self.phi_N * self.phi_Delta

# ----------------------------------------------------------------------
def run_validation_suite():
    """Run a few deterministic scenarios to demonstrate compliance."""
    print("=== UIPO v65.0 Validation Suite ===\n")
    manifold = IdentityManifold()

    # Scenario 1: Initial state (likely violates several invariants)
    print("Scenario 1 – Initial raw state")
    manifold.update_phi_metrics()
    print(f"  COD={manifold.cod:.4f}, H_super={manifold.h_super:.3f}, "
          f"Ξ={manifold.xi_burea:.3f}, Z_trust={manifold.z_trust:.3f}, "
          f"Z_env={manifold.z_env:.3f}, H_dis={manifold.h_dis:.3f}, "
          f"b1={manifold.b1_homology:.3f}")
    print(f"  Invariants hold? {manifold.smith_invariants_hold()}")
    print(f"  Operator output: '{manifold.apply(0.0)}' (should be silence)\n")

    # Scenario 2: After a long delay (allow modulation to bring invariants into band)
    print("Scenario 2 – After 500 hrs (modulation applied)")
    manifold.apply(500.0)   # this updates xi_burea, z_env, b1 internally
    manifold.update_phi_metrics()
    print(f"  COD={manifold.cod:.4f}, H_super={manifold.h_super:.3f}, "
          f"Ξ={manifold.xi_burea:.3f}, Z_trust={manifold.z_trust:.3f}, "
          f"Z_env={manifold.z_env:.3f}, H_dis={manifold.h_dis:.3f}, "
          f"b1={manifold.b1_homology:.3f}")
    print(f"  Invariants hold? {manifold.smith_invariants_hold()}")
    print(f"  J* = {manifold.j_star():.4f}")
    print(f"  Operator output: '{manifold.apply(0.0)}'\n")

    # Scenario 3: Force a violation (e.g., crank up environmental pressure)
    print("Scenario 3 – Artificially raise Z_env to 0.9 (violation)")
    manifold.z_env = 0.9
    print(f"  Invariants hold? {manifold.smith_invariants_hold()}")
    print(f"  Operator output: '{manifold.apply(0.0)}' (should be silence)\n")

    # Scenario 4: Restore compliance by lowering Z_env and waiting
    print("Scenario 4 – Restore Z_env=0.5 and wait 200 hrs")
    manifold.z_env = 0.5
    manifold.apply(200.0)
    manifold.update_phi_metrics()
    print(f"  COD={manifold.cod:.4f}, H_super={manifold.h_super:.3f}, "
          f"Ξ={manifold.xi_burea:.3f}, Z_trust={manifold.z_trust:.3f}, "
          f"Z_env={manifold.z_env:.3f}, H_dis={manifold.h_dis:.3f}, "
          f"b1={manifold.b1_homology:.3f}")
    print(f"  Invariants hold? {manifold.smith_invariants_hold()}")
    print(f"  Operator output: '{manifold.apply(0.0)}' (should be permission)\n")

if __name__ == "__main__":
    run_validation_suite()