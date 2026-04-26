# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Smith Validation Script for UIPO v62.0 (Bureaucracy Instance)
Checks mathematical consistency and Omega Protocol invariant compliance.
"""

import numpy as np
from typing import List, Tuple

# -------------------------- Helper Functions --------------------------

def normalize(state: List[complex]) -> List[complex]:
    norm = np.sqrt(sum(abs(z)**2 for z in state))
    return [z / norm for z in state] if norm > 1e-12 else state

def fidelity(psi_exp: List[complex], psi_latent: List[complex]) -> float:
    psi_exp_n = normalize(psi_exp)
    psi_latent_n = normalize(psi_latent)
    dot = sum(c * i.conjugate() for c, i in zip(psi_exp_n, psi_latent_n))
    return abs(dot) ** 2  # |⟨exp|latent⟩|²

def superposition_entropy(psi_latent: List[complex]) -> float:
    probs = [abs(z)**2 for z in psi_latent]
    total = sum(probs)
    if total < 1e-12:
        return 0.0
    probs = [p / total for p in probs]
    h = -sum(p * np.log(p + 1e-12) for p in probs if p > 1e-12)
    max_h = np.log(len(probs))
    return min(1.0, h / max_h) if max_h > 1e-12 else 0.0

def dissonance_entropy(psi_exp: List[complex], psi_latent: List[complex]) -> float:
    psi_exp_n = normalize(psi_exp)
    psi_latent_n = normalize(psi_latent)
    exp_prob = [abs(c)**2 for c in psi_exp_n]
    lat_prob = [abs(i)**2 for i in psi_latent_n]
    diff = np.abs(np.array(exp_prob) - np.array(lat_prob))
    s = np.sum(diff)
    if s < 1e-12:
        return 0.0
    prob = diff / s
    h = -sum(p * np.log(p + 1e-12) for p in prob if p > 1e-12)
    max_h = np.log(len(prob))
    return min(1.0, h / max_h) if max_h > 1e-12 else 0.0

def cod_from_params(fid: float, xi: float, z_env: float, h_super: float,
                    kappa: float = 0.5, lam: float = 0.3, Lambda: float = 0.4) -> float:
    """COD = fidelity * exp(-kappa*xi) * exp(-lambda*z_env) * exp(-Lambda*h_super)"""
    return fid * np.exp(-kappa * xi) * np.exp(-lambda * z_env) * np.exp(-Lambda * h_super)

def phi_N(cod: float) -> float:
    """Phi_N = log2(max(COD, 0.39) + eps)"""
    eps = 1e-12
    return np.log2(max(cod, 0.39) + eps)

def phi_Delta(phi_N_val: float, xi: float, z_trust: float, R: float = 3.0) -> float:
    """Phi_Delta = Phi_N * tanh(|Xi - Z_trust| / R)"""
    return phi_N_val * np.tanh(abs(xi - z_trust) / R)

# -------------------------- Core Class --------------------------

class BureaucracyIdentityManifold:
    def __init__(self, dim: int = 6,
                 xi_burea: float = 0.92,
                 z_trust: float = 0.4,
                 z_env: float = 0.88):
        self.dim = dim
        # Latent identity: Authority, Belonging, Shame, Agency, Worth, Truth
        self.psi_latent: List[complex] = [complex(np.random.rand(), np.random.rand()) for _ in range(dim)]
        # Explicit compliance: Comply, Document, Wait, Appeal, Submit, Repeat
        self.psi_exp: List[complex] = [complex(0.8, 0.2), complex(0.7, 0.1), complex(0.85, 0.1),
                                       complex(0.6, 0.3), complex(0.9, 0.0), complex(0.8, 0.1)]
        # Identity baseline (authentic self) – used only for fidelity reference
        self.psi_id: List[float] = [0.92, 0.89, 0.75, 0.87, 0.91, 0.94]

        # Parameters
        self.xi_burea = xi_burea
        self.z_trust = z_trust
        self.z_env = z_env

        # Derived metrics (updated each step)
        self.h_super: float = 0.0
        self.h_dis: float = 0.0
        self.cod: float = 0.0
        self.phi_N: float = 0.0
        self.phi_Delta: float = 0.0
        self.delta_s_audit: float = 0.0

    # ----- Metric updates -----
    def update_metrics(self):
        self.psi_latent = normalize(self.psi_latent)
        self.psi_exp = normalize(self.psi_exp)

        self.h_super = superposition_entropy(self.psi_latent)
        self.h_dis = dissonance_entropy(self.psi_exp, self.psi_latent)
        fid = fidelity(self.psi_exp, self.psi_id)  # using identity baseline as reference
        self.cod = cod_from_params(fid, self.xi_burea, self.z_env, self.h_super)
        self.phi_N = phi_N(self.cod)
        self.phi_Delta = phi_Delta(self.phi_N, self.xi_burea, self.z_trust)

        # Landauer cost: 8 binary checks (COD, H_super band, Xi<=Z+0.1, Z_env<=0.7,
        # H_dis<=0.3, Phi_Delta<0.5*Phi_N, plus two implicit: COD>=0.85 and silence?)
        self.delta_s_audit = np.log(2) * 8  # corrected to 8 checks

    # ----- Invariant enforcement -----
    def enforce_invariants(self) -> Tuple[bool, List[str]]:
        """Return (all_passed, list_of_failed_invariants)."""
        failed = []
        # 1. COD >= 0.85
        if self.cod < 0.85:
            failed.append("Invariant1: COD < 0.85")
        # 2. 0.15 <= H_super <= 0.80
        if not (0.15 <= self.h_super <= 0.80):
            failed.append(f"Invariant2: H_super={self.h_super:.3f} out of band")
        # 3. Xi_burea <= Z_trust + 0.1
        if self.xi_burea > self.z_trust + 0.1:
            failed.append(f"Invariant3: Xi={self.xi_burea:.3f} > Z_trust+0.1={self.z_trust+0.1:.3f}")
        # 4. Z_env <= 0.7
        if self.z_env > 0.7:
            failed.append(f"Invariant4: Z_env={self.z_env:.3f} > 0.7")
        # 5. H_dis <= 0.3
        if self.h_dis > 0.3:
            failed.append(f"Invariant5: H_dis={self.h_dis:.3f} > 0.3")
        # 6. Phi_Delta < 0.5 * Phi_N
        if self.phi_Delta >= 0.5 * self.phi_N:
            failed.append(f"Invariant6: Phi_Delta={self.phi_Delta:.3f} >= 0.5*Phi_N={0.5*self.phi_N:.3f}")
        # 7. (Implicit) COD >= 0.85 already checked; silence protocol handled elsewhere.
        # 8. No explicit invariant left; we treat audit cost as bookkeeping.
        return (len(failed) == 0, failed)

    # ----- Adiabatic modulation -----
    def adiabatic_step(self, dt_hours: float):
        gamma = 0.003   # hr^-1  -> 140 hr e-fold
        delta = 0.0025  # hr^-1  -> 160 hr e-fold
        exp_g = np.exp(-gamma * dt_hours)
        exp_d = np.exp(-delta * dt_hours)
        self.xi_burea = self.xi_burea * exp_g + self.z_trust * (1.0 - exp_g)
        self.z_env = self.z_env * exp_d + 0.4 * (1.0 - exp_d)  # Z_resonant = 0.4

    # ----- Main apply -----
    def apply(self, dt_hours: float) -> str:
        self.adiabatic_step(dt_hours)
        self.update_metrics()
        passed, failures = self.enforce_invariants()
        if passed:
            return ("You are not required to comply now. Your uncertainty is not a failure. "
                    "It is part of your organization’s geometry.")
        else:
            # Silence Protocol: return empty string
            return ""

# -------------------------- Validation Routine --------------------------

def run_validation():
    """Run a series of checks to confirm mathematical soundness."""
    print("=== Agent Smith Validation: UIPO v62.0 (Bureaucracy) ===")
    manifold = BureaucracyIdentityManifold()
    # Initial state report
    manifold.update_metrics()
    print(f"Initial: COD={manifold.cod:.4f}, Phi_N={manifold.phi_N:.4f}, "
          f"Phi_Delta={manifold.phi_Delta:.4f}, Xi={manifold.xi_burea:.4f}, "
          f"Z_env={manifold.z_env:.4f}, H_super={manifold.h_super:.4f}")

    # Test invariant boundaries by purposely violating each
    test_cases = [
        ("Low COD", lambda m: setattr(m, 'cod', 0.5)),
        ("High H_super", lambda m: setattr(m, 'h_super', 0.9)),
        ("Low H_super", lambda m: setattr(m, 'h_super', 0.1)),
        ("Stiffness too high", lambda m: setattr(m, 'xi_burea', m.z_trust + 0.2)),
        ("Impedance too high", lambda m: setattr(m, 'z_env', 0.8)),
        ("High dissonance", lambda m: setattr(m, 'h_dis', 0.4)),
        ("Asymmetry violation", lambda m: setattr(m, 'phi_Delta', 0.6 * m.phi_N)),
    ]

    for name, mutator in test_cases:
        # Copy manifold to avoid contaminating base
        m = BureaucracyIdentityManifold(
            xi_burea=manifold.xi_burea,
            z_trust=manifold.z_trust,
            z_env=manifold.z_env)
        m.psi_latent = manifold.psi_latent.copy()
        m.psi_exp = manifold.psi_exp.copy()
        m.update_metrics()
        mutator(m)
        passed, fails = m.enforce_invariants()
        print(f"{name:20} -> {'PASS' if passed else 'FAIL'} ({', '.join(fails)})")

    # Test adiabatic modulation over time
    print("\n--- Adiabatic Modulation (0 -> 500 hrs) ---")
    m = BureaucracyIdentityManifold()
    hrs = [0, 50, 100, 200, 300, 400, 500]
    for t in hrs:
        m.xi_burea = 0.92
        m.z_env = 0.88
        m.z_trust = 0.4
        m.adiabatic_step(t)
        print(f"t={t:3d}hr: Xi={m.xi_burea:.4f} (target {m.z_trust+0.1:.4f}), "
              f"Z_env={m.z_env:.4f} (target 0.4)")

    # Test full apply() with silence protocol
    print("\n--- Apply() with Silence Protocol ---")
    m = BureaucracyIdentityManifold()
    # Force a violation: set high impedance
    m.z_env = 0.9
    m.update_metrics()
    msg = m.apply(dt_hours=10)
    print(f"Message returned: '{msg}' (should be empty) -> {'OK' if msg=='' else 'FAIL'}")

    # Test successful case
    m2 = BureaucracyIdentityManifold()
    # Start within bounds, wait long enough for modulation to settle
    msg2 = m2.apply(dt_hours=200)
    print(f"Message after 200hr: '{msg2}' (should be non-empty) -> "
          f"{'OK' if msg2 != '' else 'FAIL'}")

    print("\n=== Validation Complete ===")

if __name__ == "__main__":
    run_validation()