# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Validation Script
--------------------------------
Checks the mathematical consistency of the Higher‑Order Lattice Polarization
derivation with respect to the Omega invariants:
    - mass‑positivity (both fermion masses > 0)
    - real effective mass
    - lattice‑spacing positivity (no collapse)
    - Poisson‑recovery source term well‑defined
    - entropy normalization (if requested)

The script can be used to test arbitrary parameter points
(Phi_N, Phi_Delta, g, m, epsilon_i) and to verify that the
proposed corrections respect the invariants.
"""

import numpy as np
import itertools

# ----------------------------------------------------------------------
# User‑definable parameters (feel free to change for a scan)
# ----------------------------------------------------------------------
g      = 0.5          # coupling constant
m      = 1.0          # bare mass scale
Phi_N  = 0.2          # scalar background (to be tested)
Phi_D  = 0.8          # anisotropy background (to be tested)
epsilons = np.array([0.3, -0.3, 0.0])   # example anisotropic coefficients, sum=0
lattice_crit = 2.0    # Phi_Delta^crit = 1 / max|eps_i|
k_smooth   = 10.0     # sharpness of smooth cutoff (tanh)
use_smooth_cutoff = True
check_entropy = True
# ----------------------------------------------------------------------


def mass_eff(Phi_N, Phi_D):
    """Effective mass from the geometric mean."""
    eps = g * Phi_N / m
    return m * np.sqrt(1 - 2 * eps * np.cosh(Phi_D) + eps**2)


def masses_individual(Phi_N, Phi_D):
    """Individual electron/proton effective masses."""
    eps = g * Phi_N / m
    m_e = m * (1 - eps * np.exp(+Phi_D))
    m_p = m * (1 - eps * np.exp(-Phi_D))
    return m_e, m_p


def lattice_spacings(Phi_D, smooth=True):
    """Lattice spacing a_i for each direction i."""
    a0 = 1.0   # set bare spacing to 1 (scale irrelevant for positivity test)
    if smooth:
        # smooth cutoff: 0.5*(1+tanh[k*(crit-|Phi_D|)])
        cutoff = 0.5 * (1 + np.tanh(k_smooth * (lattice_crit - np.abs(Phi_D))))
        a_i = a0 * (1 + epsilons * Phi_D * cutoff)
    else:
        # hard Heaviside cut‑off
        cutoff = np.where(np.abs(Phi_D) < lattice_crit, 1.0, 0.0)
        a_i = a0 * (1 + epsilons * Phi_D * cutoff)
    return a_i


def source_term_PhiN(Phi_N, Phi_D):
    """
    Proxy for the Poisson source: ∂^2 Phi_N ~ g * delta m_eff.
    We compute delta m_eff = m_eff - m (shift from bare mass).
    If the lattice collapses (any a_i <= 0) we flag the source as ill‑posed.
    """
    m_eff_val = mass_eff(Phi_N, Phi_D)
    delta_m = m_eff_val - m
    a_i = lattice_spacings(Phi_D, smooth=use_smooth_cutoff)
    collapsed = np.any(a_i <= 0)
    return delta_m, collapsed


def entropy_virtual_pairs(Phi_N, Phi_D, Nk=50):
    """
    Compute Shannon entropy of virtual‑pair momentum distribution
    on a simple cubic lattice with Nk points per direction.
    Returns normalized entropy (0 <= S <= ln(Nstates)).
    """
    # momentum grid in first Brillouin zone: [-pi, pi]
    ks = np.linspace(-np.pi, np.pi, Nk)
    kx, ky, kz = np.meshgrid(ks, ks, ks, indexing='ij')
    k2 = kx**2 + ky**2 + kz**2
    m_eff2 = mass_eff(Phi_N, Phi_D)**2
    omega2 = k2 + m_eff2
    p = 1.0 / omega2
    p_norm = p / np.sum(p)   # normalize
    S = -np.sum(p_norm * np.log(p_norm + 1e-15))  # avoid log(0)
    return S


# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def validate_point(Phi_N, Phi_D):
    """Return a dict with boolean flags for each invariant."""
    # 1. Mass positivity (both fermions)
    m_e, m_p = masses_individual(Phi_N, Phi_D)
    pos_masses = (m_e > 0) and (m_p > 0)

    # 2. Real effective mass (m_eff^2 > 0)
    m_eff_sq = mass_eff(Phi_N, Phi_D)**2
    real_mass = m_eff_sq > 0

    # 3. Lattice spacing positivity (no collapse)
    a_i = lattice_spacings(Phi_D, smooth=use_smooth_cutoff)
    lattice_ok = np.all(a_i > 0)

    # 4. Poisson‑recovery source well‑defined
    delta_m, collapsed = source_term_PhiN(Phi_N, Phi_D)
    poisson_ok = (not collapsed) and np.isfinite(delta_m)

    # 5. Entropy (optional)
    if check_entropy:
        S = entropy_virtual_pairs(Phi_N, Phi_D)
        entropy_ok = np.isfinite(S) and (S >= 0)
    else:
        entropy_ok = True
        S = None

    return {
        "Phi_N": Phi_N,
        "Phi_D": Phi_D,
        "m_e": m_e,
        "m_p": m_p,
        "m_eff": np.sqrt(m_eff_sq) if real_mass else np.nan,
        "pos_masses": pos_masses,
        "real_mass": real_mass,
        "lattice_ok": lattice_ok,
        "poisson_ok": poisson_ok,
        "entropy": S,
        "entropy_ok": entropy_ok,
        "all_ok": pos_masses and real_mass and lattice_ok and poisson_ok and entropy_ok,
    }


# ----------------------------------------------------------------------
# Example usage: scan a small grid to illustrate violations
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print("Omega‑Protocol Validation Scan")
    print("-" * 60)
    # Define a modest grid around the nominal point
    Phi_N_vals = np.linspace(0.0, 0.5, 6)
    Phi_D_vals = np.linspace(-1.5, 1.5, 9)

    violations = []
    for Phi_N in Phi_N_vals:
        for Phi_D in Phi_D_vals:
            res = validate_point(Phi_N, Phi_D)
            if not res["all_ok"]:
                violations.append((Phi_N, Phi_D, res))
                # Print first few violations for brevity
                if len(violations) <= 5:
                    print(f"Violation @ Phi_N={Phi_N:.3f}, Phi_D={Phi_D:.3f}:")
                    for k, v in res.items():
                        if k not in ("all_ok", "Phi_N", "Phi_D"):
                            print(f"  {k}: {v}")
                    print()

    print(f"Total points scanned: {len(Phi_N_vals)*len(Phi_D_vals)}")
    print(f"Points violating any invariant: {len(violations)}")
    if len(violations) > 5:
        print("... (only first 5 shown above)")

    # ------------------------------------------------------------------
    # Optional: demonstrate the exact positivity bound
    # ------------------------------------------------------------------
    print("\nExact positivity bound check:")
    eps = g * Phi_N / m
    bound = np.exp(-np.abs(Phi_D))
    print(f"For Phi_N={Phi_N}, Phi_D={Phi_D}:")
    print(f"  eps = g*Phi_N/m = {eps:.5f}")
    print(f"  Required eps < exp(-|Phi_D|) = {bound:.5f}")
    print(f"  Condition satisfied? {eps < bound}")