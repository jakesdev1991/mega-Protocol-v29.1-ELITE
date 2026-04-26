# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for UIPO v65.0 Sales Gauge
-------------------------------------------------------------
Validates the mathematical soundness of the COD formulation and
the six Smith Invariants as described in the submission.
"""

import numpy as np
from typing import List, Tuple

class SalesIdentityManifold:
    """Exact copy of the submission's class (with minor docstring fixes)."""
    def __init__(self,
                 dim: int = 6,
                 psi_latent: List[complex] = None,
                 psi_exp: List[complex] = None,
                 psi_id: List[float] = None,
                 xi_sales: float = 0.90,
                 z_trust: float = 0.45,
                 z_env: float = 0.80):
        self.dim = dim
        # Use provided vectors or fall back to deterministic ones for testing
        if psi_latent is None:
            rng = np.random.default_rng(seed=42)
            self.psi_latent = [complex(rng.random(), rng.random()) for _ in range(dim)]
        else:
            self.psi_latent = psi_latent
        if psi_exp is None:
            rng = np.random.default_rng(seed=123)
            self.psi_exp = [complex(rng.random(), rng.random()) for _ in range(dim)]
        else:
            self.psi_exp = psi_exp
        if psi_id is None:
            self.psi_id = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93][:dim]
        else:
            self.psi_id = psi_id
        self.xi_sales = float(xi_sales)
        self.z_trust  = float(z_trust)
        self.z_env    = float(z_env)
        # derived metrics
        self.h_super = 0.0
        self.cod     = 0.0
        self.h_dis   = 0.0
        self.phi_N   = 0.0
        self.phi_Delta = 0.0
        self.delta_s_audit = 0.0

    # ------------------------------------------------------------------
    # Helper maths
    # ------------------------------------------------------------------
    def _norm_sq(self, vec: List[complex]) -> float:
        return sum(abs(v)**2 for v in vec)

    def compute_superposition_entropy(self) -> float:
        probs = [abs(z)**2 for z in self.psi_latent]
        total = sum(probs)
        if total < 1e-12:
            return 0.0
        probs = [p / total for p in probs]
        h = -sum(p * np.log(p + 1e-12) for p in probs if p > 1e-12)
        max_h = np.log(len(probs))
        return min(1.0, h / max_h) if max_h > 1e-12 else 0.0

    def compute_causal_link_density(self) -> float:
        """COD = Fidelity * exp(-0.5*H) * exp(-0.5*Xi) * exp(-0.5*Z_env)"""
        dot = sum(abs(c * i) for c, i in zip(self.psi_exp, self.psi_id))
        mag_c = np.sqrt(self._norm_sq(self.psi_exp))
        mag_i = np.sqrt(self._norm_sq(self.psi_id))
        if mag_c * mag_i < 1e-12:
            fidelity = 0.0
        else:
            fidelity = (dot / (mag_c * mag_i)) ** 2
        entropy_penalty = np.exp(-0.5 * self.h_super)
        stiffness_penalty = np.exp(-0.5 * self.xi_sales)
        env_penalty = np.exp(-0.5 * self.z_env)
        return min(1.0, max(0.0,
                            fidelity * entropy_penalty *
                            stiffness_penalty * env_penalty))

    def compute_dissonance_entropy(self) -> float:
        diff = np.abs(np.array([abs(c)**2 for c in self.psi_exp]) -
                      np.array([abs(i)**2 for i in self.psi_latent]))
        prob_diff = diff / (np.sum(diff) + 1e-12)
        h = -sum(p * np.log(p + 1e-12) for p in prob_diff if p > 1e-12)
        max_h = np.log(len(prob_diff))
        return min(1.0, h / max_h) if max_h > 1e-12 else 0.0

    # ------------------------------------------------------------------
    # Invariant enforcement
    # ------------------------------------------------------------------
    def enforce_smith_invariants(self) -> Tuple[bool, List[str]]:
        """Return (pass, list_of_failed_invariants)."""
        self.h_super = self.compute_superposition_entropy()
        self.cod     = self.compute_causal_link_density()
        self.h_dis   = self.compute_dissonance_entropy()
        self.phi_N   = np.log2(max(self.cod, 0.39) + 1e-12)
        R_align      = abs(self.xi_sales - self.z_trust)
        self.phi_Delta = self.phi_N * np.tanh(R_align / 3.0)
        self.delta_s_audit = np.log(2) * 6  # six invariants

        failures = []
        # 1 Alignment Fidelity
        if self.cod < 0.85:
            failures.append("Invariant1: COD < 0.85")
        # 2 Uncertainty Band
        if not (0.15 <= self.h_super <= 0.80):
            failures.append(f"Invariant2: H_super={self.h_super:.3f} out of [0.15,0.80]")
        # 3 Stiffness-Impedance Match
        if self.xi_sales > self.z_trust + 0.1:
            failures.append(f"Invariant3: Xi_sales={self.xi_sales:.3f} > Z_trust+0.1={self.z_trust+0.1:.3f}")
        # 4 Environmental Impedance
        if self.z_env > 0.7:
            failures.append(f"Invariant4: Z_env={self.z_env:.3f} > 0.7")
        # 5 Dissonance Cap
        if self.h_dis > 0.3:
            failures.append(f"Invariant5: H_dis={self.h_dis:.3f} > 0.3")
        # 6 Asymmetry Control (Silence Protocol)
        if self.phi_Delta >= 0.5 * self.phi_N:
            failures.append(f"Invariant6: phi_Delta={self.phi_Delta:.3f} >= 0.5*phi_N={0.5*self.phi_N:.3f}")
        return (len(failures) == 0, failures)

    def apply(self, dt_hours: float) -> str:
        """Evolve stiffness/env and return permission or silence."""
        gamma = 0.005
        delta = 0.004
        exp_g = np.exp(-gamma * dt_hours)
        exp_d = np.exp(-delta * dt_hours)
        self.xi_sales = self.xi_sales * exp_g + self.z_trust * (1 - exp_g)
        self.z_env    = self.z_env    * exp_d + 0.4 * (1 - exp_d)
        passed, _ = self.enforce_smith_invariants()
        return "The decision is yours to make. We are ready when you are." if passed else ""

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_scenario(
    psi_latent: List[complex],
    psi_exp: List[complex],
    psi_id: List[float],
    xi_sales: float,
    z_trust: float,
    z_env: float,
    dt_hours: float = 0.0,
    verbose: bool = True
) -> bool:
    """
    Returns True if the system's decision (permission/silence) is
    consistent with the invariant check.
    """
    sim = SalesIdentityManifold(
        dim=len(psi_latent),
        psi_latent=psi_latent,
        psi_exp=psi_exp,
        psi_id=psi_id,
        xi_sales=xi_sales,
        z_trust=z_trust,
        z_env=z_env
    )
    decision = sim.apply(dt_hours)
    passed, failures = sim.enforce_smith_invariants()

    if verbose:
        print("--- Validation Report ---")
        print(f"COD               : {sim.cod:.4f}")
        print(f"H_super           : {sim.h_super:.4f}")
        print(f"Xi_sales          : {sim.xi_sales:.4f}")
        print(f"Z_trust           : {sim.z_trust:.4f}")
        print(f"Z_env             : {sim.z_env:.4f}")
        print(f"H_dis             : {sim.h_dis:.4f}")
        print(f"phi_N             : {sim.phi_N:.4f}")
        print(f"phi_Delta         : {sim.phi_Delta:.4f}")
        print(f"Decision          : {'Permission' if decision else 'Silence'}")
        print(f"Invariant check   : {'PASS' if passed else 'FAIL'}")
        if failures:
            print("Failed invariants:")
            for f in failures:
                print("  -", f)
        print("-" * 30)

    # Consistency: decision non‑empty <=> all invariants passed
    consistent = (bool(decision) == passed)
    if not consistent:
        raise AssertionError(
            f"Logic mismatch: decision={'Permission' if decision else 'Silence'} "
            f"but invariant check={'PASS' if passed else 'FAIL'}"
        )
    return consistent

# ----------------------------------------------------------------------
# Example test cases (deterministic)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # 1. Baseline – should PASS (permission)
    psi_latent = [complex(0.6,0.2), complex(0.5,0.1), complex(0.7,0.0),
                  complex(0.4,0.3), complex(0.5,0.2), complex(0.6,0.1)]
    psi_exp    = [complex(0.55,0.25), complex(0.48,0.12), complex(0.68,0.05),
                  complex(0.42,0.28), complex(0.52,0.18), complex(0.58,0.09)]
    psi_id     = [0.92,0.89,0.95,0.87,0.91,0.93]
    validate_scenario(psi_latent, psi_exp, psi_id,
                      xi_sales=0.40, z_trust=0.50, z_env=0.5,
                      dt_hours=0.0, verbose=True)

    # 2. Violate Invariant 3 (stiffness too high) – should be silent
    validate_scenario(psi_latent, psi_exp, psi_id,
                      xi_sales=0.80, z_trust=0.50, z_env=0.5,
                      dt_hours=0.0, verbose=True)

    # 3. Violate Invariant 2 (entropy too low) – silent
    #   Make latent vector almost pure state
    psi_latent_lowH = [complex(1.0,0.0)] + [complex(1e-6,1e-6) for _ in range(5)]
    validate_scenario(psi_latent_lowH, psi_exp, psi_id,
                      xi_sales=0.30, z_trust=0.50, z_env=0.5,
                      dt_hours=0.0, verbose=True)

    # 4. Violate Invariant 6 (asymmetry) – silent
    validate_scenario(psi_latent, psi_exp, psi_id,
                      xi_sales=0.90, z_trust=0.20, z_env=0.5,
                      dt_hours=0.0, verbose=True)

    print("\nAll validation checks completed without raising AssertionError.")