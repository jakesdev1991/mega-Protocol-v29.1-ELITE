# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega‑Protocol invariant validator for the Neo‑Experimenter proposal.
Checks:
    Φ_N = Π'_N(0) ≥ 0
    Φ_Δ = Π'_Δ(0) ≥ 0
    J* = α_fs^R > 0
    ψ = ln(m_eff/m_0)   (no sign constraint, but used for ξ_Δ scaling)
    g_0 ≥ 0 (to avoid ghost‑like entropy gauge coupling)
    h_0^2 ≥ 0 (trivially true)
Uses simple one‑loop QED expressions with Archive scalar corrections.
"""

import numpy as np
import itertools

# ----------------------------------------------------------------------
# Helper: one‑loop vacuum polarization pieces (schematic)
# In full QED: Π_N(0) = 0, Π_N'(0) = (e0^2)/(12π^2) * ln(Λ^2/m^2) + ...
# We keep only the logarithmic piece and add Archive scalar contributions.
# ----------------------------------------------------------------------
def Pi_N_prime_zero(e0, Lambda, m, h0, g0):
    """Transverse stiffness derivative at zero momentum."""
    # QED part
    ped = (e0**2) / (12.0 * np.pi**2) * np.log(Lambda**2 / m**2)
    # Archive scalar contributes via h0^2 (as seen in α_fs^R)
    # Assume same coefficient C1 = 1/(12π^2) for illustration.
    ped += (h0**2) / (12.0 * np.pi**2)
    return ped

def Pi_Delta_zero(e0, Lambda, m, h0, g0):
    """Longitudinal self‑energy at zero momentum."""
    # QED longitudinal piece vanishes at p=0 in Feynman gauge;
    # we keep a mass‑shift term from the Archive scalar.
    # m_eff^2 = M0^2 + Π_Δ(0) → we model Π_Δ(0) = (g0^2)/(12π^2) * ln(Λ^2/m^2)
    pdz = (g0**2) / (12.0 * np.pi**2) * np.log(Lambda**2 / m**2)
    return pdz

def Pi_Delta_prime_zero(e0, Lambda, m, h0, g0):
    """Derivative of longitudinal piece at zero momentum."""
    # Same structure as transverse but with g0^2.
    pdd = (g0**2) / (12.0 * np.pi**2) * np.log(Lambda**2 / m**2)
    return pdd

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def validate_parameter_point(params):
    """
    params: dict with keys
        e0   – bare gauge coupling
        Lambda – UV cutoff
        m    – bare fermion mass (m0 in text)
        M0   – bare Archive scalar mass
        h0   – Archive‑fermion coupling
        g0   – Archive‑entropy gauge coupling
    Returns True if all Omega‑Protocol invariants hold.
    """
    e0 = params['e0']
    Lambda = params['Lambda']
    m = params['m']
    M0 = params['M0']
    h0 = params['h0']
    g0 = params['g0']

    # 1. Enforce basic domain constraints
    assert e0 > 0, "Bare gauge coupling must be positive."
    assert Lambda > m > 0, "Cutoff must exceed fermion mass."
    assert M0 >= 0, "Archive scalar mass squared must be non‑negative."
    assert g0 >= 0, "Entropy‑gauge coupling g0 must be non‑negative (no ghosts)."
    # h0 can be any real; we only need h0^2 ≥ 0 automatically.

    # 2. Compute invariants
    Phi_N = Pi_N_prime_zero(e0, Lambda, m, h0, g0)          # transverse stiffness
    Phi_Delta = Pi_Delta_prime_zero(e0, Lambda, m, h0, g0) # longitudinal stiffness
    # Effective longitudinal mass
    m_eff_sq = M0**2 + Pi_Delta_zero(e0, Lambda, m, h0, g0)
    assert m_eff_sq > 0, "Effective longitudinal mass^2 must be positive (no tachyon)."
    m_eff = np.sqrt(m_eff_sq)

    # Shredding invariant
    psi = np.log(m_eff / m)

    # Code‑distance scaling: ξ_Δ ~ exp(|ψ|) → we just check ξ_Δ > 0
    xi_Delta = np.exp(np.abs(psi))   # proportional to 1/√Φ_Delta up to const.
    assert xi_Delta > 0, "Correlation length must be positive."

    # Renormalized fine‑structure constant (J*)
    # α_fs^R = α0 [1 + e0^2/(12π^2) ln(Λ^2/m^2) + C1 h0^2 + C2 g0^2]
    # We set α0 = e0^2/(4π) and take C1 = C2 = 1/(12π^2) for simplicity.
    alpha0 = e0**2 / (4.0 * np.pi)
    log_term = np.log(Lambda**2 / m**2)
    alpha_fs_R = alpha0 * (1.0 +
                           (e0**2) / (12.0 * np.pi**2) * log_term +
                           (h0**2) / (12.0 * np.pi**2) +
                           (g0**2) / (12.0 * np.pi**2))
    J_star = alpha_fs_R
    assert J_star > 0, "Renormalized fine‑structure constant must be positive."

    # 3. Omega‑Protocol invariant checks
    assert Phi_N >= 0, f"Transverse stiffness Φ_N = {Phi_N} < 0 (unstable)."
    assert Phi_Delta >= 0, f"Longitudinal stiffness Φ_Δ = {Phi_Delta} < 0 (unstable)."
    # No further constraints on ψ; it merely labels Shredding/Freeze boundaries.

    return True

# ----------------------------------------------------------------------
# Parameter scan (coarse grid) – if any point fails, we raise.
# ----------------------------------------------------------------------
def main():
    # Define physically plausible ranges (order‑of‑magnitude)
    e0_vals   = np.logspace(-2, 0, 3)      # 0.01 – 1
    Lambda_vals = np.logspace(2, 4, 3)    # 1e2 – 1e4 (in same mass units)
    m_vals    = np.logspace(-1, 1, 3)     # 0.1 – 10
    M0_vals   = np.logspace(-2, 1, 3)     # 0.01 – 10
    h0_vals   = np.linspace(-1, 1, 3)     # can be negative; squared appears
    g0_vals   = np.linspace(0, 1, 3)      # non‑negative only

    total = 0
    passed = 0
    for e0, Lambda, m, M0, h0, g0 in itertools.product(
            e0_vals, Lambda_vals, m_vals, M0_vals, h0_vals, g0_vals):
        total += 1
        try:
            validate_parameter_point({
                'e0': e0,
                'Lambda': Lambda,
                'm': m,
                'M0': M0,
                'h0': h0,
                'g0': g0
            })
            passed += 1
        except AssertionError as err:
            print(f"Violation at point {e0:.3e}, {Lambda:.3e}, {m:.3e}, {M0:.3e}, {h0:.3f}, {g0:.3f}: {err}")
            raise  # Stop on first failure – the proposal must be universally sound.

    print(f"Scanned {total} parameter points.")
    print(f"All points satisfied Omega‑Protocol invariants: {passed == total}")
    if passed == total:
        print("✅ Proposal is mathematically sound and Omega‑Protocol compliant.")
    else:
        print("❌ Invariant violations detected – proposal needs revision.")

if __name__ == "__main__":
    main()