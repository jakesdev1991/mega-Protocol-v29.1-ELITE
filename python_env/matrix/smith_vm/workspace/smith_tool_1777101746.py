# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for QALF v2.1
------------------------------------------------
Validates the corrected set of invariants:
    COD          = |<Ψ_sub|Ψ_env>|^2                     (0..1)
    Φ_N          = COD                                 (identity fidelity)
    ψ            = ln(Φ_N)                             (real, ≤0)
    H_gait       = Shannon entropy of gait instability (0..1)
    ΔS_audit     = k_B * ln(2) * C_audit               (dimensionless)
    Ξ_foot, Ξ_terrain = shoe & terrain stiffness (same units)
    Φ_Δ          = ψ * tanh((Ξ_foot-Ξ_terrain)/R_max)
    b1           = first Betti number of causal lattice (int)
    γ            = AFO decay rate (0.02 hr^-1) – not an invariant, just a model param
    R_max        = 2.8 (stiffness units)

Invariants (Ω‑Protocol):
    Φ‑1: COD          ≥ 0.85
    Φ‑2: ψ            ≥ ln(0.95)   <=> COD ≥ 0.95   (after correction)
    Φ‑3: Ξ_foot       ≤ 3.0
    Φ‑4: H_gait       ≤ 0.3
    Φ‑5: ΔS_audit subtracted from Φ (no direct bound, but we check it's non‑negative)
    Φ‑6: Φ_Δ          < 0.5 * Φ_N
    Φ‑7: b1           = 0
"""

import math
from dataclasses import dataclass
from typing import NamedTuple

class ViolationError(RuntimeError):
    pass

@dataclass
class QALFState:
    # Measured / estimated quantities
    COD: float               # |<Ψ_sub|Ψ_env>|^2
    H_gait: float            # normalized gait entropy
    C_audit: float           # audit count (dimensionless)
    Xi_foot: float           # shoe stiffness
    Xi_terrain: float        # terrain stiffness
    b1: int                  # first Betti number from persistent homology
    # Optional: model parameters (not invariants)
    gamma: float = 0.02      # hr^-1, AFO rate
    R_max: float = 2.8       # stiffness units

    def __post_init__(self):
        # Basic sanity checks
        if not 0.0 <= self.COD <= 1.0:
            raise ValueError("COD must be in [0,1]")
        if not 0.0 <= self.H_gait <= 1.0:
            raise ValueError("H_gait must be normalized to [0,1]")
        if self.C_audit < 0:
            raise ValueError("Audit count cannot be negative")
        if self.Xi_foot < 0 or self.Xi_terrain < 0:
            raise ValueError("Stiffness values must be non‑negative")
        if self.b1 < 0:
            raise ValueError("b1 cannot be negative")

    # ----- Invariant evaluators -----
    def phi_N(self) -> float:
        return self.COD

    def psi(self) -> float:
        # ln(COD) is -inf at COD=0; we treat COD=0 as violation anyway
        return math.log(self.COD) if self.COD > 0 else float('-inf')

    def Phi_Delta(self) -> float:
        return self.psi() * math.tanh((self.Xi_foot - self.Xi_terrain) / self.R_max)

    def total_Phi(self) -> float:
        # Φ = log2( COD / (H_gait + ΔS_audit) ) + ψ * tanh(...)
        # ΔS_audit = k_B ln 2 * C_audit ; we set k_B ln 2 = 1 for dimensionless audit entropy
        delta_S_audit = self.C_audit  # because k_B ln 2 = 1 in our normalized units
        inner = self.COD / max(self.H_gait + delta_S_audit, 1e-12)  # avoid div0
        term1 = math.log2(inner) if inner > 0 else float('-inf')
        term2 = self.Phi_Delta()
        return term1 + term2

    def check_invariants(self):
        # Φ‑1
        if self.COD < 0.85:
            raise ViolationError(f"Φ‑1 failed: COD={self.COD:.3f} < 0.85")
        # Φ‑2 (corrected)
        if self.psi() < math.log(0.95):
            raise ViolationError(f"Φ‑2 failed: ψ={self.psi():.3f} < ln(0.95)≈{-0.0513:.3f} (implies COD<0.95)")
        # Φ‑3
        if self.Xi_foot > 3.0:
            raise ViolationError(f"Φ‑3 failed: Ξ_foot={self.Xi_foot:.3f} > 3.0")
        # Φ‑4
        if self.H_gait > 0.3:
            raise ViolationError(f"Φ‑4 failed: H_gait={self.H_gait:.3f} > 0.3")
        # Φ‑5 (audit cost must be non‑negative; subtraction already done in total_Phi)
        if self.C_audit < 0:
            raise ViolationError(f"Φ‑5 failed: negative audit count {self.C_audit}")
        # Φ‑6
        if not (self.Phi_Delta() < 0.5 * self.phi_N()):
            raise ViolationError(
                f"Φ‑6 failed: Φ_Δ={self.Phi_Delta():.3f} ≥ 0.5*Φ_N={0.5*self.phi_N():.3f}"
            )
        # Φ‑7
        if self.b1 != 0:
            raise ViolationError(f"Φ‑7 failed: b1={self.b1} ≠ 0 (topological loop detected)")
        # All good
        return True

def demo():
    # Example of a *passing* state (values chosen to satisfy all invariants)
    state = QALFState(
        COD=0.96,          # >0.95 → satisfies ψ≥ln(0.95)
        H_gait=0.22,
        C_audit=0.05,      # low audit entropy
        Xi_foot=1.8,
        Xi_terrain=2.0,
        b1=0,
        gamma=0.02,
        R_max=2.8
    )
    try:
        state.check_invariants()
        print("✅ Omega Protocol validation PASSED")
        print(f"   COD={state.COD:.3f}, ψ={state.psi():.3f}, Φ_Δ={state.Phi_Delta():.3f}")
        print(f"   Total Φ = {state.total_Phi():.3f}")
    except ViolationError as e:
        print("❌ Omega Protocol validation FAILED:", e)

    # Example of a *failing* state (COD too low)
    bad = QALFState(
        COD=0.80,   # violates Φ‑1 and Φ‑2
        H_gait=0.25,
        C_audit=0.0,
        Xi_foot=2.5,
        Xi_terrain=2.5,
        b1=0
    )
    try:
        bad.check_invariants()
    except ViolationError as e:
        print("\nExpected failure:", e)

if __name__ == "__main__":
    demo()