# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ω‑Protocol invariant validator for the Higher‑Order Lattice Polarization
derivation.  Returns PASS/FAIL and diagnostic info.
"""

import numpy as np

def gap_equation(phi_delta, lam, m0_sq, beta, kappa=0.0, gamma=0.0):
    """
    Mean‑field gap equation derived from:
        phi_delta = (lam/V) * Σ_p phi_delta / (p^2 + m_eff^2)
    With a UV cutoff Λ and approximating the sum by an integral:
        Σ_p 1/(p^2 + m_eff^2) ≈ 2π^2 * (Λ - sqrt(m_eff^2)*atan(Λ/sqrt(m_eff^2)))
    For simplicity we set Λ=1 and absorb constants into lam.
    """
    # effective mass squared with optional safeguard
    if kappa == 0.0:
        m_eff_sq = m0_sq - lam * phi_delta**2
    else:
        m_eff_sq = m0_sq - lam * phi_delta**2 / (1.0 + kappa * phi_delta**2)
    # avoid division by zero or negative under sqrt in the integral
    if m_eff_sq <= 0:
        return np.inf   # signals tachyonic/run-away
    # crude integral approximation (UV cutoff = 1)
    Lambda = 1.0
    integral = 2.0 * np.pi**2 * (Lambda - np.sqrt(m_eff_sq) * np.arctan(Lambda/np.sqrt(m_eff_sq)))
    return lam * integral * phi_delta   # RHS of gap eq.

def poisson_source_finite(phi_delta_max, beta, gamma=0.0):
    """
    Checks whether the source term rho = rho0 + beta * phi_delta^2 / (1+gamma*phi_delta^2)
    remains bounded.  We set rho0 = 0 for the test; any finite bound implies a finite
    Phi_N solution via the Poisson integral in 3D (∫ rho/|x| d^3x < ∞ if rho bounded).
    """
    if gamma == 0.0:
        rho = beta * phi_delta_max**2
    else:
        rho = beta * phi_delta_max**2 / (1.0 + gamma * phi_delta_max**2)
    return np.isfinite(rho)

def validate(lam, m0_sq, beta, kappa=0.0, gamma=0.0, max_iter=50, tol=1e-6):
    """
    Main validation routine.
    Returns a dict with pass/fail flags and messages.
    """
    # 1. Mass‑gap invariant
    phi_crit = np.sqrt(m0_sq / lam) if lam > 0 else np.inf
    # 2. Iterate gap equation starting from a small seed
    phi = 1e-3
    history = [phi]
    for i in range(max_iter):
        rhs = gap_equation(phi, lam, m0_sq, beta, kappa, gamma)
        if not np.isfinite(rhs):
            # tachyonic condition hit
            return {
                "PASS": False,
                "FAIL_REASON": f"Tachyonic mass^2 at iteration {i}: phi={phi:.3e}",
                "CRITICAL_PHI": phi_crit,
                "EFF_MASS_SQ": m0_sq - lam*phi**2/(1+kappa*phi**2) if kappa else m0_sq - lam*phi**2,
            }
        # simple fixed‑point iteration
        phi_new = rhs
        if abs(phi_new - phi) < tol:
            phi = phi_new
            break
        phi = phi_new
        history.append(phi)
    else:
        # did not converge within max_iter
        phi = history[-1]

    # 3. Check if phi exceeded critical value
    if phi > phi_crit * (1 + 1e-12):   # allow tiny numerical overshoot
        return {
            "PASS": False,
            "FAIL_REASON": f"Asymmetry exceeded critical value: phi={phi:.3e} > phi_c={phi_crit:.3e}",
            "CRITICAL_PHI": phi_crit,
            "FINAL_PHI": phi,
        }

    # 4. Poisson source boundedness check
    source_ok = poisson_source_finite(phi, beta, gamma)
    if not source_ok:
        return {
            "PASS": False,
            "FAIL_REASON": f"Poisson source diverges for phi={phi:.3e}",
            "FINAL_PHI": phi,
        }

    # All checks passed
    return {
        "PASS": True,
        "FINAL_PHI": phi,
        "CRITICAL_PHI": phi_crit,
        "EFF_MASS_SQ": m0_sq - lam*phi**2/(1+kappa*phi**2) if kappa else m0_sq - lam*phi**2,
        "HISTORY": history,
    }

# ----------------------------------------------------------------------
# Example usage (feel free to edit parameters)
if __name__ == "__main__":
    # Baseline parameters from the thought experiment
    lam   = 0.1
    m0_sq = 1.0
    beta  = 1.0   # arbitrary positive coupling to Phi_N source
    # Try without safeguards first
    print("=== Baseline (no safeguards) ===")
    res = validate(lam, m0_sq, beta, kappa=0.0, gamma=0.0, max_iter=30)
    print(res)

    # Now with a simple quartic stabiliser in the mass term (kappa>0)
    print("\n=== With mass‑gap safeguard (kappa=0.5) ===")
    res = validate(lam, m0_sq, beta, kappa=0.5, gamma=0.0, max_iter=30)
    print(res)

    # And with source regularisation (gamma>0)
    print("\n=== With source regularisation (gamma=0.5) ===")
    res = validate(lam, m0_sq, beta, kappa=0.0, gamma=0.5, max_iter=30)
    print(res)