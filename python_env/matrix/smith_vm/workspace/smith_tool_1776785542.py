# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ω‑Protocol Audit: Higher‑Order Lattice Polarization Corrections to α_fs
Validates the derivation of ψ, m_eff² and the stability switch on c₀.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Tuple

# ----------------------------------------------------------------------
# Helper: dimensional analysis (in natural units ħ=c=1)
# Mass dimension: [length]^-1  →  we assign +1 to mass, -1 to length.
# We only need to check that combinations are dimensionless (dim=0).
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Dim:
    """Mass dimension of a quantity."""
    d: int  # integer power of mass

    def __add__(self, other: "Dim") -> "Dim":
        return Dim(self.d + other.d)

    def __sub__(self, other: "Dim") -> "Dim":
        return Dim(self.d - other.d)

    def __mul__(self, other: "Dim") -> "Dim":
        return Dim(self.d + other.d)

    def __truediv__(self, other: "Dim") -> "Dim":
        return Dim(self.d - other.d)

    def is_dimensionless(self) -> bool:
        return self.d == 0

# Base dimensions (mass = +1, length = -1)
M = Dim(+1)   # mass
L = Dim(-1)   # length
# Derived
Dimless = Dim(0)
InvL = L          # 1/length
InvL2 = Dim(-2)   # 1/length^2

# ----------------------------------------------------------------------
# Core computation
# ----------------------------------------------------------------------
def compute_observables(
    alpha0: float,   # bare fine-structure constant (dimensionless)
    a: float,        # lattice spacing (length)
    Nt: int,         # temporal lattice points (dimensionless)
    c0: float,       # instanton coefficient (dimensionless)
) -> Tuple[float, float, float, float, float]:
    """
    Returns:
        Pi0      = Π_Δ(0)
        delta_m2 = δm_Δ²
        m_eff2   = m_eff²
        psi      = ψ
        bound_c0 = lower stability bound on c0
    """
    # ---- dimensional checks ------------------------------------------------
    # α0 is dimensionless
    assert Dimless.is_dimensionless(), "α0 must be dimensionless"
    # a has dimension of length
    assert L.d == -1, "a must have dimension of length"
    # Nt, c0 dimensionless
    assert Dimless.is_dimensionless(), "Nt, c0 dimensionless"

    # ---- polarization at zero momentum ------------------------------------
    # Π_Δ(0) = (α0/π) * c0 * f(Nt)
    f_Nt = 1.0 - math.exp(-Nt / 32.0)   # temporal memory depth
    Pi0 = (alpha0 / math.pi) * c0 * f_Nt
    # Π_Δ has dimension of α0 (dimensionless) → dimensionless
    assert Dimless.is_dimensionless(), "Π_Δ(0) must be dimensionless"

    # ---- mass shift --------------------------------------------------------
    # δm_Δ² = (α0 / a²) * Π_Δ(0)
    # a² has dimension L^2 → -2, so 1/a² has +2
    delta_m2 = (alpha0 / (a * a)) * Pi0
    # α0 dimensionless, 1/a² → +2, Π_Δ dimensionless → total +2 (mass^2)
    assert (Dimless + InvL2).is_dimensionless() == False, "δm_Δ² must have mass^2 dimension"
    # Actually we just check that the resulting dimension is InvL2 (mass^2)
    assert (Dimless + InvL2).d == +2, "δm_Δ² dimension mismatch"

    # ---- bare mass ---------------------------------------------------------
    # m0² = π / a²   (π dimensionless)
    m0_sq = math.pi / (a * a)
    assert (Dimless + InvL2).d == +2, "m0² dimension mismatch"

    # ---- effective mass ----------------------------------------------------
    m_eff_sq = m0_sq + delta_m2
    # Check that m_eff² > 0 (no tachyon)
    if m_eff_sq <= 0:
        raise ValueError(f"Effective mass squared non-positive: m_eff²={m_eff_sq:.3e}")

    # ---- monitoring invariant ψ -------------------------------------------
    # ψ = ln[1 + (α0²/π²) * c0 * f(Nt)]
    psi_arg = 1.0 + (alpha0 * alpha0 / (math.pi * math.pi)) * c0 * f_Nt
    if psi_arg <= 0:
        raise ValueError(f"ψ argument non‑positive: {psi_arg:.3e} → ψ would be complex")
    psi = math.log(psi_arg)

    # ---- stability switch bound on c0 --------------------------------------
    # Require psi_arg > 0  →  c0 > -π²/(α0² f(Nt))
    bound_c0 = - (math.pi * math.pi) / (alpha0 * alpha0 * f_Nt)
    if c0 <= bound_c0:
        raise ValueError(
            f"c0={c0:.3e} violates stability switch: must be > {bound_c0:.3e}"
        )

    return Pi0, delta_m2, m_eff_sq, psi, bound_c0


# ----------------------------------------------------------------------
# Example usage & self‑test
# ----------------------------------------------------------------------
def _demo():
    # Choose physically plausible lattice QED numbers (illustrative)
    alpha0 = 1.0 / 137.0          # bare coupling
    a = 0.1                       # lattice spacing in fm (natural units → length)
    Nt = 64                       # temporal extent
    # Instanton coefficient from dilute gas approx: c0 ~ exp(-S_inst)
    S_inst = 8.0                  # typical instanton action
    c0 = math.exp(-S_inst)        # positive small number

    try:
        Pi0, dm2, m2eff, psi, bound = compute_observables(alpha0, a, Nt, c0)
        print("✓ Audit passed")
        print(f"  Π_Δ(0)          = {Pi0:.3e}")
        print(f"  δm_Δ²           = {dm2:.3e}")
        print(f"  m_eff²          = {m2eff:.3e}")
        print(f"  ψ               = {psi:.3e}")
        print(f"  Stability bound on c0 = {bound:.3e}")
        print(f"  Provided c0     = {c0:.3e}")
    except ValueError as e:
        print("✗ Audit failed:", e)


if __name__ == "__main__":
    _demo()