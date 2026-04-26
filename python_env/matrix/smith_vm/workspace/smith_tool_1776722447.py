# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega‑QED Shredding‑Flaw Validator
-----------------------------------
Checks a parameter set for compliance with the Omega Protocol invariants
and detects premature divergence / lattice collapse that would break
Poisson recovery of Φ_N.

Author: Agent Smith (Matrix Guardian)
"""

import math
import numpy as np

def validate_point(g, m, Phi_N, Phi_Delta, epsilons):
    """
    Parameters
    ----------
    g : float
        Coupling constant in the mass‑modulation ansatz.
    m : float
        Bare mass scale.
    Phi_N : float
        Isotropic scalar field.
    Phi_Delta : float
        Anisotropic scalar field.
    epsilons : array‑like
        Anisotropy coefficients ε_i (must sum to zero).

    Returns
    -------
    dict
        Validation results and flags.
    """
    epsilons = np.asarray(epsilons, dtype=float)
    if not np.isclose(epsilons.sum(), 0.0):
        raise ValueError("Anisotropy coefficients must sum to zero.")

    # Basic derived quantities
    eps = g * Phi_N / m                     # ε ≡ gΦ_N/m
    coshD = math.cosh(Phi_Delta)
    exp_absD = math.exp(abs(Phi_Delta))

    # Effective masses
    m_e = m * (1 - eps * math.exp(Phi_Delta))
    m_p = m * (1 - eps * math.exp(-Phi_Delta))
    m_eff_sq = m_e * m_p                     # = m^2 * (1 - 2ε coshΦΔ + ε^2)
    m_eff = math.sqrt(max(m_eff_sq, 0.0))    # guard against tiny negatives from rounding

    # 1) Mass‑positivity (individual)
    pos_e = m_e > 0
    pos_p = m_p > 0

    # 2) Shredding bound (1): Φ_N < (m/g) * exp(-|ΦΔ|)
    shred_bound = Phi_N < (m / g) * math.exp(-abs(Phi_Delta))

    # 3) Lattice‑collapse bound (5): |ΦΔ| < 1 / max|ε_i|
    max_eps = np.max(np.abs(epsilons))
    lattice_crit = 1.0 / max_eps if max_eps > 0.0 else float('inf')
    lattice_ok = abs(Phi_Delta) < lattice_crit

    # 4) Effective expansion parameter (perturbative safety)
    eps_eff = eps * coshD
    eps_eff_ok = eps_eff < 1.0

    # 5) Renormalized expansion (corrected prescription)
    tilde_eps = eps * exp_absD
    tilde_eps_ok = tilde_eps < 1.0

    # 6) Reality of m_eff (product > 0)
    m_eff_real = m_eff_sq > 0.0

    # 7) Poisson‑recovery: all lattice spacings a_i = a0(1+ε_i ΦΔ) must stay >0
    #    We set a0 = 1 w.l.o.g.; the condition is 1 + ε_i ΦΔ > 0 ∀i.
    a_i = 1.0 + epsilons * Phi_Delta
    lattice_spacings_ok = np.all(a_i > 0.0)

    # Overall compliance (Omega Protocol)
    compliant = (
        pos_e and pos_p and shred_bound and lattice_ok and
        eps_eff_ok and tilde_eps_ok and m_eff_real and lattice_spacings_ok
    )

    # Assemble report
    report = {
        "epsilon": eps,
        "coshΦΔ": coshD,
        "exp|ΦΔ|": exp_absD,
        "m_e": m_e,
        "m_p": m_p,
        "m_eff": m_eff,
        "m_eff_sq": m_eff_sq,
        "mass_pos_e": pos_e,
        "mass_pos_p": pos_p,
        "shredding_bound_ok": shred_bound,
        "lattice_crit": lattice_crit,
        "lattice_bound_ok": lattice_ok,
        "eps_eff": eps_eff,
        "eps_eff_ok": eps_eff_ok,
        "tilde_eps": tilde_eps,
        "tilde_eps_ok": tilde_eps_ok,
        "m_eff_real": m_eff_real,
        "lattice_spacings": a_i.tolist(),
        "lattice_spacings_ok": bool(lattice_spacings_ok),
        "poisson_recovery_ok": bool(lattice_spacings_ok and m_eff_real),
        "overall_compliant": bool(compliant),
        "shredding_flag": not compliant
    }
    return report

def pretty_print(rep):
    print("\n=== Omega‑QED Shredding Validation ===")
    for k, v in rep.items():
        if isinstance(v, float):
            print(f"{k:25}: {v:.6g}")
        else:
            print(f"{k:25}: {v}")
    print("\nShredding Detected?" , "YES" if rep["shredding_flag"] else "NO")
    print("Protocol Compliant?" , "YES" if rep["overall_compliant"] else "NO")

# ----------------------------------------------------------------------
# Example usage – feel free to modify the parameters to test edge cases.
if __name__ == "__main__":
    # Sample parameters (feel free to tweak)
    g_val   = 0.02
    m_val   = 1.0
    PhiN_val = 0.3          # try increasing to see shredding
    PhiD_val = 1.5          # try large positive/negative
    epsilons = [0.2, -0.1, -0.1]   # must sum to zero

    rep = validate_point(g_val, m_val, PhiN_val, PhiD_val, epsilons)
    pretty_print(rep)

    # ------------------------------------------------------------------
    # Additionally, we can scan a grid to locate the shredding threshold.
    print("\n--- Grid scan for premature ε_eff ≥ 1 ---")
    PhiN_scan = np.linspace(0.01, 0.5, 50)
    PhiD_scan = np.linspace(-2.0, 2.0, 50)
    violations = []
    for PhiN in PhiN_scan:
        for PhiD in PhiD_scan:
            r = validate_point(g_val, m_val, PhiN, PhiD, epsilons)
            if not r["eps_eff_ok"]:
                violations.append((PhiN, PhiD, r["eps_eff"]))
    if violations:
        print(f"Found {len(violations)} points where ε_eff ≥ 1 (premature blow‑up).")
        print("Example worst case:", max(violations, key=lambda x: x[2]))
    else:
        print("No ε_eff ≥ 1 found in the scanned region.")