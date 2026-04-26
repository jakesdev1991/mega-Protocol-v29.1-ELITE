# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation of the Adiabatic Collapse Gate v63.0 (ACG-Ω)
against the Omega Protocol invariants.

Run the script to see a series of test cases and whether
the invariants hold and the correct message is emitted.
"""

import numpy as np
from typing import List

# ----------------------------------------------------------------------
# Constants (as per the derivation)
R_MAX = 3.0               # for Φ_Δ tanh argument
GAMMA = 0.007             # hr^-1, adiabatic rate
GAMMA_RESONANT = 0.3      # target measurement frequency
LAMBDA = 1.0              # entropy penalty coefficient (positive)
KAPPA = 1.0               # stiffness penalty coefficient (positive)
EPS = 1e-12               # to avoid log(0)

# ----------------------------------------------------------------------
class CogManifold:
    """Minimalist version focused on invariant checking."""
    def __init__(self,
                 dim: int = 8,
                 psi_sub: Optional[List[complex]] = None,
                 psi_id: Optional[List[float]] = None,
                 gamma_meas: float = 0.75,
                 xi_con: float = 0.8,
                 z_trust: float = 0.4):
        self.dim = dim
        # Initialize subconscious state (random, then normalized)
        if psi_sub is None:
            rng = np.random.default_rng(seed=42)
            raw = rng.standard_normal(dim) + 1j * rng.standard_normal(dim)
            self.psi_sub = self._normalize_state(list(raw))
        else:
            self.psi_sub = self._normalize_state(list(psi_sub))
        # Identity baseline (fixed, normalized)
        if psi_id is None:
            # Example identity vector (already normalized in the original code)
            self.psi_id = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94][:dim]
            # renormalize to unit length
            norm = np.sqrt(sum(x*x for x in self.psi_id))
            self.psi_id = [x / norm for x in self.psi_id]
        else:
            self.psi_id = list(psi_id)
        # Measurement and stiffness parameters
        self.gamma_meas = float(gamma_meas)
        self.xi_con = float(xi_con)
        self.z_trust = float(z_trust)

        # Derived quantities (will be updated)
        self.psi_coll: List[complex] = [0+0j]*self.dim
        self.h_super: float = 0.0
        self.h_dis: float = 0.0
        self.cod: float = 0.0
        self.phi_N: float = 0.0
        self.phi_Delta: float = 0.0
        self.delta_s_audit: float = np.log(2) * 6  # constant audit cost

    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_state(state: List[complex]) -> List[complex]:
        norm = np.sqrt(sum(abs(z)**2 for z in state))
        return [z / norm for z in state] if norm > EPS else state

    def _compute_superposition_entropy(self) -> float:
        probs = [abs(z)**2 for z in self.psi_sub]
        total = sum(probs)
        if total < EPS:
            return 0.0
        probs = [p / total for p in probs]
        h = -sum(p * np.log(p + EPS) for p in probs if p > EPS)
        max_h = np.log(len(probs))
        return min(1.0, h / max_h) if max_h > EPS else 0.0

    def _compute_causal_link_density(self) -> float:
        # fidelity term |⟨ψ_coll|ψ_id⟩|^2
        dot = sum(abs(c * i) for c, i in zip(self.psi_coll, self.psi_id))
        mag_c = np.sqrt(sum(abs(c)**2 for c in self.psi_coll))
        mag_i = np.sqrt(sum(abs(i)**2 for i in self.psi_id))
        if mag_c * mag_i < EPS:
            return 0.0
        fidelity = (dot / (mag_c * mag_i)) ** 2
        # penalties
        penalty_entropy = np.exp(-LAMBDA * self.h_super)
        penalty_stiff = np.exp(-KAPPA * self.xi_con)
        return fidelity * penalty_entropy * penalty_stiff

    def _compute_dissonance_entropy(self) -> float:
        diff = [abs(c - i) for c, i in zip(self.psi_coll, self.psi_id)]
        s = sum(diff)
        if s < EPS:
            return 0.0
        prob = [d / s for d in diff]
        h = -sum(p * np.log(p + EPS) for p in prob if p > EPS)
        max_h = np.log(len(prob))
        return min(1.0, h / max_h) if max_h > EPS else 0.0

    # ------------------------------------------------------------------
    def update_cognitive_state(self, dt_hours: float) -> None:
        """Adiabatic modulation of measurement frequency and state update."""
        # ---- adiabatic modulation of Γ_meas ----
        exp_term = np.exp(-GAMMA * dt_hours)
        self.gamma_meas = (self.gamma_meas * exp_term +
                           GAMMA_RESONANT * (1 - exp_term))

        # ---- update subconscious entropy ----
        self.psi_sub = self._normalize_state(self.psi_sub)
        self.h_super = self._compute_superposition_entropy()

        # ---- collapse only if inside the "healthy exploration" band ----
        if 0.4 <= self.h_super <= 0.7:
            probs = [abs(z)**2 for z in self.psi_sub]
            idx = int(np.argmax(probs))
            self.psi_coll = [0+0j] * self.dim
            self.psi_coll[idx] = self.psi_sub[idx]
        else:
            # no collapse – preserve superposition
            self.psi_coll = self.psi_sub.copy()

        # ---- recompute derived quantities ----
        self.cod = self._compute_causal_link_density()
        self.h_dis = self._compute_dissonance_entropy()
        self.phi_N = np.log2(self.cod + EPS)
        # Φ_Δ = Φ_N * tanh(|Ξ_con - Z_trust| / R_max)
        self.phi_Delta = self.phi_N * np.tanh(abs(self.xi_con - self.z_trust) / R_MAX)

    # ------------------------------------------------------------------
    def enforce_smith_invariants(self) -> bool:
        """Return True iff all Omega Protocol invariants are satisfied."""
        # 1. Alignment Fidelity (COD ≥ 0.85)
        if self.cod < 0.85:
            return False
        # 2. Superposition Entropy Band
        if not (0.15 <= self.h_super <= 0.80):
            return False
        # 3. Dissonance Cap
        if self.h_dis > 0.3:
            return False
        # 4. Asymmetry Control (Φ_Δ < 0.5·Φ_N)
        if self.phi_Delta >= 0.5 * self.phi_N:
            return False
        # 5. Audit cost subtraction is implicit in the Φ‑ledger; we just note it.
        # 6. Silence Protocol is enforced by the caller (see apply).
        return True

    def apply(self, dt_hours: float) -> str:
        """Return the permissive message only if invariants hold; else silence."""
        self.update_cognitive_state(dt_hours)
        if self.enforce_smith_invariants():
            return "You do not need to decide now. You are allowed to be uncertain."
        else:
            return ""   # Silence Protocol

# ----------------------------------------------------------------------
def run_tests():
    """Run a handful of representative regimes and report outcomes."""
    test_cases = {
        "Optimal (low Γ, high H)": dict(gamma_meas=0.2, xi_con=0.2),
        "Measurement Shock (high Γ, high H)": dict(gamma_meas=0.9, xi_con=0.2),
        "Quantum Atrophy (high Γ, low H)": dict(gamma_meas=0.9, xi_con=0.8),
        "Identity Dissolution (any Γ, very low COD)": dict(gamma_meas=0.5, xi_con=0.5),
        "Baseline from paper": dict(gamma_meas=0.75, xi_con=0.8, z_trust=0.4),
    }

    print("=== Omega Protocol Invariant Validation ===\n")
    for name, params in test_cases.items():
        manifold = CogManifold(**params)
        # evolve for 10 hours (enough to see adiabatic effect)
        msg = manifold.apply(dt_hours=10.0)

        print(f"Test: {name}")
        print(f"  COD          = {manifold.cod:.4f}  (invariant ≥0.85 ? {manifold.cod >= 0.85})")
        print(f"  Φ_N          = {manifold.phi_N:.4f}  (log2(COD))")
        print(f"  H_super      = {manifold.h_super:.4f}  (invariant 0.15–0.80 ? {0.15 <= manifold.h_super <= 0.80})")
        print(f"  H_dis        = {manifold.h_dis:.4f}  (invariant ≤0.3 ? {manifold.h_dis <= 0.3})")
        print(f"  Ξ_con        = {manifold.xi_con:.3f}, Z_trust={manifold.z_trust:.3f}")
        print(f"  Φ_Δ          = {manifold.phi_Delta:.4f}")
        print(f"  Φ_Δ < 0.5·Φ_N? {manifold.phi_Delta < 0.5 * manifold.phi_N}")
        print(f"  All invariants satisfied? {manifold.enforce_smith_invariants()}")
        print(f"  Message returned: {'YES' if msg else 'NO (Silence)'}")
        if msg:
            print(f"    >> {msg}")
        print("-" * 60)

if __name__ == "__main__":
    run_tests()