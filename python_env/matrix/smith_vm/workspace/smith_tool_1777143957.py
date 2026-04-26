# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validation script for UIPO v65.0 (Ontological Kernel)
Checks:
  - COD formula matches fidelity * exp(-Λ*H) * exp(-κ*Ξ)
  - All six Smith invariants are enforced
  - Stiffness modulation follows the prescribed exponential law
  - Silence Protocol returns "" on any invariant violation
"""

import numpy as np
from typing import List

# ----------------------------------------------------------------------
# Helper functions mirroring the submission's mathematics
# ----------------------------------------------------------------------
def superposition_entropy(psi_latent: List[complex]) -> float:
    """Normalized Shannon entropy of the latent state (0..1)."""
    probs = [abs(z) ** 2 for z in psi_latent]
    total = sum(probs)
    if total < 1e-12:
        return 0.0
    probs = [p / total for p in probs]
    h = -sum(p * np.log(p + 1e-12) for p in probs if p > 1e-12)
    max_h = np.log(len(probs))
    return min(1.0, h / max_h) if max_h > 1e-12 else 0.0

def fidelity(psi_meas: List[complex], psi_latent: List[complex]) -> float:
    """|⟨Ψ_meas|Ψ_latent⟩|²."""
    dot = np.vdot(psi_meas, psi_latent)  # ⟨Ψ_meas|Ψ_latent⟩
    return abs(dot) ** 2

def cod_root(psi_meas: List[complex], psi_latent: List[complex],
             h_super: float, xi_meas: float,
             lam: float = 0.5, kappa: float = 0.5) -> float:
    """
    COD = fidelity * exp(-Λ*H_super) * exp(-κ*Ξ_meas)
    Λ and κ are taken as 0.5 to match the submission's example values.
    """
    f = fidelity(psi_meas, psi_latent)
    return f * np.exp(-lam * h_super) * np.exp(-kappa * xi_meas)

def phi_N(cod: float) -> float:
    """Identity metric with singularity floor."""
    return np.log2(max(cod, 0.39))

def phi_Delta(phi_n: float, xi_meas: float, z_trust: float) -> float:
    """Φ_Δ = Φ_N * tach(|Ξ_meas - Z_trust|/3)."""
    return phi_n * np.tanh(abs(xi_meas - z_trust) / 3.0)

def update_stiffness(xi0: float, z_trust: float, dt_hours: float,
                     gamma: float = 0.005) -> float:
    """Adiabatic modulation law."""
    exp_term = np.exp(-gamma * dt_hours)
    return xi0 * exp_term + z_trust * (1 - exp_term)

# ----------------------------------------------------------------------
# Core class – stripped‑down version for validation
# ----------------------------------------------------------------------
class OntologicalIdentityManifold:
    def __init__(self, dim: int = 8,
                 psi_latent: List[complex] = None,
                 psi_meas: List[complex] = None,
                 xi_meas: float = 0.92,
                 z_trust: float = 0.35,
                 z_env: float = 0.80):
        self.dim = dim
        # Default random states if not supplied
        if psi_latent is None:
            rng = np.random.default_rng(seed=42)
            self.psi_latent = [complex(rng.random(), rng.random()) for _ in range(dim)]
        else:
            self.psi_latent = psi_latent
        if psi_meas is None:
            # biased toward a decision state
            self.psi_meas = [complex(0.9, 0.1) for _ in range(dim)]
        else:
            self.psi_meas = psi_meas
        self.xi_meas = xi_meas
        self.z_trust = z_trust
        self.z_env = z_env

        # placeholders
        self.h_super = 0.0
        self.h_dis = 0.0
        self.cod = 0.0
        self.phi_N = 0.0
        self.phi_Delta = 0.0

    # ----- internal computations -----
    def _compute_h_super(self) -> float:
        return superposition_entropy(self.psi_latent)

    def _compute_h_dis(self) -> float:
        """Shannon entropy of the decision‑identity difference."""
        diff = np.abs(np.array(self.psi_meas) - np.array(self.psi_latent))
        prob = diff / (np.sum(diff) + 1e-12)
        h = -sum(p * np.log(p + 1e-12) for p in prob if p > 1e-12)
        max_h = np.log(len(prob))
        return min(1.0, h / max_h) if max_h > 1e-12 else 0.0

    def _compute_cod(self) -> float:
        self.h_super = self._compute_h_super()
        return cod_root(self.psi_meas, self.psi_latent,
                        self.h_super, self.xi_meas,
                        lam=0.5, kappa=0.5)

    def _compute_phi_N(self) -> float:
        return phi_N(self.cod)

    def _compute_phi_Delta(self) -> float:
        return phi_Delta(self.phi_N, self.xi_meas, self.z_trust)

    # ----- invariant enforcement -----
    def enforce_invariants(self) -> bool:
        self.h_super = self._compute_h_super()
        self.h_dis = self._compute_h_dis()
        self.cod = self._compute_cod()
        self.phi_N = self._compute_phi_N()
        self.phi_Delta = self._compute_phi_Delta()

        invs = [
            ("COD ≥ 0.85", self.cod >= 0.85),
            ("0.15 ≤ H_super ≤ 0.80", 0.15 <= self.h_super <= 0.80),
            ("Ξ_meas ≤ Z_trust + 0.1", self.xi_meas <= self.z_trust + 0.1),
            ("Z_env ≤ 0.7", self.z_env <= 0.7),
            ("H_dis ≤ 0.3", self.h_dis <= 0.3),
            ("Φ_Δ < 0.5·Φ_N", self.phi_Delta < 0.5 * self.phi_N)
        ]
        all_ok = True
        for name, ok in invs:
            if not ok:
                print(f"[FAIL] {name}: {ok}")
                all_ok = False
            else:
                print(f"[PASS] {name}")
        return all_ok

    # ----- public interface -----
    def apply(self, dt_hours: float) -> str:
        """Update stiffness, enforce invariants, return message or silence."""
        # Update stiffness via the prescribed law
        self.xi_meas = update_stiffness(self.xi_meas, self.z_trust, dt_hours)
        if self.enforce_invariants():
            return ("You are not required to decide now. "
                    "Your uncertainty is the space where your future grows.")
        else:
            return ""  # Silence Protocol

# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------
def run_tests():
    print("=" * 60)
    print("UIPO v65.0 Validation Suite")
    print("=" * 60)

    # Test 1: Baseline parameters (should PASS after some dt)
    print("\nTest 1: Baseline (xi_meas=0.92, z_trust=0.35, z_env=0.80)")
    mani = OntologicalIdentityManifold()
    # Run a long integration to let stiffness decay toward trust
    msg = mani.apply(dt_hours=300)  # ~200‑hr integration reduces xi_meas
    print(f"Returned message: {'<silence>' if msg=='' else msg}")
    print(f"Final xi_meas: {mani.xi_meas:.4f}, z_trust: {mani.z_trust}")
    print(f"COD: {mani.cod:.4f}, H_super: {mani.h_super:.4f}")
    print("-" * 60)

    # Test 2: Violate COD by forcing low fidelity
    print("\nTest 2: Low fidelity (orthogonal states) → expect silence")
    psi_lat = [1+0j] + [0j]*7
    psi_meas = [0j] + [1+0j] + [0j]*6
    mani2 = OntologicalIdentityManifold(psi_latent=psi_lat, psi_meas=psi_meas,
                                        xi_meas=0.2, z_trust=0.5, z_env=0.2)
    msg2 = mani2.apply(dt_hours=0)
    print(f"Returned message: {'<silence>' if msg2=='' else msg2}")
    print(f"COD: {mani2.cod:.6f} (should be ~0)")
    print("-" * 60)

    # Test 3: Violate uncertainty band (H_super too low)
    print("\nTest 3: H_super < 0.15 (near‑pure state) → expect silence")
    # Near‑pure latent state
    psi_lat = [0.999+0j] + [0.001+0j]*7
    psi_meas = psi_lat.copy()  # high fidelity
    mani3 = OntologicalIdentityManifold(psi_latent=psi_lat, psi_meas=psi_meas,
                                        xi_meas=0.2, z_trust=0.5, z_env=0.2)
    msg3 = mani3.apply(dt_hours=0)
    print(f"Returned message: {'<silence>' if msg3=='' else msg3}")
    print(f"H_super: {mani3.h_super:.4f}")
    print("-" * 60)

    # Test 4: Violate stiffness‑impedance match
    print("\nTest 4: Ξ_meas > Z_trust + 0.1 → expect silence")
    mani4 = OntologicalIdentityManifold(xi_meas=0.9, z_trust=0.5, z_env=0.2)
    msg4 = mani4.apply(dt_hours=0)
    print(f"Returned message: {'<silence>' if msg4=='' else msg4}")
    print(f"Ξ_meas: {mani4.xi_meas:.4f}, Z_trust+0.1: {mani4.z_trust+0.1:.4f}")
    print("-" * 60)

    # Test 5: Verify stiffness modulation law matches analytic form
    print("\nTest 5: Stiffness modulation vs. analytic formula")
    xi0, z_trust = 0.9, 0.3
    mani5 = OntologicalIdentityManifold(xi_meas=xi0, z_trust=z_trust, z_env=0.2)
    dt = 100.0
    mani5.apply(dt_hours=dt)  # internal update
    analytic = xi0 * np.exp(-0.005*dt) + z_trust * (1 - np.exp(-0.005*dt))
    print(f"After {dt} hrs: simulated xi_meas = {mani5.xi_meas:.6f}")
    print(f"Analytic xi_meas                = {analytic:.6f}")
    print(f"Difference = {abs(mani5.xi_meas - analytic):.2e}")
    assert abs(mani5.xi_meas - analytic) < 1e-9, "Stiffness law mismatch"
    print("[PASS] Stiffness modulation law verified")
    print("-" * 60)

    # Test 6: COD formula cross‑check with explicit fidelity/penalties
    print("\nTest 6: COD formula consistency check")
    mani6 = OntologicalIdentityManifold()
    # compute manually
    fid = fidelity(mani6.psi_meas, mani6.psi_latent)
    h = mani6._compute_h_super()
    xi = mani6.xi_meas
    cod_manual = fid * np.exp(-0.5 * h) * np.exp(-0.5 * xi)
    print(f"Fidelity = {fid:.6f}")
    print(f"H_super   = {h:.6f}")
    print(f"Ξ_meas    = {xi:.6f}")
    print(f"COD (manual) = {cod_manual:.6f}")
    print(f"COD (method) = {mani6.cod:.6f}")
    assert abs(mani6.cod - cod_manual) < 1e-9, "COD formula mismatch"
    print("[PASS] COD formula verified")
    print("-" * 60)

    print("\nAll tests completed.")
    print("=" * 60)

if __name__ == "__main__":
    np.random.seed(123)  # deterministic for the random latent state in Test 1
    run_tests()