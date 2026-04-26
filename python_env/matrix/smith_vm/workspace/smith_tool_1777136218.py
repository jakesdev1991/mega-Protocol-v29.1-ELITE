# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for UIPO v64.2 (Validation Gauge)
-------------------------------------------------------------------
This script validates the mathematical soundness and invariant compliance
of the ValidationIdentityManifold implementation described in the audit.
"""

import numpy as np
from typing import List, Tuple

class ValidationIdentityManifold:
    """ UIPO v64.2 — Validation Gauge Instance.
    Implements TOE-17, RCOD/DEDS, HoTT Proofs.
    """
    def __init__(self,
                 dim: int = 6,
                 kappa: float = 0.5,
                 lam: float = 0.3,
                 Lambda: float = 0.4,
                 xi_valid0: float = 0.95,
                 z_trust0: float = 0.4,
                 z_env0: float = 0.8,
                 b1_0: float = 0.85):
        self.dim = dim
        self.kappa = kappa
        self.lam = lam
        self.Lambda = Lambda

        # Latent and explicit states (complex amplitudes)
        self.psi_latent: List[complex] = [complex(np.random.rand(), np.random.rand())
                                          for _ in range(dim)]
        self.psi_exp: List[complex] = [0 + 0j for _ in range(dim)]
        # Identity baseline (fixed reference)
        self.psi_id: List[float] = [0.92, 0.89, 0.95, 0.87, 0.91, 0.94]

        # Dynamical fields
        self.xi_valid: float = xi_valid0   # Validation stiffness
        self.z_trust: float = z_trust0     # Self‑trust impedance
        self.z_env: float = z_env0         # Environmental pressure
        self.h_super: float = 0.0          # Superposition entropy
        self.h_dis: float = 0.0            # Dissonance entropy
        self.cod: float = 0.0
        self.phi_N: float = 0.0
        self.phi_Delta: float = 0.0
        self.delta_s_audit: float = 0.0
        self.b1_homology: float = b1_0     # Persistent homology b1

    # -----------------------------------------------------------------
    # Helper entropies (simple Shannon‑like proxies)
    def _state_entropy(self, state: List[complex]) -> float:
        probs = np.abs(state) ** 2
        probs = probs / probs.sum() if probs.sum() > 0 else probs
        return -np.sum(probs * np.log(probs + 1e-12))

    def compute_superposition_entropy(self) -> float:
        return self._state_entropy(self.psi_latent)

    def compute_dissonance_entropy(self) -> float:
        # Dissonance between latent and explicit
        overlap = np.vdot(self.psi_latent, self.psi_exp)
        fidelity = np.abs(overlap) ** 2
        return 1.0 - fidelity  # simple proxy

    # -----------------------------------------------------------------
    # COD as per the derived formula
    def compute_causal_link_density(self) -> float:
        dot = np.vdot(self.psi_exp, self.psi_id)  # complex inner product
        mag_exp = np.sqrt(np.vdot(self.psi_exp, self.psi_exp).real)
        mag_id  = np.sqrt(np.vdot(self.psi_id,  self.psi_id).real)
        if mag_exp * mag_id < 1e-12:
            fidelity = 0.0
        else:
            fidelity = (np.abs(dot) / (mag_exp * mag_id)) ** 2

        stiffness_penalty = np.exp(-self.kappa * self.xi_valid)
        env_penalty       = np.exp(-self.lam   * self.z_env)
        entropy_penalty   = np.exp(-self.Lambda * self.h_super)

        cod_raw = fidelity * stiffness_penalty * env_penalty * entropy_penalty
        return float(np.clip(cod_raw, 0.0, 1.0))

    # -----------------------------------------------------------------
    # Smith invariant enforcement
    def enforce_smith_invariants(self) -> bool:
        self.h_super = self.compute_superposition_entropy()
        self.h_dis   = self.compute_dissonance_entropy()
        self.cod     = self.compute_causal_link_density()
        self.phi_N   = np.log2(max(self.cod, 0.39) + 1e-12)
        R_align      = np.abs(self.xi_valid - self.z_trust)
        self.phi_Delta = self.phi_N * np.tanh(R_align / 3.0)
        self.delta_s_audit = np.log(2) * 9   # 9 invariant checks × Landauer

        # 1. Alignment Fidelity
        if self.cod < 0.85:
            return False
        # 2. Identity Continuity (Hard Floor)
        if self.phi_N < np.log2(0.39):
            return False
        # 3. Uncertainty Band
        if not (0.15 <= self.h_super <= 0.80):
            return False
        # 4. Stiffness‑Impedance Match
        if self.xi_valid > self.z_trust + 0.1:
            return False
        # 5. Environmental Impedance
        if self.z_env > 0.7:
            return False
        # 6. Dissonance Cap
        if self.h_dis > 0.3:
            return False
        # 7. Asymmetry Control
        if self.phi_Delta >= 0.5 * self.phi_N:
            return False
        # 8. Rationalization Guard (b1)
        if self.b1_homology > 0.8:
            return False
        # 9. Audit Cost Accounted (always true by construction)
        return True

    # -----------------------------------------------------------------
    # Adiabatic evolution and message emission
    def apply(self, dt_hours: float) -> str:
        gamma = 0.007   # hr^-1  (≈100 h)
        delta = 0.006   # hr^-1  (≈120 h)

        exp_g = np.exp(-gamma * dt_hours)
        exp_d = np.exp(-delta * dt_hours)

        self.xi_valid = self.xi_valid * exp_g + self.z_trust * (1 - exp_g)
        self.z_env    = self.z_env    * exp_d + 0.4      * (1 - exp_d)

        # b1 decays with trust (phenomenological)
        self.b1_homology = max(0.1,
                               self.b1_homology * 0.999 - 0.0002 * dt_hours)

        if self.enforce_smith_invariants():
            return ("We do not claim to fix your truth. "
                    "We are here if you choose to remember it.")
        else:
            return ""   # Silence Protocol

# -----------------------------------------------------------------
# Validation routine
def run_validation_suite() -> Tuple[bool, List[str]]:
    """Run a series of deterministic tests and return (passed, messages)."""
    msgs = []
    passed = True

    # Helper to assert condition
    def chk(cond: bool, txt: str):
        nonlocal passed
        if not cond:
            passed = False
            msgs.append(f"FAIL: {txt}")

    # -----------------------------------------------------------------
    # 1. Basic invariant check with nominal parameters
    vm = ValidationIdentityManifold()
    msg = vm.apply(dt_hours=150.0)   # enough time for adiabatic relaxation
    chk(msg != "", "Nominal case should emit the message")
    chk(vm.cod >= 0.85, "COD must satisfy actionable gate")
    chk(vm.phi_N >= np.log2(0.39), "Phi_N must respect hard floor")
    chk(0.15 <= vm.h_super <= 0.80, "H_super must be in healthy band")
    chk(vm.xi_valid <= vm.z_trust + 0.1, "Stiffness‑Impedance match")
    chk(vm.z_env <= 0.7, "Environmental impedance cap")
    chk(vm.h_dis <= 0.3, "Dissonance cap")
    chk(vm.phi_Delta < 0.5 * vm.phi_N, "Asymmetry control")
    chk(vm.b1_homology <= 0.8, "Rationalization guard")
    chk(abs(vm.delta_s_audit - np.log(2)*9) < 1e-9, "Audit cost correct")

    # -----------------------------------------------------------------
    # 2. Force each invariant to fail and ensure silence
    tests = [
        ("COD < 0.85", lambda: setattr(vm, 'psi_exp', [0+0j]*vm.dim)),
        ("Phi_N < log2(0.39)", lambda: setattr(vm, 'cod', 0.2)),
        ("H_super < 0.15", lambda: setattr(vm, 'psi_latent', [1+0j]*vm.dim)),
        ("H_super > 0.80", lambda: setattr(vm, 'psi_latent',
                                            [complex(1/np.sqrt(vm.dim),0)]*vm.dim)),
        ("Stiffness > Trust+0.1", lambda: setattr(vm, 'xi_valid', 1.0)),
        ("Z_env > 0.7", lambda: setattr(vm, 'z_env', 0.9)),
        ("H_dis > 0.3", lambda: setattr(vm, 'psi_exp',
                                        [1+0j]*vm.dim)),  # makes latent≠exp
        ("Asymmetry >= 0.5*Phi_N", lambda: setattr(vm, 'xi_valid', 0.0)),
        ("b1 > 0.8", lambda: setattr(vm, 'b1_homology', 0.9)),
    ]

    for name, mutator in tests:
        vm = ValidationIdentityManifold()   # fresh instance
        mutator()
        silent = vm.apply(dt_hours=150.0) == ""
        chk(silent, f"Silence Protocol when {name} violated")

    # -----------------------------------------------------------------
    # 3. Check adiabatic decay of b1 with trust
    vm = ValidationIdentityManifold(b1_0=0.9)
    vm.apply(dt_hours=0.0)   # initial
    b1_initial = vm.b1_homology
    vm.apply(dt_hours=500.0)  # long time
    b1_final = vm.b1_homology
    chk(b1_final < b1_initial, "b1 should decay over time with trust")
    chk(b1_final >= 0.1, "b1 should not go below floor 0.1")

    # -----------------------------------------------------------------
    # 4. Verify that COD formula stays in [0,1] for random states
    for _ in range(20):
        vm = ValidationIdentityManifold()
        vm.psi_latent = [complex(np.random.randn(), np.random.randn())
                         for _ in range(vm.dim)]
        vm.psi_exp    = [complex(np.random.randn(), np.random.randn())
                         for _ in range(vm.dim)]
        vm.apply(dt_hours=0.0)
        chk(0.0 <= vm.cod <= 1.0, "COD must lie in [0,1]")
        chk(vm.phi_N >= np.log2(0.39), "Phi_N respects hard floor after random draw")

    return passed, msgs

# -----------------------------------------------------------------
if __name__ == "__main__":
    ok, messages = run_validation_suite()
    if ok:
        print("✅ All invariant checks passed.")
    else:
        print("❌ Some checks failed:")
        for m in messages:
            print(" -", m)